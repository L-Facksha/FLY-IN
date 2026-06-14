from graph import Graph
from algorithm import Dijkstra


class Traffic():
    def __init__(self, graph: Graph, dijkstra: Dijkstra, nb_drones: int) -> None:
        self.graph = graph
        self.dijkstra = dijkstra
        self.nb_drones = nb_drones
        self.paths: dict[int, list[str]] = {}
        self.drone_zone: dict[int, str] = {}
        self.drone_step: dict[int, int] = {}
        self.zone_count: dict[str, int] = {}
        self.link_count: dict[tuple[str, str], int] = {}

    def construction_paths(self):
        path = self.dijkstra.run(self.graph.start, self.graph.end)
        for drone_id in range(1, self.nb_drones + 1):
            self.paths[drone_id] = path
            self.drone_zone[drone_id] = self.graph.start
            self.drone_step[drone_id] = 0

        for zone in self.graph.neighbors:
            self.zone_count[zone] = 0

        self.zone_count[self.graph.start] = self.nb_drones
        print(self.drone_step)
        print(self.zone_count)
        # print(self.paths)

    def can_move(self, nb_drone: int) -> bool:
        step = self.drone_step[nb_drone]
        path = self.paths[nb_drone]

        if step >= len(path) - 1:
            return False

        current = path[step]
        next_zone = path[step + 1]

        if self.graph.zone_type.get(next_zone, 'normal') == 'blocked':
            return False

        if self.zone_count[next_zone] >=\
                self.graph.get_zone_capacity(next_zone):
            return False

        link_cap = self.graph.get_link_capacity(current, next_zone)
        link_used = self.link_count.get((current, next_zone), 0) +\
            self.link_count.get((next_zone, current), 0)
        print("link_capas:", self.graph.link_capacity)
        print("link_count:", self.link_count)
        print("current_zone:", current)
        print("next_zone:", next_zone)
        print("link_used:", link_used)
        print("link_cap:", link_cap)
        if link_used >= link_cap:
            return False

        return True
