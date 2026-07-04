import yaml
import os
from dataclasses import dataclass, field
from typing import List, Dict, Any
from pathlib import Path


CATEGORY_ORDER = [ # Ordering category display
    "Recon",
    "Scanning",
    "Enumeration",
    "Fuzzing",
    "Vulnerability Analysis",
    "Exploitation",
    "Bruteforce",
    "Post-Exploitation",
]

@dataclass
class ScanConfig:

    category: str
    subcategory: str = ""
    group: str = ""

    name: str = ""
    tool: str = ""
    command: str = ""
    

    services: List[str] = field(default_factory=list)
    default_ports: List[int] = field(default_factory=list)
    parameters: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    description: str = ""
    tags: List[str] = field(default_factory=list)



class ConfigLoader:

    def __init__(self, config_dir: str | None = None):

        if config_dir is None:

            base_dir = (
                Path(__file__).resolve().parent.parent
            )

            config_dir = (base_dir/ "config"/ "scans")

        self.config_dir = Path(config_dir)

        self.scans: List[ScanConfig] = []

        self._load()

    def _load(self):
        if not self.config_dir.exists():            # Create standard config hierarchy if missing

            self.config_dir.mkdir(
                parents=True,
                exist_ok=True
            )
            return
            
        for root, _, files in os.walk(str(self.config_dir)):
            for file in files:
                if file.endswith((".yaml", ".yml")):
                    self._parse_file(os.path.join(root, file))

    def _parse_file(self, filepath: str):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                
            # If data is a list of scans
            if isinstance(data, dict) and "scans" in data:
                scans_list = data["scans"]
            elif isinstance(data, list):
                scans_list = data
            else:
                return

            for scan_data in scans_list:
                # Basic validation
                cmd_template = scan_data.get("command")
                if "name" not in scan_data or not cmd_template:
                    continue

                params = scan_data.get("parameters", {})   


                self.scans.append(
                    ScanConfig(
                        category=scan_data.get("category", "Uncategorized"),
                        subcategory=scan_data.get("subcategory", ""),
                        group=scan_data.get("group", ""),
                        name=scan_data.get("name"),
                        tool=scan_data.get("tool", ""),
                        command=cmd_template,
                        services=scan_data.get("services", []),
                        default_ports=scan_data.get("default_ports",[]),
                        parameters=params,
                        description=scan_data.get("description", ""),
                        tags=scan_data.get("tags", []),
                    )
                )
        except Exception as e:
            print(f"[CONFIG ERROR] {filepath}")
            print(e)

    def get_categories(self):

        tree = {}

        for scan in self.scans:

            category = scan.category or "Other"

            subcategory = scan.subcategory or "General"

            group = scan.group or scan.tool or "Misc"

            tree.setdefault(category, {})
            tree[category].setdefault(subcategory, {})
            tree[category][subcategory].setdefault(group, [])

            tree[category][subcategory][group].append(scan)

        
        ordered_tree = {}

        for category in CATEGORY_ORDER:

            if category in tree:
                ordered_tree[category] = tree[category]

        # append uncategorized leftovers
        for category in tree:

            if category not in ordered_tree:
                ordered_tree[category] = tree[category]

        return ordered_tree
