from graph import Graph
from algorithm import Dijkstra
import sys
RED = "\033[31m"
RESET = "\033[0m"


class Traffic():
    def __init__(self, graph: Graph, dijkstra: Dijkstra, nb_drones: int)\
            -> None:
        self.graph = graph
        self.dijkstra = dijkstra
        self.nb_drones = nb_drones
        self.paths: dict[int, list[str]] = {}
        self.drone_zone: dict[int, str] = {}
        self.drone_step: dict[int, int] = {}
        self.zone_count: dict[str, int] = {}

    def construction_paths(self) -> None:
        path = self.dijkstra.run(self.graph.start, self.graph.end)

        if not path:
            raise ValueError("No path found")

        for drone_id in range(1, self.nb_drones + 1):
            self.paths[drone_id] = path
            self.drone_zone[drone_id] = self.graph.start
            self.drone_step[drone_id] = 0

        for zone in self.graph.neighbors:
            self.zone_count[zone] = 0

        self.zone_count[self.graph.start] = self.nb_drones
        # print("zone_count", self.zone_count)
        # print(self.paths)

    def plan_turn(self) -> list[str]:
        turn_zone: dict[str, int] = {}
        turn_link: dict[tuple[str, str], int] = {}
        moves: list[str] = []

        for drone_id in range(1, self.nb_drones + 1):
            if self.drone_zone[drone_id] == self.graph.end:
                continue

            step = self.drone_step[drone_id]
            path = self.paths[drone_id]
            # print(f"{RED}Paths:{RESET}", self.paths)
            # print(f"{RED}path:{RESET}", path, "\n")
            # print(f"{RED}drone_step:{RESET}", self.drone_step, "\n")
            if step >= len(path) - 1:
                continue

            current_zone = path[step]
            next_zone = path[step + 1]

            if self.graph.zone_type.get(next_zone, 'normal') == 'blocked':
                continue

            zone_cap = self.graph.get_zone_capacity(next_zone)

            if self.zone_count.get(next_zone, 0) +\
                    turn_zone.get(next_zone, 0) >= zone_cap:
                continue

            link_cap = self.graph.get_link_capacity(current_zone, next_zone)
            link_used = turn_link.get((current_zone, next_zone), 0) +\
                turn_link.get((next_zone, current_zone), 0)

            if link_used >= link_cap:
                continue

            moves.append(f"D{drone_id}-{next_zone}")
            turn_zone[next_zone] = turn_zone.get(next_zone, 0) + 1
            turn_link[(current_zone, next_zone)] = turn_link.get(
                (current_zone, next_zone), 0
            ) + 1
            # print(f"{RED}Drone_zone:{RESET}", self.drone_zone)
            # print(f"{RED}zone_count:{RESET}", self.zone_count, "\n")
            self.zone_count[current_zone] -= 1
            self.zone_count[next_zone] += 1
            self.drone_zone[drone_id] = next_zone
            self.drone_step[drone_id] += 1
            # print(f"{RED}Drone_zone:{RESET}", self.drone_zone)
            # print(f"{RED}zone_count:{RESET}", self.zone_count, "\n")
            # print("llallaa", current_zone)
            # print("link_used:", link_used)
            # print("link_use:", link_used)
            # print(moves)

        return moves

    def run(self) -> list[list[str]]:
        try:
            self.construction_paths()
            turns: list[list[str]] = []
            max_turn = 1000

            for _ in range(1, max_turn + 1):
                if all(self.drone_zone[d] == self.graph.end
                       for d in range(1, self.nb_drones + 1)):
                    break

                moves = self.plan_turn()
                if moves:
                    turns.append(moves)
                else:
                    raise ValueError("No drone can move anymore")

            return turns
        except Exception as error:
            print(f"{RED}ERROR{RESET}: {error}", file=sys.stderr)
            sys.exit(1)
