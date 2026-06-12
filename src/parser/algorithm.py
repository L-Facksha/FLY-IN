from graph import Graph


class Dijkstra:
    def __init__(self, graph: Graph) -> None:
        self.graph = graph

    def run(self, start: str, end: str) -> list[str]:
        dist: dict[str, int] = {}
        prev: dict[str, str] = {}
        visited: set[str] = set()

        for zone in self.graph.neighbors:
            dist[zone] = 999999
        dist[start] = 0

        while True:
            current: str | None = None

            for zone in self.graph.neighbors:
                if zone not in visited:
                    if zone is None or dist[zone] < dist[current]:
                        current = zone

            if current is None or current == end:
                break

            visited.add(current)

            for neighbor in self.graph.neighbors(current):
                if neighbor in visited:
                    continue
                new_cost = dist[current] + \
                    self.graph.get_cost(current, neighbor)
                if new_cost < dist[neighbor]:
                    dist[neighbor] = new_cost
                    prev[neighbor] = current
