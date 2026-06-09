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

    def parse_nb_drones(self, line, indx):
        nb = re.findall(r"-?\d+", line)
        if not nb:
            raise ValueError(f"ERROR: nb_drones must be integer, line {indx}")
        elif int(nb[0]) < 0:
            raise ValueError(f"ERROR: nb_drones must be positive, line {indx}")
        if len(nb) != 1:
            raise ValueError(
                f"Invalid nb_drones format: 'nb_drones: number', line {indx}")

        self.nb_drones = int(nb[0])

    def parse_metadata(self, zone_name, line, indx):
        allowed = ['zone', 'color', 'max_drones']
        allowed_zone = ['priority', 'restricted', 'normal', 'blocked']
        extract = re.search(r"\[(.*?)\]", line)
        if not extract:
            raise ValueError(
                f"Invalid metadata format, line {indx}\nMetadata mus be inside []"
            )
        metadata = extract.group(1).split(" ")
        data = {}

        for item in metadata:
            if "=" not in item:
                raise ValueError(
                    f"Invalid metadata entry: '{item}', line {indx}"
                )
            parts = item.split("=")
            if len(parts) != 2:
                raise ValueError(
                    f"Invalid metadat entry: '{item}', line {indx}"
                )

            key, val = parts
            if key not in allowed:
                raise ValueError(
                    f"Unknown metadata key: '{key}', line {indx}\nvalid keys:{allowed}"
                )
            if key == "zone":
                if val not in allowed_zone:
                    raise ValueError(
                        f"Invalid value: '{val}', line {indx}\nvalid value:{allowed_zone}"
                    )
            if key == "max_drones":
                if not val.isdigit() or int(val) <= 0:
                    raise ValueError(
                        f"Metadata value must be positive number: '{key}={val}', line {indx}"
                    )

            data[key] = int(val) if val.isdigit() else val

        self.zone_metadata[zone_name] = data

    def parse_hubs(self, line, indx):
        if line.startswith("start_hub"):
            if self.start_hub:
                raise ValueError(
                    "Multiple start_hub declarations"
                )
            line = line.split(":")[1]

            extract = re.search(r"(\w+)\s(-?\d+)\s(-?\d+)", line)

            if not extract:
                raise ValueError(
                    f"ERROR: Invalid format:{line}, line {indx}")

            self.start_hub = extract.group(1)
            self.x = int(extract.group(2))
            self.y = int(extract.group(3))
            if (self.x, self.y) in self.zone_coords.values():
                raise ValueError(
                    f"Duplicate coordinate:{line}, line {indx}"
                )

            self.zone_coords[self.start_hub] = (self.x, self.y)
            if "=" in line or "[" in line or "]" in line:
                self.parse_metadata(self.start_hub, line, indx)

        elif line.startswith("hub"):
            line = line.split(":")[1]
            extract = re.search(r"(\w+)\s(-?\d+)\s(-?\d+)", line)
            if not extract:
                raise ValueError(
                    f"ERROR: Invalid format:{line}, line {indx}")
            zone_name = extract.group(1)
            self.x = int(extract.group(2))
            self.y = int(extract.group(3))
            if (self.x, self.y) in self.zone_coords.values():
                raise ValueError(
                    f"Duplicate coordinate:{line}, line {indx}"
                )

            if zone_name in self.zone_coords:
                raise ValueError(
                    f"WARNING: Duplicate hub '{zone_name}', line {indx}")

            self.zone_coords[zone_name] = (self.x, self.y)
            if "=" in line or "[" in line or "]" in line:
                self.parse_metadata(zone_name, line, indx)

        elif line.startswith("end_hub"):
            if self.end_hub:
                raise ValueError(
                    f"Multiple end_hub declarations, line {indx}"
                )
            line = line.split(":")[1]
            extract = re.search(r"(\w+)\s(-?\d+)\s(-?\d+)", line)
            if not extract:
                raise ValueError(
                    f"ERROR: Invalid format:{line}, line {indx}")
            self.end_hub = extract.group(1)
            self.x = int(extract.group(2))
            self.y = int(extract.group(3))
            if (self.x, self.y) in self.zone_coords.values():
                raise ValueError(
                    f"Duplicate coordinate:{line}, line {indx}"
                )

            self.zone_coords[self.end_hub] = (self.x, self.y)
            if "=" in line or "[" in line or "]" in line:
                self.parse_metadata(self.end_hub, line, indx)

    def parse_connection(self, line, indx):
        try:
            extract = re.search(r"(\w+)-(\w+)", line)
            if not extract:
                raise ValueError(
                    f"Invalide connection format:{line}, line {indx}")
            from_zone = extract.group(1)
            to_zone = extract.group(2)

            if from_zone not in self.zone_coords:
                raise ValueError(f"Unknown hub: {from_zone}, line {indx}")
            if to_zone not in self.zone_coords:
                raise ValueError(f"Unknown hub: {to_zone}, line {indx}")
            if (from_zone, to_zone) in self.connection:
                raise ValueError(
                    f"Duplicate connection {from_zone}-{to_zone}, line {indx}")

            self.connection.append((from_zone, to_zone))
            extract = re.search(r"\[(.*?)\]", line)
            if extract:
                check = extract.group(1)
                if not check.startswith("max_link_capacity="):
                    raise ValueError(
                        f"Invalid format: usage [max_link_capacity=number], line {indx}")

                capacity = int(check.split("=")[1])

                if capacity <= 0:
                    raise ValueError(
                        f"max_link_capacity must be positive, line {indx}")

                self.link_capacity[(from_zone, to_zone)] = capacity

        except Exception as error:
            print(f"ERROR: {error}")

    def parse_file(self):
        nb_drones = False
        try:
            lines = self.map.splitlines()
            for indx, line in enumerate(lines, 1):
                line = line.strip()
                if line.startswith("#") or line == "":
                    continue

                elif line.startswith("nb_drones"):
                    if nb_drones:
                        raise ValueError(
                            "Multiple nb_drones declaration"
                        )
                    nb_drones = True
                    self.parse_nb_drones(line, indx)

                elif line.startswith("start_hub") or line.startswith("hub") or line.startswith("end_hub"):
                    self.parse_hubs(line, indx)

                elif line.startswith("connection"):
                    line = line.split(":")[1]
                    self.parse_connection(line, indx)

            if not nb_drones:
                raise ValueError(
                    "Missing nb_drones declaration"
                )
            if self.start_hub == "" or self.end_hub == "":
                raise ValueError(
                    "ERORR: You missing <start_hub> or <end_hub> !!")

            if not self.connection:
                raise ValueError(
                    "Map must contain at less one connection"
                )
            for key, val in self.zone_metadata.items():
                if "zone" not in val:
                    self.zone_type[key] = "normal"
                    continue
                self.zone_type[key] = val["zone"]
        except Exception as error:
            print(f"{error}")


sel = Parser()
sel.load_file()
sel.parse_file()
# print(sel.nb_drones)
# print(sel.start_hub)
# print(sel.end_hub)
# print(sel.zone_coords)
# print(sel.zone_metadata)
# print(sel.connection)
# print(sel.link_capacity)
print(sel.zone_type)
