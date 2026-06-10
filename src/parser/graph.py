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
        zone_costs = {
            'normal': 1,
            'priority': 1,
            'restricted': 2,
            'blocked': 999
        }

        for zone in parser.zones:
            self.neighbors[zone] = []

        for from_zone, to_zone in parser.connection:
            self.neighbors[from_zone].append(to_zone)
            self.neighbors[to_zone].append(from_zone)

            from_type = parser.zone_type.get(from_zone, 'normal')
            to_type = parser.zone_type.get(to_zone, 'normal')

            self.costs[(from_zone, to_zone)] = zone_costs[to_type]
            self.costs[(to_zone, from_zone)] = zone_costs[from_type]

        for zone in parser.zones:
            if parser.zone_type.get(zone, 'normal') == 'blocked':
                for other in self.neighbors:
                    if zone in self.neighbors[other]:
                        self.neighbors[other].remove(zone)
                self.neighbors[zone] = []

        self.zone_capacity = parser.zone_capacity.copy()
        self.link_capacity = parser.link_capacity.copy()
