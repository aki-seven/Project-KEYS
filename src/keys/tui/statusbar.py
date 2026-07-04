from textual.widgets import Static


class StatusBar(Static):

    def __init__(self):

        super().__init__(
            "",
            id="status-bar"
        )

    def update_status(
        self,
        target: str,
        active: int,
        completed: int,
        theme: str = "OFFSEC_VOID"
    ):

        self.update(
            f" TARGET: {target} "
            f"| ACTIVE: {active} "
            f"| COMPLETED: {completed} "
            f"| THEME: {theme} "
            f"| CTRL+Q Quit "
        )