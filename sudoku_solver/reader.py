import cv2
import numpy as np
from imutils import contours
from PIL import ImageGrab, Image
import pytesseract

from .board import Board1D

__all__ = ["from_clipboard"]

pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"


def from_clipboard() -> Board1D:
    loaded_img = ImageGrab.grabclipboard()
    if not isinstance(loaded_img, Image.Image):
        raise ValueError("Clipboard does not contain an image")

    # produce a binary image with strictly black or white, pixels
    # lines/numbers/noise is white, and background is black
    # static global threshold seems to work a bit nicer than adaptive thresholding
    # using screenshots of the boards from https://sudoku.game; 230 threshold found through trial and error
    gray_img = cv2.cvtColor(np.array(loaded_img), cv2.COLOR_BGR2GRAY)
    _, thresh_img = cv2.threshold(gray_img, 230, 255, cv2.THRESH_BINARY_INV)

    # Finds all shaped regions, using whites as "entities", and blacks as the empty space
    grid_img = thresh_img.copy()
    cntrs, _ = cv2.findContours(thresh_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    for c in cntrs:
        # We want to remove (i.e. black out) all of the small shapes; this includes, any random noise
        # as well as all of the numbers. The square 9x9 grid should be left intact.
        # Area of < 3000 to detect contours for numbers + any other noise found through trial and error
        if cv2.contourArea(c) < 3000:
            cv2.drawContours(grid_img, [c], -1, (0, 0, 0), cv2.FILLED)

    grid_img = 255 - grid_img

    # Finds shaped regions, again, using whites as "entities", and blacks as empty space
    # because we've inverted to the original, this should match against each of
    # the 81 boxes, and the outside border
    grid_cntrs, _ = cv2.findContours(grid_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # filter to just each individual cell, which is area <8000 (found through trial and error)
    grid_cntrs = [c for c in grid_cntrs if cv2.contourArea(c) < 8000]

    # Orders such that 1st row is indexes 0-8, 2nd row is 9-17, etc
    grid_cntrs, _ = contours.sort_contours(grid_cntrs, method="left-to-right")
    grid_cntrs, _ = contours.sort_contours(grid_cntrs, method="top-to-bottom")

    sudoku_grid: list[int | None] = []

    for cell in grid_cntrs:
        # uses each contour to create a cropped mask of each individual cell
        x, y, w, h = cv2.boundingRect(cell)
        masked = gray_img[y : y + h, x : x + w]
        _, masked = cv2.threshold(masked, 127, 255, cv2.THRESH_BINARY)

        # check if cell is completely white pixels; skip to avoid garbage from the OCR
        if cv2.countNonZero(masked) == masked.shape[0] * masked.shape[1]:
            sudoku_grid.append(None)
            continue

        # we make the text smaller because the OCR struggles with images with big font text
        masked = cv2.resize(masked, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_CUBIC)

        # run OCR in psm 10 (for detecting a singular character)
        maybe_digit: str = pytesseract.image_to_string(masked, config=r"--psm 10")
        maybe_digit = maybe_digit.strip()

        if len(maybe_digit) > 1 or not maybe_digit.isdigit():
            raise ValueError(f"parsed unidentifiable sudoku cell <{maybe_digit}>")

        sudoku_grid.append(int(maybe_digit))

        # visual debugging
        # mask = np.zeros(gray_img.shape, dtype=np.uint8)
        # cv2.drawContours(mask, [cell], -1, (255, 255, 255), -1)
        # masked = cv2.bitwise_and(gray_img, mask)
        # cv2.imshow("masked cell", masked)
        # cv2.waitKey(500)

    return sudoku_grid
