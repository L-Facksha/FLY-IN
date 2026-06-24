from graph import Graph
from algorithm import Dijkstra
import sys

class Traffic():
    def __init__(self, graph: Graph, djikstra: Dijkstra, nb_drones: int) -> None:
        self.graph = graph
        self.djikstra = djikstra
        self.paths: dict[int, list[str]] = {}
        self.nb_drones: int = nb_drones
        self.drone_path_index: dict[int, int] = {}
        self.drone_zone: dict[int, str] = {}
        self.zone_count: dict[str, int] = {}
        self.turn_leving: dict[str, int] = {}
        self.in_transit: dict[int, tuple[str, str]] = {}

    def contruction_paths(self) -> None:
        all_paths = self.djikstra.find_all_paths()

        if not all_paths:
            raise ValueError("Path not found")

        for drone_id in range(1, self.nb_drones + 1):
            indx = drone_id % len(all_paths)
            self.paths[drone_id] = all_paths[indx]
            self.drone_zone[drone_id] = self.graph.start
            self.drone_path_index[drone_id] = 0
            
        for zone in self.graph.neighbors:
            self.zone_count[zone] = 0
            self.turn_leving[zone] = 0

        self.zone_count[self.graph.start] = self.nb_drones
    
    def plan_turn(self) -> list[str]:
        
            
            