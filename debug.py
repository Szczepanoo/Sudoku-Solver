import cv2
import numpy as np


def _to_color(img):
    """Zapewnia 3 kanały (BGR)"""
    if len(img.shape) == 2:
        return cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    return img


def show_cells_grid(cells, title="Cells", with_indices=True):
    """
    Wyświetla 81 komórek jako jeden obraz 9x9
    """
    rows = []

    for r in range(9):
        row_imgs = []
        for c in range(9):
            img = cells[r * 9 + c]
            img = _to_color(img)

            img = cv2.resize(img, (64, 64))

            if with_indices:
                cv2.putText(
                    img,
                    f"{r},{c}",
                    (5, 15),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.4,
                    (0, 0, 255),
                    1,
                    cv2.LINE_AA,
                )

            row_imgs.append(img)

        row = np.hstack(row_imgs)
        rows.append(row)

    grid_img = np.vstack(rows)

    cv2.imshow(title, grid_img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def debug_cells(raw_cells, processed_cells):
    """
    Pokazuje RAW i PROCESSED komórki
    """
    show_cells_grid(raw_cells, title="RAW cells")
    show_cells_grid(processed_cells, title="Processed cells")