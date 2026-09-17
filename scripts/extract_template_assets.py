"""Extract fixed artwork from the unmodified 2026 template exported by Word.
Run with Python + PyMuPDF from the repository root; rebuild with latexmk after extraction.
"""
from pathlib import Path
import pymupdf as fitz
root = Path(__file__).resolve().parent.parent
source = fitz.open(root / 'reference/2026/word-render.pdf')
assets = {
    'cover2026.pdf': (0, (0, 0, 595.2, 770)),
    'abstract-header2026.pdf': (1, (0, 0, 595.2, 338)),
    'keywords2026.pdf': (1, (63.84, 431, 137, 457)),
    'title.pdf': (0, (127, 217, 478, 307)),
    'logo.pdf': (0, (110, 90, 482, 168)),
}
for name, (page, bounds) in assets.items():
    rect = fitz.Rect(bounds)
    output = fitz.open()
    target = output.new_page(width=rect.width, height=rect.height)
    target.show_pdf_page(target.rect, source, page, clip=rect)
    output.save(root / 'figures' / name, garbage=4, deflate=True)
