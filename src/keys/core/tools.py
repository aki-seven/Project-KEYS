import shutil


class ToolRegistry:

    def __init__(self):

        self.available_tools: dict[str, bool] = {}

    def detect_tools(
        self,
        tools: list[str]
    ):

        for tool in tools:

            self.available_tools[tool] = (
                shutil.which(tool) is not None
            )

    def is_available(
        self,
        tool: str
    ) -> bool:

        return self.available_tools.get(
            tool,
            False
        )