"""Computer vision module (research question A)."""

from vision.glyph_render import ensure_glyphs, motif_name, render_glyph
from vision.pipeline import compare_shapes, detect_sign_boxes, vision_report

__all__ = [
    "compare_shapes",
    "detect_sign_boxes",
    "ensure_glyphs",
    "motif_name",
    "render_glyph",
    "vision_report",
]
