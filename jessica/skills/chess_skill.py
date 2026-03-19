"""
Chess skill: Play chess with Jessica using algebraic notation.
Maintains game state and uses basic AI for moves.
"""
import os
import json
from pathlib import Path
import chess
import chess.engine
import random

GAMES_DIR = Path(__file__).resolve().parent.parent / "data" / "chess_games"


def can_handle(intent):
    i = intent.get("intent", "")
    text = (intent.get("text", "") or "").lower()
    
    return (i == "play_chess" or 
            "play chess" in text or 
            "chess move" in text or
            text.startswith("move ") or
            text.startswith("e4") or text.startswith("d4") or  # Common openings
            "resign" in text and "chess" in text or
            "show board" in text)


def load_game(user="default"):
    """Load current game state or create new."""
    GAMES_DIR.mkdir(parents=True, exist_ok=True)
    game_file = GAMES_DIR / f"{user}_current.json"
    
    if game_file.exists():
        try:
            data = json.load(open(game_file, "r"))
            board = chess.Board(data.get("fen"))
            return board, data.get("moves", [])
        except Exception:
            pass
    
    return chess.Board(), []


def save_game(board: chess.Board, moves: list, user="default"):
    """Persist game state."""
    GAMES_DIR.mkdir(parents=True, exist_ok=True)
    game_file = GAMES_DIR / f"{user}_current.json"
    
    data = {
        "fen": board.fen(),
        "moves": moves,
        "pgn": board_to_pgn(board, moves)
    }
    
    with open(game_file, "w") as f:
        json.dump(data, f, indent=2)


def board_to_pgn(board: chess.Board, moves: list) -> str:
    """Convert move history to PGN notation."""
    pgn_moves = []
    for i, move in enumerate(moves):
        if i % 2 == 0:
            pgn_moves.append(f"{i//2 + 1}. {move}")
        else:
            pgn_moves[-1] += f" {move}"
    return " ".join(pgn_moves)


def get_ai_move(board: chess.Board) -> chess.Move:
    """Simple AI move selection (random legal move with basic heuristics)."""
    legal_moves = list(board.legal_moves)
    
    if not legal_moves:
        return None
    
    # Prioritize captures
    captures = [m for m in legal_moves if board.is_capture(m)]
    if captures and random.random() < 0.7:
        return random.choice(captures)
    
    # Prioritize center control early game
    if board.fullmove_number < 10:
        center_squares = [chess.E4, chess.D4, chess.E5, chess.D5]
        center_moves = [m for m in legal_moves if m.to_square in center_squares]
        if center_moves and random.random() < 0.6:
            return random.choice(center_moves)
    
    return random.choice(legal_moves)


def format_board(board: chess.Board) -> str:
    """ASCII board representation."""
    return str(board)


def run(intent, context, relevant, manager):
    text = (intent.get("text", "") or "").lower().strip()
    user = "default"
    
    # New game
    if "new game" in text or "start chess" in text:
        board = chess.Board()
        moves = []
        save_game(board, moves, user)
        return {
            "reply": "New chess game started! You play White. Make your move (e.g., 'e4', 'Nf3').",
            "board": format_board(board)
        }
    
    # Show board
    if "show board" in text or "show game" in text:
        board, moves = load_game(user)
        status = ""
        if board.is_checkmate():
            status = "Checkmate!"
        elif board.is_check():
            status = "Check!"
        elif board.is_stalemate():
            status = "Stalemate!"
        
        return {
            "reply": f"Current board position. {status}\nYour turn!" if not board.turn == chess.BLACK else f"Current board. {status}\nMy turn.",
            "board": format_board(board),
            "moves": " ".join(moves[-10:])
        }
    
    # Resign
    if "resign" in text:
        board, moves = load_game(user)
        return {
            "reply": "You resigned. Good game! Say 'new game' to play again.",
            "board": format_board(board)
        }
    
    # Parse move
    board, moves = load_game(user)
    
    # Extract potential move notation
    words = text.split()
    move_str = None
    for word in words:
        # Try to parse as chess move
        if len(word) >= 2 and any(c.isdigit() for c in word):
            move_str = word
            break
    
    if not move_str:
        # Check if entire message is a move
        move_str = text.replace("move ", "").replace("chess ", "").strip()
    
    if not move_str or len(move_str) < 2:
        return {
            "reply": "Please specify a move in algebraic notation (e.g., 'e4', 'Nf3', 'Qxe5'). Say 'show board' to see the current position.",
            "board": format_board(board)
        }
    
    # Validate and apply user move
    try:
        user_move = board.parse_san(move_str)
        if user_move not in board.legal_moves:
            return {
                "reply": f"Illegal move: {move_str}. Try again.",
                "board": format_board(board)
            }
        
        board.push(user_move)
        moves.append(board.san(user_move))
        
        # Check game over after user move
        if board.is_checkmate():
            save_game(board, moves, user)
            return {
                "reply": f"You played {move_str}. Checkmate! You win! 🎉",
                "board": format_board(board)
            }
        elif board.is_stalemate():
            save_game(board, moves, user)
            return {
                "reply": f"You played {move_str}. Stalemate - it's a draw.",
                "board": format_board(board)
            }
        
        status = " Check!" if board.is_check() else ""
        
        # AI move
        ai_move = get_ai_move(board)
        if not ai_move:
            save_game(board, moves, user)
            return {
                "reply": f"You played {move_str}.{status} I have no legal moves!",
                "board": format_board(board)
            }
        
        board.push(ai_move)
        moves.append(board.san(ai_move))
        save_game(board, moves, user)
        
        # Check game over after AI move
        if board.is_checkmate():
            return {
                "reply": f"You played {move_str}. I played {board.san(ai_move)}. Checkmate! I win.",
                "board": format_board(board)
            }
        elif board.is_stalemate():
            return {
                "reply": f"You played {move_str}. I played {board.san(ai_move)}. Stalemate - draw.",
                "board": format_board(board)
            }
        
        ai_status = " Check!" if board.is_check() else ""
        
        return {
            "reply": f"You played {move_str}.{status} I played {board.san(ai_move)}.{ai_status} Your move!",
            "board": format_board(board),
            "moves": " ".join(moves[-6:])
        }
        
    except ValueError as e:
        return {
            "reply": f"Invalid move notation: {move_str}. Use standard algebraic notation (e.g., e4, Nf3, Bxc6). Error: {e}",
            "board": format_board(board)
        }
