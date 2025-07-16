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
        if king_square is None:
            continue  # should not happen, but just in case
        file = chess.square_file(king_square)
        rank = chess.square_rank(king_square)
        has_castled = (king_square in [chess.G1, chess.C1] if color == chess.WHITE else king_square in [chess.G8, chess.C8])
        on_home_rank = (rank == 0 if color == chess.WHITE else rank == 7)
        in_center = file in [3, 4]  # d/e files
        endgame = sum(len(board.pieces(t, color)) for t in [chess.QUEEN, chess.ROOK, chess.BISHOP, chess.KNIGHT]) <= 2

        # Strongly penalize king NOT castled and still on first rank but not in castling spot
        if not has_castled and on_home_rank and king_square not in ([chess.E1, chess.G1, chess.C1] if color == chess.WHITE else [chess.E8, chess.G8, chess.C8]) and not endgame:
            score -= 200 if color == chess.WHITE else -200

        # Moderate penalty for king off home rank before endgame (i.e. Kd2, Ke2, etc.)
        if not has_castled and not on_home_rank and not endgame:
            score -= 100 if color == chess.WHITE else -100

        # Small penalty for king still on e1/e8 and uncastled
        if not has_castled and (king_square == (chess.E1 if color == chess.WHITE else chess.E8)) and not endgame:
            score -= 60 if color == chess.WHITE else -60

        # Big bonus for castling before endgame
        if has_castled and not endgame:
            score += 100 if color == chess.WHITE else -100

        # Opposite-side castling Empire bonus
        white_king = board.king(chess.WHITE)
        black_king = board.king(chess.BLACK)
        if white_king in [chess.C1] and black_king in [chess.G8]:
            score += 200 if color == chess.WHITE else -200
        if white_king in [chess.G1] and black_king in [chess.C8]:
            score += 200 if color == chess.WHITE else -200

        # Encourage king centralization in endgame
        if endgame and in_center and (rank in [3, 4]):
            score += 40 if color == chess.WHITE else -40
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
    
    if board.is_checkmate():
        return 10000 if board.turn == chess.BLACK else -10000
    return 0

def evaluate(board):
    return (
        material_score(board)
        + king_safety(board)
        + piece_activity(board)
        + pawn_structure(board)
        + king_attack(board)
        
    )
