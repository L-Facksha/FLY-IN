from parser import Parser
from traffic import Traffic
from graph import Graph
from algorithm import Dijkstra
from simulator import Simulator
from viz import Visualizer

p = Parser()
p.load_file()
p.parse_file()

g = Graph(p)
g.build(p)

d = Dijkstra(g)

t = Traffic(g, d, p.nb_drones)
# t.run()
turns = t.run()

s = Simulator(g, t)
s.print_turns()
viz = Visualizer(g, turns)
viz.run()
