from typing import List
from classify import extract_digit, preprocess_cell
from debug import debug_cells, debug_ocr_cell
import numpy as np

Grid = List[List[int]]


def image_to_grid(img: np.ndarray, debug=False) -> Grid:

    if img is None:
        raise ValueError("Nie można wczytać obrazu")

    h, w = img.shape[:2]
    cell_h = h // 9
    cell_w = w // 9

    grid = [[0 for _ in range(9)] for _ in range(9)]

    raw_cells = []
    processed_cells = []

    for r in range(9):
        for c in range(9):
            y1 = int(r * cell_h + cell_h * 0.1)
            y2 = int((r + 1) * cell_h - cell_h * 0.1)
            x1 = int(c * cell_w + cell_w * 0.1)
            x2 = int((c + 1) * cell_w - cell_w * 0.1)

            cell = img[y1:y2, x1:x2]
            raw_cells.append(cell)

            processed = preprocess_cell(cell)
            processed_cells.append(processed)

            processed = preprocess_cell(cell)

            digit = extract_digit(cell)

            if debug:
                debug_ocr_cell(
                    cell,
                    processed,
                    digit,
                    r,
                    c,
                    save_dir="debug_cells"
                )

            grid[r][c] = digit

    if debug:
        debug_cells(raw_cells, processed_cells)

    return grid