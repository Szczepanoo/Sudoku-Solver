import cv2
import numpy as np


def order_points(pts):
    pts = pts.reshape(4, 2).astype(np.float32)

    s = pts.sum(axis=1)
    diff = np.diff(pts, axis=1)

    return np.array([
        pts[np.argmin(s)],      # top-left
        pts[np.argmin(diff)],   # top-right
        pts[np.argmax(s)],      # bottom-right
        pts[np.argmax(diff)]    # bottom-left
    ], dtype=np.float32)


def warp_sudoku(image, quad):
    rect = order_points(quad)

    size = 900

    dst = np.array([
        [0, 0],
        [size - 1, 0],
        [size - 1, size - 1],
        [0, size - 1]
    ], dtype=np.float32)

    M = cv2.getPerspectiveTransform(rect, dst)

    return cv2.warpPerspective(image, M, (size, size))


def looks_like_sudoku(warped):
    gray = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)

    thresh = cv2.adaptiveThreshold(
        gray,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        11,
        2
    )

    lines = cv2.HoughLinesP(
        thresh,
        rho=1,
        theta=np.pi / 180,
        threshold=150,
        minLineLength=500,
        maxLineGap=20
    )

    if lines is None:
        return False

    vertical = 0
    horizontal = 0

    for line in lines:
        x1, y1, x2, y2 = line[0]

        dx = abs(x2 - x1)
        dy = abs(y2 - y1)

        if dx < 15 and dy > 300:
            vertical += 1

        elif dy < 15 and dx > 300:
            horizontal += 1

    return vertical >= 8 and horizontal >= 8


def detect_sudoku(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    blur = cv2.GaussianBlur(gray, (7, 7), 0)

    thresh = cv2.adaptiveThreshold(
        blur,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        11,
        2
    )

    contours, _ = cv2.findContours(
        thresh,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    candidates = []

    for cnt in contours:
        area = cv2.contourArea(cnt)

        if area < 10000:
            continue

        perimeter = cv2.arcLength(cnt, True)

        approx = cv2.approxPolyDP(
            cnt,
            0.02 * perimeter,
            True
        )

        if len(approx) == 4:
            candidates.append((area, approx))

    candidates.sort(reverse=True, key=lambda x: x[0])

    for _, quad in candidates:
        warped = warp_sudoku(image, quad)

        if looks_like_sudoku(warped):
            return warped

    return None