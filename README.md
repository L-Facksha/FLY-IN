V# *This project has been created as part of the 42 curriculum by azebahad*

# FLY-IN

## Description

FLY-IN is a drone traffic simulation project that models autonomous drones navigating through a network of interconnected hubs while respecting movement and capacity constraints.

The objective is to transport all drones from a designated **start hub** to an **end hub** in the minimum number of simulation turns. The simulation considers several real-world constraints, including:

- Zone capacities
- Link capacities
- Blocked zones
- Restricted zones
- Priority zones

The project is implemented in **Python** using an object-oriented architecture and includes both a **terminal simulation**.

---

## Features

- Complete map parser with validation
- Weighted graph construction
- Dijkstra shortest-path algorithm
- Multiple shortest-path extraction
- Multi-drone traffic scheduler
- Capacity-aware routing
- Support for blocked, restricted and priority zones
- Colored terminal output using Rich
- Interactive visualization using Pygame
- Static type checking with mypy
- Documentation using NumPy-style docstrings

---

## Project Structure

```text
.
├── algorithm.py
├── graph.py
├── parser.py
├── traffic.py
├── simulator.py
├── main.py
├── maps/
└── README.md
```

---

## Instructions

### Requirements

- Python 3.10+
- pip

### Install dependencies

```bash
make install
```

### Run the simulation

```bash
uv run main.py <path_map>
or 
make run ARGS<path_map>
```

---

## Input Format

Example map:

```text
nb_drones: 5

start_hub: A 0 0 [color=green]

hub: B 4 0 [zone=priority]

hub: C 8 0 [zone=restricted]

end_hub: D 12 0 [color=red]

connection: A-B
connection: B-C
connection: C-D
```

---

# Algorithm Choices and Implementation Strategy

## 1. Parser

The parser is responsible for reading and validating the map file before the simulation begins.

It verifies:

- number of drones
- hub declarations
- coordinates
- metadata
- capacities
- graph connections

Invalid maps immediately generate descriptive errors.

---

## 2. Graph Construction

The validated map is transformed into a weighted graph.

The graph stores:

- adjacency list
- movement costs
- zone capacities
- link capacities
- zone colors
- zone types

Movement costs are assigned according to the destination zone:

| Zone Type | Cost |
|-----------|-----:|
| Normal | 1 |
| Priority | 1 |
| Restricted | 2 |
| Blocked | ∞ |

Blocked zones are removed from the graph.

---

## 3. Pathfinding

The project uses **Dijkstra's algorithm**.

First, Dijkstra computes the minimum distance from the start hub to every reachable hub.

A Depth-First Search (DFS) is then performed to reconstruct every shortest path.

When several shortest paths exist, they are ordered according to:

1. Number of priority zones.
2. Path length.

This allows drones to naturally prefer routes containing priority zones.

---

## 4. Traffic Scheduling

The simulation proceeds one turn at a time.

For every turn:

- drones currently travelling through restricted zones are updated;
- each remaining drone attempts to move;
- link capacities are verified;
- zone capacities are checked;
- restricted zones require two turns to traverse;
- deadlocks are detected automatically.

The scheduler maximizes simultaneous movements while respecting every project constraint.

---

## Visual Representation

## Terminal Interface

The terminal interface combines **ANSI escape codes** and the **Rich** library to provide a clear and visually appealing simulation output.

**ANSI escape codes** are used to color zone names according to their configured metadata, making it easy to distinguish hubs and follow drone movements.

The **Rich** library is used to improve the presentation of the simulation by displaying:

- a formatted title panel;
- styled turn headers;
- organized turn-by-turn output;
- the final simulation statistics.

This combination enhances readability while keeping the simulation lightweight and easy to follow directly from the terminal.


## Technologies

- Python
- Rich
- mypy
- Ruff

---

## Resources

### Documentation

- Python Documentation: https://docs.python.org/3/
- Rich Documentation: https://rich.readthedocs.io/
- mypy Documentation: https://mypy.readthedocs.io/
- DSA Dijkstra's Algorithm: https://www.w3schools.com/dsa/dsa_algo_graphs_dijkstra.php
- DFS Algorithm: https://www.codecademy.com/article/depth-first-search-dfs-algorithm
- DFS visualization: https://www.cs.usfca.edu/~galles/visualization/DFS.html

### Algorithms

- Dijkstra's Algorithm
- Graph Theory
- Depth-First Search (DFS)

### AI Usage

AI assistance was primarily used for:

- explaining the theory and implementation of **Dijkstra's algorithm**, including how shortest paths are computed and reconstructed.
- explaining how **Depth-First Search (DFS)** is used to enumerate all shortest paths after the shortest distances have been calculated.
- improving understanding of graph algorithms and their application to drone routing.

---
