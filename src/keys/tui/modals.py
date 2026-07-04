from textual.screen import ModalScreen
from textual.app import ComposeResult
from textual.widgets import Label, Input, Button, Static
from textual.containers import Vertical, Horizontal, ScrollableContainer

from keys.core.config_loader import ScanConfig
from keys.core.state import global_state

import pyperclip

class ScanParameterModal(ModalScreen[dict | None]):
    """Dynamic parameter modal for scan execution."""

    def __init__(
        self,
        scan: ScanConfig,
        target: str,
        port: str = "all",
        **kwargs
    ):
        super().__init__(**kwargs)

        self.scan = scan
        self.target = target
        self.port = port

    def compose(self) -> ComposeResult:
        with Vertical(id="modal-dialog", classes="panel"):

            yield Label(
                f"Launch: {self.scan.name}",
                classes="panel-title"
            )

            if self.scan.description:
                yield Label(self.scan.description)

            with ScrollableContainer(id="modal-form"): # vertical before

                for param_name, param_schema in self.scan.parameters.items():

                    default_val = str(
                        param_schema.get("default", "")
                    )

                    default_val = default_val.replace(
                        "{target}",
                        self.target
                    )

                    # Auto-fill contextual values
                    if param_name == "target":

                        default_val = self.target

                    elif param_name in ("ports", "port"):

                        matching_ports = []

                        # service-aware autofill
                        if self.scan.services:

                            for protocol, ports in global_state.services.items():

                                for port, service in ports.items():

                                    if service in self.scan.services:

                                        matching_ports.append(
                                            str(port)
                                        )

                        # fallback to discovered TCP ports
                        elif global_state.tcp_ports:

                            matching_ports = [
                                str(port)
                                for port in sorted(
                                    global_state.tcp_ports
                                )
                            ]

                        # discovered service ports
                        if matching_ports:

                            default_val = ",".join(
                                matching_ports
                            )

                        # YAML-defined defaults
                        elif self.scan.default_ports:

                            default_val = ",".join(
                                str(port)
                                for port in self.scan.default_ports
                            )

                        # final fallback
                        else:

                            default_val = self.port

                    param_type = param_schema.get(
                        "type",
                        "string"
                    )

                    yield Label(
                        f"{param_name} ({param_type})"
                    )

                    yield Input(
                        value=default_val,
                        id=f"input_{param_name}"
                    )


                yield Label(
                    "Command Preview",
                    classes="panel-title"
                )

                yield Static(
                    "",
                    id="command-preview",
                    classes="panel"
                )

            with Horizontal(id="modal-actions"):
                yield Button( # COpy action button
                    "⧉ Copy",
                    variant="success",
                    id="btn-copy-command"
                )

                yield Button(
                    "Launch",
                    variant="success",
                    id="btn-launch"
                )

                yield Button(
                    "Cancel",
                    variant="error",
                    id="btn-cancel"
                )

    def on_mount(self) -> None:
        """Focus first input automatically."""

        inputs = self.query(Input)
        if inputs:
            inputs.first().focus()

        preview = self.query_one(
            "#command-preview",
            Static
        )

        preview.update(
            self.build_command_preview()
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:

        if event.button.id == "btn-copy-command":

            command = self.build_raw_command()

            pyperclip.copy(command)

            return

        if event.button.id == "btn-cancel":
            self.dismiss(None)
            return

        if event.button.id == "btn-launch":

            result: dict[str, str] = {}

            for param_name in self.scan.parameters:

                widget_id = f"#input_{param_name}"

                inp = self.query_one(widget_id, Input)

                result[param_name] = inp.value.strip()

            self.dismiss(result)

    def build_raw_command(self) -> str:

        command = self.scan.command

        for param_name in self.scan.parameters:

            widget_id = f"#input_{param_name}"

            try:

                inp = self.query_one(
                    widget_id,
                    Input
                )

                value = inp.value.strip()

            except Exception:

                value = ""

            command = command.replace(
                f"{{{param_name}}}",
                value
            )

        return command
    
    def build_command_preview(self) -> str:

        return self.highlight_command(
            self.build_raw_command()
        )
    
    def highlight_command(
        self,
        command: str
    ) -> str:

        parts = command.split()

        highlighted = []

        for i, part in enumerate(parts):

            if i == 0:
                highlighted.append(
                    f"[bold cyan]{part}[/bold cyan]"
                )

            elif part.startswith("-"):
                highlighted.append(
                    f"[orange1]{part}[/orange1]"
                )

            elif "/" in part:
                highlighted.append(
                    f"[magenta]{part}[/magenta]"
                )

            elif "." in part:
                highlighted.append(
                    f"[green]{part}[/green]"
                )

            else:
                highlighted.append(part)

        return " ".join(highlighted)
    
    def on_input_changed(
        self,
        event: Input.Changed
    ):

        preview = self.query_one(
            "#command-preview",
            Static
        )

        preview.update(
            self.build_command_preview()
        )


    # def on_input_changed( # kept for debugging, will be removed later
    #     self,
    #     event: Input.Changed
    # ):

    #     preview = self.query_one(
    #         "#command-preview",
    #         Static
    #     )

    #     preview.update(
    #         self.build_command_preview()
    #     )