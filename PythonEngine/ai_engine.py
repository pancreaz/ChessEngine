import random
import time
import chess

# Piece-Square Tables (PST) in Centipawns (from White perspective, flip row for Black)
PAWN_TABLE = [
     0,  0,  0,  0,  0,  0,  0,  0,
    50, 50, 50, 50, 50, 50, 50, 50,
    10, 10, 20, 30, 30, 20, 10, 10,
     5,  5, 10, 25, 25, 10,  5,  5,
     0,  0,  0, 20, 20,  0,  0,  0,
     5, -5,-10,  0,  0,-10, -5,  5,
     5, 10, 10,-20,-20, 10, 10,  5,
     0,  0,  0,  0,  0,  0,  0,  0
]

KNIGHT_TABLE = [
   -50,-40,-30,-30,-30,-30,-40,-50,
   -40,-20,  0,  0,  0,  0,-20,-40,
   -30,  0, 10, 15, 15, 10,  0,-30,
   -30,  5, 15, 20, 20, 15,  5,-30,
   -30,  0, 15, 20, 20, 15,  0,-30,
   -30,  5, 10, 15, 15, 10,  5,-30,
   -40,-20,  0,  5,  5,  0,-20,-40,
   -50,-40,-30,-30,-30,-30,-40,-50
]

BISHOP_TABLE = [
   -20,-10,-10,-10,-10,-10,-10,-20,
   -10,  0,  0,  0,  0,  0,  0,-10,
   -10,  0,  5, 10, 10,  5,  0,-10,
   -10,  5,  5, 10, 10,  5,  5,-10,
   -10,  0, 10, 10, 10, 10,  0,-10,
   -10, 10, 10, 10, 10, 10, 10,-10,
   -10,  5,  0,  0,  0,  0,  5,-10,
   -20,-10,-10,-10,-10,-10,-10,-20
]

ROOK_TABLE = [
     0,  0,  0,  0,  0,  0,  0,  0,
     5, 10, 10, 10, 10, 10, 10,  5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
     0,  0,  0,  5,  5,  0,  0,  0
]

QUEEN_TABLE = [
   -20,-10,-10, -5, -5,-10,-10,-20,
   -10,  0,  0,  0,  0,  0,  0,-10,
   -10,  0,  5,  5,  5,  5,  0,-10,
    -5,  0,  5,  5,  5,  5,  0, -5,
     0,  0,  5,  5,  5,  5,  0, -5,
   -10,  5,  5,  5,  5,  5,  0,-10,
   -10,  0,  5,  0,  0,  0,  0,-10,
   -20,-10,-10, -5, -5,-10,-10,-20
]

KING_MIDDLEGAME_TABLE = [
   -30,-40,-40,-50,-50,-40,-40,-30,
   -30,-40,-40,-50,-50,-40,-40,-30,
   -30,-40,-40,-50,-50,-40,-40,-30,
   -30,-40,-40,-50,-50,-40,-40,-30,
   -20,-30,-30,-40,-40,-30,-30,-20,
   -10,-20,-20,-20,-20,-20,-20,-10,
    20, 20,  0,  0,  0,  0, 20, 20,
    20, 30, 10,  0,  0, 10, 30, 20
]

PIECE_VALUES = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 20000
}

class PythonChessAI:
    def __init__(self):
        self.nodes_evaluated = 0

    def evaluate_board(self, board: chess.Board) -> int:
        """Evaluates the board position in centipawns relative to White."""
        if board.is_checkmate():
            return -100000 if board.turn == chess.WHITE else 100000
        if board.is_stalemate() or board.is_insufficient_material() or board.is_fifty_moves():
            return 0

        score = 0

        for square, piece in board.piece_map().items():
            value = PIECE_VALUES[piece.piece_type]
            sq_idx = square if piece.color == chess.WHITE else chess.square_mirror(square)

            pst_score = 0
            if piece.piece_type == chess.PAWN:
                pst_score = PAWN_TABLE[sq_idx]
            elif piece.piece_type == chess.KNIGHT:
                pst_score = KNIGHT_TABLE[sq_idx]
            elif piece.piece_type == chess.BISHOP:
                pst_score = BISHOP_TABLE[sq_idx]
            elif piece.piece_type == chess.ROOK:
                pst_score = ROOK_TABLE[sq_idx]
            elif piece.piece_type == chess.QUEEN:
                pst_score = QUEEN_TABLE[sq_idx]
            elif piece.piece_type == chess.KING:
                pst_score = KING_MIDDLEGAME_TABLE[sq_idx]

            total_piece_score = value + pst_score
            if piece.color == chess.WHITE:
                score += total_piece_score
            else:
                score -= total_piece_score

        return score

    def order_moves(self, board: chess.Board, moves):
        """Move ordering heuristic: Captures first (MVV-LVA)."""
        def move_priority(move: chess.Move):
            score = 0
            if board.is_capture(move):
                victim = board.piece_at(move.to_square)
                attacker = board.piece_at(move.from_square)
                victim_val = PIECE_VALUES[victim.piece_type] if victim else 100
                attacker_val = PIECE_VALUES[attacker.piece_type] if attacker else 100
                score += 10000 + (victim_val * 10 - attacker_val)
            if move.promotion:
                score += 8000
            return score

        return sorted(moves, key=move_priority, reverse=True)

    def minimax(self, board: chess.Board, depth: int, alpha: int, beta: int, maximizing_player: bool) -> int:
        self.nodes_evaluated += 1

        if depth == 0 or board.is_game_over():
            return self.evaluate_board(board)

        legal_moves = self.order_moves(board, list(board.legal_moves))

        if maximizing_player:
            max_eval = -999999
            for move in legal_moves:
                board.push(move)
                eval_score = self.minimax(board, depth - 1, alpha, beta, False)
                board.pop()
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = 999999
            for move in legal_moves:
                board.push(move)
                eval_score = self.minimax(board, depth - 1, alpha, beta, True)
                board.pop()
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break
            return min_eval

    def get_best_move(self, fen: str, difficulty: str = "medium") -> dict:
        """Finds the best move for a given FEN position and difficulty."""
        board = chess.Board(fen)
        self.nodes_evaluated = 0

        legal_moves = list(board.legal_moves)
        if not legal_moves:
            return {"best_move": None, "evaluation": 0, "nodes_evaluated": 0, "time_ms": 0}

        # Set search depth based on difficulty
        difficulty = difficulty.lower()
        if difficulty == "easy":
            depth = 1
            # 25% chance to make random move for Easy mode
            if random.random() < 0.25:
                random_move = random.choice(legal_moves)
                return {
                    "best_move": random_move.uci(),
                    "evaluation": self.evaluate_board(board) / 100.0,
                    "depth_searched": 1,
                    "nodes_evaluated": 1,
                    "time_ms": 1,
                    "difficulty": "easy (random noise)"
                }
        elif difficulty == "hard":
            depth = 4
        else:
            depth = 3  # Medium default

        start_time = time.time()
        best_move = None
        is_max = (board.turn == chess.WHITE)
        best_eval = -999999 if is_max else 999999
        alpha = -999999
        beta = 999999

        ordered_moves = self.order_moves(board, legal_moves)

        for move in ordered_moves:
            board.push(move)
            eval_score = self.minimax(board, depth - 1, alpha, beta, not is_max)
            board.pop()

            if is_max:
                if eval_score > best_eval:
                    best_eval = eval_score
                    best_move = move
                alpha = max(alpha, eval_score)
            else:
                if eval_score < best_eval:
                    best_eval = eval_score
                    best_move = move
                beta = min(beta, eval_score)

        elapsed_ms = int((time.time() - start_time) * 1000)

        if best_move is None:
            best_move = random.choice(legal_moves)

        return {
            "best_move": best_move.uci(),
            "from_square": chess.square_name(best_move.from_square),
            "to_square": chess.square_name(best_move.to_square),
            "promotion": chess.piece_symbol(best_move.promotion).upper() if best_move.promotion else None,
            "evaluation": round(best_eval / 100.0, 2), # Convert centipawns to pawns
            "depth_searched": depth,
            "nodes_evaluated": self.nodes_evaluated,
            "time_ms": elapsed_ms,
            "difficulty": difficulty
        }
