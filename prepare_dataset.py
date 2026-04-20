#!/usr/bin/env python3

import os
import cv2
import argparse


def preprocess_cell(cell):
    gray = cv2.cvtColor(cell, cv2.COLOR_BGR2GRAY)
    gray = cv2.equalizeHist(gray)

    _, th = cv2.threshold(
        gray, 0, 255,
        cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
    )

    return th


def split_into_cells(img, margin=0.1):
    h, w = img.shape[:2]
    cell_h = h // 9
    cell_w = w // 9

    cells = []

    for r in range(9):
        for c in range(9):
            y1 = int(r * cell_h + cell_h * margin)
            y2 = int((r + 1) * cell_h - cell_h * margin)
            x1 = int(c * cell_w + cell_w * margin)
            x2 = int((c + 1) * cell_w - cell_w * margin)

            cell = img[y1:y2, x1:x2]
            cells.append((r, c, cell))

    return cells


def process_image(image_path, output_dir, preprocess=False):
    img = cv2.imread(image_path)

    if img is None:
        print(f"❌ Nie można wczytać: {image_path}")
        return

    filename = os.path.splitext(os.path.basename(image_path))[0]

    cells = split_into_cells(img)

    for r, c, cell in cells:
        if preprocess:
            cell = preprocess_cell(cell)

        # resize dla spójności datasetu
        cell = cv2.resize(cell, (28, 28))

        out_name = f"{filename}_r{r}_c{c}.png"
        out_path = os.path.join(output_dir, out_name)

        cv2.imwrite(out_path, cell)


def main():
    parser = argparse.ArgumentParser(description="Prepare dataset from sudoku images")
    parser.add_argument("input_dir", help="folder z obrazami sudoku")
    parser.add_argument("output_dir", help="folder wyjściowy")
    parser.add_argument("--preprocess", action="store_true", help="zastosuj preprocessing")
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    images = [
        f for f in os.listdir(args.input_dir)
        if f.lower().endswith((".png", ".jpg", ".jpeg"))
    ]

    print(f"📂 Znaleziono {len(images)} obrazów")

    for img_name in images:
        path = os.path.join(args.input_dir, img_name)
        print(f"➡️ Przetwarzam: {img_name}")
        process_image(path, args.output_dir, preprocess=args.preprocess)

    print("✅ Dataset gotowy")


if __name__ == "__main__":
    main()