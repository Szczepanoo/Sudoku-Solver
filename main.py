#!/usr/bin/env python3

import cv2
import numpy as np
import easyocr
import argparse
from typing import List, Optional, Tuple

Grid = List[List[int]]

# =========================
# ====== SOLVER ===========
# =========================

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


# =========================
# ====== OCR (EasyOCR) ====
# =========================

reader = easyocr.Reader(['en'], gpu=False)


def preprocess_cell(cell):
    gray = cv2.cvtColor(cell, cv2.COLOR_BGR2GRAY)

    # lepszy kontrast
    gray = cv2.equalizeHist(gray)

    # threshold
    _, th = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # usuń szum
    kernel = np.ones((3, 3), np.uint8)
    th = cv2.morphologyEx(th, cv2.MORPH_OPEN, kernel)

    return th


def extract_digit(cell):
    processed = preprocess_cell(cell)

    # puste pole
    if cv2.countNonZero(processed) < 50:
        return 0

    results = reader.readtext(processed, detail=0, paragraph=False)

    if not results:
        return 0

    text = results[0].strip()

    # filtr tylko cyfr
    if text.isdigit():
        val = int(text)
        if 1 <= val <= 9:
            return val

    return 0


# =========================
# ====== IMAGE ============
# =========================

def image_to_grid(path: str) -> Grid:
    img = cv2.imread(path)

    if img is None:
        raise ValueError("Nie można wczytać obrazu")

    h, w = img.shape[:2]
    cell_h = h // 9
    cell_w = w // 9

    grid = [[0 for _ in range(9)] for _ in range(9)]

    for r in range(9):
        for c in range(9):
            y1 = int(r * cell_h + cell_h * 0.1)
            y2 = int((r + 1) * cell_h - cell_h * 0.1)
            x1 = int(c * cell_w + cell_w * 0.1)
            x2 = int((c + 1) * cell_w - cell_w * 0.1)

            cell = img[y1:y2, x1:x2]

            digit = extract_digit(cell)
            grid[r][c] = digit

    return grid


# =========================
# ====== OUTPUT ===========
# =========================

def print_grid(grid):
    for row in grid:
        print(" ".join(str(x) for x in row))


def draw_solution(original_path, grid):
    img = cv2.imread(original_path)
    h, w = img.shape[:2]
    cell_h = h // 9
    cell_w = w // 9

    for r in range(9):
        for c in range(9):
            val = grid[r][c]
            if val != 0:
                x = int(c * cell_w + cell_w * 0.3)
                y = int(r * cell_h + cell_h * 0.7)

                cv2.putText(
                    img,
                    str(val),
                    (x, y),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 255, 0),
                    2,
                    cv2.LINE_AA,
                )

    cv2.imwrite("solution.png", img)


# =========================
# ====== MAIN =============
# =========================

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("image", help="ścieżka do obrazu sudoku")
    args = parser.parse_args()

    print("📸 OCR (EasyOCR)...")
    grid = image_to_grid(args.image)

    print("\n🧩 Wykryte sudoku:")
    print_grid(grid)

    print("\n🧠 Rozwiązywanie...")
    if solve_backtrack(grid):
        print("\n✅ Rozwiązanie:")
        print_grid(grid)

        draw_solution(args.image, grid)
        print("\n💾 Zapisano solution.png")
    else:
        print("❌ Nie znaleziono rozwiązania")


if __name__ == "__main__":
    main()