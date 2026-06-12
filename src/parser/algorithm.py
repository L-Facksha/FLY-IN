from graph import Graph


class Dijkstra:
    def __init__(self, graph: Graph) -> None:
        self.graph = graph

    def run(self, start: str, end: str) -> list[str]:
        dist: dict[str, int] = {}
        prev: dict[str, str] = {}
        visited: set[str] = set()

        for zone in self.graph.neighbors:
            dist[zone] = 9999

        dist[start] = 0

        while True:
            current: str | None = None

            for zone in self.graph.neighbors:
                if zone not in visited:
                    if current is None or dist[zone] < dist[current]:
                        current = zone

            if current is None or current == end:
                break

            visited.add(current)
            for neighbor in self.graph.get_neighbors(current):
                if neighbor in visited:
                    continue
                new_cost = dist[current] + \
                    self.graph.get_cost(current, neighbor)

                if new_cost < dist[neighbor]:
                    dist[neighbor] = new_cost
                    prev[neighbor] = current

        if start != end and end not in prev:
            return []
        path = []
        current = end
        while current in prev:
            path.append(current)
            current = prev[current]

        path.append(start)
        path.reverse()
        return path
