import time
from sudoku_solver import from_clipboard, SudokuBoard, create_ps_script, run_ps_script

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

    inputs = []
    for y in range(9):
        for x in range(9):
            inputs.append("{RIGHT}")
            inputs.append(str(board[x, y]))
        inputs.append("{DOWN}")

    script_path = create_ps_script(inputs)
    run_ps_script(script_path)
