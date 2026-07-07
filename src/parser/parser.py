import sys
import re
from rich.console import Console
from typing import Any
from pathlib import Path
RED = "\033[91m"


class Parser():
    def __init__(self):
        self.map: str = ""
        self.nb_drones: int = 0
        self.start_hub: str = ""
        self.end_hub: str = ""
        self.zones: list[str] = []
        self.zone_type: dict[str, str] = {}
        self.x: int = 0
        self.y: int = 0
        self.zone_coords: dict[str, tuple[int, int]] = {}
        self.zone_metadata: dict[str, dict[str, Any]] = {}
        self.connection: list[tuple[str, str]] = []
        self.zone_capacity: dict[str, int] = {}
        self.c_metadata: dict[str, int] = {}
        self.link_capacity: dict[tuple[str, str], int] = {}
        self.console = Console()

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
            sys.exit(1)

    def parse_nb_drones(self, line, indx):
        nb = re.fullmatch(r"nb_drones:\s+(-?\d+)", line)
        if not nb:
            raise ValueError(
                f"ERROR: Invalid format nb_drones '{line}', line: {indx}")

        self.nb_drones = int(nb.group(1))

        if self.nb_drones <= 0:
            raise ValueError(f"ERROR: nb_drones must be positive, line {indx}")

    def parse_metadata(self, zone_name, line, indx):
        allowed = ['zone', 'color', 'max_drones']
        allowed_zone = ['priority', 'restricted', 'normal', 'blocked']
        extract = re.findall(r"\[(.*?)\]", line)[-1]

        if not extract:
            raise ValueError(
                f"Invalid metadata format, line {indx}\n\
Metadata mus be inside []"
            )
        metadata = extract.split(" ")

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
                    f"Unknown metadata key: '{key}', line {indx}\n\
valid keys:{allowed}"
                )
            if key == "zone":
                if val not in allowed_zone:
                    raise ValueError(
                        f"Invalid value: '{val}', line {indx}\n\
valid value:{allowed_zone}"
                    )
            if key == "max_drones":
                if not val.isdigit() or int(val) <= 0:
                    raise ValueError(
                        f"Metadata value must be positive number: \
'{key}={val}', line {indx}"
                    )

            if key == 'color':
                if val == '':
                    raise ValueError(
                        f"Unknown metadata value: {key}, line {indx}"
                    )

            if key in data:
                raise ValueError(
                    f"ERROR: Duplicate metadata key: '{key}', line {indx}")

            data[key] = int(val) if val.isdigit() else val

        self.zone_metadata[zone_name] = data

    def parse_hubs(self, line, indx):
        if line.startswith("start_hub"):
            if self.start_hub:
                raise ValueError(
                    "Multiple start_hub declarations"
                )

            extract = re.fullmatch(
                r"start_hub:\s([^\s-]+)\s(-?\d+)\s+(-?\d+)\s(\[(.*?)\])?",
                line
            )

            if not extract:
                raise ValueError(
                    f"ERROR: Invalid format, line {indx}")

            self.start_hub = extract.group(1)

            self.x = int(extract.group(2))
            self.y = int(extract.group(3))
            if (self.x, self.y) in self.zone_coords.values():
                raise ValueError(
                    f"Duplicate coordinate:{line}, line {indx}"
                )

            self.zone_coords[self.start_hub] = (self.x, self.y)
            self.zones.append(self.start_hub)

            line = line.split(self.start_hub)[-1]

            if "=" in line or "[" in line or "]" in line:
                self.parse_metadata(self.start_hub, line, indx)

        elif line.startswith("hub"):
            extract = re.fullmatch(
                r"hub:\s([^\s-]+)\s(-?\d+)\s+(-?\d+)\s(\[(.*?)\])?", line)

            if not extract:
                raise ValueError(
                    f"ERROR: Invalid format, line {indx}")

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
            self.zones.append(zone_name)

            line = line.split(zone_name)[-1]

            if "=" in line or "[" in line or "]" in line:
                self.parse_metadata(zone_name, line, indx)

        elif line.startswith("end_hub"):
            if self.end_hub:
                raise ValueError(
                    f"Multiple end_hub declarations, line {indx}"
                )
            extract = re.fullmatch(
                r"end_hub:\s([^\s-]+)\s(-?\d+)\s+(-?\d+)\s(\[(.*?)\])?",
                line
            )

            if not extract:
                raise ValueError(
                    f"ERROR: Invalid format, line {indx}")

            self.end_hub = extract.group(1)

            self.x = int(extract.group(2))
            self.y = int(extract.group(3))
            if (self.x, self.y) in self.zone_coords.values():
                raise ValueError(
                    f"Duplicate coordinate:{line}, line {indx}"
                )

            self.zone_coords[self.end_hub] = (self.x, self.y)
            self.zones.append(self.end_hub)

            line = line.split(self.end_hub)[-1]

            if re.search(r"\[.*\]", line):
                self.parse_metadata(self.end_hub, line, indx)

    def parse_connection(self, line, indx):
        try:
            extract = re.fullmatch(
                r"connection:\s([^\s-]+)-([^\s-]+)(\s\[(.*?)\])?", line)

            # print(line)
            if not extract:
                raise ValueError(
                    f"Invalide connection format, line {indx}")

            from_zone = extract.group(1)
            to_zone = extract.group(2)
            metadata = extract.group(4)

            if from_zone not in self.zone_coords:
                raise ValueError(f"Unknown hub: {from_zone}, line {indx}")
            if to_zone not in self.zone_coords:
                raise ValueError(f"Unknown hub: {to_zone}, line {indx}")
            if (from_zone, to_zone) in self.connection or \
                    (to_zone, from_zone) in self.connection:

                raise ValueError(
                    f"Duplicate connection {from_zone}-{to_zone}, line {indx}")

            if from_zone == to_zone:
                raise ValueError(
                    f"ERROR: Connection not alowed '{from_zone}', line {indx}")

            self.connection.append((from_zone, to_zone))

            if metadata:
                check = re.fullmatch(r"max_link_capacity=(-?\d+)", metadata)
                if not check:
                    raise ValueError(
                        f"Invalid format: Usage ['max_link_capacity=number'],\
line {indx}"
                    )

                capacity = int(check.group(1))

                if capacity <= 0:
                    raise ValueError(
                        f"max_link_capacity must be positive, line {indx}")

                self.link_capacity[(from_zone, to_zone)] = capacity

        except Exception as error:
            self.console.print(f"💥 ERROR: {error}", style='bold red')
            sys.exit(1)

    def parse_file(self):
        nb_drones = False
        try:
            lines = self.map.splitlines()
            for indx, line in enumerate(lines, 1):
                line = line.strip()

                first_word = line.split(':')[0].strip()

                if line.startswith("#") or line == "":
                    continue

                elif first_word == "nb_drones":
                    if nb_drones:
                        raise ValueError(
                            "Multiple nb_drones declaration"
                        )

                    filter_line = line.split('#', 1)[0].strip()
                    nb_drones = True

                    self.parse_nb_drones(filter_line, indx)

                elif first_word == "connection":
                    filter_line = line.split('#', 1)[0].strip()
                    self.parse_connection(filter_line, indx)

                elif first_word not in ('start_hub', 'hub', 'end_hub'):
                    raise ValueError(
                        f"ERROR: Invalid format: '{first_word}', line {indx} ")

                elif first_word in ('start_hub', 'hub', 'end_hub'):
                    filter_line = line.split('#', 1)[0].strip()
                    self.parse_hubs(filter_line, indx)

            if not nb_drones:
                raise ValueError(
                    "Missing nb_drones declaration"
                )
            if self.start_hub == "" or self.end_hub == "":
                raise ValueError(
                    "ERORR: Missing 'start_hub' or 'end_hub' !!")

            if not self.connection:
                raise ValueError(
                    "Map must contain at less one connection"
                )

            for zone in self.zones:
                meta = self.zone_metadata.get(zone, {})
                self.zone_type[zone] = meta.get('zone', 'normal')
                if zone not in self.zone_capacity:
                    self.zone_capacity[zone] = meta.get('max_drones', 1)
            self.zone_capacity[self.start_hub] = self.nb_drones
            self.zone_capacity[self.end_hub] = self.nb_drones

        except Exception as error:
            self.console.print(f"💥 {error}", style='bold red')
            sys.exit(1)


# sel = Parser()
# sel.load_file()
# sel.parse_file()
# print(sel.nb_drones)
# print(sel.start_hub)
# print(sel.end_hub)
# print(sel.zone_coords)
# print(sel.zone_metadata)
# print(sel.zone_capacity)
# print(sel.connection)
# print("\n", "*"*197)
# print(sel.zones)
# print(sel.link_capacity)
# print(sel.zone_type)
