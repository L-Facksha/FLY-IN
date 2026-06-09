from parser import Parser


class Graph():
    def __init__(self, parser: Parser) -> None:
        self.start: str = parser.start_hub
        self.end: str = parser.end_hub
        self.neighbors: dict[str, list[str]] = {}
        self.costs: dict[tuple[str, str], int] = {}
        self.zone_capacity: dict[str, int] = {}
        self.link_capacity: dict[tuple[str, str], int] = {}

    def build(self, parser: Parser):
        for zone in parser.zones:
            self.neighbors[zone] = []
        
        for from_zone, to_zone in parser.connection:
            self.neighbors[from_zone].append(to_zone)
            self.neighbors[to_zone].append(from_zone)
        
        self.zone_capacity = parser.zone_capacity.copy()
        self.link_capacity = parser.link_capacity.copy()

