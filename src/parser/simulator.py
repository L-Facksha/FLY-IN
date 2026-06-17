from graph import Graph
from traffic import Traffic

RESET = "\033[0m"
color_map: dict[str, str] = {
    'red': "\033[31m",
    'green': "\033[32m",
    'yellow': "\033[33m",
    'blue': "\033[34m",
    'purple': "\033[35m",
    'cyan': "\033[36m",
    'white':   "\033[37m",
    'orange': "\033[38;5;208m",
    'brown': "\033[38;5;94m",
    'maroon': "\033[38;5;52m",
    'gold': "\033[38;5;220m",
    'darkred': "\033[38;5;88m",
    'crimson': "\033[38;5;161m",
    'black':   "\033[38;5;240m",
    'rainbow': "\033[38;5;213m",
}



class Simulator():
    def __init__(self, graph: Graph, traffic: Traffic) -> None:
        self.graph = graph
        self.traffic = traffic

    def colorize_zone(self, zone: str) -> str:
        color_name = self.graph.zone_color.get(zone, '')
        color_codde = color_map.get(color_name, RESET)
        return f"{color_codde}{zone}{RESET}"

    def colorize_move(self, move: str) -> str:
        parts = move.split('-')
        drone = parts[0]
        zone = parts[1]
        return f"{drone}-{self.colorize_zone(zone)}"

    def print_turns(self) -> None:
        turns = self.traffic.run()
        for turn in turns:
            colored = [self.colorize_move(mv) for mv in turn]
            print(' '.join(colored))
        
        print(f"\nTotal turns: {len(turns)}")
