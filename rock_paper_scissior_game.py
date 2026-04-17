"""
Rock Paper Scissior Game (Console Version)

This script is intentionally longer than 100 lines and includes:
- Input validation
- Score tracking
- Best-of match mode
- Match history
- Optional replay loop
"""

from __future__ import annotations

import random
import time
from dataclasses import dataclass, field
from typing import Dict, List, Tuple


VALID_CHOICES: Tuple[str, str, str] = ("rock", "paper", "scissior")
SHORTCUTS: Dict[str, str] = {"r": "rock", "p": "paper", "s": "scissior"}


@dataclass
class RoundResult:
    round_number: int
    player_choice: str
    computer_choice: str
    winner: str  # "player", "computer", or "draw"


@dataclass
class GameState:
    player_name: str
    player_score: int = 0
    computer_score: int = 0
    draws: int = 0
    rounds_played: int = 0
    history: List[RoundResult] = field(default_factory=list)

    def add_round(self, player_choice: str, computer_choice: str, winner: str) -> None:
        self.rounds_played += 1
        if winner == "player":
            self.player_score += 1
        elif winner == "computer":
            self.computer_score += 1
        else:
            self.draws += 1
        self.history.append(
            RoundResult(
                round_number=self.rounds_played,
                player_choice=player_choice,
                computer_choice=computer_choice,
                winner=winner,
            )
        )


def normalize_choice(raw_choice: str) -> str:
    cleaned = raw_choice.strip().lower()
    if cleaned in SHORTCUTS:
        return SHORTCUTS[cleaned]
    return cleaned


def get_player_choice() -> str:
    while True:
        user_input = input("Choose rock, paper, or scissior (r/p/s): ")
        choice = normalize_choice(user_input)
        if choice in VALID_CHOICES:
            return choice
        print("Invalid input. Please enter rock, paper, scissior, or r/p/s.")


def get_computer_choice() -> str:
    return random.choice(VALID_CHOICES)


def decide_winner(player_choice: str, computer_choice: str) -> str:
    if player_choice == computer_choice:
        return "draw"

    win_map = {
        "rock": "scissior",
        "paper": "rock",
        "scissior": "paper",
    }
    if win_map[player_choice] == computer_choice:
        return "player"
    return "computer"


def print_round_result(state: GameState, last_round: RoundResult) -> None:
    print("\n--- Round Result ---")
    print(f"Round: {last_round.round_number}")
    print(f"{state.player_name} chose: {last_round.player_choice}")
    print(f"Computer chose: {last_round.computer_choice}")

    if last_round.winner == "player":
        print(f"Winner: {state.player_name}")
    elif last_round.winner == "computer":
        print("Winner: Computer")
    else:
        print("Round is a draw.")

    print("\nCurrent Score:")
    print(f"{state.player_name}: {state.player_score}")
    print(f"Computer: {state.computer_score}")
    print(f"Draws: {state.draws}")
    print("---------------------\n")


def print_match_summary(state: GameState) -> None:
    print("\n========== MATCH SUMMARY ==========")
    print(f"Player: {state.player_name}")
    print(f"Rounds Played: {state.rounds_played}")
    print(f"Final Score -> {state.player_name}: {state.player_score}, Computer: {state.computer_score}, Draws: {state.draws}")
    print("-----------------------------------")
    for item in state.history:
        if item.winner == "player":
            label = state.player_name
        elif item.winner == "computer":
            label = "Computer"
        else:
            label = "Draw"
        print(
            f"Round {item.round_number:02d}: "
            f"{state.player_name}={item.player_choice} | Computer={item.computer_choice} | Winner={label}"
        )
    print("===================================\n")


def ask_best_of() -> int:
    while True:
        raw = input("Play best of how many rounds? (odd number, e.g. 3/5/7): ").strip()
        if not raw.isdigit():
            print("Please enter a valid positive odd number.")
            continue
        value = int(raw)
        if value <= 0:
            print("Number should be greater than zero.")
            continue
        if value % 2 == 0:
            print("Please enter an odd number so there can be a clear winner.")
            continue
        return value


def has_match_winner(state: GameState, best_of: int) -> bool:
    target = (best_of // 2) + 1
    return state.player_score >= target or state.computer_score >= target


def play_match() -> None:
    print("Welcome to Rock Paper Scissior!")
    print("Tip: You can type full words or shortcuts r/p/s.\n")

    player_name = input("Enter your name: ").strip() or "Player"
    best_of = ask_best_of()
    state = GameState(player_name=player_name)

    print(f"\nStarting best-of-{best_of} match...")
    time.sleep(0.6)

    while not has_match_winner(state, best_of):
        player_choice = get_player_choice()
        computer_choice = get_computer_choice()
        winner = decide_winner(player_choice, computer_choice)
        state.add_round(player_choice, computer_choice, winner)

        print("Computer is choosing", end="", flush=True)
        for _ in range(3):
            time.sleep(0.25)
            print(".", end="", flush=True)
        print()

        print_round_result(state, state.history[-1])

    print_match_summary(state)
    if state.player_score > state.computer_score:
        print(f"Congratulations {state.player_name}, you won the match!\n")
    else:
        print("Computer won the match. Better luck next time!\n")


def ask_replay() -> bool:
    while True:
        raw = input("Do you want to play again? (y/n): ").strip().lower()
        if raw in {"y", "yes"}:
            return True
        if raw in {"n", "no"}:
            return False
        print("Please enter y or n.")


def main() -> None:
    random.seed()
    print("=" * 42)
    print("      ROCK PAPER SCISSIOR - PYTHON GAME")
    print("=" * 42)

    while True:
        play_match()
        if not ask_replay():
            print("\nThanks for playing. Bye!")
            break
        print("\nRestarting a new match...\n")
        time.sleep(0.6)


if __name__ == "__main__":
    main()
