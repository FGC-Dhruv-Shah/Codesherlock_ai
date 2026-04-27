"""Tic-Tac-Toe game logic with a simple CLI runner.

This module exposes a reusable TicTacToe class and helper functions that can
be used both from a command-line script and from a UI framework like Streamlit.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Tuple


Position = Tuple[int, int]


@dataclass
class TicTacToe:
    """Stateful 3x3 tic-tac-toe game."""

    board: List[List[str]] = field(
        default_factory=lambda: [[" " for _ in range(3)] for _ in range(3)]
    )
    current_player: str = "X"
    winner: Optional[str] = None
    is_draw: bool = False
    move_count: int = 0

    def reset(self) -> None:
        """Reset the game to initial state."""
        self.board = [[" " for _ in range(3)] for _ in range(3)]
        self.current_player = "X"
        self.winner = None
        self.is_draw = False
        self.move_count = 0

    def get_available_moves(self) -> List[Position]:
        """Return all open squares on the board."""
        moves: List[Position] = []
        for row in range(3):
            for col in range(3):
                if self.board[row][col] == " ":
                    moves.append((row, col))
        return moves

    def make_move(self, row: int, col: int) -> bool:
        """Place current player's symbol if move is valid."""
        if not self._is_valid_move(row, col):
            return False

        self.board[row][col] = self.current_player
        self.move_count += 1
        self._update_game_status()
        if not self.is_game_over():
            self.current_player = "O" if self.current_player == "X" else "X"
        return True

    def _is_valid_move(self, row: int, col: int) -> bool:
        """Validate move boundaries and occupancy."""
        if row < 0 or row > 2 or col < 0 or col > 2:
            return False
        return self.board[row][col] == " "

    def _update_game_status(self) -> None:
        """Update winner or draw state after a move."""
        winner = self._check_winner()
        if winner:
            self.winner = winner
            self.is_draw = False
            return

        if self.move_count >= 9:
            self.is_draw = True

    def _check_winner(self) -> Optional[str]:
        """Check rows, columns, and diagonals for a winning line."""
        lines = []

        for row in range(3):
            lines.append(self.board[row])

        for col in range(3):
            lines.append([self.board[row][col] for row in range(3)])

        lines.append([self.board[0][0], self.board[1][1], self.board[2][2]])
        lines.append([self.board[0][2], self.board[1][1], self.board[2][0]])

        for line in lines:
            if line[0] != " " and line[0] == line[1] == line[2]:
                return line[0]
        return None

    def is_game_over(self) -> bool:
        """Return True when the game has ended."""
        return self.winner is not None or self.is_draw

    def render_board(self) -> str:
        """Return a plain-text board for CLI display."""
        rows = []
        for row in self.board:
            rows.append(f" {row[0]} | {row[1]} | {row[2]} ")
        return "\n---+---+---\n".join(rows)

    def get_status_message(self) -> str:
        """Return user-friendly status message."""
        if self.winner:
            return f"Player {self.winner} wins!"
        if self.is_draw:
            return "It's a draw!"
        return f"Player {self.current_player}'s turn."


def parse_position(raw: str) -> Optional[Position]:
    """Parse user input of the form 'row,col' or 'row col'."""
    cleaned = raw.strip().replace(",", " ")
    parts = [p for p in cleaned.split(" ") if p]
    if len(parts) != 2:
        return None
    try:
        row = int(parts[0]) - 1
        col = int(parts[1]) - 1
    except ValueError:
        return None
    if row not in (0, 1, 2) or col not in (0, 1, 2):
        return None
    return row, col


def run_cli_game() -> None:
    """Interactive command-line game loop."""
    game = TicTacToe()
    print("Welcome to Tic-Tac-Toe")
    print("Enter moves as row,col using values 1 to 3.")
    print("Type 'quit' to exit.\n")

    while True:
        print(game.render_board())
        print(game.get_status_message())

        if game.is_game_over():
            play_again = input("Play again? (y/n): ").strip().lower()
            if play_again == "y":
                game.reset()
                print()
                continue
            print("Goodbye!")
            break

        raw = input("Your move: ").strip()
        if raw.lower() == "quit":
            print("Goodbye!")
            break

        position = parse_position(raw)
        if position is None:
            print("Invalid input. Use row,col with values from 1 to 3.\n")
            continue

        success = game.make_move(*position)
        if not success:
            print("That cell is already occupied. Try another move.\n")
            continue

        print()


if __name__ == "__main__":
    run_cli_game()
