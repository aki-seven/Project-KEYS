from textual.widgets import (
    Static,
    Tree,
    RichLog,
    Label,
    ListView,
    ListItem,
    Collapsible
)

from textual.containers import Vertical
from textual.app import ComposeResult
from textual.message import Message

from keys.core.config_loader import ConfigLoader, ScanConfig
from keys.core.state import global_state

class LaunchScan(Message):

    def __init__(self, scan: ScanConfig):
        self.scan = scan
        super().__init__()


class ScanSelected(Message):

    def __init__(self, scan_id: str):
        self.scan_id = scan_id
        super().__init__()


class TargetInfo(Static):

    def __init__(self, target: str):
        super().__init__(
            f"TARGET: {target}",
            id="target-info"
        )


class ScanMenu(Vertical):

    def __init__(self, config_loader: ConfigLoader, tool_registry):
        self.config_loader = config_loader
        self.tool_registry = tool_registry
        super().__init__(
            id="scan-menu",
            classes="panel"
        )

    def compose(self) -> ComposeResult:

        yield Label(
            "Available Scans",
            classes="panel-title"
        )

        tree: Tree[ScanConfig] = Tree("Categories")

        tree.root.expand()

        categories = self.config_loader.get_categories()


        for category_name, subcats in categories.items():

            category_node = tree.root.add(
                category_name,
                expand=True
            )

            for subcategory_name, groups in subcats.items():

                subcategory_node = category_node.add(
                    subcategory_name,
                    expand=False
                )

                for group_name, scans in groups.items():

                    group_node = subcategory_node.add(
                        group_name,
                        expand=False
                    )

                    for scan in scans:

                        # Greying Feature 
                        recommended = any(
                            service in global_state.recommended_services
                            for service in scan.services
                        )

                        available = self.tool_registry.is_available(
                            scan.tool
                        )

                        label = scan.name

                        if recommended:
                            label = f"[bold cyan][+][/bold cyan] {label}"

                        if not available:
                            label = f"[dim]{label}[/dim]"

                        group_node.add_leaf(
                            label,
                            data=scan
                        )

        yield tree

    def on_tree_node_selected(
        self,
        event: Tree.NodeSelected
    ):

        scan = event.node.data

        if not isinstance(scan, ScanConfig):
            return

        if not self.tool_registry.is_available(
            scan.tool
        ):
            return

        self.post_message(
            LaunchScan(scan)
        )

class ScanTracker(Vertical):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        self.waiting_items: dict[
            str,
            ListItem
        ] = {}

        self.active_items: dict[
            str,
            ListItem
        ] = {}

        self.completed_items: dict[
            str,
            ListItem
        ] = {}

        self.spinner_frames = [
            "⠋",
            "⠙",
            "⠹",
            "⠸",
            "⠼",
            "⠴",
            "⠦",
            "⠧",
            "⠇",
            "⠏"
        ]

        self.spinner_index = 0

    def next_spinner(self) -> str:

        frame = self.spinner_frames[
            self.spinner_index
        ]

        self.spinner_index = (
            self.spinner_index + 1
        ) % len(self.spinner_frames)

        return frame

    def compose(self) -> ComposeResult:

        yield Label(
            "Queue",
            classes="panel-title"
        )

        self.waiting_list = ListView(
            id="waiting-list"
        )

        yield self.waiting_list

        yield Label(
            "Active Scans",
            classes="panel-title"
        )

        self.active_list = ListView(
            id="active-list"
        )

        yield self.active_list

        yield Label(
                "Completed Scans",
                classes="panel-title"
            )

        self.completed_list = ListView(
                id="completed-list"
            )

        yield self.completed_list

    def add_waiting(
        self,
        scan_id: str,
        name: str,
        position: int
    ):

        label = Label(
            f"[{position}] "
            f"{scan_id[:8]} - {name}"
        )

        item = ListItem(label)

        item.scan_id = scan_id

        self.waiting_items[scan_id] = item

        self.waiting_list.append(item)

    def remove_waiting(
        self,
        scan_id: str
    ):

        item = self.waiting_items.get(
            scan_id
        )

        if item:

            item.remove()

            del self.waiting_items[
                scan_id
            ]

    def add_active(
        self,
        scan_id: str,
        name: str
    ):
        
        self.remove_waiting(
            scan_id
        )

        spinner = self.next_spinner()

        label = Label(
            f"[bold #ff8800]{spinner}[/] "
            f"{scan_id[:8]} - {name}"
        )        

        item = ListItem(label)

        item.scan_id = scan_id

        self.active_items[scan_id] = item

        self.active_list.append(item)

    def remove_active(
        self,
        scan_id: str
    ):

        item = self.active_items.get(scan_id)

        if item:

            item.remove()

            del self.active_items[scan_id]

    def add_completed(
        self,
        scan_id: str,
        name: str,
        success: bool
    ):

        if scan_id in self.completed_items:
            return

        icon = "✔" if success else "✖"

        label = Label(
            f"{icon} "
            f"{scan_id[:8]} - {name}"
        )

        item = ListItem(label)

        item.scan_id = scan_id

        self.completed_items[
            scan_id
        ] = item

        self.completed_list.append(item)

    def on_list_view_selected(
        self,
        event: ListView.Selected
    ):

        item = event.item

        if hasattr(item, "scan_id"):

            self.post_message(
                ScanSelected(item.scan_id)
            )

class ScanDetailViewer(Vertical):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.scan_buffers: dict[str, list[str]] = {}
        self.max_buffer_lines = 800 #5000 Reduce buffer size to prevent memory issues

        self.current_scan_id: str | None = None
        self.pending_lines: list[str] = []

    def compose(self) -> ComposeResult:



        yield Label(
            "Terminal Log",
            classes="panel-title"
        )

        self.log_viewer = RichLog(
            id="scan-detail-log",
            auto_scroll=False,
            wrap=False,
            markup=False,
            highlight=False
        )

        yield self.log_viewer

    def append_output(
        self,
        scan_id: str,
        line: str
    ):

        if scan_id not in self.scan_buffers:

            self.scan_buffers[scan_id] = []
            # bounded memory retention
            if len(
                self.scan_buffers[scan_id]
            ) > self.max_buffer_lines:

                self.scan_buffers[scan_id] = (
                    self.scan_buffers[scan_id][-self.max_buffer_lines:]
                )

        self.scan_buffers[scan_id].append(
            line
        )

        # bounded memory retention
        if len(
            self.scan_buffers[scan_id]
        ) > self.max_buffer_lines:

            self.scan_buffers[scan_id] = (
                self.scan_buffers[scan_id][-self.max_buffer_lines:]
            )

        # render only selected scan
        if self.current_scan_id != scan_id:
            return

        self.pending_lines.append(
            line
        )

    def show_scan(
        self,
        scan_id: str
    ):

        self.current_scan_id = scan_id

        self.log_viewer.clear()

        buffer = self.scan_buffers.get(
            scan_id,
            []
        )

        if buffer:

            self.log_viewer.write(
                "\n".join(buffer)
            )

            self.log_viewer.scroll_end(
                animate=False
            )

    def flush_pending_output(self):

        if not self.pending_lines:
            return

        self.log_viewer.write(
            "\n".join(
                self.pending_lines
            )
        )

        self.pending_lines.clear()

        self.log_viewer.scroll_end(
            animate=False
        )