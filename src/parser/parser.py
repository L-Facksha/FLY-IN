import sys
import re
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
        self.zone_coords: dict[str, tuple[int, int]] = {}
        self.zone_metadata: dict[str, dict[str, str]] = {}
        self.connection: list[tuple[str, str]] = []
        self.zone_capacity: dict[str, int] = {}
        self.c_metadata: dict[str, int] = {}
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

        except Exception as error:
            print(f"{error}")

    def parse_nb_drones(self, line):
        nb = re.findall(r"\d+", line)
        if len(nb) != 1:
            raise ValueError("Invalid nb_drones format")
        self.nb_drones = int(nb[0])

    def parse_hubs(self, line):
        if line.startswith("start_hub"):
            d_start = line.split(":")[1]
            extract = re.findall(r"\w+\s*-?\d+\s*-?\d+", d_start)



    def parse_file(self):
        nb_drones = False
        try:
            lines = self.map.splitlines()
            for line in lines:
                line = line.strip()
                if line.startswith("#") or line == "":
                    continue

                elif line.startswith("nb_drones") and not nb_drones:
                    nb_drones = True
                    self.parse_nb_drones(line)

                elif line.startswith("start_hub") or line.startswith("hub") or line.startswith("end_hub"):

