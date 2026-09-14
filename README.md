 This project has been created as part of the 42 curriculum by *gabde-so*, *juasanta*

 # A-Maze-ing 🧩

 ## Description

### What is A-Maze-ing?

A-Maze-ing is a Python maze generator and visualizer. Given a configuration file,
it procedurally generates a valid maze, writes it to an output file using a
hexadecimal wall encoding, and renders it visually in the terminal. The maze can be *perfect*, meaning there is exactly one path between the entry and the exit.

### Project overview

The project covers several areas of computer science:

- **Graph theory**: maze generation relies on spanning tree algorithms.
- **Pathfinding**: the shortest path between entry and exit is computed using BFS.
- **Visualization**: the maze is displayed in the terminal using ANSI colours.
- **Code reusability**: the maze generation logic can be packaged as a standalone
  pip-installable Python module (`mazegen-*`).
- **"42" easter egg**: a visible "42" pattern is embedded into ~~almost~~ every generated maze
  using fully closed cells.

### The team

| Member | Role |
|---|---|
| gabde-so | Imperfect maze generation algorithms, configuration parser, visualizatio, 42 pattern, bonus game |
| juasanta | Perfect maze generation algorithms, pathfinding, output file format, reusable module, bonus loading animation |

---

## Instructions

### Using the Makefile

```bash
# Install dependencies
make install

# Run with default config
make run

# Run in debug mode (pdb)
make debug

# Lint (flake8 + mypy)
make lint

# Optional stricter lint
make lint-strict

# Builds the package using poetry
make build

# Clean caches
make clean
```

### Using the script directly

```bash
python3 a_maze_ing.py config.txt
```

- `a_maze_ing.py` is the main entry point (name is mandatory per subject).
- `config.txt` is the path to your configuration file (see section below).

### Using the standalone module

Install from the built package:

```bash
pip install .whl-file
# or
pip install .tar.gz-file
```

Basic usage example:

```python
from mazegen import MazeGenerator

# Instantiate with custom parameters
gen = MazeGenerator(width=20, height=15, seed=42, perfect=True)
gen.generate()

# Access the maze grid (list of lists of cells objects)
grid = gen.get_grid         # access the hex value of each cell

# Access entry / exit
entry = gen.entry        # (x, y)
exit_  = gen.exit        # (x, y)

# The output of the maze will be accesible through the output file sent during the creation of Maze object.
```

Using the terminal:

```bash
python3 -c "
from mazegen import MazeGenerator
m = MazeGenerator(10, 10, (0,0), (9,9), 'out.txt', perfect=False, seed='test')
m.generate()
solution=m._path_finding()

print(solution)
"
```

Build the package from source:

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install build
python3 -m build        # produces dist/mazegen-*.whl and dist/mazegen-*.tar.gz
```

---

## Config file structure

The configuration file follows a simple `KEY=VALUE` format. Lines starting with
`#` are treated as comments and ignored.

```ini
# ─── Mandatory keys ───────────────────────────────────────────
WIDTH=10            # Number of columns (cells)
HEIGHT=10         # Number of rows (cells)
ENTRY=0,0           # Entry cell coordinates (x,y), 0-indexed
EXIT=0,0         # Exit cell coordinates (x,y), 0-indexed
OUTPUT_FILE=maze.txt  # Path of the output file to write
PERFECT=True        # True → exactly one path from entry to exit

# ─── Optional keys ────────────────────────────────────────────
SEED=42             # interger seed for reproducibility (default: random)
```

Constraints:
- `WIDTH` and `HEIGHT` must be positive integers ≥ 3 (below that the "42"
  pattern cannot fit and a warning is printed).
- `ENTRY` and `EXIT` must be different cells inside the maze bounds.

A default `config.txt` is provided at the root of the repository.

---

## The maze algorithm

### Backtracking (recursive / iterative DFS)

The **randomised depth-first search** (also called *recursive backtracker*) works as
follows:
1. Start from a random cell; mark it visited.
2. Pick a random unvisited neighbour; carve a passage to it; move there.
3. If no unvisited neighbour exists, backtrack to the previous cell.
4. Repeat until all cells are visited.

It produces mazes with long, winding corridors and few dead-ends. As you can see this algorithm is recursive however to avoid the Python recursive limit we decided to use an iteration through a stack to increase efficiency when creating large mazes.

### Breadth-first search (pathfinding only)

BFS is **not** used for generation — it is used to compute the **shortest valid
path** from entry to exit once the maze has been built. It explores cells level by
level, guaranteeing the minimum number of steps, and reconstructs the path as a
sequence of N / E / S / W characters.

### Why these algorithm?

We chose **backtracking as the default** because it naturally avoids 3×3 open areas (the corridor-width constraint from the subject) and produces mazes that feel challenging to solve visually.

The algorithm produces a *perfect maze* (spanning trees), making the BFS solution
path always unique when `PERFECT=True`.

---

## The reusability of A-Maze-ing

The maze generation logic lives entirely in `mazegen/maze_generator.py` and is
distributed as the `mazegen` package (see *Using the standalone module* above).

What is reusable:

- `MazeGenerator` — instantiate with `width`, `height`, `seed`, `perfect`,
  `algorithm` (`"backtracking"`).
- `.generate()` — builds the maze in-place.
- `.grid` — 2-D list of int bitmasks (N=bit0, E=bit1, S=bit2, W=bit3).
- `_path_finding()` — string of N/E/S/W directions (shortest path).
- `.entry` / `.exit` — `(x, y)` tuples.
- The output file writer (`_create_output()`).

What is *not* part of the reusable module:

- The configuration file parser (`config_parser.py`).
- The terminal visualization (`maze_visualizer.py`).
- The main program (`a_maze_ing.py`)
- The bonus game using the curses library

The module has no external dependencies beyond the Python standard library, so it
can be installed in any Python 3.10+ environment without conflicts.

## Bonuses

For A-maze-ing, we considered many bonus features and successfully implemented a few. Due to the short time frame, we decided not to pursue options like adding extra animations or additional maze generation algorithms.

Here are the bonus features we included in our project:

- **Loading Animation:** A custom animation plays during every maze generation.

- **Smart Entry/Exit Adjustments:** If a user selects an entry or exit point that falls inside a wall, the system automatically moves that point to the nearest available open path.

- **Interactive Game Mode:** Users can actually play through the generated maze! Movement is controlled using the keyboard arrow keys (`UP`, `DOWN`, `LEFT`, `RIGHT`), and pressing Q exits the game. A success message is displayed once the player reaches the exit. This interactive window utilizes the `curses` library; since this is part of the Python Standard Library for UNIX, no external dependencies are required to run the game.

---

## Project planning and development

### Roles

**gabde-so:** 
- Maze generation (imperfect maze logic, validation logic)
- Config parser
- Terminal renderer (ANSI)
- "42" pattern placement
- Main program logic
- Bonus interactive game

**juasanta:**
- Maze generation(backtracking)
- Hex output writer
- BFS solver
- Makefile
- README
- reusable module packaging

The original planned agenda:
# Agenda
## Developer A: The Core Architect (Logic & Data)

- **Maze Engine:** Design the `MazeGenerator` class and the data structures holding the grid.
- **Generation Algorithm:** Implement the logic to carve the maze, ensuring connectivity, handling the `PERFECT` flag , and carving the "42" pattern. Use at least two algorithms.
- **Solver (Pathfinding):** Write the algorithm (like BFS) to find the shortest path from `ENTRY` to `EXIT`.
- **Packaging:** Handle the modern Python packaging (creating the `mazegen-*` `.whl` or `.tar.gz` file).

## Developer B: The Integrator (I/O, Visuals & UI)
- **Config & Parser:** Build the system to read and validate `config.txt` and extract the mandatory keys. [GABI]
- **File Output:** Translate the maze state into the exact hexadecimal format, appending the entry/exit and the N/E/S/W solution string.
- **Visual Interface (MLX)** Since we discussed MLX, build the graphical window, draw the maze, and map the key hooks (regenerate, toggle path, change colors) .
- **Infrastructure:** Set up the `Makefile` (rules for install, run, lint, etc.).

As you can see we wanted to implement more bonuses but due to the time we decided not to and we also didn't use MLX and ended going with ANSI.

## Resources

### Bibliography

- Jamis Buck, *Mazes for Programmers* (Pragmatic Bookshelf, 2015) — the reference
  book on maze generation algorithms and their properties.
- Sedgewick & Wayne, *Algorithms* (4th ed.) — graph theory foundations (spanning
  trees, BFS).

### Useful links

- https://weblog.jamisbuck.org/2011/2/7/maze-generation-algorithm-recap
  — Jamis Buck's comprehensive comparison of maze algorithms with animations.
- https://en.wikipedia.org/wiki/Maze_generation_algorithm
  — Wikipedia overview of generation strategies.
- https://www.geeksforgeeks.org/dsa/breadth-first-search-or-bfs-for-a-graph/
  — GeeksForGeeks Breadth First Search or BFS for a Graph
- https://en.wikipedia.org/wiki/Breadth-first_search
  — Wikipedia overview of Breadth-first search
- https://en.wikipedia.org/wiki/Backtracking
  — Wikipedia overview of Backtracking
- https://docs.python.org/3/library/collections.html#collections.deque
  — Python deque used for BFS.
- https://flake8.pycqa.org/en/latest/ — flake8 linting reference.
- https://mypy.readthedocs.io/en/stable/ — mypy static typing reference.
- https://packaging.python.org/en/latest/tutorials/packaging-projects/
  — Official Python packaging guide (used to build the `mazegen` wheel).
- https://docs.python.org/3/library/curses.html
  — Python Curses documentation

### How AI was used

AI assistance was used in the following ways during this project:

- **README structure**: Helped draft and organise this README based on the project subject requirements.
- **MYPY strict:** AI helped us to solve the most strict cases that were raising MYPY errors.
- **Translation:** AI Helped us to translate some of the information to English
- **Explain complex concepts:** AI was used to summarize complex algorithm logic. 