from collections.abc import Iterable
from typing import cast, overload

__all__ = ["SudokuBoard", "Board1D", "Board2D"]

type Board1D = Iterable[int | None]
type Board2D = Iterable[Iterable[int | None]]


box_index = lambda x, y: (y // 3) * 3 + (x // 3)


class SudokuBoard:
    board: Board1D = cast(Board1D, None)
    _rows: list[set[int]] = cast(list[set[int]], None)
    _cols: list[set[int]] = cast(list[set[int]], None)
    _boxes: list[set[int]] = cast(list[set[int]], None)

    def __init__(self, board: Board1D | Board2D):
        _board = list(board)

        if isinstance(_board[0], Iterable):
            if len(_board) != 9 or any(
                not isinstance(row, Iterable) or len(list(row)) != 9 for row in _board
            ):
                raise ValueError("Board must be 9x9")
            self.board = [cell for row in _board for cell in cast(Board1D, row)]
        else:
            if len(_board) != 81:
                raise ValueError("Board must be 9x9")
            self.board = cast(Board1D, _board)

        self._init_trackers()

    @overload
    def __getitem__(self, index: int) -> int | None: ...

    @overload
    def __getitem__(self, index: tuple[int, int]) -> int | None: ...

    def __getitem__(self, index):
        if isinstance(index, int):
            return self.board[index]
        elif isinstance(index, tuple) and len(index) == 2:
            col, row = index
            if not (0 <= row < 9 and 0 <= col < 9):
                raise IndexError("Row and column indices must be between 0 and 8")
            return self.board[row * 9 + col]
        else:
            raise IndexError("Invalid index type")

    @overload
    def __setitem__(self, index: int, value: int | None) -> None: ...

    @overload
    def __setitem__(self, index: tuple[int, int], value: int | None) -> None: ...

    def __setitem__(self, index, value):
        if isinstance(index, int):
            self.board[index] = value
        elif isinstance(index, tuple) and len(index) == 2:
            col, row = index
            if not (0 <= row < 9 and 0 <= col < 9):
                raise IndexError("Row and column indices must be between 0 and 8")
            self.board[row * 9 + col] = value
        else:
            raise IndexError("Invalid index type")

    def _add_to_trackers(self, x: int, y: int, value: int) -> None:
        self._rows[y].add(value)
        self._cols[x].add(value)
        self._boxes[box_index(x, y)].add(value)

    def _init_trackers(self):
        self._rows = [set() for _ in range(9)]
        self._cols = [set() for _ in range(9)]
        self._boxes = [set() for _ in range(9)]

        for y in range(9):
            for x in range(9):
                value = self[x, y]
                if value is None:
                    continue
                if not (1 <= value <= 9):
                    raise ValueError("Cell values must be between 1 and 9")
                self._add_to_trackers(x, y, value)

    def __str__(self):
        rows = []
        celltostr = lambda x, y: str(self[x, y]) if self[x, y] is not None else "."
        for y in range(9):
            row = " | ".join(
                f"{celltostr(x, y)} {celltostr(x+1, y)} {celltostr(x+2, y)}"
                for x in range(0, 9, 3)
            )
            rows.append(f"| {row} |")
        row_divider = "\n" + ("-" * 25) + "\n"
        return (
            row_divider
            + row_divider.join("\n".join(rows[i : i + 3]) for i in range(0, 9, 3))
            + row_divider
        )

    def _get_remaining(self, x: int, y: int) -> set[int]:
        used_numbers = self._rows[y] | self._cols[x] | self._boxes[box_index(x, y)]
        return set(range(1, 10)) - used_numbers

    def _is_only_box_cell(self, x: int, y: int, value: int) -> bool:
        box_row_start = (y // 3) * 3
        num_available_rows = sum(
            1
            for row in range(box_row_start, box_row_start + 3)
            if value not in self._rows[row]
        )

        box_col_start = (x // 3) * 3
        num_available_cols = sum(
            1
            for col in range(box_col_start, box_col_start + 3)
            if value not in self._cols[col]
        )

        return num_available_rows == 1 and num_available_cols == 1

    def _is_only_row_cell(self, y: int, value: int) -> bool:
        num_available_cols = sum(
            1
            for x in range(9)
            if (
                self[x, y] is None
                and value not in self._cols[x]
                and value not in self._boxes[box_index(x, y)]
            )
        )
        return num_available_cols == 1

    def _is_only_col_cell(self, x: int, value: int) -> bool:
        num_available_rows = sum(
            1
            for y in range(9)
            if (
                self[x, y] is None
                and value not in self._rows[y]
                and value not in self._boxes[box_index(x, y)]
            )
        )
        return num_available_rows == 1

    def solve(self):
        has_changed = True
        is_solved = False

        while has_changed:
            has_changed = False
            is_solved = True

            for y in range(9):
                for x in range(9):
                    if self[x, y] is not None:
                        continue
                    is_solved = False

                    remaining = self._get_remaining(x, y)
                    if len(remaining) == 1:
                        value = remaining.pop()
                        self[x, y] = value
                        self._add_to_trackers(x, y, value)
                        has_changed = True
                    elif len(remaining) == 0:
                        raise RuntimeError(
                            f"Invalid board: no valid values for cell ({x}, {y})"
                        )
                    else:
                        for value in remaining:
                            if (
                                self._is_only_box_cell(x, y, value)
                                or self._is_only_row_cell(y, value)
                                or self._is_only_col_cell(x, value)
                            ):
                                self[x, y] = value
                                self._add_to_trackers(x, y, value)
                                has_changed = True
                                break

        if not is_solved:
            raise RuntimeError("Could not solve the board with simple elimination")
