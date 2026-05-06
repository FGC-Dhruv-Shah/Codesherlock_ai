import random


def create_board():
    return [[" " for _ in range(3)] for _ in range(3)]


def print_board(board):
    print("\n  1   2   3")
    for i, row in enumerate(board):
        print(f"{i+1} {' | '.join(row)}")
        if i < 2:
            print("  ---------")
    print()


def check_winner(board, player):
    for row in board:
        if all(cell == player for cell in row):
            return True
    for col in range(3):
        if all(board[row][col] == player for row in range(3)):
            return True
    if all(board[i][i] == player for i in range(3)):
        return True
    if all(board[i][2 - i] == player for i in range(3)):
        return True
    return False


def is_full(board):
    return all(cell != " " for row in board for cell in row)


def get_available_moves(board):
    return [(r, c) for r in range(3) for c in range(3) if board[r][c] == " "]


def minimax(board, is_maximizing):
    if check_winner(board, "O"):
        return 1
    if check_winner(board, "X"):
        return -1
    if is_full(board):
        return 0

    if is_maximizing:
        best = -10
        for r, c in get_available_moves(board):
            board[r][c] = "O"
            best = max(best, minimax(board, False))
            board[r][c] = " "
        return best
    else:
        best = 10
        for r, c in get_available_moves(board):
            board[r][c] = "X"
            best = min(best, minimax(board, True))
            board[r][c] = " "
        return best


def ai_move(board):
    best_score = -10
    best_move = None
    for r, c in get_available_moves(board):
        board[r][c] = "O"
        score = minimax(board, False)
        board[r][c] = " "
        if score > best_score:
            best_score = score
            best_move = (r, c)
    return best_move


def get_player_move(board):
    while True:
        try:
            row = int(input("Enter row (1-3): ")) - 1
            col = int(input("Enter col (1-3): ")) - 1
            if 0 <= row <= 2 and 0 <= col <= 2 and board[row][col] == " ":
                return row, col
            print("Invalid move. Try again.")
        except ValueError:
            print("Please enter a number.")


def choose_mode():
    print("=== Tic Tac Toe ===")
    print("1. Player vs Player")
    print("2. Player vs AI")
    while True:
        choice = input("Choose mode (1 or 2): ").strip()
        if choice in ("1", "2"):
            return int(choice)
        print("Invalid choice.")


def play_game():
    mode = choose_mode()
    board = create_board()
    players = ["X", "O"]
    current = 0

    while True:
        print_board(board)
        player = players[current]
        print(f"Player {player}'s turn")

        if mode == 2 and player == "O":
            print("AI is thinking...")
            row, col = ai_move(board)
        else:
            row, col = get_player_move(board)

        board[row][col] = player

        if check_winner(board, player):
            print_board(board)
            if mode == 2 and player == "O":
                print("AI wins!")
            else:
                print(f"Player {player} wins!")
            break

        if is_full(board):
            print_board(board)
            print("It's a draw!")
            break

        current = 1 - current

    again = input("Play again? (y/n): ").strip().lower()
    if again == "y":
        play_game()


if __name__ == "__main__":
    play_game()
