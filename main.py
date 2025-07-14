import chess
import chess.pgn

# --- IMPORT YOUR BOTS HERE ---
from dumbot import random_bot_move
from alpha_beta import alpha_beta_bot_move
from monte_carlo import monte_carlo_bot_move
# Assign which function is the engine for each side
# Use None for human player
bot_white = alpha_beta_bot_move     
bot_black = None                

def get_move_from(engine, board):
    """Get move either from bot engine or human input."""
    if engine is None:
        # Human move
        while True:
            user_input = input("Your move: ").strip()
            if user_input.lower() in ["quit", "exit"]:
                return None
            try:
                move = board.parse_san(user_input)
                if move in board.legal_moves:
                    return move
                print("Illegal move.")
            except ValueError:
                print("Invalid move, try again.")
    else:
        # Bot move
        return engine(board)

def main():
    board = chess.Board()
    game = chess.pgn.Game()
    node = game

    print("Welcome to ChessBot!\n")

    while not board.is_game_over():
        print(board)
        print(f"\nFEN: {board.fen()}")
        print(f"Turn: {'White' if board.turn else 'Black'}")
        engine = bot_white if board.turn else bot_black

        move = get_move_from(engine, board)
        if move is None:
            print("Game exited early.")
            return

        board.push(move)
        node = node.add_variation(move)

    print(board)
    result = board.result()
    print(f"\nGame Over! Result: {result}")
    game.headers["Result"] = result
    print("\nPGN:")
    print(game)

if __name__ == "__main__":
    main()
