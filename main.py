#!/usr/bin/env python3

import argparse
from image_processing import image_to_grid
from solver import solve_backtrack
from output import print_grid, draw_solution


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("image", help="ścieżka do obrazu sudoku")
    parser.add_argument("--debug", action="store_true", help="tryb debug (podgląd komórek)")
    args = parser.parse_args()

    print("📸 Wczytywanie zdjęcia...")
    grid = image_to_grid(args.image, debug=args.debug)

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