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
    for color in [chess.WHITE, chess.BLACK]:
        king_square = board.king(color)
        has_castled = (king_square in [chess.G1, chess.C1] if color == chess.WHITE else king_square in [chess.G8, chess.C8])
        endgame = sum(len(board.pieces(t, color)) for t in [chess.QUEEN, chess.ROOK, chess.BISHOP, chess.KNIGHT]) <= 2
        # Penalize uncastled king
        if not has_castled and not endgame:
            if (color == chess.WHITE and king_square == chess.E1) or (color == chess.BLACK and king_square == chess.E8):
                score -= 50 if color == chess.WHITE else -50
        # Bonus for castled king
        if has_castled and not endgame:
            score += 30 if color == chess.WHITE else -30
        # Penalize king in center in endgame
        if endgame and chess.square_file(king_square) in [3, 4] and chess.square_rank(king_square) in [3, 4]:
            score += 20 if color == chess.WHITE else -20
    return score

def piece_activity(board):
    score = 0
    for color in [chess.WHITE, chess.BLACK]:
        sign = 1 if color == chess.WHITE else -1
        # Knights and bishops not on back rank
        for piece_type in [chess.KNIGHT, chess.BISHOP]:
            for sq in board.pieces(piece_type, color):
                if (color == chess.WHITE and chess.square_rank(sq) > 0) or (color == chess.BLACK and chess.square_rank(sq) < 7):
                    score += 10 * sign
        # Central control
        for sq in CENTER_SQUARES:
            piece = board.piece_at(sq)
            if piece and piece.color == color:
                score += 10 * sign
        # Rooks on open file
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
        for file in set(files):
            if files.count(file) > 1:
                score -= 15 * sign
        for sq in pawns:
            file = chess.square_file(sq)
            neighbor_files = [file - 1, file + 1]
            has_neighbor = any(
                any(chess.square_file(p) == nf for p in pawns)
                for nf in neighbor_files if 0 <= nf < 8
            )
            if not has_neighbor:
                score -= 10 * sign
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

def king_attack(board):
    score = 0
    # Reward if attacking squares around enemy king
    for color in [chess.WHITE, chess.BLACK]:
        sign = 1 if color == chess.WHITE else -1
        enemy = not color
        king_sq = board.king(enemy)
        if king_sq is None:
            continue
        king_file = chess.square_file(king_sq)
        king_rank = chess.square_rank(king_sq)
        # Squares around the king
        attack_squares = [
            chess.square(f, r)
            for f in range(max(0, king_file-1), min(7, king_file+1)+1)
            for r in range(max(0, king_rank-1), min(7, king_rank+1)+1)
            if chess.square(f, r) != king_sq
        ]
        # Count how many of these squares are attacked by our pieces
        num_attacked = sum(board.is_attacked_by(color, sq) for sq in attack_squares)
        score += 15 * num_attacked * sign

        # Bonus for pieces close to king (excluding pawns)
        for piece_type in [chess.QUEEN, chess.ROOK, chess.KNIGHT, chess.BISHOP]:
            for sq in board.pieces(piece_type, color):
                dist = max(abs(chess.square_file(sq)-king_file), abs(chess.square_rank(sq)-king_rank))
                if dist <= 2:
                    score += (12 - 2*dist) * sign  # closer pieces score more

        # Bonus if king is currently in check
        if board.is_check() and board.turn == enemy:
            score += 30 * sign  # moderate; tune as you wish
    return score

def mate_score(board):
    """Huge bonus/penalty for mate (in case search stops at mate)."""
    if board.is_checkmate():
        # The side to move is checkmated, so the previous player wins
        return 10000 if board.turn == chess.BLACK else -10000
    return 0

def evaluate(board):
    return (
        material_score(board)
        + king_safety(board)
        + piece_activity(board)
        + pawn_structure(board)
        + king_attack(board)
        + mate_score(board)
    )
