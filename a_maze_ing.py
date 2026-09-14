from utils import parse_config, maze_visualizer, elegant_spinner
from mazegen import MazeGenerator
from typing import Union
import sys
import subprocess
import curses
from bonus import user_solver


def start_maze(
        seed: Union[str, None] = "USE_CONFIG"
        ) -> Union[MazeGenerator, None]:
    """
    Entry point for initializing and running the maze generation process.

    Validates command-line arguments, parses the configuration file, and
    generates a maze based on the resulting settings. Expects exactly one
    command-line argument pointing to a file named 'config.txt'.

    Args:
        seed (Union[str, None], optional): Seed value for the maze's random
            generation, enabling reproducible outputs. When set to the default
            value "USE_CONFIG", the seed defined in 'config.txt' is used
            instead. Pass None or any string to override it explicitly.
            Defaults to "USE_CONFIG".

    Returns:
        MazeGenerator: A fully constructed and generated maze object if the
            process completes successfully.
        None: If any of the following occur:
            - The number of command-line arguments is not exactly one.
            - The provided argument is not named 'config.txt'.
            - Any exception is raised during config parsing or maze generation.

    Side Effects:
        - Displays a spinner animation before clearing the terminal.
        - Clears the terminal screen via a subprocess call.
        - Prints error messages to stderr on argument validation failure.
        - Prints error messages to stdout if an exception is caught.
    """
    if len(sys.argv[1:]) != 1:
        print("Error - 'config.txt' file is mandatory", file=sys.stderr)
        return None
    elif sys.argv[1] != 'config.txt':
        print("Error - The file must be named 'config.txt'",
              file=sys.stderr)
        return None
    try:
        elegant_spinner(0.3)
        subprocess.run("clear")
        config = parse_config(sys.argv[1])
        maze_perfect = MazeGenerator(
            width=config.width,
            height=config.height,
            entry=config.entry,
            exit=config.exit_,
            output=config.output_file,
            perfect=config.perfect,
            seed=config.seed if seed == "USE_CONFIG" else seed
        )
        maze_perfect.generate()
    except Exception as err:
        print('Error -', err)
        return None
    else:
        return maze_perfect


def main() -> None:
    """
    Main interactive loop for the A-Maze-ing maze generation application.

    Clears the terminal and initializes the maze via `start_maze()`, then
    enters an interactive menu loop that allows the user to visualize and
    manipulate the maze until they choose to exit.

    Menu Options:
        1. Generate New Maze:  Generates a new random maze (seed=None),
                               replacing the current one.
        2. Show/Hide Exit Path: Toggles the visibility of the solution
                                path overlay on the maze.
        3. Change Wall Color:  Cycles the wall color through 6 available
                               options (wraps back to 1 after 6).
        4. Exit:               Breaks the loop and terminates the program.

    Control Flow:
        - The loop continues as long as `maze` is a valid `MazeGenerator`
          object (i.e. truthy). If `start_maze()` returns None on init,
          the loop body is never entered.
        - On each iteration, the current maze is re-rendered before the
          menu is displayed.

    Error Handling:
        ValueError:       Triggered by a non-integer menu input. Prints an
                          error message and re-displays the menu.
        EOFError:         Triggered when stdin is closed unexpectedly.
                          Prints a message and exits the program.
        KeyboardInterrupt: Triggered by Ctrl+C. Prints a message and exits
                           the program.

    Side Effects:
        - Clears the terminal screen at startup and after every input.
        - Renders the maze to the terminal on each iteration via
          `maze_visualizer()`.
        - Calls `sys.exit(0)` on KeyboardInterrupt.

    Returns:
        None
    """
    subprocess.run("clear")
    maze = start_maze()
    color_maze = 1
    show_path = False

    while maze:
        if maze:
            maze_visualizer(
                maze.grid,
                maze.entry,
                maze.exit,
                color_maze,
                show_path)
        print("==== A-Maze-ing ====")
        print("1. Generate New Maze")
        print("2. Show/Hide Exit Path")
        print("3. Change Wall Color")
        print("4. To play")
        print("5. Exit")
        try:
            option = int(input("Enter your choice (1-5): "))
        except ValueError:
            subprocess.run("clear")
            print("Error: invalid value")
        except EOFError:
            subprocess.run("clear")
            print("User closed the program")
            break
        except KeyboardInterrupt:
            subprocess.run("clear")
            print("User closed the program")
            sys.exit(0)
        else:
            subprocess.run("clear")
            if option == 1:
                maze = start_maze(seed=None)
            elif option == 2:
                show_path = not show_path
            elif option == 3:
                color_maze += 1
                color_maze = 1 if color_maze > 6 else color_maze
            elif option == 4:
                try:
                    curses.wrapper(user_solver, maze.grid, maze.entry,
                                   maze.exit)
                except Exception as err:
                    print('Error -', err)
                    break
            elif option == 5:
                break
            else:
                print("Incorrect value\n")


if __name__ == "__main__":
    main()
