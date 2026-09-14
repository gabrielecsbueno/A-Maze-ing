from mazegen.maze_generator import Cell, Directions
from typing import List
import time
import sys
import itertools


def maze_visualizer(grid: List[List[Cell]],
                    entry: tuple[int, int],
                    exit_: tuple[int, int],
                    color_index: int = 1,
                    show_path: bool = False
                    ) -> None:
    """
    Render the maze as an ASCII block art in the terminal using ANSI colours.

    Each cell is drawn as a 2-character-wide block. Walls are represented by
    filled block characters and open passages by spaces. The top border, cell
    interiors, and south walls are drawn row by row. Special cells (entry,
    exit, solution path, and pattern '42') are highlighted with distinct
    colours.

    Args:
        grid (List[List[Cell]]): 2-D grid of Cell objects produced by
            MazeGenerator.
        entry (tuple[int, int]): (col, row) coordinates of the maze entry.
        exit_ (tuple[int, int]): (col, row) coordinates of the maze exit.
        color_index (int): Index into the wall colour palette (1–6).
            Defaults to 1 (cyan).
        show_path (bool): When True, highlights cells whose `exit_path`
            attribute is True to display the solution path.
            Defaults to False.
    """
    color = [
        '\033[m',
        '\033[36m',
        '\033[35m',
        '\033[34m',
        '\033[33m',
        '\033[0;38;2;247;110;158;49m',
        '\033[0;38;2;255;234;0;49m'
    ]
    ch_asc = color[color_index] + '\u2588\033[m'
    ch_asc_pattern = '\u2588'
    ch_asc_entry = '\033[32m\u2588\033[m'
    ch_asc_exit = '\033[31m\u2588\033[m'
    ch_asc_path = '\033[0;38;2;159;95;95;49m\u2588\033[m'

    height = len(grid)
    width = len(grid[0])

    top = ch_asc
    for x in range(width):
        cell = grid[0][x]
        wall = ch_asc * 2 if (cell.walls & Directions.NORTH.value) else ' ' * 2
        top += wall + ch_asc
    output_maze = top + '\n'

    for y in range(height):
        row = ch_asc
        for x in range(width):
            cell = grid[y][x]
            if cell.is_pattern:
                paint = ch_asc_pattern * 2
            elif (x, y) == entry:
                paint = ch_asc_entry * 2
            elif (x, y) == exit_:
                paint = ch_asc_exit * 2
            elif cell.exit_path and show_path is True:
                paint = ch_asc_path * 2
            else:
                paint = ' ' * 2
            wall = ch_asc if cell.walls & Directions.EAST.value else ' '
            row += paint + wall
        output_maze += row + '\n'

        bottom = ch_asc
        for x in range(width):
            cell = grid[y][x]
            wall = (ch_asc * 2 if (cell.walls & Directions.SOUTH.value)
                    else ' ' * 2)
            bottom += wall + ch_asc
        output_maze += bottom + '\n'

    print(output_maze)


def elegant_spinner(duration: float = 5) -> None:
    """
    Display an animated spinner in the terminal for a given duration.

    Args:
        duration (float): How many seconds to run the spinner.
            Defaults to 5.
    """
    spinner = itertools.cycle(
        ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'])
    end_time = time.time() + duration

    CYAN = "\033[36m"
    RESET = "\033[0m"
    while time.time() < end_time:
        sys.stdout.write(f"\rLoading maze {CYAN}{next(spinner)}{RESET}")
        sys.stdout.flush()
        time.sleep(0.04)

    sys.stdout.write("\rLoading Complete!   \n")
