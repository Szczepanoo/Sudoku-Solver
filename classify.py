import torch
import torch.nn as nn
import cv2
import numpy as np

# =========================
# CONFIG
# =========================

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
DEVICE = 'cpu'

# =========================
# MODEL
# =========================

class DigitCNN(nn.Module):
    def __init__(self):
        super().__init__()

        self.conv = nn.Sequential(
            nn.Conv2d(1, 32, 3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),

            nn.Conv2d(32, 64, 3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
        )

        self.fc = nn.Sequential(
            nn.Flatten(),
            nn.Linear(64 * 7 * 7, 128),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(128, 10)
        )

    def forward(self, x):
        x = self.conv(x)
        return self.fc(x)


# =========================
# LOAD MODEL (lazy)
# =========================

_model = None


def get_model():
    global _model

    if _model is None:
        model = DigitCNN().to(DEVICE)
        model.load_state_dict(
            torch.load("digit_cnn.pth", map_location=DEVICE)
        )
        model.eval()

        print(f"🧠 CNN loaded on {DEVICE}")
        _model = model

    return _model


# =========================
# PREPROCESS
# =========================

def preprocess_cell(cell):
    gray = cv2.cvtColor(cell, cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(gray, (28, 28))
    gray = gray / 255.0
    gray = (gray - 0.5) / 0.5

    return gray


# =========================
# CLASSIFICATION
# =========================

def extract_digit(cell):
    img = preprocess_cell(cell)

    # puste pole
    if np.count_nonzero(img) < 0.05 * img.size:
        return 0

    tensor = torch.tensor(img, dtype=torch.float32)
    tensor = tensor.unsqueeze(0).unsqueeze(0).to(DEVICE)

    model = get_model()

    with torch.no_grad():
        logits = model(tensor)
        pred = torch.argmax(logits, dim=1).item()

    return pred