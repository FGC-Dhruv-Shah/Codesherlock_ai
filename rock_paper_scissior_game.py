"""Simple one-try Rock Paper Scissior game."""

import random


VALID_CHOICES = ("rock", "paper", "scissior")
SHORTCUTS = {"r": "rock", "p": "paper", "s": "scissior"}


def normalize_choice(raw_choice: str) -> str:
    """Convert user input to a normalized game choice."""
    choice = raw_choice.strip().lower()
    if choice in SHORTCUTS:
        return SHORTCUTS[choice]
    return choice


def decide_winner(player_choice: str, computer_choice: str) -> str:
    """Return 'player', 'computer', or 'draw'."""
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


def main() -> None:
    print("Rock Paper Scissior (Single Try)")
    print("Enter one choice only: rock, paper, scissior (or r/p/s)")

    raw_input_value = input("Your choice: ")
    player_choice = normalize_choice(raw_input_value)

    if player_choice not in VALID_CHOICES:
        print("Invalid input. Game ended (single try only).")
        return

    computer_choice = random.choice(VALID_CHOICES)
    winner = decide_winner(player_choice, computer_choice)

    print(f"\nYou chose: {player_choice}")
    print(f"Computer chose: {computer_choice}")

    if winner == "draw":
        print("Result: Draw.")
    elif winner == "player":
        print("Result: You win!")
    else:
        print("Result: Computer wins!")


if __name__ == "__main__":
    main()
