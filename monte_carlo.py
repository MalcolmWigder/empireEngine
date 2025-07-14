import random
from base_evaluation import evaluate
import chess

def semi_random_move(board, top_n=3):
    moves = list(board.legal_moves)
    move_scores = []
    for move in moves:
        board.push(move)
        score = evaluate(board)
        board.pop()
        move_scores.append((score, move))
    maximizing = board.turn == chess.WHITE
    move_scores.sort(reverse=maximizing, key=lambda x: x[0])
    candidates = [move for _, move in move_scores[:min(top_n, len(move_scores))]]
    return random.choice(candidates)

def random_playout(board, max_depth=16, top_n=3):
    board = board.copy()
    for _ in range(max_depth):
        if board.is_game_over():
            break
        move = semi_random_move(board, top_n)
        board.push(move)
    # Handle end of playout: mate/draw or evaluation
    if board.is_checkmate():
        return 99999 if board.turn == chess.BLACK else -99999
    if board.is_stalemate() or board.is_insufficient_material() or board.can_claim_draw():
        return 0
    return evaluate(board)

def monte_carlo_bot_move(board, playouts_per_move=15, playout_depth=16, top_n=3):
    legal_moves = list(board.legal_moves)
    move_scores = []
    for move in legal_moves:
        total = 0
        for _ in range(playouts_per_move):
            board.push(move)
            score = random_playout(board, playout_depth, top_n)
            board.pop()
            total += score
        avg_score = total / playouts_per_move
        move_scores.append((avg_score, move))
    maximizing = board.turn == chess.WHITE
    best = max if maximizing else min
    best_move = best(move_scores, key=lambda x: x[0])[1]
    return best_move
