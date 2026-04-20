import cv2
import torch
import numpy as np
from PIL import Image
from transformers import TrOCRProcessor, VisionEncoderDecoderModel

# =========================
# CONFIG
# =========================

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

print(f"🧠 TrOCR using: {DEVICE}")

processor = TrOCRProcessor.from_pretrained("microsoft/trocr-small-printed")

model = VisionEncoderDecoderModel.from_pretrained(
    "microsoft/trocr-small-printed"
).to(DEVICE)


# =========================
# PREPROCESS
# =========================

def preprocess_cell(cell):
    gray = cv2.cvtColor(cell, cv2.COLOR_BGR2GRAY)

    # kontrast
    gray = cv2.equalizeHist(gray)

    # threshold
    _, th = cv2.threshold(
        gray, 0, 255,
        cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
    )

    return th


# =========================
# OCR
# =========================

def extract_digit(cell):
    processed = preprocess_cell(cell)

    if cv2.countNonZero(processed) < 30:
        return 0

    pil_img = Image.fromarray(processed)

    pixel_values = processor(
        pil_img,
        return_tensors="pt"
    ).pixel_values.to(DEVICE)

    with torch.no_grad():
        generated_ids = model.generate(
            pixel_values,
            max_new_tokens=2,
            num_beams=1
        )

    text = processor.batch_decode(
        generated_ids,
        skip_special_tokens=True
    )[0].strip()

    # 🔥 NORMALIZACJA POD SUDOKU
    return normalize_digit(text)


# =========================
# POSTPROCESS
# =========================

def normalize_digit(text: str) -> int:
    if not text:
        return 0

    text = text.strip()

    # typowe błędy OCR
    mapping = {
        "I": "1",
        "l": "1",
        "|": "1",
        "O": "0",
        "S": "5",
        "B": "8",
        "G": "6"
    }

    text = mapping.get(text, text)

    if text.isdigit():
        val = int(text)
        if 1 <= val <= 9:
            return val

    return 0