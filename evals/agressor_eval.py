import chess
from evals.base_evaluation import material_score, piece_activity, pawn_structure, king_attack, king_safety, mate_score

PIECE_VALUES = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 0,
}

CENTER_SQUARES = [chess.D4, chess.E4, chess.D5, chess.E5]

def aggression_score(board):
    score = 0
    for color in [chess.WHITE, chess.BLACK]:
        sign = 1 if color == chess.WHITE else -1
        enemy = not color
        king_sq = board.king(enemy)
        if king_sq is None:
            continue
        # 1. Bonus for delivering check
        if board.is_check() and board.turn == enemy:
            score += 40 * sign
        # 2. Bonus for attacking around the enemy king
        king_file = chess.square_file(king_sq)
        king_rank = chess.square_rank(king_sq)
        attack_squares = [
            chess.square(f, r)
            for f in range(max(0, king_file-1), min(7, king_file+1)+1)
            for r in range(max(0, king_rank-1), min(7, king_rank+1)+1)
            if chess.square(f, r) != king_sq
        ]
        num_attacked = sum(board.is_attacked_by(color, sq) for sq in attack_squares)
        score += 15 * num_attacked * sign
        # 3. Bonus for pieces near enemy king (especially queen/rook)
        for piece_type, dist_bonus in [(chess.QUEEN, 20), (chess.ROOK, 15), (chess.KNIGHT, 10), (chess.BISHOP, 5)]:
            for sq in board.pieces(piece_type, color):
                dist = max(abs(chess.square_file(sq)-king_file), abs(chess.square_rank(sq)-king_rank))
                if dist <= 2:
                    score += (dist_bonus - 5*dist) * sign
        # 4. Bonus for pawns advanced on king side (potential pawn storms)
        for sq in board.pieces(chess.PAWN, color):
            pawn_file = chess.square_file(sq)
            pawn_rank = chess.square_rank(sq)
            # On same file or next file as king, and advanced
            if abs(pawn_file - king_file) <= 1:
                if (color == chess.WHITE and pawn_rank >= 4) or (color == chess.BLACK and pawn_rank <= 3):
                    score += 50 * sign
        # 5. Penalty for being behind in development (few developed pieces)
        minor_pieces = len(board.pieces(chess.KNIGHT, color)) + len(board.pieces(chess.BISHOP, color))
        if minor_pieces < 4:
            score -= (4 - minor_pieces) * 5 * sign
        # 6. Slight bonus for being down material if actively attacking (the "Tal bonus")
        if board.is_check() or num_attacked >= 3:
            mat_score = sum(PIECE_VALUES[pt] * (len(board.pieces(pt, color)) - len(board.pieces(pt, enemy)))
                            for pt in PIECE_VALUES)
            if mat_score < 0:
                score += abs(mat_score) * 0.10 * sign  # up to 10% back if you’re attacking
    return score

def mate_score(board):
    if board.is_checkmate():
        return 10000 if board.turn == chess.BLACK else -10000
    return 0

# Use your own king_safety, piece_activity, pawn_structure here, or the ones from above

def evaluate_aggressive(board):
    # For aggression phase: focus on mate, aggression, but include basics
    return (
        0.6 * material_score(board)
        + 0.3 * aggression_score(board)
        + 0.5 * king_attack(board)
        + 0.3 * piece_activity(board)
        + 0.2 * pawn_structure(board)
        + mate_score(board)
    )

def evaluate_balanced(board):
    # Your usual evaluation, e.g. the sum of everything
    return (
        material_score(board)
        + king_safety(board)
        + piece_activity(board)
        + pawn_structure(board)
        + king_attack(board)
        + mate_score(board)
    )

def evaluate(board):
    """Switches between aggressive and balanced evaluation based on move number."""
    if board.fullmove_number < 25:
        return evaluate_aggressive(board)
    else:
        return evaluate_balanced(board)
