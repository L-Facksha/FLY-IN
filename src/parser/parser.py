import sys
import re
from typing import Any
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
        self.x: int = 0
        self.y: int = 0
        self.zone_coords: dict[str, tuple[int, int]] = {}
        self.zone_metadata: dict[str, dict[str, Any]] = {}
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
        nb = re.findall(r"-?\d+", line)
        if not nb:
            raise ValueError("ERROR: nb_drones must be integer")
        elif int(nb[0]) < 0:
            raise ValueError("ERROR: nb_drones must be positive")
        if len(nb) != 1:
            raise ValueError("Invalid nb_drones format: 'nb_drones: number'")

        self.nb_drones = int(nb[0])

    def parse_metadata(self, zone_name, line):
        extract = re.search(r"\[(.*?)\]", line)
        metadata = extract.group(1).split(" ")
        data = {}

        for item in metadata:
            key, val = item.split("=")
            data[key] = int(val) if val.isdigit() else val

        self.zone_metadata[zone_name] = data

    def parse_hubs(self, line):
        if line.startswith("start_hub") and self.start_hub == "":
            line = line.split(":")[1]

            extract = re.search(r"(\w+)\s(-?\d+)\s(-?\d+)", line)

            if not extract:
                raise ValueError(
                    f"ERROR: Invalid format:{line}")

            self.start_hub = extract.group(1)
            self.x = int(extract.group(2))
            self.y = int(extract.group(3))

            self.zone_coords[self.start_hub] = (self.x, self.y)
            if "=" in line:
                self.parse_metadata(self.start_hub, line)

        elif line.startswith("hub"):
            line = line.split(":")[1]
            extract = re.search(r"(\w+)\s(-?\d+)\s(-?\d+)", line)
            if not extract:
                raise ValueError(
                    f"ERROR: Invalid format:{line}")
            zone_name = extract.group(1)
            self.x = int(extract.group(2))
            self.y = int(extract.group(3))

            if zone_name in self.zone_coords:
                raise ValueError(f"WARNING: Duplicate hub <{zone_name}>")

            self.zone_coords[zone_name] = (self.x, self.y)
            if "=" in line:
                self.parse_metadata(zone_name, line)

        elif line.startswith("end_hub") and self.end_hub == "":
            line = line.split(":")[1]
            extract = re.search(r"(\w+)\s(-?\d+)\s(-?\d+)", line)
            if not extract:
                raise ValueError(
                    f"ERROR: Invalid format:{line}")
            self.end_hub = extract.group(1)
            self.x = int(extract.group(2))
            self.y = int(extract.group(3))

            self.zone_coords[self.end_hub] = (self.x, self.y)
            if "=" in line:
                self.parse_metadata(self.end_hub, line)

    def parse_connection(self, line):
        try:
            extract = re.search(r"(\w+)-(\w+)", line)
            if not extract:
                raise ValueError(f"Invalide connection format:{line}")
            from_zone = extract.group(1)
            to_zone = extract.group(2)

            if from_zone not in self.zone_coords:
                raise ValueError(f"Unknown hub: {from_zone}")
            if to_zone not in self.zone_coords:
                raise ValueError(f"Unknown hub: {to_zone}")
            if (from_zone, to_zone) in self.connection:
                raise ValueError(f"Duplicate connection {from_zone}-{to_zone}")

            self.connection.append((from_zone, to_zone))

            extract = re.search(r"\[(.*?)\]", line)
            if extract:
                check = extract.group(1)
                if not check.startswith("max_link_capacity="):
                    raise ValueError(
                        "Invalid format: usage [max_link_capacity=number]")

                capacity = int(check.split("=")[1])

                if capacity <= 0:
                    raise ValueError("max_link_capacity must be positive")
                self.link_capacity[(from_zone, to_zone)] = capacity

        except Exception as error:
            print(f"ERROR: {error}")
            return 1

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
                    self.parse_hubs(line)

                elif line.startswith("connection"):
                    line = line.split(":")[1]
                    print(line)
                    res = self.parse_connection(line)
                    if res == 1:
                        sys.exit(1)

            if self.start_hub == "" or self.end_hub == "":
                raise ValueError(
                    "ERORR: You missing <start_hub> or <end_hub> !!")

            for key, val in self.zone_metadata.items():
                if "zone" not in val:
                    continue
                self.zone_type[key] = val["zone"]
        except Exception as error:
            print(f"{error}")
            return 1


sel = Parser()
sel.load_file()
sel.parse_file()
# print(sel.nb_drones)
# print(sel.start_hub)
# print(sel.end_hub)
# print(sel.zone_coords)
# print(sel.zone_metadata)
# print(sel.connection)
print(sel.link_capacity)
# print(sel.zone_type)
