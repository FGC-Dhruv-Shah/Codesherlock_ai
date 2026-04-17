"""Simple one-try Rock Paper Scissior game.

This version stays beginner-friendly and still plays only one round.
The code is intentionally expanded with helper functions and clear prints
to keep it readable while meeting the requested file length.
"""

import random


VALID_CHOICES = ("rock", "paper", "scissior")
SHORTCUTS = {"r": "rock", "p": "paper", "s": "scissior"}


def print_divider() -> None:
    """Print a divider line for cleaner output."""
    print("-" * 50)


def print_title() -> None:
    """Print the game title and mode."""
    print_divider()
    print("ROCK PAPER SCISSIOR")
    print("Mode: Single Try (one round only)")
    print_divider()


def print_instructions() -> None:
    """Print user instructions."""
    print("Instructions:")
    print("1) Enter one choice only.")
    print("2) Valid full words: rock, paper, scissior")
    print("3) Valid shortcuts: r, p, s")
    print("4) Invalid input ends the game immediately.")
    print_divider()


def normalize_choice(raw_choice: str) -> str:
    """Convert user input to a normalized game choice."""
    choice = raw_choice.strip().lower()
    if choice in SHORTCUTS:
        return SHORTCUTS[choice]
    return choice


def is_valid_choice(choice: str) -> bool:
    """Check if normalized input is valid."""
    return choice in VALID_CHOICES


def get_player_choice_once() -> str:
    """Take one user input only and normalize it."""
    raw_value = input("Your choice: ")
    return normalize_choice(raw_value)


def get_computer_choice() -> str:
    """Pick one random choice for computer."""
    return random.choice(VALID_CHOICES)


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


def winner_message(winner: str) -> str:
    """Return a readable winner message."""
    if winner == "draw":
        return "Result: Draw."
    if winner == "player":
        return "Result: You win!"
    return "Result: Computer wins!"


def print_round_result(player_choice: str, computer_choice: str, winner: str) -> None:
    """Print final round result."""
    print_divider()
    print("Round Result")
    print_divider()
    print(f"You chose: {player_choice}")
    print(f"Computer chose: {computer_choice}")
    print(winner_message(winner))
    print_divider()


def print_invalid_input_message(user_choice: str) -> None:
    """Print invalid input feedback and end message."""
    print_divider()
    print(f"Invalid input: '{user_choice}'")
    print("Game ended (single try only).")
    print("Please run again and enter rock/paper/scissior or r/p/s.")
    print_divider()


def run_single_try_game() -> None:
    """Run one complete round only."""
    player_choice = get_player_choice_once()

    if not is_valid_choice(player_choice):
        print_invalid_input_message(player_choice)
        return

    computer_choice = get_computer_choice()
    winner = decide_winner(player_choice, computer_choice)
    print_round_result(player_choice, computer_choice, winner)


def main() -> None:
    """Main entry point."""
    print_title()
    print_instructions()
    run_single_try_game()


if __name__ == "__main__":
    main()
