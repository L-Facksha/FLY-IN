from graph import Graph


class Dijkstra:
    def __init__(self, graph: Graph) -> None:
        self.graph = graph

    def find_all_paths(self) -> list[list[str]]:
        """Find all optimal paths from start to end."""
        start = self.graph.start
        end = self.graph.end

        dist: dict[str, int] = {}
        visited: set[str] = set()
        for zone in self.graph.neighbors:
            dist[zone] = 9999
        dist[start] = 0

        while True:
            current: str | None = None
            for zone in self.graph.neighbors:
                if zone not in visited and dist[zone] < 9999:
                    if current is None or dist[zone] < dist[current]:
                        current = zone
            if current is None:
                break
            visited.add(current)
            for nb in self.graph.get_neighbors(current):
                if nb in visited:
                    continue
                new_cost = dist[current] + self.graph.get_cost(current, nb)
                if new_cost < dist[nb]:
                    dist[nb] = new_cost

        all_paths: list[list[str]] = []

        def dfs(zone: str, path: list[str]) -> None:
            if zone == end:
                all_paths.append(list(path))
                return
            for neighbor in self.graph.get_neighbors(zone):
                if self.graph.zone_type.get(neighbor, 'normal') == 'blocked':
                    continue
                cost_nex_zone = self.graph.get_cost(zone, neighbor)
                if dist[neighbor] == dist[zone] + cost_nex_zone:
                    path.append(neighbor)
                    dfs(neighbor, path)
                    path.pop()

        dfs(start, [start])

        # if not all_paths:
        #     return [self.run(start, end)]

        def score(p: list[str]) -> tuple[int, int]:
            pri = sum(1 for z in p
                      if self.graph.zone_type.get(z) == 'priority')
            return (-pri, len(p))

        all_paths.sort(key=score)
        return all_paths

    # def run(self, start: str, end: str) -> list[str]:
    #     dist: dict[str, int] = {}
    #     prev: dict[str, str] = {}
    #     visited: set[str] = set()

    #     for zone in self.graph.neighbors:
    #         dist[zone] = 9999

    #     dist[start] = 0

    #     while True:
    #         current: str | None = None

    #         for zone in self.graph.neighbors:
    #             if zone not in visited and dist[zone] < 9999:
    #                 if current is None:
    #                     current = zone
    #                 elif dist[zone] < dist[current]:
    #                     current = zone
    #                 elif dist[zone] == dist[current]:
    #                     if self.graph.zone_type.get(zone) == 'priority' and\
    #                         self.graph.zone_type.get(current) != \
    #                             'priority':
    #                         current = zone

    #         if current is None or current == end:
    #             break

    #         visited.add(current)
    #         for neighbor in self.graph.get_neighbors(current):
    #             if neighbor in visited:
    #                 continue
    #             new_cost = dist[current] + \
    #                 self.graph.get_cost(current, neighbor)

    #             if new_cost < dist[neighbor]:
    #                 dist[neighbor] = new_cost
    #                 prev[neighbor] = current

    #     if start != end and end not in prev:
    #         return []
    #     path: list[str] = []
    #     current = end
    #     while current in prev:
    #         path.append(current)
    #         current = prev[current]

    #     path.append(start)
    #     path.reverse()
    #     return path
