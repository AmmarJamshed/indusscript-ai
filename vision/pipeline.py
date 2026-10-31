"""Optional computer-vision pipeline for inscription images.

Visual similarity answers research question A only.
Do not infer meaning of a sign from its appearance.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np

from config.logging_config import setup_logging
from config.settings import EXTERNAL_DIR, ensure_directories

logger = setup_logging("vision")


def _cv2():
    try:
        import cv2  # type: ignore
        return cv2
    except ImportError as exc:
        raise ImportError("opencv-python-headless is required for vision features") from exc


def load_image(path: str | Path) -> np.ndarray:
    cv2 = _cv2()
    img = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise FileNotFoundError(path)
    return img


def preprocess(image: np.ndarray) -> np.ndarray:
    cv2 = _cv2()
    blur = cv2.GaussianBlur(image, (3, 3), 0)
    _, thr = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    return thr


def detect_sign_boxes(image: np.ndarray, min_area: int = 50) -> list[tuple[int, int, int, int]]:
    cv2 = _cv2()
    proc = preprocess(image)
    contours, _ = cv2.findContours(proc, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    boxes = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        if w * h >= min_area:
            boxes.append((x, y, w, h))
    boxes.sort(key=lambda b: b[0])
    return boxes


def crop_signs(image: np.ndarray, boxes: list[tuple[int, int, int, int]]) -> list[np.ndarray]:
    return [image[y : y + h, x : x + w] for x, y, w, h in boxes]


def rotate_image(image: np.ndarray, angle: float) -> np.ndarray:
    cv2 = _cv2()
    h, w = image.shape[:2]
    m = cv2.getRotationMatrix2D((w / 2, h / 2), angle, 1.0)
    return cv2.warpAffine(image, m, (w, h), borderValue=255)


def image_embedding(image: np.ndarray, size: tuple[int, int] = (32, 32)) -> np.ndarray:
    """Lightweight classical embedding (HOG-like flattened resize).

    Replace with a trained CNN / CLIP encoder when PyTorch models are available.
    """
    cv2 = _cv2()
    resized = cv2.resize(image, size)
    vec = resized.astype(np.float32).flatten()
    norm = np.linalg.norm(vec) or 1.0
    return vec / norm


def compare_shapes(a: np.ndarray, b: np.ndarray) -> float:
    ea, eb = image_embedding(a), image_embedding(b)
    return float(np.dot(ea, eb))


def classify_known_sign(
    crop: np.ndarray,
    catalogue: dict[str, np.ndarray],
) -> tuple[str | None, float]:
    """Nearest-neighbour against an Indus-specific catalogue only."""
    if not catalogue:
        return None, 0.0
    best_id, best_score = None, -1.0
    for sid, proto in catalogue.items():
        score = compare_shapes(crop, proto)
        if score > best_score:
            best_id, best_score = sid, score
    return best_id, float(best_score)


def vision_report(image_paths: list[str | Path]) -> dict[str, Any]:
    ensure_directories()
    results = []
    for path in image_paths:
        try:
            img = load_image(path)
            boxes = detect_sign_boxes(img)
            results.append(
                {
                    "path": str(path),
                    "n_boxes": len(boxes),
                    "boxes": boxes[:50],
                }
            )
        except Exception as exc:  # noqa: BLE001
            results.append({"path": str(path), "error": str(exc)})
    return {
        "research_question": "A",
        "n_images": len(image_paths),
        "results": results,
        "catalogue_policy": "Indus recognition must use an Indus sign catalogue only.",
        "caveat": (
            "Visual similarity does not imply shared phonetics, semantics or ancestry. "
            "Egyptian hieroglyphs may be used as a labelled CV benchmark, not as a key "
            "to Indus meanings."
        ),
        "output_dir": str(EXTERNAL_DIR / "vision"),
    }
