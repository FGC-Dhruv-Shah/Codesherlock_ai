"""Simple Tic Tac Toe game logic."""

from dataclasses import dataclass, field
from typing import List, Optional


WIN_LINES = [
    (0, 1, 2),
    (3, 4, 5),
    (6, 7, 8),
    (0, 3, 6),
    (1, 4, 7),
    (2, 5, 8),
    (0, 4, 8),
    (2, 4, 6),
]


@dataclass
class TicTacToe:
    board: List[str] = field(default_factory=lambda: [""] * 9)
    current_player: str = "X"
    winner: Optional[str] = None
    game_over: bool = False

    def reset(self) -> None:
        self.board = [""] * 9
        self.current_player = "X"
        self.winner = None
        self.game_over = False

    def available_moves(self) -> List[int]:
        return [idx for idx, cell in enumerate(self.board) if cell == ""]

    def make_move(self, index: int) -> bool:
        if self.game_over:
            return False
        if index < 0 or index > 8:
            return False
        if self.board[index] != "":
            return False

        self.board[index] = self.current_player
        self._update_status()

        if not self.game_over:
            self.current_player = "O" if self.current_player == "X" else "X"
        return True

    def status_message(self) -> str:
        if self.winner:
            return f"Player {self.winner} wins!"
        if self.is_draw():
            return "It's a draw!"
        return f"Player {self.current_player}'s turn"

    def _update_status(self) -> None:
        self.winner = self.check_winner()
        if self.winner or self.is_draw():
            self.game_over = True

    def check_winner(self) -> Optional[str]:
        for a, b, c in WIN_LINES:
            if self.board[a] and self.board[a] == self.board[b] == self.board[c]:
                return self.board[a]
        return None

    def is_draw(self) -> bool:
        return self.winner is None and all(cell != "" for cell in self.board)


if __name__ == "__main__":
    game = TicTacToe()
    print("Simple CLI Tic Tac Toe")
    print("Enter positions 1-9 to play. Ctrl+C to exit.\n")

    while not game.game_over:
        for row in range(3):
            vals = [game.board[row * 3 + col] or "." for col in range(3)]
            print(" ".join(vals))
        print(game.status_message())
        move = input("Move: ").strip()
        if not move.isdigit() or not game.make_move(int(move) - 1):
            print("Invalid move, try again.\n")
            continue
        print()

    for row in range(3):
        vals = [game.board[row * 3 + col] or "." for col in range(3)]
        print(" ".join(vals))
    print(game.status_message())
