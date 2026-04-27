"""Streamlit UI for tic_tac_toe.py game logic."""

import streamlit as st

from tic_tac_toe import TicTacToe


st.set_page_config(page_title="Tic-Tac-Toe", page_icon="🎮", layout="centered")
st.title("🎮 Tic-Tac-Toe")
st.caption("Built with Python + Streamlit")


def init_game() -> None:
    if "game" not in st.session_state:
        st.session_state.game = TicTacToe()


def reset_game() -> None:
    st.session_state.game = TicTacToe()


def board_to_markdown(board: list[list[str]]) -> str:
    """Return a simple markdown representation of board state."""
    rows = []
    for row in board:
        visible = [cell if cell != " " else "·" for cell in row]
        rows.append(" | ".join(visible))
    return "\n".join(rows)


def get_button_label(cell: str) -> str:
    """Convert empty cells to a visible placeholder."""
    return cell if cell != " " else " "


def status_banner(game: TicTacToe) -> None:
    if game.winner:
        st.success(f"Player {game.winner} wins! 🎉")
    elif game.is_draw:
        st.info("It's a draw! 🤝")
    else:
        st.warning(f"Player {game.current_player}'s turn")


def render_board(game: TicTacToe) -> None:
    """Draw interactive 3x3 grid of buttons."""
    for row in range(3):
        cols = st.columns(3, gap="small")
        for col in range(3):
            cell = game.board[row][col]
            disabled = cell != " " or game.is_game_over()
            with cols[col]:
                if st.button(
                    get_button_label(cell),
                    key=f"cell_{row}_{col}",
                    use_container_width=True,
                    disabled=disabled,
                ):
                    game.make_move(row, col)
                    st.rerun()


def render_controls(game: TicTacToe) -> None:
    left, right = st.columns([1, 1])
    with left:
        if st.button("Reset Game", use_container_width=True):
            reset_game()
            st.rerun()
    with right:
        st.metric("Moves Played", game.move_count)


def render_sidebar(game: TicTacToe) -> None:
    with st.sidebar:
        st.header("Game Info")
        st.write(f"Current Player: `{game.current_player}`")
        st.write(f"Winner: `{game.winner if game.winner else 'None'}`")
        st.write(f"Is Draw: `{game.is_draw}`")
        st.write(f"Available Moves: `{len(game.get_available_moves())}`")

        st.divider()
        st.subheader("Board Snapshot")
        st.code(board_to_markdown(game.board))
        st.caption("Use Reset Game to start over.")


def main() -> None:
    init_game()
    game: TicTacToe = st.session_state.game

    status_banner(game)
    st.divider()
    render_board(game)
    st.divider()
    render_controls(game)
    render_sidebar(game)


if __name__ == "__main__":
    main()
