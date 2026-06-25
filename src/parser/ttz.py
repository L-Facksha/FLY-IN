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
            indx = (drone_id - 1) % len(all_paths)
            self.paths[drone_id] = all_paths[indx]
            self.drone_zone[drone_id] = self.graph.start
            self.drone_path_index[drone_id] = 0

        for zone in self.graph.neighbors:
            self.zone_count[zone] = 0
            self.turn_leving[zone] = 0

        self.zone_count[self.graph.start] = self.nb_drones

    def plan_turn(self) -> list[str]:
        turn_zone: dict[str, int] = {}
        moves: list[str] = []
        confirmed: list[tuple[int, str, str]] = []
        just_arrived: set[int] = set()
        transit_drone: list[int] = []
        turn_link: dict[tuple[str, str], int] = {}

        for transit_id, (conn, to_zone) in self.in_transit.items():
            self.zone_count[to_zone] += 1
            self.turn_leving[to_zone] -= 1
            self.drone_zone[transit_id] = to_zone
            self.drone_path_index[transit_id] += 1

            transit_drone.append(transit_id)

            if transit_id in self.in_transit:
                continue

        for transit_id in transit_drone:
            del self.in_transit[transit_id]

        for drone_id in range(1, self.nb_drones + 1):
            if self.drone_zone[drone_id] == self.graph.end:
                continue

            setp = self.drone_path_index[drone_id]
            path = self.paths[drone_id]

            if setp >= len(path) - 1:
                continue

            current_zone = path[setp]
            next_zone = path[setp + 1]

            zone_type = self.graph.zone_type.get(next_zone, 'normal')

            if zone_type == 'blocked':
                continue

            link_cap = self.graph.get_link_capacity(current_zone, next_zone)
            link_used = (turn_link.get((current_zone, next_zone), 0) +
                         turn_link.get((next_zone, current_zone), 0))

            if link_used >= link_cap:
                continue

            zone_cap = self.graph.get_zone_capacity(next_zone)
            future_occupancy = (
                self.zone_count.get(next_zone, 0)
                + self.turn_leving.get(next_zone, 0)
            )

            if future_occupancy >= zone_cap:
                continue

            if zone_type == 'restricted':
                conn = f"{current_zone}-{next_zone}"
                self.zone_count[current_zone] -= 1
                self.drone_zone[drone_id] = conn
                self.in_transit[drone_id] = (conn, next_zone)

                self.turn_leving[next_zone] += 1

                turn_link[(current_zone, next_zone)] = \
                    turn_link.get((current_zone, next_zone), 0) + 1
                moves.append(f"D{drone_id}-{conn}")
