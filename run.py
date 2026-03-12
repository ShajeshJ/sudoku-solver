import time
from sudoku_solver import from_clipboard, SudokuBoard

if __name__ == "__main__":
    input_board = from_clipboard()

    board = SudokuBoard(input_board)

    print("Initial board:")
    print(board)

    print("Solving...")

    try:
        start = time.perf_counter() * 1000
        board.solve()
        end = time.perf_counter() * 1000
    finally:
        print(board)

    print(f"Solved in {end - start:.4f} ms")
