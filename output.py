import cv2


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