import random

def random_bot_move(board):
    """Return a random legal move (as a python-chess Move object)."""
    return random.choice(list(board.legal_moves))
