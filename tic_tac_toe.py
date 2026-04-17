"""Tic-tac-toe: TicTacToe class and CLI. Moves: row,col (1–3); type quit to exit."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Tuple

Position = Tuple[int, int]


@dataclass
class TicTacToe:
    board: List[List[str]] = field(default_factory=lambda: [[" "] * 3 for _ in range(3)])
    current_player: str = "X"
    winner: Optional[str] = None
    is_draw: bool = False
    move_count: int = 0

    def reset(self) -> None:
        self.board = [[" "] * 3 for _ in range(3)]
        self.current_player, self.winner, self.is_draw, self.move_count = "X", None, False, 0

    def get_available_moves(self) -> List[Position]:
        return [(r, c) for r in range(3) for c in range(3) if self.board[r][c] == " "]

    def make_move(self, row: int, col: int) -> bool:
        if not (0 <= row < 3 and 0 <= col < 3 and self.board[row][col] == " "):
            return False
        self.board[row][col] = self.current_player
        self.move_count += 1
        w = self._check_winner()
        if w:
            self.winner, self.is_draw = w, False
        elif self.move_count >= 9:
            self.is_draw = True
        elif not self.is_game_over():
            self.current_player = "O" if self.current_player == "X" else "X"
        return True

    def _check_winner(self) -> Optional[str]:
        b = self.board
        lines = [b[r] for r in range(3)] + [[b[r][c] for r in range(3)] for c in range(3)]
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
    parts = [p for p in raw.strip().replace(",", " ").split() if p]
    if len(parts) != 2:
        return None
    try:
        row, col = int(parts[0]) - 1, int(parts[1]) - 1
    except ValueError:
        return None
    return (row, col) if 0 <= row < 3 and 0 <= col < 3 else None


def run_cli_game() -> None:
    game = TicTacToe()
    print("Welcome to Tic-Tac-Toe\nEnter moves as row,col (1–3). Type quit to exit.\n")
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
