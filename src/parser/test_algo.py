from graph import Graph

class dijkstra():
    def __init__(self, graph: Graph):
        self.graph = graph
        
    def find_all_paths(self):
        start = self.graph.start
        end = self.graph.end
        dist: dict[str, int] = {}
        visited: set[str] = set()

        for zone in self.graph.neighbors:
            dist[zone] = 9999
        
        dist[start] = 0
        
        while True:
            current: None | str = None
            for zone in self.graph.neighbors:
                if zone not in visited and dist[zone] < 9999:
                    if current is None or dist[zone] < dist[current]:
                        current = zone
            if current is None:
                break
            visited.add(current)    
            for nb in self.graph.get_neighbors(current):
                
                
                    
                