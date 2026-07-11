*This project has been created as part of the 42 curriculum by [L-Facksha].*

---

<div align="center">

# 🚁 FLY-IN — Drone Routing Simulation

[![Dijkstra Visualizer](https://img.shields.io/badge/▶%20Dijkstra-Interactive%20Visualizer-4f6ef7?style=for-the-badge)](https://l-facksha.github.io/FLY-IN/dijkstra.html)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![License](https://img.shields.io/badge/License-42-green?style=for-the-badge)](https://42.fr)

</div>

---

## 📋 Description

**Fly-in** is a multi-drone routing simulation written in Python. The goal is to move a fleet of drones from a single **start zone** to a single **goal zone** through a network of connected zones, minimizing the total number of simulation turns.

The system:
- Reads a custom map file format defining zones, connections, capacities, and zone types
- Computes optimal paths for each drone using **Dijkstra's algorithm + DFS**
- Schedules drone movement turn by turn respecting all constraints
- Displays results in a **colored terminal output** and an optional **graphical interface**

### Zone Types

| Type | Cost (turns) | Description |
|---|---|---|
| `normal` | 1 | Standard zone — default type |
| `priority` | 1 | Preferred in pathfinding over normal zones |
| `restricted` | 2 | Drone enters link on turn 1, arrives on turn 2 |
| `blocked` | ∞ | Inaccessible — drones cannot enter |

---

## 🗂️ File Structure

```
FLY-IN/
├── main.py           — entry point
├── parser.py         — map file parser and validator
├── graph.py          — weighted graph structure
├── algorithm.py      — Dijkstra + DFS pathfinding
├── traffic.py        — multi-drone simulation engine
├── simulator.py      — colored terminal output
├── visualizer.py     — pygame graphical interface
├── dijkstra.html     — interactive algorithm visualizer
├── Makefile
├── README.md
└── maps/
    ├── easy/
    ├── medium/
    ├── hard/
    └── challenger/
```

---

## ⚙️ Instructions

### Requirements

- Python **3.10** or later
- `uv` package manager
- `rich` — styled terminal output
- `pygame` — graphical interface *(optional)*

### Install

```bash
make install
```

### Run

```bash
make run ARGS=maps/easy/02_simple_fork.txt
```

Or directly:

```bash
python3 main.py maps/easy/02_simple_fork.txt
```

### Graphical Visualizer

```bash
python3 visualizer.py maps/easy/02_simple_fork.txt
```

### Debug

```bash
make debug ARGS=maps/easy/02_simple_fork.txt
```

### Lint

```bash
make lint
make lint-strict   # optional — stricter mypy checks
```

### Clean

```bash
make clean
```

---

## 🗺️ Map Format

```
nb_drones: 4

start_hub: start 0 0 [color=green]
hub: junction 1 0 [color=yellow max_drones=2]
hub: path_a   2 1 [zone=normal   color=blue]
hub: path_b   2 -1 [zone=priority color=blue]
end_hub: goal 3 0 [color=red max_drones=4]

connection: start-junction    [max_link_capacity=2]
connection: junction-path_a
connection: junction-path_b
connection: path_a-goal
connection: path_b-goal
```

**Zone metadata** *(all optional)*:
- `zone=<normal|priority|restricted|blocked>` — default: `normal`
- `max_drones=<N>` — default: `1` *(start and goal always accept all drones)*
- `color=<name>` — any single-word color name for visual output

**Connection metadata** *(optional)*:
- `max_link_capacity=<N>` — default: `1`

---

## 📤 Output Format

Each line represents one simulation turn. Moves are separated by ` | `:

```
D1-start | D2-start | D3-start | D4-start
D1-start-junction | D2-start-junction
D1-junction | D2-junction
D1-path_b | D2-path_a
D1-goal | D2-goal
```

| Format | Meaning |
|---|---|
| `D<id>-<zone>` | Drone arrived at zone |
| `D<id>-<from>-<to>` | Drone in transit on restricted link (turn 1 of 2) |

Drones that do not move are omitted. Drones at goal are no longer tracked.

---

## 🧠 Algorithm Choices and Implementation Strategy

### Pipeline

```
Input file → Parser → Graph → Dijkstra → Traffic → Simulator → Output
```

---

### 1. Parser — `parser.py`

Reads and validates the custom map format line by line using **regular expressions**. Extracts drone count, zone definitions with metadata, and connection declarations. Detects:
- Duplicate zones and connections
- Invalid formats and unknown keywords
- Missing `start_hub`, `end_hub`, or `nb_drones`
- Invalid capacity values and zone types

---

### 2. Graph — `graph.py`

Transforms raw parser data into a queryable graph structure:
- **Adjacency list** — bidirectional neighbor lookup per zone
- **Edge weights** — movement cost based on the destination zone type
- **Capacity storage** — zone and link capacities
- **Zone colors** — metadata colors for visual output

Blocked zones are removed from all neighbor lists during construction so pathfinding never routes through them.

---

### 3. Dijkstra + DFS — `algorithm.py`

Finding optimal paths is done in two phases:

**Phase 1 — Dijkstra distances**

Computes the shortest cost from `start` to every zone using a standard greedy Dijkstra loop with a linear scan for the minimum (no priority queue — graph sizes are small enough).

**Time complexity: O(V²)** where V = number of zones.

**Phase 2 — DFS path enumeration**

A depth-first search traverses only edges satisfying:

```
dist[neighbor] == dist[current] + edge_cost
```

This guarantees every collected path is optimal. Produces **all** shortest paths, not just one.

**Practical complexity: O(P × L)** where P = paths found, L = path length.

**Total algorithm complexity:**

```
T(V, P, L) = O(V²  +  P×L  +  P×L×log P)
           = O(2809 +  60   +  95)          ← challenger map values
           = O(V²)                           ← V² dominates
```

Paths are sorted by a score function:
```python
def _score(p) -> tuple[int, int]:
    pri = sum(1 for z in p if zone_type[z] == 'priority')
    return (-pri, len(p))   # more priority zones first, shorter paths first
```

Drones are distributed across all found paths in **round-robin order**, maximizing throughput by spreading load across multiple routes.

---

### 4. Traffic Simulation — `traffic.py`

The simulation runs turn by turn. Each turn has two phases:

**Phase 1 — Arrive transit drones**

Drones that entered a restricted link last turn **must** arrive this turn. The subject states a drone cannot wait on a connection.

**Phase 2 — Move available drones**

For each drone not in transit, check in order:
1. **Link capacity** — reject if connection is full this turn
2. **Zone type** — skip blocked zones
3. **Zone capacity** — computed as:

```
zone_used = zone_count[next]
          - leaving[next]         ← drones leaving next_zone this turn
          + entering[next]        ← drones entering next_zone this turn
```

This accounts for drones entering and leaving the **same zone in the same turn**, allowing maximum throughput.

State updates are deferred until **after the full loop** so earlier drones do not block later ones in the same turn.

**Restricted zone handling**: drone enters link (turn 1, output: `D<id>-<from>-<to>`), arrives next turn (turn 2, output: `D<id>-<zone>`). Zone capacity for restricted destinations is checked at turn 1 using `entering_next_zone` to prevent overbooking.

A **deadlock** is detected when `plan_turn()` returns an empty list while not all drones have reached the goal.

---

## 🎨 Visual Representation

### Terminal Output

Colorized using **ANSI escape codes**. Each zone name is rendered in the color declared in the map file. Turn labels use **Rich** (bold, italic, underline). A styled header panel displays the project name.

```
╭────────────────────────────────╮
│            FLY-IN              │
╰────────────────────────────────╯
- TURN: 0
D1-start | D2-start | D3-start | D4-start

- TURN: 1
D1-start-junction | D2-start-junction

- TURN: 2
D1-junction | D2-junction

Total turns: 7
```

Restricted transit moves are shown as `D<id>-<from>-<to>` on turn 1 and `D<id>-<zone>` on arrival — making the 2-turn movement visually explicit.

---

### Interactive Dijkstra Visualizer

An interactive HTML visualizer is provided at [`dijkstra.html`](dijkstra.html), accessible via the badge at the top of this README.

**Features:**
- Step-by-step walkthrough of Dijkstra's algorithm on a sample graph
- Live distance table updating after each step
- Color-coded nodes: current (yellow), visited (green), updated (blue), path (red)
- Prev / Next step buttons and a progress bar

---

### Pygame Graphical Interface — `visualizer.py`

A full graphical interface built with **Pygame** showing the routing network and animating drone movements in real time.

**Features:**
- Zones drawn as colored circles using metadata colors
- Connections drawn as lines with capacity labels
- Drones shown as small labeled circles that animate smoothly between zones
- Drones on restricted links appear **mid-edge** between the two zone nodes
- Multiple drones at the same zone spread in a circle to remain visible
- Live side panel: current turn, drone positions, this turn's moves
- Speed control buttons: ×0.25 to ×8
- Hover tooltip: zone type, color, capacity, cost, and drones present
- **Live zone editor**: press `E` on any hovered zone to change its type, color, or capacity — simulation reruns instantly

**Controls:**

| Key / Action | Effect |
|---|---|
| `Space` | Play / Pause |
| `→` / `←` | Step forward / back one turn |
| `↑` / `↓` | Speed up / slow down |
| `E` | Edit hovered zone |
| `R` | Rerun simulation |
| `T` | Toggle drone movement trails |
| `Q` / `Esc` | Quit |
| Click speed buttons | Set speed directly |

---

## 📊 Performance Results

| Difficulty | Map | Drones | Turns |
|---|---|---|---|
| Easy | Linear path | 2 | ≤ 6 |
| Easy | Simple fork | 4 | ≤ 8 |
| Medium | Dead end trap | 5 | ≤ 12 |
| Hard | Maze nightmare | 8 | ≤ 30 |
| **Challenger** | **The Impossible Dream** | **25** | **43** ✅ |

> The challenger map target is ≤ 45 turns. Our algorithm achieves **43 turns**.

---

## 📚 Resources

### Dijkstra's Algorithm
- [Computerphile — Dijkstra's Algorithm (YouTube)](https://www.youtube.com/watch?v=GazC3A4OQTE) — clear visual explanation
- [Abdul Bari — Dijkstra (YouTube)](https://www.youtube.com/watch?v=XB4MIexjvY0) — detailed walkthrough with examples
- [VisuAlgo — Interactive SSSP Visualizer](https://visualgo.net/en/sssp) — step through Dijkstra on custom graphs
- [cp-algorithms.com — Dijkstra](https://cp-algorithms.com/graph/dijkstra.html) — implementation reference with complexity analysis
- [Wikipedia — Dijkstra's algorithm](https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm) — formal definition and pseudocode

### Multi-Agent Pathfinding
- [MAPF — Moving AI Lab](https://www.movingai.com/MAPF/) — research overview of multi-agent pathfinding problems
- [Conflict-Based Search for Optimal MAPF](https://ojs.aaai.org/index.php/AAAI/article/view/8140) — academic reference for coordinated drone routing

### Python Tools
- [Rich documentation](https://rich.readthedocs.io/) — styled terminal output library
- [Pygame documentation](https://www.pygame.org/docs/) — 2D graphics and input handling
- [flake8 documentation](https://flake8.pycqa.org/) — Python style checker
- [mypy documentation](https://mypy.readthedocs.io/) — static type checker

---

<div align="center">

Made with ❤️ at **1337**

</div>
