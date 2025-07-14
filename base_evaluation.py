import chess

PIECE_VALUES = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 0,
}

CENTER_SQUARES = [chess.D4, chess.E4, chess.D5, chess.E5]

def material_score(board):
    score = 0
    for piece_type, value in PIECE_VALUES.items():
        score += value * (len(board.pieces(piece_type, chess.WHITE)) - len(board.pieces(piece_type, chess.BLACK)))
    return score

def king_safety(board):
    score = 0
    # Penalize king if it hasn't castled and it's not endgame
    for color in [chess.WHITE, chess.BLACK]:
        king_square = board.king(color)
        has_castled = (
            (king_square in [chess.G1, chess.C1] if color == chess.WHITE else king_square in [chess.G8, chess.C8])
        )
        # Endgame if both sides have <=1 minor/major piece
        endgame = sum(len(board.pieces(t, color)) for t in [chess.QUEEN, chess.ROOK, chess.BISHOP, chess.KNIGHT]) <= 2
        if not has_castled and not endgame:
            # Penalize being on original square and not castled
            if (color == chess.WHITE and king_square == chess.E1) or (color == chess.BLACK and king_square == chess.E8):
                score -= 50 if color == chess.WHITE else -50
        # Bonus for king castled
        if has_castled and not endgame:
            score += 30 if color == chess.WHITE else -30
        # Penalize king in center in late game
        if endgame and chess.square_file(king_square) in [3, 4] and chess.square_rank(king_square) in [3, 4]:
            score += 20 if color == chess.WHITE else -20
    return score

def piece_activity(board):
    score = 0
    # Developed pieces bonus, central control, rook on open file
    for color in [chess.WHITE, chess.BLACK]:
        sign = 1 if color == chess.WHITE else -1
        # Knights and bishops not on back rank
        for piece_type in [chess.KNIGHT, chess.BISHOP]:
            for sq in board.pieces(piece_type, color):
                if (color == chess.WHITE and chess.square_rank(sq) > 0) or (color == chess.BLACK and chess.square_rank(sq) < 7):
                    score += 10 * sign
        # Central control bonus
        for sq in CENTER_SQUARES:
            piece = board.piece_at(sq)
            if piece and piece.color == color:
                score += 10 * sign
        # Rooks on open file bonus
        for sq in board.pieces(chess.ROOK, color):
            file_idx = chess.square_file(sq)
            file_squares = [chess.square(file_idx, r) for r in range(8)]
            if not any(board.piece_at(sq2) and board.piece_at(sq2).piece_type == chess.PAWN for sq2 in file_squares):
                score += 15 * sign
    return score

def pawn_structure(board):
    score = 0
    for color in [chess.WHITE, chess.BLACK]:
        sign = 1 if color == chess.WHITE else -1
        pawns = board.pieces(chess.PAWN, color)
        files = [chess.square_file(sq) for sq in pawns]
        # Doubled pawns penalty
        for file in set(files):
            if files.count(file) > 1:
                score -= 15 * sign
        # Isolated pawns penalty
        for sq in pawns:
            file = chess.square_file(sq)
            neighbor_files = [file - 1, file + 1]
            has_neighbor = any(
                any(chess.square_file(p) == nf for p in pawns)
                for nf in neighbor_files if 0 <= nf < 8
            )
            if not has_neighbor:
                score -= 10 * sign
        # Passed pawns bonus
        for sq in pawns:
            file = chess.square_file(sq)
            rank = chess.square_rank(sq)
            is_passed = True
            for opp_sq in board.pieces(chess.PAWN, not color):
                opp_file = chess.square_file(opp_sq)
                opp_rank = chess.square_rank(opp_sq)
                if abs(opp_file - file) <= 1:
                    if (color == chess.WHITE and opp_rank > rank) or (color == chess.BLACK and opp_rank < rank):
                        is_passed = False
                        break
            if is_passed:
                score += 20 * sign
    return score

def evaluate(board):
    return (
        material_score(board)
        + king_safety(board)
        + piece_activity(board)
        + pawn_structure(board)
    )
