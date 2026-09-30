# Python Chess AI Microservice (FastAPI REST API)

A standalone Python REST API microservice for Chess position evaluation and AI move prediction powered by **FastAPI**, **python-chess**, Minimax with Alpha-Beta Pruning, and Piece-Square Tables.

---

## 🚀 Quick Start

### 1. Run the FastAPI Microservice
In your terminal, navigate to `PythonEngine/` and run:
```bash
python main.py
```
* Or using Uvicorn directly:
```bash
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

### 2. Interactive API Documentation (Swagger UI)
Once running, open your web browser or Postman to:
- **Swagger UI Interactive Docs:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc Documentation:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 📡 REST API Endpoints

### 1. `GET /health`
Health check endpoint.
```json
{
  "status": "ok",
  "service": "Chess-AI-Microservice",
  "version": "1.0.0"
}
```

### 2. `POST /api/v1/predict-move`
Predicts the best move for a given FEN position and difficulty.

**Request Body:**
```json
{
  "fen": "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1",
  "difficulty": "medium"
}
```

**Response Body:**
```json
{
  "status": "success",
  "fen": "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1",
  "best_move": "e7e5",
  "from_square": "e7",
  "to_square": "e5",
  "promotion": null,
  "evaluation": 0.15,
  "depth_searched": 3,
  "nodes_evaluated": 420,
  "time_ms": 45,
  "difficulty": "medium"
}
```

### 3. `POST /api/v1/evaluate`
Evaluates a board position in centipawns.

**Request Body:**
```json
{
  "fen": "r1bqkbnr/pppp1ppp/2n5/1B2p3/4P3/5N2/PPPP1PPP/RNBQK2R b KQkq - 3 3"
}
```

**Response Body:**
```json
{
  "fen": "r1bqkbnr/pppp1ppp/2n5/1B2p3/4P3/5N2/PPPP1PPP/RNBQK2R b KQkq - 3 3",
  "evaluation": 0.35,
  "is_check": false,
  "is_checkmate": false,
  "is_stalemate": false,
  "turn": "black"
}
```
