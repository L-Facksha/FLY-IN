from parser import Parser


class Graph():
    """
    Represent the map as a weighted graph.

    The graph is built from the parsed map data and stores the
    adjacency list, movement costs, zone capacities, link capacities,
    zone types, and zone colors used during pathfinding and simulation.

    Parameters
    ----------
    parser : Parser
        Parser containing the validated map data.
    """

    def __init__(self, parser: Parser) -> None:
        """
        Initialize an empty graph.

        Parameters
        ----------
        parser : Parser
            Parser containing the validated map information.
        """
        self.start: str = parser.start_hub
        self.end: str = parser.end_hub
        self.neighbors: dict[str, list[str]] = {}
        self.costs: dict[tuple[str, str], int] = {}
        self.zone_capacity: dict[str, int] = {}
        self.link_capacity: dict[tuple[str, str], int] = {}
        self.zone_type: dict[str, str] = parser.zone_type.copy()
        self.zone_color: dict[str, str] = {}

    def build(self, parser: Parser) -> None:
        """
        Build the graph from the parsed map.

        Creates the adjacency list, assigns movement costs based on
        zone types, removes blocked zones from the graph, and copies
        zone capacities, link capacities, and colors.

        Parameters
        ----------
        parser : Parser
            Parser containing the validated map data.
        """
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

            meta = parser.zone_metadata.get(zone, {})
            self.zone_color[zone] = meta.get('color', '')

        self.zone_capacity = parser.zone_capacity.copy()
        self.link_capacity = parser.link_capacity.copy()

    def get_neighbors(self, zone: str) -> list[str]:
        """
        Return the neighboring zones of a given zone.

        Parameters
        ----------
        zone : str
            Name of the zone.

        Returns
        -------
        list[str]
            List of adjacent zones.
        """
        return self.neighbors.get(zone, [])

    def get_cost(self, from_zone: str, to_zone: str) -> int:
        """
        Return the movement cost between two connected zones.

        Parameters
        ----------
        from_zone : str
            Starting zone.
        to_zone : str
            Destination zone.

        Returns
        -------
        int
            Cost of moving from ``from_zone`` to ``to_zone``.
        """
        return self.costs.get((from_zone, to_zone), 1)

    def get_zone_capacity(self, zone: str) -> int:
        """
        Return the maximum number of drones allowed in a zone.

        Parameters
        ----------
        zone : str
            Name of the zone.

        Returns
        -------
        int
            Zone capacity. Returns ``1`` if no capacity is defined.
        """
        return self.zone_capacity.get(zone, 1)

    def get_link_capacity(self, from_zone: str, to_zone: str) -> int:
        """
        Return the capacity of the connection between two zones.

        The capacity is treated as bidirectional. If no explicit
        capacity is defined, a default value of ``1`` is returned.

        Parameters
        ----------
        from_zone : str
            Starting zone.
        to_zone : str
            Destination zone.

        Returns
        -------
        int
            Maximum number of drones allowed to use the connection
        """
        return self.link_capacity.get(
            (from_zone, to_zone),
            self.link_capacity.get((to_zone, from_zone), 1)
        )
