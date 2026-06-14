#!/usr/bin/env python3

import sys
import cv2
import numpy as np

from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QTextEdit
)
from PyQt5.QtGui import QPixmap, QImage
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

        self.setWindowTitle("Sudoku Solver (Ctrl+V)")
        self.resize(900, 600)

        self.image = None

        # UI
        self.image_label = QLabel("Wklej obraz (Ctrl+V)")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("border: 1px solid gray;")

        self.solve_btn = QPushButton("Solve")
        self.solve_btn.clicked.connect(self.solve)

        self.result_box = QTextEdit()
        self.result_box.setReadOnly(True)

        # layout
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.solve_btn)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.image_label)
        main_layout.addLayout(btn_layout)
        main_layout.addWidget(self.result_box)

        self.setLayout(main_layout)

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

    # =========================
    # Display
    # =========================

    def display_image(self):
        if self.image is None:
            return

        pixmap = cv_to_qt(self.image)
        self.image_label.setPixmap(pixmap.scaled(
            self.image_label.width(),
            self.image_label.height(),
            Qt.KeepAspectRatio
        ))

    # =========================
    # Solve
    # =========================

    def solve(self):

        print("START SOLVE")
        
        if self.image is None:
            self.result_box.setText("Brak obrazu")
            return

        print("SAVE")

        # zapis tymczasowy (bo masz pipeline plikowy)
        # cv2.imwrite("temp_input.png", self.image)

        print("IMAGE_TO_GRID")

        grid = image_to_grid("temp_input.png")

        print("GRID READY")
        print(grid)

        print("BACKTRACK START")

        if solve_backtrack(grid):
            text = "\n".join(" ".join(str(x) for x in row) for row in grid)
            self.result_box.setText(text)
        else:
            self.result_box.setText("Brak rozwiązania")

        print("BACKTRACK END")


# =========================
# MAIN
# =========================

def main():
    app = QApplication(sys.argv)
    window = SudokuApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()