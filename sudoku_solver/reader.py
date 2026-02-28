from PIL import ImageGrab, ImageFilter, Image
from .board import Board2D

__all__ = ["from_clipboard"]


def from_clipboard(filepath: str) -> None:
    img = ImageGrab.grabclipboard()
    if not isinstance(img, Image.Image):
        raise ValueError("Clipboard does not contain an image")
    img = img.filter(ImageFilter.SMOOTH_MORE).filter(ImageFilter.MedianFilter(3))
    img = img.convert("L")
    img.save(filepath, format="PNG")
