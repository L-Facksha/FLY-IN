from parser import Parser


# from traffic import Traffic
# from algorithm import Dijkstra
# from graph import Graph
# from parser import Parser
# import sys
# sys.argv = ["test.py", "/goinfre/azebahad/FLY-IN/maps/hard/01_maze_nightmare.txt"]


# p = Parser()
# p.load_file()
# p.parse_file()

# g = Graph(p)
# g.build(p)

# d = Dijkstra(g)
# t = Traffic(g, d, p.nb_drones)
# t.construction_paths()

# # manually fill all zones on the path to force deadlock
# path = t.dijkstra.run(g.start, g.end)
# print("Path:", path)

# # block every zone except start
# for zone in path[1:]:
#     t.zone_count[zone] = g.get_zone_capacity(zone)

# print("Forcing deadlock...")
# moves = t.plan_turn()
# print("Moves:", moves)   # → [] empty

# now simulate what run() does
# if not moves:
#     print("ERROR: No drone can move anymore")
from graph import Graph
from algorithm import Dijkstra
from traffic import Traffic
import sys

# sys.argv = ["test.py", "maps/easy/02_simple_fork.txt"]

p = Parser()
p.load_file()
p.parse_file()

g = Graph(p)
g.build(p)

d = Dijkstra(g)
t = Traffic(g, d, p.nb_drones)
try:
    t.construction_paths()

    # test one turn at a time
    print("=== Turn 1 ===")
    moves = t.plan_turn()
    print(moves)

    print("=== Turn 2 ===")
    moves = t.plan_turn()
    print(moves)

    print("=== Turn 3 ===")
    moves = t.plan_turn()
    print(moves)

    print("=== Turn 4 ===")
    moves = t.plan_turn()   # ← actually call it
    print(moves)

    print("=== Turn 5 ===")
    moves = t.plan_turn()
    print(moves)

    print("=== Turn 6 ===")
    moves = t.plan_turn()
    print(moves)

    print("=== Turn 7 ===")
    moves = t.plan_turn()
    print(moves)

    print("=== Turn 8 ===")
    moves = t.plan_turn()
    print(moves)

    print("=== Turn 9 ===")
    moves = t.plan_turn()
    print(moves)

    print("=== Turn 10 ===")
    moves = t.plan_turn()
    print(moves)

    print("=== Turn 11 ===")
    moves = t.plan_turn()
    print(moves)

    print("=== Turn 12 ===")
    moves = t.plan_turn()
    print(moves)

    print("=== Turn 13 ===")
    moves = t.plan_turn()
    print(moves)

    print("=== Turn 14 ===")
    moves = t.plan_turn()
    print(moves)

    print("=== Turn 15 ===")
    moves = t.plan_turn()
    print(moves)

    print("=== Turn 16 ===")
    moves = t.plan_turn()
    print(moves)

    print("=== Turn 17 ===")
    moves = t.plan_turn()
    print(moves)

    print("=== Turn 18 ===")
    moves = t.plan_turn()
    print(moves)

    print("=== Turn 19 ===")
    moves = t.plan_turn()
    print(moves)

    print("=== Turn 20 ===")
    moves = t.plan_turn()
    print(moves)

    print("=== Turn 21 ===")
    moves = t.plan_turn()
    print(moves)

    print("=== Turn 22 ===")
    moves = t.plan_turn()
    print(moves)

    print("=== Turn 23 ===")
    moves = t.plan_turn()
    print(moves)

    print("=== Turn 24 ===")
    moves = t.plan_turn()
    print(moves)

    print("=== Turn 25 ===")
    moves = t.plan_turn()
    print(moves)

    print("=== Turn 26 ===")
    moves = t.plan_turn()
    print(moves)

    print("=== Turn 27 ===")
    moves = t.plan_turn()
    print(moves)

    print("=== Turn 28 ===")
    moves = t.plan_turn()
    print(moves)

    print("=== Turn 29 ===")
    moves = t.plan_turn()
    print(moves)

    print("=== Turn 30 ===")
    moves = t.plan_turn()
    print(moves)

    print("=== Turn 31 ===")
    moves = t.plan_turn()
    print(moves)

    print("=== Turn 32 ===")
    moves = t.plan_turn()
    print(moves)

    print("=== Turn 33 ===")
    moves = t.plan_turn()
    print(moves)

    print("=== Turn 34 ===")
    moves = t.plan_turn()
    print(moves)

    print("=== Turn 35 ===")
    moves = t.plan_turn()
    print(moves)

    print("=== Turn 36 ===")
    moves = t.plan_turn()
    print(moves)

    print("=== Turn 37 ===")
    moves = t.plan_turn()
    print(moves)

    print("=== Turn 38 ===")
    moves = t.plan_turn()
    print(moves)

    print("=== Turn 39 ===")
    moves = t.plan_turn()
    print(moves)

    print("=== Turn 40 ===")
    moves = t.plan_turn()
    print(moves)

    print("=== Turn 41 ===")
    moves = t.plan_turn()
    print(moves)

    # print("=== Turn 42 ===")
    # moves = t.plan_turn()

    # print("=== Turn 43 ===")
    # moves = t.plan_turn()

    # print("=== Turn 44 ===")
    # moves = t.plan_turn()

    # print("=== Turn 45 ===")
    # moves = t.plan_turn()

    # print("=== Turn 46 ===")
    # moves = t.plan_turn()

    # print("=== Turn 47 ===")
    # moves = t.plan_turn()

    # print("=== Turn 48 ===")
    # moves = t.plan_turn()

    # print("=== Turn 49 ===")
    # moves = t.plan_turn()

    # print("=== Turn 50 ===")
    # moves = t.plan_turn()

    # print("=== Turn 51 ===")
    # moves = t.plan_turn()

    # print("=== Turn 52 ===")
    # moves = t.plan_turn()

    # print("=== Turn 53 ===")
    # moves = t.plan_turn()

    # print("=== Turn 54 ===")
    # moves = t.plan_turn()

    # print("=== Turn 55 ===")
    # moves = t.plan_turn()

    # print("=== Turn 56 ===")
    # moves = t.plan_turn()

    # print("=== Turn 57 ===")
    # moves = t.plan_turn()

    # print("=== Turn 58 ===")
    # moves = t.plan_turn()

    # print("=== Turn 59 ===")
    # moves = t.plan_turn()

    # print("=== Turn 60 ===")
    # moves = t.plan_turn()
except Exception as error:
    print(error)
# print("=== drone positions ===")
# print(t.drone_zone)

# print("=== drone steps ===")
# print(t.drone_step)
# print("zone_count:", t.zone_count)
# print("drone_zone:", t.drone_zone)

# t = Traffic(g, d, p.nb_drones)
turns = t.run()

for i, turn in enumerate(turns, 1):
    print(f"Turn {i}: {' '.join(turn)}")

print(f"\nTotal turns: {len(turns)}")
####################################################
# print(g.get_neighbors("start"))                    # ['gate_hell1']
# print(g.get_cost("start", "gate_hell1"))           # 1
# print(g.get_cost("gate_hell3", "maze_loop1"))      # 2 (restricted)
# print(g.get_zone_capacity("start"))                # 25
# print(g.get_link_capacity("start", "gate_hell1"))  # 1
# path = d.run(g.start, g.end)
# print(path)
# print("Cost:", sum(g.get_cost(path[i], path[i+1]) for i in range(len(path)-1)))


# import re

# data = "connection: gate_hell1-gate_hell2 [max_link_capacity=5]"
# data = data.split(":")[1]


# extract = re.search(r"(\w+)\-(\w+)", data)
# from_zone = extract.group(1)
# to_zone = extract.group(2)
# print(from_zone, to_zone)
# # extract = re.search(r"\[(.*?)\]", data)
# # check = extract.group(1).split("=")[0]
# try:
#     extract = re.search(r"\[(.*?)\]", data)
#     check = extract.group(1)
#     if not "max_link_capacity" in check:
#         raise
# except:
#     raise ValueError("Invalid format: usage [max_link_capacity=number]")

# capacity = int(extract.group(1).split("=")[1])
# link_capacity = {}
# link_capacity[(from_zone, to_zone)] = capacity
# print(link_capacity)
# print(extract)
# print(int(extract.group(1).split("=")[1]))


# extract = re.search(r"\[(.*?)\]", data)


# meta = extract.group().split(" ")

# res = {}
# for item in meta:
#     key, val = item.split("=")
#     res[key] = int(val) if val.isdigit() else val

# print(res)


# cords = re.search(r"(\w+)\s*(-?\d+)\s*(-?\d+)", data)
# print(cords)
# st = cords.group(1)
# nb = cords.group(2)
# d_nb = int(cords.group(2))
# d_nbx = int(cords.group(3))
# di: dict[str, tuple[int, int]] = {}
# # if len(nb) != 1:
# #     print("Invalid nb_drones format")
# di[st] = (d_nb, d_nbx)
# print(type(nb))
# print(nb)
# print(type(d_nb))
# print(d_nb)
# print(di)
