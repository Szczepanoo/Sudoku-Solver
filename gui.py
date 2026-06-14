#!/usr/bin/env python3

import sys
import cv2
import ctypes

from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QGridLayout
)

from PyQt5.QtGui import QPixmap, QImage, QFont, QIcon
from PyQt5.QtCore import Qt

from image_processing import image_to_grid
from solver import solve_backtrack


def cv_to_qt(img):
    """Konwersja OpenCV (BGR) -> QPixmap"""
    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    h, w, ch = rgb.shape
    bytes_per_line = ch * w
    qt_img = QImage(rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
    return QPixmap.fromImage(qt_img)


class SudokuApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Sudoku Solver")
        self.setWindowIcon(QIcon("icon.ico"))
        self.resize(900, 700)

        self.image = None

        # =========================
        # UI
        # =========================

        title = QLabel("🧩 Sudoku Solver")
        title.setAlignment(Qt.AlignCenter)

        title_font = QFont()
        title_font.setPointSize(22)
        title_font.setBold(True)
        title.setFont(title_font)

        self.image_label = QLabel(
            "📋 Wklej zdjęcie sudoku\n\nCtrl + V"
        )
        self.image_label.setObjectName("ImageArea")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumHeight(320)

        self.solve_btn = QPushButton("Rozwiąż Sudoku")
        self.solve_btn.setCursor(Qt.PointingHandCursor)
        self.solve_btn.clicked.connect(self.solve)

        # Plansza sudoku
        self.grid_labels = []
        self.sudoku_grid = QGridLayout()
        self.sudoku_grid.setSpacing(0)

        for r in range(9):
            row = []

            for c in range(9):
                cell = QLabel("")
                cell.setAlignment(Qt.AlignCenter)
                cell.setFixedSize(55, 55)

                top = 3 if r % 3 == 0 else 1
                left = 3 if c % 3 == 0 else 1
                bottom = 3 if r == 8 else 1
                right = 3 if c == 8 else 1

                cell.setStyleSheet(f"""
                    background-color: #252526;
                    border-top: {top}px solid #888;
                    border-left: {left}px solid #888;
                    border-right: {right}px solid #888;
                    border-bottom: {bottom}px solid #888;
                    color: white;
                    font-size: 22px;
                    font-weight: bold;
                """)

                row.append(cell)
                self.sudoku_grid.addWidget(cell, r, c)

            self.grid_labels.append(row)

        # =========================
        # Layout
        # =========================

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.solve_btn)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        main_layout.addWidget(title)
        main_layout.addWidget(self.image_label)
        main_layout.addLayout(btn_layout)
        
        board_widget = QWidget()
        board_widget.setLayout(self.sudoku_grid)

        main_layout.addWidget(board_widget, alignment=Qt.AlignCenter)

        self.setLayout(main_layout)

        # =========================
        # Style
        # =========================

        self.setStyleSheet("""
        QWidget {
            background-color: #1e1e1e;
            color: #f0f0f0;
            font-size: 14px;
        }

        QLabel {
            color: #f0f0f0;
        }

        QLabel#ImageArea {
            background-color: #252526;
            border: 2px dashed #4b5563;
            border-radius: 15px;
            font-size: 18px;
            padding: 20px;
        }

        QPushButton {
            background-color: #2563eb;
            color: white;
            border: none;
            border-radius: 10px;
            padding: 12px;
            font-size: 15px;
            font-weight: bold;
            min-height: 24px;
        }

        QPushButton:hover {
            background-color: #3b82f6;
        }

        QPushButton:pressed {
            background-color: #1d4ed8;
        }

        QTextEdit {
            background-color: #252526;
            border: 1px solid #3c3c3c;
            border-radius: 10px;
            padding: 10px;
        }
        """)

    # =========================
    # Clipboard handling
    # =========================

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_V and (event.modifiers() & Qt.ControlModifier):
            self.paste_image()

    def paste_image(self):
        clipboard = QApplication.clipboard()

        if clipboard.mimeData().hasImage():
            self.qt_image = clipboard.image()

            if self.qt_image.isNull():
                return

            self.qt_image.save("temp_input.png")

            self.image = cv2.imread("temp_input.png")

            self.display_image()

            self.clear_board()

    # =========================
    # Display
    # =========================

    def display_image(self):
        if self.image is None:
            return

        pixmap = cv_to_qt(self.image)

        self.image_label.setPixmap(
            pixmap.scaled(
                self.image_label.width(),
                self.image_label.height(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
        )

    # =========================
    # Solve
    # =========================

    def solve(self):

        grid = image_to_grid("temp_input.png")

        original_grid = [row[:] for row in grid]

        if solve_backtrack(grid):

            for r in range(9):
                for c in range(9):

                    value = str(grid[r][c])

                    if original_grid[r][c] != 0:
                        color = "#22c55e"   # zielony OCR
                    else:
                        color = "#60a5fa"   # niebieski solver

                    top = 3 if r % 3 == 0 else 1
                    left = 3 if c % 3 == 0 else 1
                    bottom = 3 if r == 8 else 1
                    right = 3 if c == 8 else 1

                    self.grid_labels[r][c].setText(value)

                    self.grid_labels[r][c].setStyleSheet(f"""
                        background-color: #252526;
                        border-top: {top}px solid #888;
                        border-left: {left}px solid #888;
                        border-right: {right}px solid #888;
                        border-bottom: {bottom}px solid #888;
                        color: {color};
                        font-size: 22px;
                        font-weight: bold;
                    """)

        else:
            self.clear_board()
    # =========================
    # Resize handling
    # =========================

    def resizeEvent(self, event):
        super().resizeEvent(event)

        if self.image is not None:
            self.display_image()

    # =========================
    # Clear board
    # =========================

    def clear_board(self):
        for row in self.grid_labels:
            for cell in row:
                cell.setText("")


# =========================
# MAIN
# =========================

def main():
    app = QApplication(sys.argv)

    window = SudokuApp()
    window.show()

    hwnd = int(window.winId())

    value = ctypes.c_int(1)

    ctypes.windll.dwmapi.DwmSetWindowAttribute(
        hwnd,
        20,
        ctypes.byref(value),
        ctypes.sizeof(value)
    )

    sys.exit(app.exec_())

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()