from graph import Graph
from algorithm import Dijkstra
import sys

RED = "\033[31m"
RESET = "\033[0m"


class Traffic():
    def __init__(self, graph: Graph, dijkstra: Dijkstra,
                 nb_drones: int) -> None:
        """Initialise traffic manager."""
        self.graph = graph
        self.dijkstra = dijkstra
        self.nb_drones = nb_drones
        self.paths:      dict[int, list[str]] = {}
        self.drone_zone: dict[int, str] = {}
        self.drone_step: dict[int, int] = {}
        self.zone_count: dict[str, int] = {}
        self.turn_leving: dict[str, int] = {}
        # drone_id → (connection_name, destination_zone)
        self.in_transit: dict[int, tuple[str, str]] = {}

    def construction_paths(self) -> None:
        """Assign shortest path to every drone."""
        all_paths = self.dijkstra.find_all_paths()

        if not all_paths:
            raise ValueError("No path found")

        for drone_id in range(1, self.nb_drones + 1):
            idx = (drone_id - 1) % len(all_paths)
            self.paths[drone_id] = all_paths[idx]
            self.drone_zone[drone_id] = self.graph.start
            self.drone_step[drone_id] = 0

        for zone in self.graph.neighbors:
            self.zone_count[zone] = 0
            self.turn_leving[zone] = 0
        self.zone_count[self.graph.start] = self.nb_drones

    def plan_turn(self) -> list[str]:
        """Plan one simulation turn and return the list of move strings."""
        turn_link:  dict[tuple[str, str], int] = {}
        moves:      list[str] = []
        confirmed:  list[tuple[int, str, str]] = []
        just_arrived: set[int] = set()

        # drones leaving a zone this turn (normal moves + restricted departures)
        # used to compute free slots for restricted arrivals next turn
        leaving: dict[str, int] = {}
        # drones already committed to arrive at a restricted zone next turn
        entering_next: dict[str, int] = {}

        # ── Step 1: land drones finishing restricted transit ──────────────
        transit_done: list[int] = []
        for drone_id, (conn, to_zone) in self.in_transit.items():
            # guaranteed free slot (checked before putting drone on link)
            self.zone_count[to_zone] += 1
            self.drone_zone[drone_id] = to_zone
            self.drone_step[drone_id] += 1
            moves.append(f"D{drone_id}-{to_zone}")
            transit_done.append(drone_id)
            just_arrived.add(drone_id)

        for drone_id in transit_done:
            del self.in_transit[drone_id]

        # ── Step 2: move drones sitting in a zone ────────────────────────
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
            zone_type = self.graph.zone_type.get(next_zone, 'normal')

            if zone_type == 'blocked':
                continue

            # ── link capacity ────────────────────────────────────────────
            link_cap = self.graph.get_link_capacity(current_zone, next_zone)
            link_used = (turn_link.get((current_zone, next_zone), 0)
                         + turn_link.get((next_zone, current_zone), 0))
            if link_used >= link_cap:
                continue

            if zone_type == 'restricted':
                # Drone enters link NOW, arrives NEXT turn — cannot wait on link.
                # Free slots in next_zone at start of next turn:
                #   zone_cap
                #   - zone_count[next_zone]       (currently there)
                #   + leaving[next_zone]           (will leave next_zone this turn)
                #   - entering_next[next_zone]     (already committed to arrive next turn)
                zone_cap = self.graph.get_zone_capacity(next_zone)
                free_next_turn = (
                    zone_cap
                    - self.zone_count.get(next_zone, 0)
                    + leaving.get(next_zone, 0)
                    - entering_next.get(next_zone, 0)
                )
                if free_next_turn <= 0:
                    continue  # no guaranteed slot → drone stays, does NOT enter link

                conn = f"{current_zone}-{next_zone}"
                entering_next[next_zone] = entering_next.get(next_zone, 0) + 1
                leaving[current_zone] = leaving.get(current_zone, 0) + 1
                turn_link[(current_zone, next_zone)] = (
                    turn_link.get((current_zone, next_zone), 0) + 1
                )
                self.zone_count[current_zone] -= 1
                self.drone_zone[drone_id] = conn
                self.in_transit[drone_id] = (conn, next_zone)
                # self.drone_step[drone_id] += 1!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                moves.append(f"D{drone_id}-{conn}")

            else:
                # Normal / priority: arrives this same turn.
                # Effective occupancy = count - drones leaving it + drones entering it
                zone_cap = self.graph.get_zone_capacity(next_zone)
                zone_used = (
                    self.zone_count.get(next_zone, 0)
                    - self.turn_leving.get(next_zone, 0)
                )
                if zone_used >= zone_cap:
                    continue

                leaving[current_zone] = leaving.get(current_zone, 0) + 1
                turn_link[(current_zone, next_zone)] = (
                    turn_link.get((current_zone, next_zone), 0) + 1
                )
                confirmed.append((drone_id, current_zone, next_zone))
                moves.append(f"D{drone_id}-{next_zone}")

        # ── Commit normal/priority moves ──────────────────────────────────
        for drone_id, current_zone, next_zone in confirmed:
            self.zone_count[current_zone] -= 1
            self.zone_count[next_zone] += 1
            self.turn_leving[next_zone] += 1
            self.turn_leving[current_zone] -= 1
            self.drone_zone[drone_id] = next_zone
            self.drone_step[drone_id] += 1

        return moves

    def run(self) -> list[list[str]]:
        """Run full simulation and return all turns."""
        # try:
        self.construction_paths()
        turns: list[list[str]] = []

        for _ in range(1000):
            if all(self.drone_zone[d] == self.graph.end
                    for d in range(1, self.nb_drones + 1)):
                break
            moves = self.plan_turn()
            if moves:
                turns.append(moves)
            # else:
            #     raise ValueError("Deadlock — no drone can move")

        return turns

        # except Exception as error:
        #     print(f"{RED}ERROR{RESET}: {error}", file=sys.stderr)
        #     sys.exit(1)
