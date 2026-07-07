from graph import Graph
from traffic import Traffic
from rich.console import Console
from rich.panel import Panel
from rich.align import Align
from rich.rule import Rule

RESET = "\033[0m"
color_map: dict[str, int] = {
    "black": "\033[30m",
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "purple": "\033[35m",
    "cyan": "\033[36m",
    "white": "\033[37m",

    "bright_black": "\033[90m",
    "bright_red": "\033[91m",
    "bright_green": "\033[92m",
    "bright_yellow": "\033[93m",
    "bright_blue": "\033[94m",
    "bright_purple": "\033[95m",
    "bright_cyan": "\033[96m",
    "bright_white": "\033[97m",

    "orange": "\033[38;5;208m",
    "brown": "\033[38;5;94m",
    "maroon": "\033[38;5;52m",
    "gold": "\033[38;5;220m",
    "darkred": "\033[38;5;88m",
    "crimson": "\033[38;5;161m",
    "violet": "\033[38;5;135m",
    "gray": "\033[38;5;245m",
    "pink": "\033[38;5;213m",
    "teal": "\033[38;5;36m",
    "lime": "\033[38;5;154m",
    "indigo": "\033[38;5;54m",
    "lavender": "\033[38;5;183m",
    "salmon": "\033[38;5;209m",
    "coral": "\033[38;5;203m",
    "mint": "\033[38;5;121m",
    'rainbow': "\033[38;5;213m",
    "magenta":       "\033[38;5;201m",
    "dark_magenta":  "\033[38;5;90m",
    "hot_pink":      "\033[38;5;205m",
    "fuchsia":       "\033[38;5;13m",
    "orchid":        "\033[38;5;170m",
    "plum":          "\033[38;5;176m",
}


class Simulator():
    def __init__(self, graph: Graph, traffic: Traffic) -> None:
        self.graph = graph
        self.traffic = traffic

    def colorize_zone(self, zone: str) -> str:
        if '-' in zone:
            current_zone, next_zone = zone.split('-', 1)
            current_zone_color = self.graph.zone_color.get(current_zone, '')
            next_zone_color = self.graph.zone_color.get(next_zone, '')

            current_zone_color = color_map.get(current_zone_color, '')

            next_zone_color = color_map.get(next_zone_color, '')
            return (
                f"{current_zone_color}{current_zone}{RESET}"
                "-"
                f"{next_zone_color}{next_zone}{RESET}"
            )

        color_name = self.graph.zone_color.get(zone, '')
        color_codde = color_map.get(color_name, RESET)
        return f"{color_codde}{zone}{RESET}"

    def colorize_move(self, move: str) -> str:
        parts = move.split('-', 1)
        drone = parts[0]
        zone = parts[1]
        return f"{drone}-{self.colorize_zone(zone)}"

    def print_turns(self) -> None:
        turns = self.traffic.run()
        panel = Panel(
            Align.center('FLY-IN', style='bold green'), border_style="green"
        )
        console = Console()
        console.print(panel)
        start_zone = self.colorize_zone(self.graph.start)
        initial = ' | '.join(
            f"D{d}-{start_zone}"
            for d in range(1, self.traffic.nb_drones + 1)
        )
        console.print("- TURN: 0", style='bold italic underline blue')
        print(initial, '\n')

        for x, turn in enumerate(turns, 1):
            colored = [self.colorize_move(mv) for mv in turn]
            console.print(f"- TURN: {x}", style='bold italic underline blue')
            print(' | '.join(colored), '\n')

        console.print(f"Total turns: {len(turns)}",
                      style='bold italic underline green')
