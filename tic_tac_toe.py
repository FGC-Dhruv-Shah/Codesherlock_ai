"""Tic-tac-toe: game state (`TicTacToe`) and a small CLI (`run_cli_game`).

Moves use 1-based row and column in the 1 to 3 range, for example "2,3" or
"2 3". Type "quit" during play to stop. The class can be embedded in a GUI
or other front end while keeping the same rules.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Tuple

__all__ = ["BOARD_SIZE", "TicTacToe", "parse_position", "run_cli_game"]

Position = Tuple[int, int]
BOARD_SIZE = 3


@dataclass
class TicTacToe:
    """Mutable 3x3 game: X opens; winner or full board (draw) ends the round."""

    board: List[List[str]] = field(
        default_factory=lambda: [[" "] * BOARD_SIZE for _ in range(BOARD_SIZE)]
    )
    current_player: str = "X"
    winner: Optional[str] = None
    is_draw: bool = False
    move_count: int = 0

    def reset(self) -> None:
        self.board = [[" "] * BOARD_SIZE for _ in range(BOARD_SIZE)]
        self.current_player, self.winner, self.is_draw, self.move_count = "X", None, False, 0

    def get_available_moves(self) -> List[Position]:
        return [
            (r, c)
            for r in range(BOARD_SIZE)
            for c in range(BOARD_SIZE)
            if self.board[r][c] == " "
        ]

    def is_valid_move(self, row: int, col: int) -> bool:
        """Return True if the cell is on the board and still empty."""
        if not (0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE):
            return False
        return self.board[row][col] == " "

    def make_move(self, row: int, col: int) -> bool:
        if not self.is_valid_move(row, col):
            return False
        self.board[row][col] = self.current_player
        self.move_count += 1
        w = self._check_winner()
        if w:
            self.winner, self.is_draw = w, False
        elif self.move_count >= BOARD_SIZE * BOARD_SIZE:
            self.is_draw = True
        elif not self.is_game_over():
            self.current_player = "O" if self.current_player == "X" else "X"
        return True

    def _check_winner(self) -> Optional[str]:
        b = self.board
        n = BOARD_SIZE
        lines = [b[r] for r in range(n)] + [[b[r][c] for r in range(n)] for c in range(n)]
        lines += [[b[0][0], b[1][1], b[2][2]], [b[0][2], b[1][1], b[2][0]]]
        for a, x, y in lines:
            if a != " " and a == x == y:
                return a
        return None

    def is_game_over(self) -> bool:
        return self.winner is not None or self.is_draw

    def render_board(self) -> str:
        return "\n---+---+---\n".join(f" {r[0]} | {r[1]} | {r[2]} " for r in self.board)

    def get_status_message(self) -> str:
        if self.winner:
            return f"Player {self.winner} wins!"
        if self.is_draw:
            return "It's a draw!"
        return f"Player {self.current_player}'s turn."


def parse_position(raw: str) -> Optional[Position]:
    """Parse 'row,col' or 'row col' into 0-based indices; return None if invalid."""
    parts = [p for p in raw.strip().replace(",", " ").split() if p]
    if len(parts) != 2:
        return None
    try:
        row, col = int(parts[0]) - 1, int(parts[1]) - 1
    except ValueError:
        return None
    if not (0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE):
        return None
    return row, col


def run_cli_game() -> None:
    """Print the board, read moves in a loop, and offer a rematch when finished."""
    game = TicTacToe()
    print("Welcome to Tic-Tac-Toe")
    print("Enter moves as row,col using values 1 to 3.")
    print("Type 'quit' to exit.\n")
    while True:
        print(game.render_board(), game.get_status_message(), sep="\n")
        if game.is_game_over():
            if input("Play again? (y/n): ").strip().lower() == "y":
                game.reset()
                print()
                continue
            print("Goodbye!")
            break
        raw = input("Your move: ").strip()
        if raw.lower() == "quit":
            print("Goodbye!")
            break
        pos = parse_position(raw)
        if pos is None:
            print("Invalid input. Use row,col with values from 1 to 3.\n")
            continue
        if not game.make_move(*pos):
            print("That cell is already occupied. Try another move.\n")
            continue
        print()


if __name__ == "__main__":
    run_cli_game()
