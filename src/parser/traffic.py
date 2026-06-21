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
        self.in_transit: dict[int, tuple[str, str]] = {}

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
        turn_zone:  dict[str, int] = {}
        turn_leave: dict[str, int] = {}
        turn_link:  dict[tuple[str, str], int] = {}
        moves: list[str] = []

        # ── Step 1: arrive drones that were in transit last turn ──
        arrived: list[int] = []
        for drone_id, (conn, to_zone) in self.in_transit.items():
            # check if destination zone has room
            zone_cap = self.graph.get_zone_capacity(to_zone)
            if (self.zone_count.get(to_zone, 0)
                    + turn_zone.get(to_zone, 0) >= zone_cap):
                # subject says: drone MUST arrive — cannot wait on link
                # this is a map design error, but we still try
                continue

            self.zone_count[to_zone] = self.zone_count.get(to_zone, 0) + 1
            self.drone_zone[drone_id] = to_zone
            self.drone_step[drone_id] += 1
            turn_zone[to_zone] = turn_zone.get(to_zone, 0) + 1
            moves.append(f"D{drone_id}-{to_zone}")
            arrived.append(drone_id)

        for drone_id in arrived:
            del self.in_transit[drone_id]

        # ── Step 2: move drones not in transit ──
        for drone_id in range(1, self.nb_drones + 1):
            if drone_id in self.in_transit:
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

            zone_cap = self.graph.get_zone_capacity(next_zone)
            if (self.zone_count.get(next_zone, 0)
                    - turn_leave.get(next_zone, 0)
                    + turn_zone.get(next_zone, 0) >= zone_cap):
                continue

            link_cap = self.graph.get_link_capacity(current_zone, next_zone)
            link_used = (turn_link.get((current_zone, next_zone), 0) +
                         turn_link.get((next_zone, current_zone), 0))
            if link_used >= link_cap:
                continue

            # ── restricted: 2-turn move ──────────────────────
            if zone_type == 'restricted':
                conn = f"{current_zone}-{next_zone}"
                self.zone_count[current_zone] -= 1
                self.in_transit[drone_id] = (conn, next_zone)
                turn_leave[current_zone] = turn_leave.get(current_zone, 0) + 1
                turn_link[(current_zone, next_zone)] = \
                    turn_link.get((current_zone, next_zone), 0) + 1
                moves.append(f"D{drone_id}-{conn}")   # required format

            # ── normal/priority: 1-turn move ─────────────────
            else:
                turn_leave[current_zone] = turn_leave.get(current_zone, 0) + 1
                turn_zone[next_zone] = turn_zone.get(next_zone, 0) + 1
                turn_link[(current_zone, next_zone)] = \
                    turn_link.get((current_zone, next_zone), 0) + 1
                self.zone_count[current_zone] -= 1
                self.zone_count[next_zone] += 1
                self.drone_zone[drone_id] = next_zone
                self.drone_step[drone_id] += 1
                moves.append(f"D{drone_id}-{next_zone}")

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


# def plan_turn(self) -> list[str]:
#         turn_zone:  dict[str, int] = {}
#         turn_link:  dict[tuple[str, str], int] = {}
#         moves:      list[str] = []
#         confirmed:  list[tuple[int, str, str]] = []

#         # ── Step 1: arrive drones in transit (turn 2 of restricted move) ──
#         transit_done: list[int] = []
#         for drone_id, (conn, to_zone) in self.in_transit.items():
#             zone_cap = self.graph.get_zone_capacity(to_zone)
#             zone_used = self.zone_count.get(to_zone, 0) + \
#                 turn_zone.get(to_zone, 0)
#             # subject says drone MUST arrive — cannot wait on connection
#             # so we always arrive regardless of zone capacity
#             turn_zone[to_zone] = turn_zone.get(to_zone, 0) + 1
#             moves.append(f"D{drone_id}-{to_zone}")
#             self.zone_count[to_zone] += 1
#             self.drone_zone[drone_id] = to_zone
#             self.drone_step[drone_id] += 1
#             transit_done.append(drone_id)

#         for drone_id in transit_done:
#             del self.in_transit[drone_id]

#         # ── Step 2: move drones not in transit ───────────────────────────
#         for drone_id in range(1, self.nb_drones + 1):
#             if drone_id in self.in_transit:
#                 continue
#             if self.drone_zone[drone_id] == self.graph.end:
#                 continue

#             step = self.drone_step[drone_id]
#             path = self.paths[drone_id]

#             if step >= len(path) - 1:
#                 continue

#             current_zone = path[step]
#             next_zone = path[step + 1]
#             zone_type = self.graph.zone_type.get(next_zone, 'normal')

#             if zone_type == 'blocked':
#                 continue

#             zone_cap = self.graph.get_zone_capacity(next_zone)
#             zone_used = self.zone_count.get(next_zone, 0) + \
#                 turn_zone.get(next_zone, 0)

#             # for restricted: don't check zone capacity now
#             # (drone goes to link this turn, zone checked on arrival)
#             if zone_type != 'restricted':
#                 if zone_used >= zone_cap:
#                     continue

#             link_cap = self.graph.get_link_capacity(current_zone, next_zone)
#             link_used = turn_link.get((current_zone, next_zone), 0) + \
#                 turn_link.get((next_zone, current_zone), 0)
#             if link_used >= link_cap:
#                 continue

#             # ── restricted: 2-turn move ──────────────────────────────────
#             if zone_type == 'restricted':
#                 conn = f"{current_zone}-{next_zone}"
#                 moves.append(f"D{drone_id}-{conn}")
#                 turn_link[(current_zone, next_zone)] = \
#                     turn_link.get((current_zone, next_zone), 0) + 1
#                 self.zone_count[current_zone] -= 1
#                 self.drone_zone[drone_id] = conn   # mid-link
#                 self.in_transit[drone_id] = (conn, next_zone)
#                 self.drone_step[drone_id] += 1

#             # ── normal/priority: 1-turn move ─────────────────────────────
#             else:
#                 turn_zone[next_zone] = turn_zone.get(next_zone, 0) + 1
#                 turn_link[(current_zone, next_zone)] = \
#                     turn_link.get((current_zone, next_zone), 0) + 1
#                 confirmed.append((drone_id, current_zone, next_zone))
#                 moves.append(f"D{drone_id}-{next_zone}")

#         # ── update state for normal moves ────────────────────────────────
#         for drone_id, current_zone, next_zone in confirmed:
#             self.zone_count[current_zone] -= 1
#             self.zone_count[next_zone] += 1
#             self.drone_zone[drone_id] = next_zone
#             self.drone_step[drone_id] += 1

#         return moves