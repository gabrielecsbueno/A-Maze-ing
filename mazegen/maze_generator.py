import random
import sys
from enum import Enum
from typing import List, Optional, Tuple, Deque, Dict
from collections import deque


class Directions(Enum):
    """
    Value of each wall in bits
    """
    NORTH = 1
    EAST = 2
    WEST = 4
    SOUTH = 8


class Opposites(Enum):
    """
    The opposite wall to delete from the new cell to visit
    """
    NORTH = Directions.SOUTH
    EAST = Directions.WEST
    WEST = Directions.EAST
    SOUTH = Directions.NORTH


class Cell:
    """
    Class that describes each cell of the grid.
    Walls: bit value for each wall NSEW value can be between 1-15.
    It defaults to 15 at the beginning (closed square)
    visited: this is for the backtrack algorithm, the algorithm will avoid
             already visited cells
    is_exit: this is for the future path finding function to mark cells that
             are part of the solution
    """
    def __init__(
        self,
        walls: int = 15,
        visited: bool = False,
        exit_path: bool = False,
        is_pattern: bool = False
    ) -> None:
        """
        Args:
            walls (int): Bitmask encoding which walls are closed (1) or open
                (0). Bits: 0=North, 1=East, 2=West, 3=South. Defaults to 15
                (all walls closed).
            visited (bool): True once the backtracking DFS has visited this
                cell. Defaults to False.
            exit_path (bool): True when this cell lies on the BFS solution
                path. Defaults to False.
            is_pattern (bool): True when this cell is part of the '42'
                pattern and must remain fully closed. Defaults to False.
        """
        self.walls = walls
        self.visited = visited
        self.exit_path = exit_path
        self.is_pattern = is_pattern


class MazeGenerator:
    """
    This is the heart of the program, it receives the parameters
    from the config.txt file and with those files it creates a Maze object.

    Parameters:
                width: int value mandatory to create a maze.
                height: int value mandatory to create a maze.
                entry: coordinates that determine where the
                       entry point of the maze is.
                exit: the point where the maze exits.
                output: this is the name of the file created with the maze
                        to print.
                perfect: this determines wether we will use a perfect or
                         non perfect maze.
                seed: optional value that becomes the seed for all the
                      random generation used.
    """
    def __init__(
        self,
        width: int,
        height: int,
        entry: Tuple[int, int],
        exit: Tuple[int, int],
        output: str,
        perfect: bool = True,
        seed: Optional[str] = None
    ) -> None:
        self.width = width
        self.height = height
        self.entry = entry
        self.exit = exit
        self.output = output
        self.perfect = perfect
        self.seed = seed
        self.rng = random.Random(seed)
        self.grid: List[List[Cell]] = []
        self.sparsity = 0.5
        self._validate()
        self.moves = [
            (Directions.NORTH, 0, -1),
            (Directions.SOUTH, 0, 1),
            (Directions.EAST, 1, 0),
            (Directions.WEST, -1, 0)
        ]

    def _validate(self) -> None:
        """
        Validates the parameters received in __init__ before
        the other methods.
        Raises a ValueError if any parameter violates project rules.
        """
        if self.width < 3 or self.height < 3:
            raise ValueError(
                f"Invalid size: width={self.width},"
                f"height={self.height} Both width and hegith must be >= 3"
            )

        entry_x, entry_y = self.entry

        if not (0 <= entry_x < self.width and 0 <= entry_y < self.height):
            raise ValueError(
                f"Entry {self.entry} outside maze limits"
                f" ({self.width}x{self.height})"
            )

        exit_x, exit_y = self.exit

        if not (0 <= exit_x < self.width and 0 <= exit_y < self.height):
            raise ValueError(
                f"Exit {self.exit} outside maze limits"
                f" ({self.width}x{self.height})"
            )

        if self.entry == self.exit:
            raise ValueError(
                f"Entry and exit cannot be the same: {self.entry}."
            )

    def _move_point(self, point: Tuple[int, int]) -> Tuple[int, int]:
        '''
        Moves the entry or exit coordinate received in the param 'point'
        to a neighboring coordinate, it will not move it to a coordinate
        that is a part of the 42 pattern.
        Returns a new coordinate.
        '''
        x, y = point
        candidates = []
        for _, dir_x, dir_y in self.moves:
            nx = x + dir_x
            ny = y + dir_y

            if 0 <= nx < self.width and 0 <= ny < self.height:
                if not self.grid[ny][nx].is_pattern:
                    candidates.append((nx, ny))
        if not candidates:
            raise ValueError("Error: It was not possible to move this point")

        return self.rng.choice(candidates)

    def _init_grid(self) -> List[List[Cell]]:
        """
        This method initiates a grid that contains cells with all closed walls
        """
        self.grid = []
        for _ in range(self.height):
            row = []
            for _ in range(self.width):
                row.append(Cell())
            self.grid.append(row)
        return self.grid

    def _make_imperfect(self, sparsity: float) -> None:
        """
        Creates loops in the perfect maze by selectively eliminating dead ends.
        After the backtracking algorithm generates a perfect maze (a spanning
        tree with no loops), this function traverses all cells to find dead
        ends—cells with exactly three closed walls—and removes one of the walls
        based on the probability defined in 'sparsity'. This connects the dead
        end to a new neighboring cell, creating a loop without forming large
        3x3 open spaces.
        Parameters:
                    sparsity (float): Probability (0.0 to 1.0) of opening each
                    dead end.
                    0.0 = no dead ends opened (maze remains perfect).
                    1.0 = all dead ends are opened.
                    0.5 is the recommended default value.
        """

        dead_ends = {7, 11, 13, 14}

        moves_dict = {d: (dx, dy) for d, dx, dy in self.moves}

        for y in range(self.height):
            for x in range(self.width):
                cell = self.grid[y][x]

                if cell.walls not in dead_ends:
                    continue

                if cell.is_pattern:
                    continue

                if self.rng.random() >= sparsity:
                    continue

                candidates = []
                for direction, dir_x, dir_y in self.moves:
                    if cell.walls & direction.value:
                        nx = x + dir_x
                        ny = y + dir_y
                        if 0 <= nx < self.width and 0 <= ny < self.height:
                            if not self.grid[ny][nx].is_pattern:
                                candidates.append(direction)

                if not candidates:
                    continue

                chosen = self.rng.choice(candidates)

                nx = x + moves_dict[chosen][0]
                ny = y + moves_dict[chosen][1]

                cell.walls &= ~chosen.value

                self.grid[ny][nx].walls &= ~Opposites[chosen.name].value.value

    def _apply_pattern42(self) -> None:
        """
        Defines the blocked cells to draw the '42' pattern on the grid.
        """
        pattern_42 = [
            [1, 0, 0, 0, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 1],
            [1, 1, 1, 0, 1, 1, 1],
            [0, 0, 1, 0, 1, 0, 0],
            [0, 0, 1, 0, 1, 1, 1]
            ]
        pattern_width = len(pattern_42[0])
        pattern_height = len(pattern_42)

        if self.height <= pattern_height + 1 or self.width <= pattern_width+1:
            print("Error: Maze too small for pattern '42'", file=sys.stderr)
            return

        start_x = (self.width - pattern_width) // 2
        start_y = (self.height - pattern_height) // 2

        for py in range(pattern_height):
            for px in range(pattern_width):
                if pattern_42[py][px] != 1:
                    continue

                grid_x = start_x + px
                grid_y = start_y + py
                cell = self.grid[grid_y][grid_x]
                cell.walls = 15
                cell.visited = True
                cell.is_pattern = True

    def _path_finding(self) -> str:
        """
        Find the shortest path from the maze entry to the exit using BFS.

        Traverses the maze grid using a breadth-first search, respecting wall
        boundaries between cells. Once the exit is found, reconstructs the path
        by backtracking through visited nodes and marks each cell along the
        route by setting its `exit_path` attribute to True.

        Modifies the maze in-place: sets `exit_path = True` on each cell
        that lies along the solution path, including the entry and exit cells.
        Wall connectivity is checked via each cell's `walls` bitmask against
        the corresponding `Directions` flag.
        Assumes `self.entry` and `self.exit` are valid (col, row) coordinates
        within the grid bounds.

        Returns:
            str: A string of cardinal direction characters ('N', 'E', 'W', 'S')
                representing the shortest path from entry to exit.
                Example: "NEESSWN"

        Raises:
            ValueError: If no path exists between the maze entry and exit.
        """
        rows = len(self.grid)
        cols = len(self.grid[0])
        visited: Dict[
            Tuple[int, int],
            Optional[Tuple[int, int, Directions]]
            ] = {self.entry: None}
        queue: Deque[Tuple[int, int]] = deque()
        queue.append(self.entry)

        while queue:
            x, y = queue.popleft()

            if (x, y) == self.exit:
                break

            current_row = self.grid[y][x]

            for move, dir_x, dir_y in self.moves:
                if current_row.walls & move.value:
                    continue
                nx, ny = x + dir_x, y + dir_y

                if not (0 <= ny < rows and 0 <= nx < cols):
                    continue

                if (nx, ny) not in visited:
                    visited[(nx, ny)] = (x, y, move)
                    queue.append((nx, ny))

        if self.exit not in visited:
            raise ValueError("Couldn't find exit path")

        path = []
        pos = self.exit
        while True:
            parent_info = visited[pos]
            if parent_info is None:
                break

            x_prev, y_prev, move = parent_info
            self.grid[pos[1]][pos[0]].exit_path = True
            if move == Directions.NORTH:
                path.append('N')
            elif move == Directions.EAST:
                path.append('E')
            elif move == Directions.WEST:
                path.append('W')
            elif move == Directions.SOUTH:
                path.append('S')
            pos = (x_prev, y_prev)

        self.grid[self.entry[1]][self.entry[0]].exit_path = True

        path.reverse()
        return "".join(path)

    def _create_output(self) -> None:
        """
        Translates the maze to a readable text file at `self.output`.

        Each row is a sequence of uppercase hex characters, one per cell,
        encoding that cell's wall configuration as a bitmask.
        Builds a plain-text representation of the maze and writes it to disk.
        Entry and exit coordinates are zero-indexed (col, row) pairs.
        The solution path is the string returned by `_path_finding()`,
        e.g. "NNEESSWW".
        The output format is structured as follows:

            <wall_bitmask_row_0>
            <wall_bitmask_row_1>
            ...
            <wall_bitmask_row_n>

            <entry_x>,<entry_y>
            <exit_x>,<exit_y>
            <solution_path>

        Side effects:
            - Calls `_path_finding()`, which marks cells along the solution
            route by setting their `exit_path` attribute to True.
            - Calls `clear_path()` immediately after to reset those flags
            before writing, ensuring the grid is left in a clean state.
            - Writes to the file at `self.output`, creating or overwriting it.

        Raises:
            Errors are caught internally and reported to stderr rather than
            propagated to the caller:
            - FileNotFoundError: If any parent directory in `self.output`
                                does not exist.
            - PermissionError: If the process lacks write access to
                                `self.output`.
            - OSError: For any other OS-level failure during the file write.
        """
        res: str = f"{self.get_grid()}"
        entry_x, entry_y = self.entry
        exit_x, exit_y = self.exit
        res += f"\n{entry_x},{entry_y}\n{exit_x},{exit_y}\n"
        exit_path = f"{self._path_finding()}"
        res += exit_path
        try:
            with open(self.output, "w") as file:
                file.write(f"{res}")
        except FileNotFoundError:
            print(f"Error: The directory layout for \
                  '{self.output}' does not exist.", file=sys.stderr)
        except PermissionError:
            print(f"Error: Permission denied when \
                  writing to '{self.output}'.", file=sys.stderr)
        except OSError as e:
            print(f"A system error occurred while\
                   saving the file: {e}", file=sys.stderr)

    def generate(self) -> None:
        """
        Method for the complete generation of the maze.

        This is the public entry point of the class. It calls the steps
        in the correct order: initializes the grid, marks the "42" pattern
        (in the future), runs the DFS to generate the perfect maze, and,
        if 'self.perfect' is False, opens dead ends to create loops.

        The external caller (a_maze_ing.py) only needs to instantiate
        MazeGenerator and call this method—there is no need to know
        the internal steps.
        """
        self._init_grid()

        self._apply_pattern42()

        entry_x, entry_y = self.entry
        exit_x, exit_y = self.exit
        if self.grid[entry_y][entry_x].is_pattern:
            print("Error: The input coordinate matches the pattern 42, moving"
                  "to a closer point", file=sys.stderr)
            self.entry = self._move_point(self.entry)
            print(f"Point moved to {self.entry}", file=sys.stderr)
        if self.grid[exit_y][exit_x].is_pattern:
            print("Error: The exit coordinate matches the pattern 42, moving"
                  "to a closer point", file=sys.stderr)
            self.exit = self._move_point(self.exit)
            print(f"Point moved to {self.exit}", file=sys.stderr)

        entry_x, entry_y = self.entry
        backtracking(self.grid, entry_x, entry_y, self.rng)

        if not self.perfect:
            self._make_imperfect(self.sparsity)

        self._create_output()

    def get_grid(self) -> str:
        """
        An useful method that returns the cell grid in hex value
        """
        grid_str: str = ""
        y_axis = len(self.grid)
        x_axis = len(self.grid[0])
        for y in range(y_axis):
            for x in range(x_axis):
                grid_str += f"{(self.grid[y][x].walls):X}"
            grid_str += "\n"
        return grid_str


def backtracking(
    grid: List[List[Cell]],
    start_x: int,
    start_y: int,
    seed: random.Random,
) -> None:
    """
    This function will visit the entry point first and then randomly
    (using a shuffle) will select the next (within boundaries)
    cell to visit using the list of tuples with moves and values
    to move in the x, y grid it will then delete the wall of the current cell
    and the opposite wall
    of the next cell to visit. This function uses recursion to visit
    the next cell and so on. At the end it generates a perfect maze.
    grid: The previously generated grid used by MazeGenerator init_grid method
    cur_x: current position in the x axis (int value)
    cur_y: current position in the y axis (int value)
    seed: a seed value for the random maze generation (Random object)
    """
    moves = [
        (Directions.NORTH, 0, -1),
        (Directions.SOUTH, 0, 1),
        (Directions.EAST, 1, 0),
        (Directions.WEST, -1, 0)
    ]
    stack = [(start_x, start_y)]
    grid[start_y][start_x].visited = True
    seed.shuffle(moves)
    while stack:
        cur_x, cur_y = stack[-1]
        unvisited_neighbors = []
        for move, dir_x, dir_y in moves:
            new_x, new_y = cur_x + dir_x, cur_y + dir_y
            if 0 <= new_x < len(grid[0]) and 0 <= new_y < len(grid):
                if not grid[new_y][new_x].visited:
                    unvisited_neighbors.append((move, new_x, new_y))

        if unvisited_neighbors:
            move, next_x, next_y = seed.choice(unvisited_neighbors)
            grid[cur_y][cur_x].walls &= ~move.value
            grid[next_y][next_x].walls &= ~Opposites[move.name].value.value
            grid[next_y][next_x].visited = True
            stack.append((next_x, next_y))

        else:
            stack.pop()
