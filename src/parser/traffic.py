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
    
    def can_move(self):

        
