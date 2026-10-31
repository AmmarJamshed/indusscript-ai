"""Render visual proxies for Indus sign IDs.

These are geometric/iconographic stand-ins for readability in the UI.
They are NOT attested palaeographic drawings and do not encode proven meanings.
"""

from __future__ import annotations

import hashlib
from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from config.settings import PROCESSED_DIR, ensure_directories

GLYPH_DIR = PROCESSED_DIR / "glyphs"
GLYPH_SIZE = 128

# Simple motif families so signs look like "script symbols", not barcode IDs.
MOTIFS = (
    "fish",
    "jar",
    "person",
    "trident",
    "tree",
    "wheel",
    "arrow",
    "crescent",
    "grid",
    "animal",
    "cross",
    "loop",
    "spear",
    "boat",
    "mountain",
    "star",
)


def _seed(sign_id: str) -> int:
    return int(hashlib.md5(sign_id.encode("utf-8")).hexdigest()[:8], 16)


def _motif_for(sign_id: str) -> str:
    return MOTIFS[_seed(sign_id) % len(MOTIFS)]


def _draw_motif(draw: ImageDraw.ImageDraw, motif: str, box: tuple[int, int, int, int], fill: int) -> None:
    x0, y0, x1, y1 = box
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    w, h = x1 - x0, y1 - y0

    if motif == "fish":
        draw.polygon([(x0, cy), (cx - 8, y0 + 18), (x1 - 10, cy), (cx - 8, y1 - 18)], outline=fill, width=3)
        draw.ellipse([x1 - 28, cy - 8, x1 - 12, cy + 8], outline=fill, width=2)
        draw.line([(x0, cy), (x0 + 18, y0 + 12)], fill=fill, width=3)
        draw.line([(x0, cy), (x0 + 18, y1 - 12)], fill=fill, width=3)
    elif motif == "jar":
        draw.rectangle([cx - 22, y0 + 28, cx + 22, y1 - 12], outline=fill, width=3)
        draw.arc([cx - 28, y0 + 10, cx + 28, y0 + 50], 200, 340, fill=fill, width=3)
        draw.line([(cx - 22, y1 - 12), (cx + 22, y1 - 12)], fill=fill, width=3)
    elif motif == "person":
        draw.ellipse([cx - 12, y0 + 14, cx + 12, y0 + 38], outline=fill, width=3)
        draw.line([(cx, y0 + 38), (cx, y1 - 28)], fill=fill, width=3)
        draw.line([(cx - 22, y0 + 55), (cx + 22, y0 + 55)], fill=fill, width=3)
        draw.line([(cx, y1 - 28), (cx - 18, y1 - 8)], fill=fill, width=3)
        draw.line([(cx, y1 - 28), (cx + 18, y1 - 8)], fill=fill, width=3)
    elif motif == "trident":
        draw.line([(cx, y1 - 10), (cx, y0 + 25)], fill=fill, width=3)
        draw.line([(cx, y0 + 25), (cx - 24, y0 + 12)], fill=fill, width=3)
        draw.line([(cx, y0 + 25), (cx + 24, y0 + 12)], fill=fill, width=3)
        draw.line([(cx, y0 + 25), (cx, y0 + 8)], fill=fill, width=3)
    elif motif == "tree":
        draw.line([(cx, y1 - 8), (cx, y0 + 45)], fill=fill, width=3)
        draw.ellipse([cx - 28, y0 + 12, cx + 28, y0 + 55], outline=fill, width=3)
        draw.line([(cx, y0 + 55), (cx - 20, y0 + 30)], fill=fill, width=2)
        draw.line([(cx, y0 + 55), (cx + 20, y0 + 30)], fill=fill, width=2)
    elif motif == "wheel":
        draw.ellipse([x0 + 18, y0 + 18, x1 - 18, y1 - 18], outline=fill, width=3)
        draw.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], outline=fill, width=2)
        for dx, dy in [(-30, 0), (30, 0), (0, -30), (0, 30)]:
            draw.line([(cx, cy), (cx + dx, cy + dy)], fill=fill, width=2)
    elif motif == "arrow":
        draw.line([(x0 + 20, cy), (x1 - 20, cy)], fill=fill, width=3)
        draw.polygon([(x1 - 20, cy), (x1 - 42, cy - 16), (x1 - 42, cy + 16)], outline=fill, width=2)
    elif motif == "crescent":
        draw.arc([x0 + 22, y0 + 18, x1 - 10, y1 - 18], 90, 270, fill=fill, width=4)
        draw.arc([x0 + 38, y0 + 26, x1 - 18, y1 - 26], 90, 270, fill=0, width=6)
    elif motif == "grid":
        for i in range(4):
            yy = y0 + 24 + i * 20
            xx = x0 + 24 + i * 20
            draw.line([(x0 + 20, yy), (x1 - 20, yy)], fill=fill, width=2)
            draw.line([(xx, y0 + 20), (xx, y1 - 20)], fill=fill, width=2)
    elif motif == "animal":
        draw.ellipse([x0 + 30, cy - 18, x1 - 18, cy + 18], outline=fill, width=3)
        draw.ellipse([x0 + 12, cy - 10, x0 + 40, cy + 12], outline=fill, width=3)
        draw.line([(x1 - 30, cy + 16), (x1 - 18, y1 - 12)], fill=fill, width=3)
        draw.line([(x0 + 48, cy + 16), (x0 + 36, y1 - 12)], fill=fill, width=3)
    elif motif == "cross":
        draw.line([(cx, y0 + 16), (cx, y1 - 16)], fill=fill, width=4)
        draw.line([(x0 + 24, cy), (x1 - 24, cy)], fill=fill, width=4)
    elif motif == "loop":
        draw.arc([x0 + 24, y0 + 20, x1 - 24, y1 - 20], 0, 360, fill=fill, width=3)
        draw.arc([cx - 6, y0 + 8, cx + 18, y0 + 36], 200, 40, fill=fill, width=3)
    elif motif == "spear":
        draw.line([(cx, y1 - 10), (cx, y0 + 20)], fill=fill, width=3)
        draw.polygon([(cx, y0 + 12), (cx - 14, y0 + 36), (cx + 14, y0 + 36)], outline=fill, width=2)
    elif motif == "boat":
        draw.arc([x0 + 18, cy - 10, x1 - 18, y1 - 16], 0, 180, fill=fill, width=3)
        draw.line([(cx, cy), (cx, y0 + 18)], fill=fill, width=3)
        draw.polygon([(cx, y0 + 18), (cx + 28, cy - 4), (cx, cy - 4)], outline=fill, width=2)
    elif motif == "mountain":
        draw.polygon([(x0 + 16, y1 - 18), (cx - 10, y0 + 28), (cx + 8, y1 - 18)], outline=fill, width=3)
        draw.polygon([(cx - 8, y1 - 18), (cx + 18, y0 + 22), (x1 - 16, y1 - 18)], outline=fill, width=3)
    else:  # star
        pts = [
            (cx, y0 + 16),
            (cx + 10, cy - 6),
            (x1 - 18, cy - 6),
            (cx + 14, cy + 8),
            (cx + 22, y1 - 18),
            (cx, cy + 14),
            (cx - 22, y1 - 18),
            (cx - 14, cy + 8),
            (x0 + 18, cy - 6),
            (cx - 10, cy - 6),
        ]
        draw.polygon(pts, outline=fill, width=2)


def render_glyph(
    sign_id: str,
    size: int = GLYPH_SIZE,
    *,
    show_label: bool = False,
) -> Image.Image:
    """Return a PIL image for a sign id."""
    img = Image.new("L", (size, size), 255)
    draw = ImageDraw.Draw(img)
    margin = 10
    draw.rounded_rectangle(
        [2, 2, size - 3, size - 3],
        radius=10,
        outline=40,
        width=2,
    )
    motif = _motif_for(sign_id)
    _draw_motif(draw, motif, (margin, margin, size - margin, size - margin - (18 if show_label else 0)), 20)
    if show_label:
        # Tiny ID under glyph for researchers; UI can hide this.
        try:
            font = ImageFont.load_default()
        except Exception:  # noqa: BLE001
            font = None
        label = sign_id[-6:] if len(sign_id) > 6 else sign_id
        draw.text((size // 2 - 18, size - 16), label, fill=90, font=font)
    return img


@lru_cache(maxsize=512)
def glyph_path(sign_id: str, size: int = GLYPH_SIZE) -> str:
    ensure_directories()
    GLYPH_DIR.mkdir(parents=True, exist_ok=True)
    safe = "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in sign_id)
    path = GLYPH_DIR / f"{safe}_{size}.png"
    if not path.exists():
        render_glyph(sign_id, size=size, show_label=False).save(path)
    return str(path)


def ensure_glyphs(sign_ids: list[str], size: int = GLYPH_SIZE) -> dict[str, str]:
    return {sid: glyph_path(sid, size) for sid in sign_ids}


def motif_name(sign_id: str) -> str:
    return _motif_for(sign_id)
