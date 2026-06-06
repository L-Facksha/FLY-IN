import sys
from pathlib import Path
RED = "\033[91m"


class Parser():
    def __init__(self):
        self.map: str = ""
        self.nb_drones: int = 0
        self.start_hub: str = ""
        self.end_hub: str = ""
        self.zone: list[str] = []
        self.zone_type: dict[str, str] = {}
        self.connection: list[tuple[str, str]] = []
        self.c_metadata: dict[str, int] = {}
        self.zone_capacity: dict[str, int] = {}
        self.link_capacity: dict[tuple[str, str], int] = {}

    def load_file(self):
        try:
            if len(sys.argv) < 2:
                raise ValueError("Usage: python3 main.py <path_map>")

            path = Path(sys.argv[1])

            if not path.exists():
                raise FileNotFoundError(f"ERROR: File not found {path}")

            with path.open('r') as f:
                self.map = f.read()

            return self.map
        except Exception as error:
            print(f"{error}")


read = Parser()
print(read.load_file())
