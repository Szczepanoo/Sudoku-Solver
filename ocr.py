import cv2
import numpy as np
import easyocr

import torch
import easyocr

def create_reader(use_gpu=True):
    if use_gpu and torch.cuda.is_available():
        print("🚀 EasyOCR: używam GPU")
        return easyocr.Reader(['en'], gpu=True)
    else:
        print("🐌 EasyOCR: fallback na CPU")
        return easyocr.Reader(['en'], gpu=False)


# global reader (lazy init)
_reader = None


def get_reader(use_gpu=True):
    global _reader
    if _reader is None:
        _reader = create_reader(use_gpu)
    return _reader


def preprocess_cell(cell):
    gray = cv2.cvtColor(cell, cv2.COLOR_BGR2GRAY)
    gray = cv2.equalizeHist(gray)

    _, th = cv2.threshold(
        gray, 0, 255,
        cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
    )

    kernel = np.ones((3, 3), np.uint8)
    th = cv2.morphologyEx(th, cv2.MORPH_OPEN, kernel)

    return th


def extract_digit(cell):
    processed = preprocess_cell(cell)

    if cv2.countNonZero(processed) < 50:
        return 0

    reader = get_reader()

    results = reader.readtext(processed, detail=0, paragraph=False)

    if not results:
        return 0

    text = results[0].strip()

    if text.isdigit():
        val = int(text)
        if 1 <= val <= 9:
            return val

    return 0