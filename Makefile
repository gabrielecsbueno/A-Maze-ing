.PHONY: install run debug clean lint lint-strict build

py := python3

install:
	pip install poetry flake8 mypy

run:
	$(py) a_maze_ing.py config.txt

debug:
	$(py) -m pdb a_maze_ing.py config.txt

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +

build:
	poetry build && mv dist/* . && rmdir dist

lint:
	-flake8 .
	mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	-flake8 .
	mypy . --strict