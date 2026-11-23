*This project has been created as part of the 42 curriculum by [L-Facksha].*

---

<div align="center">

# 🚁 FLY-IN — Drone Routing Simulation

[![Dijkstra Visualizer](https://img.shields.io/badge/▶%20Dijkstra-Interactive%20Visualizer-4f6ef7?style=for-the-badge)](https://l-facksha.github.io/FLY-IN/dijkstra.html)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![License](https://img.shields.io/badge/License-42-green?style=for-the-badge)](https://42.fr)

</div>

<p align="center"><b>Route a fleet of drones from one hub to another through a constrained network, in as few turns as possible.</b></p>

---

## 📑 Table of Contents

- [Description](#-description)
- [Key Features](#-key-features)
- [Tech Stack](#️-tech-stack)
- [Project Structure](#️-project-structure)
- [Getting Started](#️-getting-started)
- [Usage](#-usage)
- [Map Format](#️-map-format)
- [Output Format](#-output-format)
- [How It Works](#-how-it-works)
- [Visual Representation](#-visual-representation)
- [Testing and Code Quality](#-testing-and-code-quality)
- [Performance Results](#-performance-results)
- [Possible Improvements](#-possible-improvements)
- [Resources](#-resources)

---

## 📋 Description

**Fly-in** is a multi-drone routing simulation written in Python. A fleet of drones starts in a single **start hub** and has to reach a single **end hub** through a network of connected zones. The goal is to get every drone to the end hub in the **fewest simulation turns** possible.

Each zone and connection can have constraints: zone type, maximum number of drones in a zone, and maximum number of drones on a connection in the same turn.

The program:

1. Reads and validates a map file written in a custom text format.
2. Builds a weighted, undirected graph of the zones.
3. Finds **all shortest paths** with **Dijkstra's algorithm followed by a DFS**.
4. Spreads the drones over those paths and simulates their movement turn by turn, respecting every capacity constraint.
5. Prints each turn in **colored terminal output**. An optional **Pygame visualizer** animates the same simulation.

### Zone Types

| Type | Cost (turns) | Description |
|---|---|---|
| `normal` | 1 | Standard zone (default type) |
| `priority` | 1 | Same cost as `normal`, but paths with more priority zones are tried first |
| `restricted` | 2 | The drone enters the connection on turn 1 and arrives on turn 2 |
| `blocked` | ∞ | Inaccessible: removed from the graph, drones cannot enter |

---

## ✨ Key Features

- **Strict map parser**: regex-based validation with clear error messages and line numbers.
- **Optimal pathfinding**: Dijkstra distances plus a DFS that lists *every* shortest path, not just one.
- **Load balancing**: drones are assigned to the shortest paths in round-robin order to use several routes at once.
- **Capacity-aware simulation**: zone capacity (`max_drones`) and connection capacity (`max_link_capacity`) are enforced on every turn.
- **Two-turn restricted moves**: drones in transit to a restricted zone are shown on the connection, then on the zone.
- **Colored terminal output**: each zone is printed in the color declared in the map, using ANSI codes and [Rich](https://rich.readthedocs.io/).
- **Pygame visualizer** (`viz.py`): animated drones, playback controls, tooltips, and a live zone editor.
- **Interactive Dijkstra page** (`dijkstra.html`): a browser page that runs Dijkstra step by step on an editable sample graph.

---

## 🛠️ Tech Stack

| Tool | Role |
|---|---|
| **Python** | Language (the code uses modern type hints such as `str \| None` and `list[str]`) |
| **[uv](https://docs.astral.sh/uv/)** | Dependency and virtual environment manager (`make install`, `make run`) |
| **[Rich](https://rich.readthedocs.io/)** | Styled terminal output (header panel, turn labels, errors) |
| **[Pygame](https://www.pygame.org/)** | Graphical visualizer (`viz.py`, optional) |
| **[flake8](https://flake8.pycqa.org/)** / **[mypy](https://mypy.readthedocs.io/)** | Style checks and static type checks (`make lint`) |
| **HTML / CSS / JavaScript (SVG)** | Standalone Dijkstra visualizer (`dijkstra.html`) |
| **Make** | Task shortcuts |

---

## 🗂️ Project Structure

```
FLY-IN/
├── main.py           — entry point: runs Parser → Graph → Dijkstra → Traffic → Simulator
├── parser.py         — reads and validates the map file
├── graph.py          — weighted graph: adjacency list, costs, capacities, colors
├── algorithm.py      — Dijkstra + DFS: lists all shortest paths
├── traffic.py        — turn-by-turn multi-drone simulation
├── simulator.py      — colored terminal output
├── viz.py            — Pygame graphical visualizer
├── dijkstra.html     — interactive Dijkstra visualizer (browser)
├── maps.tar.gz       — archive of test maps (see below)
├── en.subject.pdf    — project subject (42)
├── pyproject.toml    — project metadata and dependencies
├── Makefile
└── README.md
```

The `maps.tar.gz` archive extracts to a `maps/` folder:

```
maps/
├── README.md       — description of every map and its challenges
├── easy/           — 01_linear_path, 02_simple_fork, 03_basic_capacity
├── medium/         — 01_dead_end_trap, 02_circular_loop, 03_priority_puzzle
├── hard/           — 01_maze_nightmare, 02_capacity_hell, 03_ultimate_challenge
└── challenger/     — 01_the_impossible_dream
```

---

## ⚙️ Getting Started

### Requirements

- **Python 3**: the code runs on Python 3.10+, but `pyproject.toml` sets `requires-python = ">=3.13"`, so `uv sync` sets up Python 3.13 or later.
- **[uv](https://docs.astral.sh/uv/)** package manager
- Dependencies declared in `pyproject.toml`: `rich`, `flake8`, `mypy`
- `pygame`: needed **only** for the graphical visualizer. It is **not** listed in `pyproject.toml`, so install it separately.

### Installation

```bash
git clone https://github.com/L-Facksha/FLY-IN.git
cd FLY-IN

# Install the dependencies listed in pyproject.toml (runs `uv sync`)
make install

# Extract the test maps into ./maps
tar -xzf maps.tar.gz
```

To use the graphical visualizer, add Pygame to the environment:

```bash
uv pip install pygame
```

---

## 🚀 Usage

### Run a simulation

```bash
make run ARGS=maps/easy/02_simple_fork.txt
```

Or run it directly in the uv environment:

```bash
uv run main.py maps/easy/02_simple_fork.txt
```

`python3 main.py <path_map>` also works if `rich` is installed in your active environment. If no map path is given, the program prints the usage and exits.

### Launch the graphical visualizer

```bash
uv run viz.py maps/easy/02_simple_fork.txt
```

### Open the Dijkstra visualizer

Open it online with the badge at the top of this README, or open [`dijkstra.html`](dijkstra.html) in any browser. No server is needed.

### Makefile targets

| Command | Description |
|---|---|
| `make install` | Install dependencies with `uv sync` |
| `make run ARGS=<map>` | Run the simulation on a map |
| `make debug ARGS=<map>` | Run the simulation in the `pdb` debugger |
| `make lint` | Run `flake8` and `mypy` with strict typing flags |
| `make clean` | Remove `__pycache__`, `.mypy_cache`, `.ruff_cache`, `.vscode`, and `*.pyc` files |

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

| Line | Syntax | Rules |
|---|---|---|
| Drone count | `nb_drones: <N>` | Required, declared once, must be positive |
| Start hub | `start_hub: <name> <x> <y> [metadata]` | Required, declared once |
| Hub | `hub: <name> <x> <y> [metadata]` | Unique name and unique coordinates |
| End hub | `end_hub: <name> <x> <y> [metadata]` | Required, declared once |
| Connection | `connection: <a>-<b> [max_link_capacity=<N>]` | Both hubs must exist; no duplicates, no self-loops |
| Comment | `# ...` | Ignored, either as a full line or after a declaration |

Zone names cannot contain spaces or `-`. The map must contain at least one connection.

**Zone metadata** *(all optional, separated by spaces inside `[...]`)*:
- `zone=<normal|priority|restricted|blocked>`: default `normal`
- `max_drones=<N>`: default `1`. Start and end hubs always accept all drones (their capacity is set to `nb_drones`).
- `color=<name>`: a single-word color name for the output. Unknown colors are printed in the default color.

**Connection metadata** *(optional)*:
- `max_link_capacity=<N>`: default `1`. Counts drones on the connection in **both** directions in the same turn.

Any invalid line stops the program with a red `💥` error message that gives the line number.

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

## 🧠 How It Works

### Pipeline

```
Input file → Parser → Graph → Dijkstra → Traffic → Simulator → Output
```

| Module | Class | Responsibility |
|---|---|---|
| `parser.py` | `Parser` | Read the file from `sys.argv[1]`, validate it, and store zones, metadata, connections, and capacities |
| `graph.py` | `Graph` | Build the adjacency list, movement costs, capacities, and colors |
| `algorithm.py` | `Dijkstra` | Compute distances and list every shortest path |
| `traffic.py` | `Traffic` | Assign paths to drones and plan every turn |
| `simulator.py` | `Simulator` | Print the turns with colors |
| `main.py` | `Main` | Connect the steps above in order |

---

### 1. Parser — `parser.py`

Reads and validates the custom map format line by line using **regular expressions**. Extracts drone count, zone definitions with metadata, and connection declarations. Detects:
- Duplicate zones, coordinates, and connections
- Invalid formats, unknown keywords, and unknown metadata keys
- Missing `start_hub`, `end_hub`, or `nb_drones`, and repeated declarations of them
- Invalid capacity values and zone types
- Connections to unknown hubs and connections from a hub to itself

---

### 2. Graph — `graph.py`

Transforms raw parser data into a queryable graph structure:
- **Adjacency list**: neighbors of each zone, in both directions
- **Edge weights**: movement cost, set by the type of the **destination** zone
- **Capacity storage**: zone and link capacities
- **Zone colors**: metadata colors for visual output

Blocked zones are removed from all neighbor lists during construction so pathfinding never routes through them.

---

### 3. Dijkstra + DFS — `algorithm.py`

Paths are found in two phases.

**Phase 1: Dijkstra distances**

Computes the shortest cost from `start` to every zone with a standard greedy Dijkstra loop. The next zone is picked with a linear scan instead of a priority queue, because the maps are small.

**Time complexity: O(V²)** where V = number of zones.

**Phase 2: DFS path enumeration**

A depth-first search traverses only edges satisfying:

```
dist[neighbor] == dist[current] + edge_cost
```

This guarantees every collected path is optimal. Produces **all** shortest paths, not just one.

**Practical complexity: O(P × L)** where P = paths found, L = path length.

**Total algorithm complexity:**

```
T(V, P, L) = O(V²  +  P×L  +  P×L×log P)
           = O(V²)          ← V² dominates (the challenger map has V = 54 zones)
```

Paths are sorted by a score function:
```python
def _score(p) -> tuple[int, int]:
    pri = sum(1 for z in p if zone_type[z] == 'priority')
    return (-pri, len(p))   # more priority zones first, shorter paths first
```

Drones are distributed across all found paths in **round-robin order**. This spreads the load over several routes and increases throughput.

---

### 4. Traffic Simulation — `traffic.py`

The simulation runs turn by turn. Each turn has two phases:

**Phase 1: Arrive transit drones**

Drones that entered a restricted link last turn **must** arrive this turn. The subject states a drone cannot wait on a connection.

**Phase 2: Move available drones**

For each drone not in transit, check in order:
1. **Link capacity**: skip the move if the connection is full this turn (both directions count)
2. **Zone type**: skip blocked zones
3. **Zone capacity**: computed as:

```
zone_used = zone_count[next]
          - leaving[next]         ← drones leaving next_zone this turn
          + entering[next]        ← drones entering next_zone this turn
```

This counts drones that enter and leave the **same zone in the same turn**, so a zone can be refilled as soon as it empties.

State updates are applied **after the full loop**, so drones checked earlier in a turn do not block drones checked later.

**Restricted zone handling**: the drone enters the link on turn 1 (output `D<id>-<from>-<to>`) and arrives on turn 2 (output `D<id>-<zone>`). Zone capacity for a restricted destination is checked on turn 1 with `entering_next_zone`, so the zone cannot be overbooked.

**Termination**: the simulation stops when every drone has reached the end hub. As a safety limit, it runs at most `nb_drones × 10` turns, so a blocked situation cannot loop forever. Turns with no moves are not printed. If no path exists between the start and end hubs, the program stops with a `Path not found` error.

---

## 🎨 Visual Representation

### Terminal Output

Colored with **ANSI escape codes**. Each zone name is printed in the color declared in the map file (about 40 named colors are supported, such as `red`, `orange`, `gold`, `teal`, and `violet`). Turn labels use **Rich** (bold, italic, underline). A styled header panel displays the project name.

```
╭────────────────────────────────╮
│            FLY-IN              │
╰────────────────────────────────╯
- TURN: 0
D1-start | D2-start | D3-start | D4-start

- TURN: 1
D1-junction | D2-junction

- TURN: 2
D1-path_a | D2-path_b | D3-junction | D4-junction

- TURN: 3
D1-goal | D2-goal | D3-path_a | D4-path_b

- TURN: 4
D3-goal | D4-goal

Total turns: 4
```

*(Actual output of `maps/easy/02_simple_fork.txt`, without colors.)*

Restricted transit moves are shown as `D<id>-<from>-<to>` on turn 1 and `D<id>-<zone>` on arrival, so the 2-turn movement is visible in the output.

---

### Interactive Dijkstra Visualizer

An interactive HTML visualizer is provided at [`dijkstra.html`](dijkstra.html), accessible via the badge at the top of this README.

**Features:**
- Step-by-step run of Dijkstra's algorithm on a sample graph (start `S`, end `Z`)
- Click a node to change its zone type (`normal`, `blocked`, `priority`, `restricted`). Drag nodes to move them.
- Live distance table (`dist`, `prev`, `done`) updated after each step
- Color-coded nodes: current, updated, neighbor, and shortest path
- **Run Dijkstra**, **Prev step** / **Next step**, **Reset map**, **Clear path** buttons, and a progress bar

---

### Pygame Graphical Interface — `viz.py`

A full graphical interface built with **Pygame** (1440×880 window) that shows the routing network and animates drone movements in real time.

**Features:**
- Zones drawn as colored circles using metadata colors
- Connections drawn as lines with capacity labels
- Drones shown as small labeled circles that move smoothly between zones
- Drones on restricted links appear **mid-edge** between the two zone nodes
- Several drones in the same zone are spread in a circle so each stays visible
- Live side panel: current turn, drone positions, this turn's moves
- Speed control buttons: ×0.25 to ×8
- Hover tooltip: zone type, color, capacity, cost, and drones present
- **Live zone editor**: press `E` while hovering a zone to change its type, color, or capacity. The simulation reruns immediately.

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

## 🧪 Testing and Code Quality

The project has no automated test suite. Code quality is checked with linting and type checking:

```bash
make lint
```

This runs `flake8 .` and `mypy .` with `--warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs`.

To check behavior, run the simulation on the provided maps, from easy to challenger:

```bash
tar -xzf maps.tar.gz    # if not already extracted
for map in maps/*/*.txt; do
    echo "== $map"
    uv run main.py "$map" | tail -n 1
done
```

See `maps/README.md` (inside the archive) for what each map tests: dead ends, loops, capacity limits, and zone types.

---

## 📊 Performance Results

Turn counts printed by `main.py` (`Total turns`) for each provided map:

| Difficulty | Map | Drones | Turns |
|---|---|---|---|
| Easy | `01_linear_path` | 2 | 4 |
| Easy | `02_simple_fork` | 4 | 4 |
| Easy | `03_basic_capacity` | 4 | 4 |
| Medium | `01_dead_end_trap` | 5 | 8 |
| Medium | `02_circular_loop` | 6 | 15 |
| Medium | `03_priority_puzzle` | 5 | 8 |
| Hard | `01_maze_nightmare` | 8 | 13 |
| Hard | `02_capacity_hell` | 12 | 16 |
| Hard | `03_ultimate_challenge` | 15 | 26 |
| **Challenger** | **`01_the_impossible_dream`** | **25** | **43** ✅ |

> The challenger map target is ≤ 45 turns (the reference record in `maps/README.md`). Our algorithm achieves **43 turns**.

---

## 🔭 Possible Improvements

Ideas based on the current implementation (not implemented):

- Use a heap-based priority queue (`heapq`) in Dijkstra for larger maps.
- Consider near-optimal paths too, not only the strictly shortest ones, to add capacity on congested maps.
- Add `pygame` to `pyproject.toml` (for example as an optional dependency) so `make install` sets up the visualizer.
- Add a `pytest` suite for the parser and simulation rules.

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
