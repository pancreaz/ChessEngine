import uvicorn
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional
import chess

from ai_engine import PythonChessAI

app = FastAPI(
    title="Standalone Python Chess AI REST Microservice",
    description="High-performance FastAPI microservice for Chess AI position evaluation and move prediction.",
    version="1.0.0"
)

# Enable CORS for C# / Web / Game Clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ai_engine = PythonChessAI()


class MovePredictionRequest(BaseModel):
    fen: str = Field(
        default="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
        description="Board position in standard FEN notation"
    )
    difficulty: Optional[str] = Field(
        default="medium",
        description="AI difficulty: 'easy', 'medium', or 'hard'"
    )


class MovePredictionResponse(BaseModel):
    status: str
    fen: str
    best_move: Optional[str]
    from_square: Optional[str]
    to_square: Optional[str]
    promotion: Optional[str]
    evaluation: float
    depth_searched: int
    nodes_evaluated: int
    time_ms: int
    difficulty: str


class PositionEvalRequest(BaseModel):
    fen: str


@app.get("/")
def read_root():
    return {
        "service": "Standalone Python Chess AI Microservice",
        "status": "running",
        "docs_url": "http://127.0.0.1:8000/docs",
        "endpoints": {
            "health": "GET /health",
            "predict_move": "POST /api/v1/predict-move",
            "evaluate": "POST /api/v1/evaluate"
        }
    }


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "Chess-AI-Microservice", "version": "1.0.0"}


@app.post("/api/v1/predict-move", response_model=MovePredictionResponse)
def predict_move(request: MovePredictionRequest):
    try:
        # Validate FEN
        board = chess.Board(request.fen)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid FEN string: {str(e)}")

    if board.is_game_over():
        return MovePredictionResponse(
            status="game_over",
            fen=request.fen,
            best_move=None,
            from_square=None,
            to_square=None,
            promotion=None,
            evaluation=ai_engine.evaluate_board(board) / 100.0,
            depth_searched=0,
            nodes_evaluated=0,
            time_ms=0,
            difficulty=request.difficulty
        )

    result = ai_engine.get_best_move(request.fen, request.difficulty)

    return MovePredictionResponse(
        status="success",
        fen=request.fen,
        best_move=result["best_move"],
        from_square=result.get("from_square"),
        to_square=result.get("to_square"),
        promotion=result.get("promotion"),
        evaluation=result["evaluation"],
        depth_searched=result["depth_searched"],
        nodes_evaluated=result["nodes_evaluated"],
        time_ms=result["time_ms"],
        difficulty=result["difficulty"]
    )


@app.post("/api/v1/evaluate")
def evaluate_position(request: PositionEvalRequest):
    try:
        board = chess.Board(request.fen)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid FEN string: {str(e)}")

    eval_score = ai_engine.evaluate_board(board) / 100.0
    return {
        "fen": request.fen,
        "evaluation": eval_score,
        "is_check": board.is_check(),
        "is_checkmate": board.is_checkmate(),
        "is_stalemate": board.is_stalemate(),
        "turn": "white" if board.turn == chess.WHITE else "black"
    }


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
