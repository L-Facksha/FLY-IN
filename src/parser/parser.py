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
        nb = re.findall(r"\d+", line)
        if len(nb) != 1:
            raise ValueError("Invalid nb_drones format")
        self.nb_drones = int(nb[0])
    
    def parse_metadata(self, zone_name, line):
        extract = re.search(r"\[(.*?)\]", line)
        metadata = extract.group().split(" ")
        data = {}

        for item in metadata:
            key, val = item.split("=")
            data[key] = val

        self.zone_metadata[zone_name] = data


    def parse_hubs(self, line):
        s_exist = False
        e_exist = False

        if self.start_hub in self.zone_coords:
            s_exist = True
        if self.end_hub in self.zone_coords:
            e_exist = True

        if line.startswith("start_hub") and not s_exist:
            extract = re.search(r"(\w+)\s*(-?\d+)\s*(-?\d+)", line)
            self.start_hub = extract.group(1)
            self.x = int(extract.group(2))
            self.y = int(extract.group(3))

            self.zone_coords[self.start_hub] = (self.x, self.y)
            self.parse_metadata(self.start_hub, line)

        elif line.startswith("hub"):
            extract = re.search(r"(\w+)\s*(-?\d+)\s*(-?\d+)", line)
            zone_name = extract.group(1)
            self.x = int(extract.group(2))
            self.y = int(extract.group(3))

            self.zone_coords[zone_name] = (self.x, self.y)
            self.parse_metadata(zone_name, line)


        elif line.startswith("end_hub") and not e_exist:
            extract = re.search(r"(\w+)\s*(-?\d+)\s*(-?\d+)", line)
            self.end_hub = extract.group(1)
            self.x = int(extract.group(2))
            self.y = int(extract.group(3))

            self.zone_coords[self.end_hub] = (self.x, self.y)
            self.parse_metadata(self.end_hub, line)
        

    def parse_connection(self, line):
        try:
            extract = re.search(r"(\w+)\-(\w+)", line)
            from_zone = extract.group(1)
            to_zone = extract.group(2)
            try:
                extract = re.search(r"\[(.*?)\]")
                check = extract.group(1)
                if not "max_link_capacity" in check:
                    raise
            except:
                raise ValueError("Invalid format: usage [max_link_capacity=number]")
            
            capacity = int(extract.group(1).split("=")[1])
            self.link_capacity[(from_zone, to_zone)] = capacity

        except Exception as error:
            print(f"ERROR: {error}")

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
                    line = line.split(":")[1]
                    self.parse_hubs(line)
                
                elif line.startswith("connection"):
                    line = line.split(":")[1]
                    self.parse_connection(line)
        except Exception as error:
            print(f"{error}")

                

