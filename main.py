from parser import Parser
from traffic import Traffic
from graph import Graph
from algorithm import Dijkstra
from simulator import Simulator


class Main():
    """
    Coordinate the execution of the FLY-IN application.

    The Main class creates and manages the core components of
    the application, including parsing the map, building the
    graph, computing paths, simulating drone traffic, and
    displaying the simulation results.
    """

    def __init__(self) -> None:
        """
        Initialize the application.

        Creates instances of the parser, graph, pathfinding
        algorithm, traffic manager, and simulator.
        """
        self.parser = Parser()
        self.graph = Graph(self.parser)
        self.dijkstra = Dijkstra(self.graph)
        self.traffic = Traffic(self.graph, self.dijkstra,
                               self.parser.nb_drones)
        self.simulation = Simulator(self.graph, self.traffic)

    def run(self) -> None:
        """
        Execute the complete simulation workflow.

        The workflow performs the following steps:

        1. Load and parse the input map.
        2. Build the graph representation.
        3. Compute the shortest paths.
        4. Simulate drone traffic.
        5. Display the simulation results.

        Returns
        -------
        None
        """
        self.parser.load_file()
        self.parser.parse_file()

        self.graph = Graph(self.parser)
        self.graph.build(self.parser)

        self.dijkstra = Dijkstra(self.graph)

        self.traffic = Traffic(
            self.graph, self.dijkstra, self.parser.nb_drones
        )
        self.traffic.run()

        self.simulation = Simulator(self.graph, self.traffic)
        self.simulation.print_turns()


if __name__ == "__main__":
    main = Main()
    main.run()
