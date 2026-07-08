from graph import Graph


class Dijkstra:
    """
    Compute the shortest paths in the graph.

    The algorithm calculates the minimum movement cost from the
    start hub to every reachable zone and extracts all shortest
    paths to the destination hub. Paths containing priority zones
    are preferred when multiple shortest paths exist.

    Parameters
    ----------
    graph : Graph
        Graph used for pathfinding.
    """
    def __init__(self, graph: Graph) -> None:
        """
        Initialize the pathfinding algorithm.

        Parameters
        ----------
        graph : Graph
            Graph containing the map topology and movement costs.
        """
        self.graph = graph

    def find_all_paths(self) -> list[list[str]]:
        """
        Find all shortest paths from the start hub to the end hub.

        The method first computes the minimum movement cost to every
        reachable zone using Dijkstra's algorithm. It then performs a
        depth-first search to reconstruct every shortest path while
        ignoring blocked zones. Finally, the paths are ordered so that
        those containing more priority zones are preferred.

        Returns
        -------
        list[list[str]]
            A list of shortest paths, where each path is represented
            as an ordered list of zone names. An empty list is returned
            if no valid path exists.
        """
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

        def _dfs(zone: str, path: list[str]) -> None:
            if zone == end:
                all_paths.append(list(path))
                return
            for neighbor in self.graph.get_neighbors(zone):
                if self.graph.zone_type.get(neighbor, 'normal') == 'blocked':
                    continue
                cost_nex_zone = self.graph.get_cost(zone, neighbor)
                if dist[neighbor] == dist[zone] + cost_nex_zone:
                    path.append(neighbor)
                    _dfs(neighbor, path)
                    path.pop()

        _dfs(start, [start])

        def _score(p: list[str]) -> tuple[int, int]:
            pri = sum(1 for z in p
                      if self.graph.zone_type.get(z) == 'priority')
            return (-pri, len(p))

        all_paths.sort(key=_score)
        return all_paths
