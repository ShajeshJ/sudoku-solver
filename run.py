import time
from sudoku_solver import from_clipboard, SudokuBoard

if __name__ == "__main__":
    from_clipboard("sudoku.png")

    # TODO: uncomment once done implementing from_clipboard
    # input_board = []
    # for i in range(9):
    #     line = input(f"Enter row {i+1} (. for empty cells): ")
    #     input_board.append([int(c) if c.isdigit() else None for c in line])

    # board = SudokuBoard(input_board)

    # print("Initial board:")
    # print(board)

    # print("Solving...")

    # try:
    #     start = time.perf_counter() * 1000
    #     board.solve()
    #     end = time.perf_counter() * 1000
    # finally:
    #     print(board)

    # print(f"Solved in {end - start:.4f} ms")
