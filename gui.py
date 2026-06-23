import sys
import cv2
import ctypes
import random
import os

from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation

from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QGridLayout, QLineEdit,
    QGraphicsOpacityEffect)

from PyQt5.QtGui import (QPixmap, QImage, QFont, 
    QIcon, QIntValidator)

from image_processing import image_to_grid
from solver import solve_backtrack, is_valid_input
from utils import resource_path

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
        self.setWindowIcon(QIcon(resource_path("icon.ico")))
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
            "📋 Paste picture of sudoku\n\nCtrl + V"
        )
        self.image_label.setObjectName("ImageArea")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumHeight(320)

        self.load_btn = QPushButton("Load")
        self.load_btn.setCursor(Qt.PointingHandCursor)
        self.load_btn.clicked.connect(self.load_sudoku)

        self.solve_btn = QPushButton("Solve")
        self.solve_btn.setCursor(Qt.PointingHandCursor)
        self.solve_btn.clicked.connect(self.solve)

        self.generate_btn = QPushButton("Generate")
        self.generate_btn.setCursor(Qt.PointingHandCursor)
        self.generate_btn.clicked.connect(self.generate_sudoku)

        self.clear_btn = QPushButton("Clear")
        self.clear_btn.setObjectName("ClearButton")
        self.clear_btn.setCursor(Qt.PointingHandCursor)
        self.clear_btn.clicked.connect(self.clear_board_by_click)

        # Plansza sudoku
        self.grid_labels = []
        self.sudoku_grid = QGridLayout()
        self.sudoku_grid.setSpacing(0)

        for r in range(9):
            row = []

            for c in range(9):
                cell = QLineEdit()
                cell.setAlignment(Qt.AlignCenter)
                cell.setFixedSize(55, 55)

                cell.setMaxLength(1)
                cell.setValidator(QIntValidator(1, 9))

                cell.textEdited.connect(
                    lambda _, c=cell: c.setStyleSheet(
                        c.styleSheet() + "color: white;"
                    )
                )

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
        btn_layout.setSpacing(10)

        btn_layout.addWidget(self.load_btn)
        btn_layout.addWidget(self.solve_btn)
        btn_layout.addWidget(self.generate_btn)
        btn_layout.addWidget(self.clear_btn)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        main_layout.addWidget(title)
        main_layout.addWidget(self.image_label)
        main_layout.addLayout(btn_layout)
        
        board_widget = QWidget()
        board_widget.setLayout(self.sudoku_grid)

        main_layout.addWidget(board_widget, alignment=Qt.AlignCenter)

        signature = QLabel("© Jacob Digital Entertainment 2026")
        signature.setStyleSheet("""
            color: #777;
            font-size: 14px;
        """)

        main_layout.addStretch()
        main_layout.addWidget(signature, alignment=Qt.AlignLeft)

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
                           
        QPushButton#ClearButton {
            background-color: #dc2626;
        }

        QPushButton#ClearButton:hover {
            background-color: #ef4444;
        }

        QPushButton#ClearButton:pressed {
            background-color: #b91c1c;
        }
                           
        """)
    

    def show_toast(self, message, duration=1500):
        toast = QLabel(message, self)

        toast.setStyleSheet("""
            background-color: #282828;
            color: white;
            border-radius: 10px;
            padding: 10px;
            font-size: 20px;
        """)

        toast.adjustSize()

        x = (self.width() - toast.width()) // 2
        y = self.height() - 80

        toast.move(x, y)
        toast.show()
        toast.raise_()

        effect = QGraphicsOpacityEffect(toast)
        effect.setOpacity(1.0)
        toast.setGraphicsEffect(effect)

        animation = QPropertyAnimation(effect, b"opacity")
        animation.setDuration(2000)
        animation.setStartValue(1.0)
        animation.setEndValue(0.0)

        def start_fade():
            animation.start()

        QTimer.singleShot(duration, start_fade)

        animation.finished.connect(toast.deleteLater)

        toast.animation = animation

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

            self.qt_image.save("JDE_SUDOKU_TEMP_IMAGE.png")

            self.image = cv2.imread("JDE_SUDOKU_TEMP_IMAGE.png")

            os.remove("JDE_SUDOKU_TEMP_IMAGE.png")

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

        # Odczyt aktualnej planszy z GUI
        grid = []

        for r in range(9):
            row = []

            for c in range(9):
                text = self.grid_labels[r][c].text().strip()

                if text == "":
                    row.append(0)
                else:
                    row.append(int(text))

            grid.append(row)

        original_grid = [row[:] for row in grid]

        if not is_valid_input(grid):
            self.show_toast("❌ Invalid input")
            return

        if solve_backtrack(grid):

            for r in range(9):
                for c in range(9):

                    # Pole było już wcześniej wypełnione
                    if original_grid[r][c] != 0:
                        continue

                    value = str(grid[r][c])

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
                        color: #22c55e;
                        font-size: 22px;
                        font-weight: bold;
                    """)
                    self.show_toast("✅ Sudoku solved!")

        else:
            self.show_toast("❌ No solution found")

    # =========================
    # Load
    # =========================

    def load_sudoku(self):

        if self.image is None:
            self.show_toast("❌ No image found")
            return

        self.clear_board()

        grid = image_to_grid(self.image)

        for r in range(9):
            for c in range(9):

                value = grid[r][c]

                if value == 0:
                    continue

                top = 3 if r % 3 == 0 else 1
                left = 3 if c % 3 == 0 else 1
                bottom = 3 if r == 8 else 1
                right = 3 if c == 8 else 1

                self.grid_labels[r][c].setText(str(value))

                self.grid_labels[r][c].setStyleSheet(f"""
                    background-color: #252526;
                    border-top: {top}px solid #888;
                    border-left: {left}px solid #888;
                    border-right: {right}px solid #888;
                    border-bottom: {bottom}px solid #888;
                    color: #888;
                    font-size: 22px;
                    font-weight: bold;
                """)
                self.show_toast("✅ Sudoku loaded!")


    # =========================
    # Generate
    # =========================

    def generate_sudoku(self):

        def is_valid(board, row, col, num):

            for x in range(9):
                if board[row][x] == num:
                    return False

            for x in range(9):
                if board[x][col] == num:
                    return False

            start_row = (row // 3) * 3
            start_col = (col // 3) * 3

            for r in range(start_row, start_row + 3):
                for c in range(start_col, start_col + 3):
                    if board[r][c] == num:
                        return False

            return True

        def fill_board(board):

            for row in range(9):
                for col in range(9):

                    if board[row][col] == 0:

                        nums = list(range(1, 10))
                        random.shuffle(nums)

                        for num in nums:

                            if is_valid(board, row, col, num):

                                board[row][col] = num

                                if fill_board(board):
                                    return True

                                board[row][col] = 0

                        return False

            return True

        # Generacja pełnego sudoku
        board = [[0 for _ in range(9)] for _ in range(9)]
        fill_board(board)

        # Kopia pełnego rozwiązania (opcjonalnie)
        self.solution = [row[:] for row in board]

        # Usuwanie pól
        cells_to_remove = 50

        for _ in range(cells_to_remove):

            row = random.randint(0, 8)
            col = random.randint(0, 8)

            board[row][col] = 0

        self.clear_board()

        for r in range(9):
            for c in range(9):

                value = board[r][c]

                if value == 0:
                    continue

                top = 3 if r % 3 == 0 else 1
                left = 3 if c % 3 == 0 else 1
                bottom = 3 if r == 8 else 1
                right = 3 if c == 8 else 1

                self.grid_labels[r][c].setText(str(value))

                self.grid_labels[r][c].setStyleSheet(f"""
                    background-color: #252526;
                    border-top: {top}px solid #888;
                    border-left: {left}px solid #888;
                    border-right: {right}px solid #888;
                    border-bottom: {bottom}px solid #888;
                    color: #888;
                    font-size: 22px;
                    font-weight: bold;
                """)
                self.show_toast("✅ Sudoku generated!")
    

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

    
    def clear_board_by_click(self):
        self.clear_board()
        self.show_toast("✅ Board cleared!")


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


if __name__ == "__main__":
    main()