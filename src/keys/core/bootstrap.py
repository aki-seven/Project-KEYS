import sys
import subprocess
import shutil

class BootstrapError(Exception):
    pass

def check_python_version():
    if sys.version_info < (3, 8):
        raise BootstrapError("Python 3.8+ is required.")

def check_python_packages():
    required = ["textual", "rich", "yaml", "pydantic"]
    missing = []
    for pkg in required:
        try:
            if pkg == "yaml":
                __import__("yaml")
            else:
                __import__(pkg)
        except ImportError:
            missing.append(pkg)
            
    if missing:
        raise BootstrapError(
            f"Missing Python packages: {', '.join(missing)}\n"
            f"Install: pip install {' '.join(missing)}"
        )

def check_system_tools():

    required_tools = [
        "nmap",
        "ffuf",
        "gobuster",
        "feroxbuster",
        "nikto",
        "nuclei",
        "hydra"
        ]
    
    missing = []
    for tool in required_tools:
        if shutil.which(tool) is None:
            missing.append(tool)
            
    if missing:
        raise BootstrapError(
            f"Missing system tools: {', '.join(missing)}\n"
            f"Please install them via your package manager (e.g., apt install nmap)."
        )

def validate_dependencies():
    """Run all pre-flight checks before launching TUI."""
    try:
        check_python_version()
        check_python_packages()
        check_system_tools()
    except BootstrapError as e:
        print("\n[ERROR] IAI Bootstrap Failed")
        print("="*40)
        print(str(e))
        print("="*40)
        sys.exit(1)
