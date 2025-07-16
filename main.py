import chess
import chess.pgn
board = chess.Board()
# --- IMPORT YOUR BOTS HERE ---
from evals.agressor_eval import evaluate as aggressive_evaluate
from evals.base_evaluation import evaluate as base_evaluate
from engines.alpha_beta import alpha_beta_bot_move

# aggressive:
bot_white = lambda b: alpha_beta_bot_move(b, depth=3, evaluate_func=aggressive_evaluate)

# regular:
bot_black = lambda b: alpha_beta_bot_move(b, depth=2, evaluate_func=base_evaluate)

            

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
