from pathlib import Path
import json

class ThemeManager:

    def __init__(self):

        self.theme_dir = (
            Path(__file__).resolve().parent
            / "themes"
        )

        self.config_path = (
            Path(__file__).resolve().parent.parent.parent
            / "config"
            / "theme.json"
        )

        self.themes = {
            css.stem: css.name
            for css in self.theme_dir.glob("*.css")
        }

        self.theme_order = sorted(
            self.themes.keys()
        )

        if not self.theme_order:
            raise RuntimeError(
                f"No themes found in {self.theme_dir}"
            )

        default_theme = self.load_theme()

        self.current_index = (
            self.theme_order.index(default_theme)
            if default_theme in self.theme_order
            else 0
        )

        

    @property
    def current_theme(self):

        return self.theme_order[
            self.current_index
        ]

    @property
    def current_path(self):

        filename = self.themes[
            self.current_theme
        ]

        return self.theme_dir / filename
    
    def save_theme(self):

        self.config_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        self.config_path.write_text(
            json.dumps(
                {
                    "theme": self.current_theme
                }, indent=4
            )
        )


    def load_theme(self):

        if not self.config_path.exists():
            return "emberstrike"

        try:

            data = json.loads(
                self.config_path.read_text()
            )

            theme = data.get(
                "theme",
                "emberstrike"
            )

            if theme in self.theme_order:
                return theme

        except Exception:
            pass

        return "emberstrike"

    def next_theme(self):

        self.current_index = (
            (self.current_index + 1)
            % len(self.theme_order)
        )

        self.save_theme()

        return self.current_path

    def previous_theme(self):

        self.current_index = (
            (self.current_index - 1)
            % len(self.theme_order)
        )

        self.save_theme()

        return self.current_path