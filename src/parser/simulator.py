from graph import Graph
from traffic import Traffic
from rich import print


class Simulator():
    def __init__(self, graph: Graph, traffic: Traffic) -> None:
        self.graph = graph
        self.traffic = traffic

    def colorize_zone(self, zone: str) -> str:
        if '-' in zone:
            parts = zone.split('-')
            current_zone = parts[0]
            next_zone = parts[1]
            current_zone_color = self.graph.zone_color.get(current_zone, '')
            next_zone_color = self.graph.zone_color.get(next_zone, '')
            return f"[{current_zone_color}]{current_zone}[/{current_zone_color}]\
-[{next_zone_color}]{next_zone}[/{next_zone_color}]"
        color_name = self.graph.zone_color.get(zone, '')
        return f"[{color_name}]{zone}[/{color_name}]"

    def colorize_move(self, move: str) -> str:
        # print(move)
        parts = move.split('-', 1)
        drone = parts[0]
        zone = parts[1]
        return f"{drone}-{self.colorize_zone(zone)}"

    def print_turns(self) -> None:
        turns = self.traffic.run()
        start_zone = self.colorize_zone(self.graph.start)
        initial = ' | '.join(
            f"D{d}-{start_zone}"
            for d in range(1, self.traffic.nb_drones + 1)
        )
        print(initial)
        for turn in turns:
            colored = [self.colorize_move(mv) for mv in turn]
            print(' | '.join(colored))

        print(f"\nTotal turns: {len(turns)}")
