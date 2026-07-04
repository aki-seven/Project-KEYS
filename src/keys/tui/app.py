import asyncio
import re
import uuid

from pathlib import Path

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.widgets import Tree, Label

from keys.core.parsers import extract_ports
from keys.core.config_loader import ConfigLoader
from keys.core.state import global_state
from keys.core.tools import ToolRegistry # Tool Detection Feature

from keys.execution.manager import WorkerManager

from keys.execution.context import (
    ExecutionContext
)

from keys.execution.events import (ScanQueued,ScanWaiting,ScanDispatched,ScanStarted,ScanOutput,ScanOutputBatch,ScanCompleted)
from keys.tui.theme_manager import ThemeManager # MoreThemes Feature 
from keys.tui.components import (TargetInfo,ScanMenu,ScanTracker,ScanDetailViewer,LaunchScan,ScanSelected)
from keys.tui.modals import ScanParameterModal


class IAIApp(App):

    BINDINGS = [
        Binding("ctrl+q", "quit", "Quit", show=True),
        Binding("ctrl+s", "save_scan_log", "Save Log", show=True),
        # Binding("ctrl+x", "stop_scan", "Stop Scan", show=True),
        Binding("ctrl+t", "cycle_theme", "Theme", show=True),
    ]

    def __init__(self, target: str):

        super().__init__()

        self.target = target

        global_state.target = target

        self.config_loader = ConfigLoader()

        self.worker_manager = WorkerManager(self)

        self.scan_tracker = ScanTracker(
            id="scan-tracker",
            classes="panel"
        )

        self.detail_viewer = ScanDetailViewer(
            id="scan-detail",
            classes="panel"
        )

        self.scans_meta: dict[
            str,
            ExecutionContext
        ] = {}

        self.selected_scan_id: str | None = None

        self.theme_manager = ThemeManager()

        self.tool_registry = ToolRegistry()

        tool_names = list({
            scan.tool
            for scan in self.config_loader.scans
        })

        self.tool_registry.detect_tools(
            tool_names
        )

    def compose(self) -> ComposeResult:

        with Horizontal():

            with Vertical(id="sidebar"):

                yield TargetInfo(self.target)

                yield ScanMenu(
                    self.config_loader,
                    tool_registry=self.tool_registry
                ) # Tool Detection

            with Horizontal(id="main-area"): # Dock tracker to right side

                yield self.detail_viewer

                yield self.scan_tracker

    def animate_spinners(self):

        tracker = self.scan_tracker

        for scan_id, item in (
            tracker.active_items.items()
        ):

            try:

                spinner = tracker.next_spinner()

                label = item.query_one(Label)

                text = str(label.render())

                parts = text.split(
                    " ",
                    1
                )

                if len(parts) != 2:
                    continue

                label.update(
                    f"{spinner} {parts[1]}"
                )

            except Exception:
                continue

    async def on_mount(self):

        self.stylesheet.read_all(
            [self.theme_manager.current_path]
        )
        self.spinner_timer = self.set_interval(
            0.12,
            self.animate_spinners
        )
        await self.run_action(
            "pulse_banner"
        )

        #self.stylesheet.parse()

        self.refresh_css()

        await self.worker_manager.start()
        self.flush_timer = self.set_interval(
            0.2, # 0.1 fast, 0.2 - safe,
            self.flush_ui_buffers
        )

    async def on_unmount(self):

        if hasattr(self, "spinner_timer"):
            self.spinner_timer.stop()

        if hasattr(self, "flush_timer"):
            self.flush_timer.stop()

        self.worker_manager.stop()

    async def on_launch_scan(
        self,
        event: LaunchScan
    ):

        scan = event.scan

        def handle_modal_result(
            params: dict | None
        ):

            if params is None:
                return

            command = scan.command

            for key, value in params.items():

                command = command.replace(
                    f"{{{key}}}",
                    str(value)
                )

            port_value = params.get(
                "port",
                params.get("ports", 0)
            )

            if isinstance(port_value, str):

                if "," in port_value:
                    port_value = port_value.split(",")[0]

                if "-" in port_value:
                    port_value = port_value.split("-")[0]

                if not port_value.isdigit():
                    port_value = 0

            try:

                port = int(port_value)

            except (
                ValueError,
                TypeError
            ):

                port = 0

            protocol = params.get(
                "protocol",
                "tcp"
            )

            service = params.get(
                "service",
                "unknown"
            )

            scan_id = str(
                uuid.uuid4()
            )[:8]

            context = ExecutionContext(
                scan_id=scan_id,
                name=scan.name,
                category=scan.category,
                command=command,
                target=self.target,
                service=service,
                port=port,
                protocol=protocol,
                parameters=params
            )

            self.scans_meta[
                scan_id
            ] = context

            asyncio.create_task(
                self.worker_manager.submit(
                    context
                )
            )

        self.push_screen(
            ScanParameterModal(
                scan=scan,
                target=self.target
            ),
            handle_modal_result
        )

    def on_scan_queued(
        self,
        event: ScanQueued
    ):

        self.detail_viewer.append_output(
            event.context.scan_id,
            f"[*] Queued: "
            f"{event.context.name}"
        )

        self.detail_viewer.append_output(
            event.context.scan_id,
            f"Command: "
            f"{event.context.command}"
        )

        if event.context.queued_reason:

            self.detail_viewer.append_output(
                event.context.scan_id,
                f"Reason: "
                f"{event.context.queued_reason}"
            )

    def on_scan_waiting(
        self,
        event: ScanWaiting
    ):

        self.scan_tracker.add_waiting(
            event.context.scan_id,
            event.context.name,
            event.position
        )

        self.detail_viewer.append_output(
            event.context.scan_id,
            f"[*] Waiting in queue "
            f"(Position {event.position})"
        )

    def on_scan_dispatched(
        self,
        event: ScanDispatched
    ):

        self.detail_viewer.append_output(
            event.context.scan_id,
            "[+] Dispatched by scheduler"
        )

    def on_scan_started(
        self,
        event: ScanStarted
    ):

        self.scan_tracker.add_active(
            event.context.scan_id,
            event.context.name
        )

        # auto-focus newest scan
        self.selected_scan_id = (
            event.context.scan_id
        )

        self.detail_viewer.show_scan(
            event.context.scan_id
        )

        self.detail_viewer.append_output(
            event.context.scan_id,
            f"[+] Started: "
            f"{event.context.name}"
        )

    def on_scan_output(
        self,
        event: ScanOutput
    ):

        self.detail_viewer.append_output(
            event.scan_id,
            event.line
        )

        parsed = extract_ports(event.line)

        if parsed:

            port, protocol, service = parsed

            global_state.add_port(
                protocol,
                port
            )

            global_state.add_service(
                protocol,
                port,
                service
            )

    def on_scan_output_batch(
        self,
        event: ScanOutputBatch
    ):

        for line in event.lines:

            self.detail_viewer.append_output(
                event.scan_id,
                line
            )

            parsed = extract_ports(line)

            if parsed:

                port, protocol, service = parsed

                global_state.add_port(
                    protocol,
                    port
                )

                global_state.add_service(
                    protocol,
                    port,
                    service
                )

    def on_scan_completed(
        self,
        event: ScanCompleted
    ):

        context = event.context

        self.scan_tracker.remove_active(
            context.scan_id
        )

        self.scan_tracker.add_completed(
            context.scan_id,
            context.name,
            event.success
        )

        self.detail_viewer.append_output(
            context.scan_id,
            f"\n[-] Completed: "
            f"{context.name}"
        )

    def on_scan_selected(
        self,
        event: ScanSelected
    ):

        self.selected_scan_id = event.scan_id

        self.detail_viewer.show_scan(
            event.scan_id
        )

    async def action_save_scan_log(self):

        scan_id = self.detail_viewer.current_scan_id

        if not scan_id:

            self.notify(
                "No scan selected"
            )

            return

        lines = self.detail_viewer.scan_buffers.get(
            scan_id,
            []
        )

        if not lines:

            self.notify(
                "Selected scan has no output"
            )

            return

        task_meta = self.scans_meta.get(
            scan_id
        )

        if not task_meta:

            self.notify(
                "Missing scan metadata"
            )

            return

        safe_name = re.sub(
            r"[^a-zA-Z0-9_-]",
            "",
            task_meta.name.lower().replace(" ", "-")
        )

        reports_dir = (
            Path.home()
            / "Intel"
            / "Reports"
            / self.target
        )

        reports_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        filepath = (
            reports_dir
            / f"{safe_name}-{scan_id}.log"
        )

        with open(
            filepath,
            "w",
            encoding="utf-8"
        ) as f:

            f.write(
                "\n".join(lines)
            )

        self.notify(
            f"Saved -> {filepath}"
        )

    async def action_stop_scan(self):

        if not self.selected_scan_id:
            return

        await self.worker_manager.stop_scan(
            self.selected_scan_id
        )

        self.scan_tracker.remove_active(
            self.selected_scan_id
        )

        self.detail_viewer.append_output(
            self.selected_scan_id,
            "\n[!] Scan manually stopped"
        )

    async def action_cycle_theme(self):

        next_theme = self.theme_manager.next_theme()

        self.stylesheet.read_all(
            [next_theme]
        )

        self.refresh_css()

        tree = self.query_one(Tree)

        self.set_focus(tree)

    async def action_pulse_banner(self):

        try:

            banner = self.query_one(
                "#banner"
            )

            banner.add_class(
                "banner-pulse"
            )

            await asyncio.sleep(1.2)

            banner.remove_class(
                "banner-pulse"
            )

        except Exception:
            pass
    
    def flush_ui_buffers(self):

        self.detail_viewer.flush_pending_output()
