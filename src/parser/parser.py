import argparse
import sys
RED="\033[91m"

class Pars_Args():
    def __init__(self):
        pass

    def pars_arg() -> argparse.Namespace:
        parser = argparse.ArgumentParser()

        parser.add_argument(
            "--e1", type=str, default="/goinfre/azebahad/FLY-IN/maps/easy/01_linear_path.txt",
            help="This for 01_linear_path.txt")
        parser.add_argument(
            "--e2", type=str, default="/goinfre/azebahad/FLY-IN/maps/easy/02_simple_fork.txt",
            help="This for 02_simple_fork.txt")
        parser.add_argument(
            "--e3", type=str, default="/goinfre/azebahad/FLY-IN/maps/easy/03_basic_capacity.txt",
            help="This for 03_basic_capacity.txt")

        parser.add_argument(
            "--h1", type=str, default="maps/hard/01_maze_nightmare.txt",
            help="This for 01_maze_nightmare.txt")
        parser.add_argument(
            "--h2", type=str, default="maps/hard/02_capacity_hell.txt",
            help="This for 02_capacity_hell.txt")
        parser.add_argument(
            "--h3", type=str, default="maps/hard/03_ultimate_challenge.txt",
            help="This for 03_ultimate_challenge.txt")

        parser.add_argument(
            "--m1", type=str, default="maps/medium/01_dead_end_trap.txt",
            help="This for 01_dead_end_trap.txt")
        parser.add_argument(
            "--m2", type=str, default="maps/medium/02_circular_loop.txt",
            help="This for 02_circular_loop.txt")
        parser.add_argument(
            "--m3", type=str, default="maps/medium/03_priority_puzzle.txt",
            help="This for 03_priority_puzzle.txt")

        return parser.parse_args()


class Parser(Pars_Args):
    def __init__(self, map_data):
        self.map = map_data
        self.nb_drones: int = 0
        self.start_hub: str = ""
        self.end_hub: str = ""
        self.zone: list[str] = []
        self.zone_type: dict[str, str] = {}
        self.connection: list[tuple[str, str]] = []
        self.c_metadata: dict[str, int] = {}
        self.zone_capacity: dict[str, int] = {}
        self.link_capacity: dict[tuple[str, str], int] = {}

    def take_data():
        try:
            if len(sys.argv) > 2 or len(sys.argv) == 1:
        except:
            
