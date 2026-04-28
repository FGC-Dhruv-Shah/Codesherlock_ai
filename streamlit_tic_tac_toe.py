"""Streamlit UI for Tic Tac Toe."""

import streamlit as st

from tic_tac_toe import TicTacToe


st.set_page_config(page_title="Tic Tac Toe", page_icon="🎮", layout="centered")


def init_game() -> None:
    if "game" not in st.session_state:
        st.session_state.game = TicTacToe()


def restart_game() -> None:
    st.session_state.game.reset()


def tile_label(value: str, index: int) -> str:
    if value:
        return value
    return str(index + 1)


def render_header() -> None:
    st.title("🎮 Tic Tac Toe")
    st.caption("Simple 2-player game built with Streamlit")
    st.info(st.session_state.game.status_message())


def render_board() -> None:
    game = st.session_state.game
    for row in range(3):
        cols = st.columns(3)
        for col in range(3):
            idx = row * 3 + col
            with cols[col]:
                st.button(
                    tile_label(game.board[idx], idx),
                    key=f"cell-{idx}",
                    use_container_width=True,
                    disabled=game.game_over or game.board[idx] != "",
                    on_click=handle_move,
                    args=(idx,),
                )


def handle_move(index: int) -> None:
    game = st.session_state.game
    moved = game.make_move(index)
    if not moved:
        st.warning("That move is not allowed.")


def render_footer() -> None:
    left, right = st.columns([1, 1])
    with left:
        st.button("Restart Game", use_container_width=True, on_click=restart_game)
    with right:
        if st.session_state.game.game_over:
            st.success("Game over")
        else:
            st.write("Keep playing!")

    st.divider()
    st.markdown(
        """
        **How to play**
        - Player **X** starts first.
        - Click a square to place your mark.
        - First to make 3 in a row wins.
        """
    )


def main() -> None:
    init_game()
    render_header()
    render_board()
    render_footer()


if __name__ == "__main__":
    main()
