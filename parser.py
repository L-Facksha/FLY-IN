import sys
import re
from rich.console import Console
from typing import Any
from pathlib import Path
RED = "\033[91m"


class Parser():
    """
    Parse and validate a drone map file.

    The parser reads a map description, validates its syntax,
    extracts hubs, connections, metadata, and capacities, and
    stores the resulting information for use by the simulation.
    """

    def __init__(self) -> None:
        """
        Initialize an empty parser.

        Creates the data structures used to store the parsed map,
        hub metadata, connections, capacities, and coordinates.
        """
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

    def load_file(self) -> None:
        """
        Load the map file specified on the command line.

        The file contents are read and stored in the parser for
        subsequent parsing.

        Raises
        ------
        FileNotFoundError
            If the specified file does not exist.
        SystemExit
            If an unrecoverable error occurs.
        """
        try:
            if len(sys.argv) < 2:
                raise ValueError(
                    "Missing <path_map>:\n"
                    "Usage: python3 main.py <path_map>\n"
                    "       OR\n"
                    "       make run ARGS=<path_map>"
                )

            path = Path(sys.argv[1])

            if not path.exists():
                raise FileNotFoundError(f"ERROR: File not found {path}")

            with path.open('r') as f:
                self.map = f.read()

        except Exception as error:
            self.console.print(f"💥 {error}", style='bold red')
            sys.exit(1)

    def _parse_nb_drones(self, line: str, indx: int) -> None:
        """
        Parse the number of drones.

        Parameters
        ----------
        line : str
            Line containing the ``nb_drones`` declaration.
        indx : int
            Line number in the map file.

        Raises
        ------
        ValueError
            If the declaration is malformed or the number of
            drones is not positive.
        """
        nb = re.fullmatch(r"nb_drones:\s+(-?\d+)", line)
        if not nb:
            raise ValueError(
                f"ERROR: Invalid format nb_drones '{line}', line: {indx}")

        self.nb_drones = int(nb.group(1))

        if self.nb_drones <= 0:
            raise ValueError(f"ERROR: nb_drones must be positive, line {indx}")

    def parse_metadata(self, zone_name: str, line: str, indx: int) -> None:
        """
        Parse metadata associated with a hub.

        Parameters
        ----------
        zone_name : str
            Name of the hub whose metadata is being parsed.
        line : str
            Line containing the metadata.
        indx : int
            Line number in the map file.

        Raises
        ------
        ValueError
            If the metadata contains invalid keys, values,
            duplicate entries, or malformed syntax.
        """
        allowed = ['zone', 'color', 'max_drones']
        allowed_zone = ['priority', 'restricted', 'normal', 'blocked']
        extract = re.fullmatch(r"[^\[]*\[([^\[\]]+)\]", line)

        if not extract:
            raise ValueError(
                f"Invalid metadata format, line {indx}\n\
Metadata mus be inside []"
            )
        metadata = extract.group(1).split(" ")

        data = {}

        for item in metadata:
            if "=" not in item:
                raise ValueError(
                    f"Invalid metadata entry, line {indx}"
                )
            parts = item.split("=")
            if len(parts) != 2:
                raise ValueError(
                    f"Invalid metadat entry, line {indx}"
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

    def _parse_hubs(self, line: str, indx: int) -> None:
        """
        Parse a start hub, hub, or end hub declaration.

        Parameters
        ----------
        line : str
            Line describing a hub.
        indx : int
            Line number in the map file.

        Raises
        ------
        ValueError
            If the hub declaration is invalid, duplicated,
            or uses duplicate coordinates.
        """
        if line.startswith("start_hub"):
            if self.start_hub:
                raise ValueError(
                    "Multiple start_hub declarations"
                )

            extract = re.fullmatch(
                r"start_hub:\s([^\s-]+)\s(-?\d+)\s(-?\d+)(\s\[(.*?)\])?",
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
                r"hub:\s([^\s-]+)\s(-?\d+)\s+(-?\d+)(\s\[(.*?)\])?", line)

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
                r"end_hub:\s([^\s-]+)\s(-?\d+)\s+(-?\d+)(\s\[(.*?)\])?",
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

    def _parse_connection(self, line: str, indx: int) -> None:
        """
        Parse a connection between two hubs.

        Parameters
        ----------
        line : str
            Line describing a connection.
        indx : int
            Line number in the map file.

        Raises
        ------
        ValueError
            If the connection is invalid, duplicated,
            references unknown hubs, or has invalid metadata.
        SystemExit
            If an unrecoverable parsing error occurs.
        """
        try:
            extract = re.fullmatch(
                r"connection:\s([^\s-]+)-([^\s-]+)(\s\[(.*?)\])?", line)

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

    def parse_file(self) -> None:
        """
        Parse the loaded map.

        Processes every line of the map, validates its syntax,
        extracts hubs, connections, metadata, and capacities,
        and initializes default values where necessary.

        Raises
        ------
        ValueError
            If the map contains invalid declarations, missing
            required fields, or inconsistent data.
        SystemExit
            If an unrecoverable parsing error occurs.
        """
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

                    self._parse_nb_drones(filter_line, indx)

                elif first_word == "connection":
                    filter_line = line.split('#', 1)[0].strip()
                    self._parse_connection(filter_line, indx)

                elif first_word not in ('start_hub', 'hub', 'end_hub'):
                    raise ValueError(
                        f"ERROR: Invalid format: '{first_word}', line {indx} ")

                elif first_word in ('start_hub', 'hub', 'end_hub'):
                    filter_line = line.split('#', 1)[0].strip()
                    self._parse_hubs(filter_line, indx)

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
            if self.zone_capacity[self.start_hub] > \
                    self.zone_capacity[self.end_hub]:
                self.console.print(
                    f"✏️  Set the capacities of the Start and End hubs to \
Number of drones -> {self.nb_drones}.",
                    style='bold yellow'
                )
            self.zone_capacity[self.end_hub] = self.nb_drones

        except Exception as error:
            self.console.print(f"💥 {error}", style='bold red')
            sys.exit(1)
