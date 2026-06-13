from parser import Parser
from graph import Graph
from algorithm import Dijkstra

p = Parser()
p.load_file()
p.parse_file()
g = Graph(p)
g.build(p)
d = Dijkstra(g)

print(g.neighbors)
print(g.get_neighbors("start"))                    # ['gate_hell1']
print(g.get_cost("start", "gate_hell1"))           # 1
print(g.get_cost("gate_hell3", "maze_loop1"))      # 2 (restricted)
print(g.get_zone_capacity("start"))                # 25
print(g.get_link_capacity("start", "gate_hell1"))  # 1
path = d.run(g.start, g.end)
print(path)
print("Cost:", sum(g.get_cost(path[i], path[i+1]) for i in range(len(path)-1)))


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
