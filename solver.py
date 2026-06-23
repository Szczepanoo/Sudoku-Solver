from typing import List, Optional, Tuple

Grid = List[List[int]]


def find_empty(grid: Grid) -> Optional[Tuple[int, int]]:
    for r in range(9):
        for c in range(9):
            if grid[r][c] == 0:
                return r, c
    return None


def is_valid(grid: Grid, row: int, col: int, val: int) -> bool:
    if any(grid[row][c] == val for c in range(9)):
        return False
    if any(grid[r][col] == val for r in range(9)):
        return False

    br, bc = (row // 3) * 3, (col // 3) * 3
    for r in range(br, br + 3):
        for c in range(bc, bc + 3):
            if grid[r][c] == val:
                return False
    return True


def solve_backtrack(grid: Grid) -> bool:
    empty = find_empty(grid)
    if not empty:
        return True

    r, c = empty
    for val in range(1, 10):
        if is_valid(grid, r, c, val):
            grid[r][c] = val
            if solve_backtrack(grid):
                return True
            grid[r][c] = 0
    return False


def is_valid_input(grid: Grid) -> bool:
    for row in range(9):
        for col in range(9):

            value = grid[row][col]

            if value == 0:
                continue

            grid[row][col] = 0

            if not is_valid(grid, row, col, value):
                grid[row][col] = value
                return False

            grid[row][col] = value

    return True