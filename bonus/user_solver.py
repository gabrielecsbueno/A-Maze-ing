import curses
from mazegen.maze_generator import Cell, Directions
from typing import List, Tuple, Any


def _maze_visualizer(
        stdscr: Any,
        grid: List[List[Cell]],
        entry: Tuple[int, int],
        exit_: Tuple[int, int],
        player: Tuple[int, int]
        ) -> None:
    """Renders the maze grid, player position, entry/exit points,
    and background patterns to the terminal screen using the
    curses library.

    This function sets up the required color pairs and iteratively
    draws the top walls, side walls, bottom walls, and specific cell
    states (like player or patterns) for each coordinate in the maze
    grid.

    Args:
        stdscr: The curses window object representing the screen.
        grid (List[List[Cell]]): A 2D list representing the maze layout,
        where each element is a `Cell` containing wall visibility flags.
        entry (tuple): The (x, y) coordinate representing the maze entrance.
        exit_ (tuple): The (x, y) coordinate representing the maze exit.
        player (tuple): The current (x, y) coordinate of the player.

    Returns:
        None
    """
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)  # walls
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)  # entry
    curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)  # exit
    curses.init_pair(4, curses.COLOR_GREEN, curses.COLOR_BLACK)  # player
    curses.init_pair(5, curses.COLOR_WHITE, curses.COLOR_BLACK)  # pattern

    height = len(grid)
    width = len(grid[0])

    ch_asc = '\u2588'
    ch_asc_visual = curses.color_pair(1)
    pattern_visual = curses.color_pair(5)

    stdscr.addstr(0, 0, ch_asc, ch_asc_visual)
    for x in range(width):
        cell = grid[0][x]
        wall = ch_asc * 2 if cell.walls & Directions.NORTH.value else ' ' * 2
        stdscr.addstr(0, 1 + x * 3, wall, ch_asc_visual)
        stdscr.addstr(0, 3 + x * 3, ch_asc, ch_asc_visual)

    for y in range(height):
        screen_row = 1 + y * 2

        stdscr.addstr(screen_row, 0, ch_asc, ch_asc_visual)
        for x in range(width):
            cell = grid[y][x]
            col = 1 + x * 3
            if (x, y) == player:
                stdscr.addstr(screen_row, col, ch_asc * 2,
                              curses.color_pair(4))
            elif cell.is_pattern:
                stdscr.addstr(screen_row, col, ch_asc * 2, pattern_visual)
            elif (x, y) == entry:
                stdscr.addstr(screen_row, col, ' ' * 2,
                              curses.color_pair(2) | curses.A_REVERSE)
            elif (x, y) == exit_:
                stdscr.addstr(screen_row, col, ' ' * 2,
                              curses.color_pair(3) | curses.A_REVERSE)
            else:
                stdscr.addstr(screen_row, col, ' ' * 2)
            east = ch_asc if cell.walls & Directions.EAST.value else ' '
            stdscr.addstr(screen_row, col + 2, east, ch_asc_visual)

        bottom_row = 2 + y * 2
        stdscr.addstr(bottom_row, 0, ch_asc, ch_asc_visual)
        for x in range(width):
            cell = grid[y][x]
            col = 1 + x * 3
            w = ch_asc * 2 if cell.walls & Directions.SOUTH.value else ' ' * 2
            stdscr.addstr(bottom_row, col, w, ch_asc_visual)
            stdscr.addstr(bottom_row, col + 2, ch_asc, ch_asc_visual)

        msg_row = 3 + y * 2
        msg = "Pres 'Q' to exit!"
        stdscr.addstr(msg_row, 0, msg)


def user_solver(
        stdscr: Any,
        grid: List[List[Cell]],
        entry: Tuple[int, int],
        exit_: Tuple[int, int]
        ) -> None:
    """Runs the interactive game loop allowing a user to manually navigate
    and solve the maze using the arrow keys.

    This function handles player movement based on keyboard input, checks
    for wall collisions using the cell's wall flags, and continuously
    refreshes the screen by calling `_maze_visualizer`. The loop terminates
    when the player reaches the exit or presses the 'q' key.

    This function valid if the window is small for the labyrinth. The rows
    and columns must be smaller than the maximum value of the window
    (getmaxyx() return of the height and width of the window).

    Args:
        stdscr: The curses window object representing the screen.
        grid (List[List[Cell]]): A 2D list representing the maze layout,
        where each element is a `Cell` containing wall visibility flags.
        entry (tuple): The starting (x, y) coordinate where the player spawns.
        exit_ (tuple): The target (x, y) coordinate the player must reach to
        win.

    Returns:
        None
    """

    height = len(grid)
    width = len(grid[0])
    validate_rows = 1 + height * 2 + 2
    validate_cols = 1 + width * 3 + 1

    max_rows, max_cols = stdscr.getmaxyx()
    if max_rows < validate_rows or max_cols < validate_cols:
        raise ValueError(
            f"Terminal too small for this maze - "
            f"Current: {max_cols}x{max_rows}"
        )

    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)  # text
    texto_verde = curses.color_pair(1)

    curses.curs_set(0)

    player = entry

    key_map = {
        curses.KEY_UP: (Directions.NORTH,  0, -1),
        curses.KEY_DOWN: (Directions.SOUTH,  0,  1),
        curses.KEY_RIGHT: (Directions.EAST,   1,  0),
        curses.KEY_LEFT: (Directions.WEST,  -1,  0),
    }

    while True:
        stdscr.clear()
        _maze_visualizer(stdscr, grid, entry, exit_, player)

        if player == exit_:
            msg = 'You have reached the exit!'
            stdscr.addstr(height, width, msg, texto_verde)
            stdscr.refresh()
            stdscr.getch()
            break

        stdscr.refresh()
        key = stdscr.getch()

        if key == ord('q'):
            break

        if key in key_map:
            direction, dx, dy = key_map[key]
            px, py = player
            if not (grid[py][px].walls & direction.value):
                player = (px + dx, py + dy)
