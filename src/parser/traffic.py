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
        # print("zone_count", self.zone_count)
        # print(self.paths)

    def can_move(self, nb_drone: int) -> bool:
        d_step = self.drone_step[nb_drone]
        path = self.paths[nb_drone]

        if d_step >= len(path) - 1:
            return False

        current = path[d_step]
        next_zone = path[d_step + 1]

        if self.graph.zone_type.get(next_zone, 'normal') == 'blocked':
            return False

        if self.zone_count[next_zone] >=\
                self.graph.get_zone_capacity(next_zone):
            return False

        link_cap = self.graph.get_link_capacity(current, next_zone)
        link_used = self.link_count.get((current, next_zone), 0) +\
            self.link_count.get((next_zone, current), 0)
        # print("link_capas:", self.graph.link_capacity)
        # print("link_count:", self.link_count)
        # print("Paths:", self.paths)
        # print("Drone_zone:", self.drone_zone)
        # print("drone_step:", self.drone_step)
        # print("current_zone:", current)
        # print("next_zone:", next_zone)
        # print("link_used:", link_used)
        # print("link_cap:", link_cap)
        if link_used >= link_cap:
            return False

        return True

    def plan_turn(self) -> list[str]:
        turn_zone: dict[str, int] = {}
        turn_link: dict[tuple[str, str], int] = {}
        moves: list[str] = []

        for drone_id in range(1, self.nb_drones + 1):
            if self.drone_zone[drone_id] == self.graph.end:
                continue

            step = self.drone_step[drone_id]
            path = self.paths[drone_id]

            if step >= len(path) - 1:
                continue

            current_zone = path[step]
            next_zone = path[step + 1]

            zone_cap = self.graph.get_zone_capacity(next_zone)

            if self.zone_count.get(next_zone, 0) +\
                    turn_zone.get(next_zone, 0) >= zone_cap:
                continue

            link_cap = self.graph.get_link_capacity(current_zone, next_zone)
            link_used = self.link_count.get((current_zone, next_zone), 0) +\
                self.link_count.get((next_zone, current_zone), 0) +\
                turn_link.get((current_zone, next_zone), 0)

            if link_used >= link_cap:
                continue

            moves.append(f"D{drone_id}-{next_zone}")
            turn_zone[next_zone] = turn_zone.get(next_zone, 0) + 1
            turn_link[(current_zone, next_zone)] = turn_link.get(
                (current_zone, next_zone), 0
            ) + 1
            self.zone_count[current_zone] -= 1
            self.zone_count[next_zone] += 1
            self.drone_zone[drone_id] = next_zone
            self.drone_step[drone_id] += 1
            # print("llallaa", current_zone)
            # print("Zone_count:", self.zone_count)

        return moves
