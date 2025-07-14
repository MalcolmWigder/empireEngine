from base_evaluation import evaluate
import chess
import math

def alpha_beta_search(board, depth, alpha, beta, maximizing_player):
    
    if depth == 0 or board.is_game_over():
        if board.is_checkmate():
            # If it's maximizing player's move and it's mate, that's bad for maximizing player
            # (because they have no legal moves)
            if board.turn == maximizing_player:
                return math.inf + depth, None
            else:
                return -math.inf - depth, None
        elif board.is_stalemate() or board.is_insufficient_material() or board.can_claim_draw():
            return 0, None
        return evaluate(board), None
    

    best_move = None
    if maximizing_player:
        max_eval = -math.inf
        for move in board.legal_moves:
            board.push(move)
            eval, _ = alpha_beta_search(board, depth - 1, alpha, beta, False)
            board.pop()
            if eval > max_eval:
                max_eval = eval
                best_move = move
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return max_eval, best_move
    else:
        min_eval = math.inf
        for move in board.legal_moves:
            board.push(move)
            eval, _ = alpha_beta_search(board, depth - 1, alpha, beta, True)
            board.pop()
            if eval < min_eval:
                min_eval = eval
                best_move = move
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval, best_move

def alpha_beta_bot_move(board, depth=3):
    """
    Returns the best move found using alpha-beta search to the given depth.
    Default depth=2 is fast; increase for more strength (but slower).
    """
    maximizing = board.turn == chess.WHITE

    _, best_move = alpha_beta_search(board, depth, -math.inf, math.inf, maximizing)
    # If no move found (shouldn't happen), fall back to random legal move
    if best_move is None:
        best_move = next(iter(board.legal_moves))
    return best_move