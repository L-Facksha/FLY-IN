# Fly-in — Drone Routing System

*This project has been created as part of the 42 curriculum by \<your_login\>.*

---

## Algorithm Visualization

[![Dijkstra Visualizer](https://img.shields.io/badge/▶%20Dijkstra-Interactive%20Visualizer-4f6ef7?style=for-the-badge)](https://<your-login>.github.io/<your-repo>/dijkstra.html)

> Click the badge above to open the interactive Dijkstra step-by-step visualizer.
> It shows exactly how the algorithm picks nodes, updates distances, and finds the shortest path.

---

## Description

Fly-in is a multi-drone routing system that navigates a fleet of drones from a start zone to a goal zone through a network of connected zones, minimizing the total number of simulation turns.

The system parses a custom map format, builds a weighted graph, finds optimal paths using Dijkstra's algorithm, and schedules drone movements while respecting all zone and connection capacity constraints.

---

## How It Works

### Pipeline

```
Input file → Parser → Graph → Dijkstra → Scheduler → Simulator → Output
```

| Step | File | Role |
|---|---|---|
| Parser | `parser.py` | Reads and validates the map file |
| Graph | `graph.py` | Builds adjacency list with weighted edges |
| Pathfinding | `dijkstra.py` | Finds shortest path per drone |
| Scheduler | `scheduler.py` | Assigns paths and coordinates movement |
| Simulator | `simulator.py` | Runs turn-by-turn, enforces all rules |
| Entry point | `main.py` | Ties everything together |

### Zone Types and Movement Costs

| Zone type | Cost (turns) | Description |
|---|---|---|
| `normal` | 1 | Standard movement |
| `priority` | 1 | Preferred in pathfinding |
| `restricted` | 2 | Drone must complete transit next turn |
| `blocked` | ∞ | Inaccessible — never entered |

---

## Algorithm

### Dijkstra's Algorithm

Dijkstra finds the shortest weighted path from start to goal. It always expands the node with the lowest total cost from the start, guaranteeing an optimal result on non-negative weighted graphs.

**Core formula:**

```
f(n) = g(n)

where g(n) = actual cost from start to node n
```

**Step-by-step:**

1. Set `dist[start] = 0`, all others `= ∞`
2. Pick the unvisited node with the lowest `dist`
3. For each neighbor: `new_cost = dist[current] + edge_cost`
4. If `new_cost < dist[neighbor]` → update it
5. Mark current as visited
6. Repeat until goal is reached
7. Reconstruct path using `prev` pointers

**Interactive visualization:**

[![Dijkstra Visualizer](https://img.shields.io/badge/▶%20Try%20it-Step%20through%20Dijkstra-4f6ef7?style=flat-square)](https://<your-login>.github.io/<your-repo>/dijkstra.html)

### Multi-Drone Scheduling

Dijkstra gives the best path per drone. The scheduler then coordinates all drones to:

- Avoid exceeding zone capacity (`max_drones`)
- Avoid exceeding connection capacity (`max_link_capacity`)
- Handle restricted zones (2-turn transit, no waiting mid-connection)
- Prevent deadlocks

---

## Instructions

### Requirements

- Python 3.10 or later
- `flake8` and `mypy` for linting

### Install

```bash
make install
```

### Run

```bash
make run maps/easy/01_linear.txt
```

### Debug

```bash
make debug maps/easy/01_linear.txt
```

### Lint

```bash
make lint
```

### Clean

```bash
make clean
```

---

## Map Format

```
nb_drones: 4

start_hub: start 0 0 [color=green]
hub: junction 1 0 [color=yellow max_drones=2]
hub: path_a 2 1 [color=blue]
end_hub: goal 3 0 [color=red max_drones=3]

connection: start-junction [max_link_capacity=2]
connection: junction-path_a
connection: path_a-goal
```

**Zone metadata (all optional):**
- `zone=<normal|priority|restricted|blocked>` — default: `normal`
- `max_drones=<N>` — default: `1`
- `color=<value>` — for visual output

**Connection metadata (optional):**
- `max_link_capacity=<N>` — default: `1`

---

## Output Format

Each line represents one simulation turn, listing all drone movements:

```
D1-roof1 D2-corridorA
D1-roof2 D2-tunnelB
D1-goal D2-goal
```

- `D<ID>-<zone>` — drone reached a zone
- `D<ID>-<connection>` — drone in transit toward a restricted zone
- Drones that do not move are omitted
- Drones that reach the goal are no longer tracked

---

## Performance Targets

| Difficulty | Map | Target |
|---|---|---|
| Easy | Linear path (2 drones) | ≤ 6 turns |
| Easy | Simple fork (4 drones) | ≤ 8 turns |
| Easy | Basic capacity (4 drones) | ≤ 6 turns |
| Medium | Dead end trap (5 drones) | ≤ 12 turns |
| Medium | Circular loop (6 drones) | ≤ 15 turns |
| Hard | Maze nightmare (8 drones) | ≤ 30 turns |
| Hard | Capacity hell (12 drones) | ≤ 35 turns |
| Challenger | The Impossible Dream (25 drones) | ≤ 45 turns |

---

## Resources

### Dijkstra's Algorithm
- [Computerphile — Dijkstra's Algorithm (YouTube)](https://www.youtube.com/watch?v=GazC3A4OQTE)
- [Abdul Bari — Dijkstra (YouTube)](https://www.youtube.com/watch?v=XB4MIexjvY0)
- [VisuAlgo — Interactive SSSP Visualizer](https://visualgo.net/en/sssp)
- [cp-algorithms.com — Dijkstra](https://cp-algorithms.com/graph/dijkstra.html)

### Multi-Agent Pathfinding
- [MAPF — Multi-Agent Pathfinding Overview](https://www.movingai.com/MAPF/)

### Python Tools
- [flake8 documentation](https://flake8.pycqa.org/)
- [mypy documentation](https://mypy.readthedocs.io/)

---

## AI Usage

AI (Claude by Anthropic) was used during this project for:

- **Understanding algorithms** — Dijkstra explained step by step with visualizations
- **Code review** — Parser and graph class reviewed for bugs and edge cases
- **Debugging** — Identifying silent error swallowing, wrong cost direction, missing defaults
- **Clarifying concepts** — Zone capacity defaults, bidirectional edges, cost assignment

All generated suggestions were reviewed, tested, and adapted manually. No code was copied without full understanding.