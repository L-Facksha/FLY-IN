from graph import Graph
from algorithm import Dijkstra
from rich.console import Console
import sys


class Traffic():
    def __init__(self, graph: Graph, dijkstra:
                 Dijkstra, nb_drone: int) -> None:
        self.graph = graph
        self.dijkstra = dijkstra
        self.nb_drones = nb_drone
        self.paths: dict[int, list[str]] = {}
        self.zone_count: dict[str, int] = {}
        self.drone_zone: dict[int, str] = {}
        self.drone_step: dict[int, int] = {}
        self.in_transit: dict[int, tuple[int, str]] = {}

    def construction_paths(self) -> None:
        all_paths = self.dijkstra.find_all_paths()

        if not all_paths:
            raise ValueError("Path not found")

        for drone_id in range(1, self.nb_drones + 1):
            indx = (drone_id - 1) % len(all_paths)
            self.paths[drone_id] = all_paths[indx]
            self.drone_zone[drone_id] = self.graph.start
            self.drone_step[drone_id] = 0

        for zone in self.graph.neighbors:
            self.zone_count[zone] = 0

        self.zone_count[self.graph.start] = self.nb_drones

    def plan_turn(self) -> list[str]:
        transit_done: list[int] = []
        just_arrived: set[int] = set()
        leaving_restricted: list[tuple[str, str]] = []

        turn_link: dict[tuple[str, str], int] = {}
        confirmed: list[tuple[int, str, str]] = []
        moves: list[str] = []
        leaving_zone: dict[str, int] = {}
        entering_next_zone: dict[str, int] = {}

        for drone_id, (conn, to_zone) in self.in_transit.items():
            self.drone_zone[drone_id] = to_zone
            self.zone_count[to_zone] += 1
            self.drone_step[drone_id] += 1
            moves.append(f"D{drone_id}-{to_zone}")
            just_arrived.add(drone_id)
            transit_done.append(drone_id)

        for drone in transit_done:
            del self.in_transit[drone]

        for drone_id in range(1, self.nb_drones + 1):
            if drone_id in self.in_transit:
                continue
            if drone_id in just_arrived:
                continue

            if self.drone_zone[drone_id] == self.graph.end:
                continue

            step = self.drone_step[drone_id]
            path = self.paths[drone_id]

            if step >= len(path) - 1:
                continue

            current_zone = path[step]
            next_zone = path[step + 1]

            link_cap = self.graph.get_link_capacity(current_zone, next_zone)
            link_used = (turn_link.get((current_zone, next_zone), 0) +
                         turn_link.get((next_zone, current_zone), 0))

            if link_used >= link_cap:
                continue

            zone_type = self.graph.zone_type.get(next_zone, 'normal')
            if zone_type == 'blocked':
                continue

            if zone_type == 'restricted':
                zone_cap = self.graph.get_zone_capacity(next_zone)
                can_move = (
                    self.zone_count.get(next_zone, 0)
                    - leaving_zone.get(next_zone, 0)
                    + entering_next_zone.get(next_zone, 0)
                )

                if can_move >= zone_cap:
                    continue

                conn = f"{current_zone}-{next_zone}"
                moves.append(f"D{drone_id}-{conn}")
                leaving_restricted.append((drone_id, current_zone))
                turn_link[(current_zone, next_zone)] = (
                    turn_link.get((current_zone, next_zone), 0) + 1
                )
                self.drone_zone[drone_id] = conn
                self.in_transit[drone_id] = (conn, next_zone)
                entering_next_zone[next_zone] = entering_next_zone.get(
                    next_zone, 0) + 1
                leaving_zone[current_zone] = leaving_zone.get(
                    current_zone, 0) + 1

            else:
                zone_cap = self.graph.get_zone_capacity(next_zone)
                can_move = (
                    self.zone_count.get(next_zone, 0)
                    - leaving_zone.get(next_zone, 0)
                    + entering_next_zone.get(next_zone, 0)
                )

                if can_move >= zone_cap:
                    continue
                moves.append(f"D{drone_id}-{next_zone}")
                confirmed.append((drone_id, current_zone, next_zone))
                leaving_zone[current_zone] = leaving_zone.get(
                    current_zone, 0) + 1
                entering_next_zone[next_zone] = entering_next_zone.get(
                    next_zone, 0) + 1
                turn_link[(current_zone, next_zone)] = (
                    turn_link.get((current_zone, next_zone), 0) + 1
                )

        for drone_id, current_zone in leaving_restricted:
            self.zone_count[current_zone] -= 1

        for drone_id, current_zone, next_zone in confirmed:
            self.zone_count[next_zone] += 1
            self.zone_count[current_zone] -= 1
            self.drone_zone[drone_id] = next_zone
            self.drone_step[drone_id] += 1

        return moves

    def run(self) -> list[list[str]]:
        try:
            console = Console()
            self.construction_paths()
            turns: list[list[str]] = []

            for _ in range(self.nb_drones * 10):
                if all(self.drone_zone[d] == self.graph.end
                        for d in range(1, self.nb_drones + 1)):
                    break
                moves = self.plan_turn()
                if moves:
                    turns.append(moves)
                else:
                    raise ValueError("Deadlock — no drone can move")

            return turns

        except Exception as error:
            console.print(f"💥 ERROR: {error}", style='bold red')
            sys.exit(1)
