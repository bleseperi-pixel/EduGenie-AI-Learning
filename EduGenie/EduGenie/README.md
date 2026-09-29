# EduGenie - Google Gemini Powered Learning Assistant

Ask questions, get simple explanations, generate quizzes, summarize passages and build learning paths.
Backend: **FastAPI**. Frontend: **HTML + CSS + JS**. AI: **Google Gemini** (Q&A, quiz, summary, learning path)
and **LaMini-Flan-T5-783M** running locally (concept explanations, with automatic Gemini fallback).

## Quick start (fastest way)

1. Unzip, then in VS Code: **File > Open Folder** > `EduGenie`.
2. **Windows:** double-click `setup.bat` (installs everything, opens `.env`). Paste your `GEMINI_API_KEY`, save.
   **macOS/Linux:** run `./setup.sh`, edit `.env`.
3. **Windows:** double-click `run.bat`. **macOS/Linux:** `./run.sh`. Your browser opens at http://127.0.0.1:8000.
   Or in VS Code press **F5** (select the `.venv` interpreter when prompted).

Setup uses the lightweight install (Gemini only). The detailed steps below cover the optional local model.

## Project structure

```
EduGenie/
├── main.py                 # FastAPI app + all API endpoints
├── gemini_client.py        # Shared Gemini helper (API key, model, errors)
├── qna.py                  # Question answering
├── explanation_module.py   # Concept explanation (local LaMini-Flan-T5, falls back to Gemini)
├── quiz_module.py          # 3 MCQs x 4 options, JSON parsing + validation
├── summary_module.py       # Summarization
├── learning_path.py        # Beginner -> advanced learning plans
├── templates/index.html    # Page
├── static/style.css        # Styling (responsive)
├── static/app.js           # Talks to the API, renders results and the interactive quiz
├── tests/test_api.py       # Offline tests (no API key needed)
├── smoke_test.py           # Live end-to-end check (needs a key + running server)
├── requirements.txt        # Full install (includes local model: torch, transformers)
├── requirements-lite.txt   # Lightweight install (Gemini only)
├── requirements-dev.txt    # Lite + pytest/httpx for tests
├── .env.example            # Copy to .env and add your key
└── .vscode/                # Debug config + settings
```

## 1. Prerequisites

- **Python 3.10+** (Windows: tick "Add Python to PATH" in the installer). Check: `python --version`
- **VS Code** with the **Python** extension
- A free **Gemini API key**: sign in at <https://aistudio.google.com/apikey> and click *Create API key*
- Disk/RAM for the local model (optional): ~3 GB download for the model plus ~2 GB for PyTorch

## 2. Set up in VS Code

1. **File > Open Folder...** and choose the `EduGenie` folder.
2. Open the terminal: **Terminal > New Terminal**.
3. Create and activate a virtual environment:

   **Windows (PowerShell)**
   ```powershell
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   ```
   If PowerShell blocks the script, run `Set-ExecutionPolicy -Scope Process Bypass` first, then activate again.

   **macOS / Linux**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
4. When VS Code asks to use the new environment, click **Yes**. (Or press `Ctrl+Shift+P` > *Python: Select Interpreter* > pick `.venv`.)
5. Install dependencies - choose ONE:
   ```bash
   pip install -r requirements.txt        # full: local explanation model + Gemini
   pip install -r requirements-lite.txt   # lightweight: Gemini only (recommended to start)
   ```
6. Add your API key: copy `.env.example` to `.env` and edit it.
   ```powershell
   copy .env.example .env      # Windows      (macOS/Linux: cp .env.example .env)
   ```
   ```
   GEMINI_API_KEY=paste_your_key_here
   ```
   If you used the **lite** install, also set `EXPLAIN_BACKEND=gemini` in `.env`.

## 3. Run

```bash
uvicorn main:app --reload
```
Open <http://127.0.0.1:8000> in your browser. Interactive API docs: <http://127.0.0.1:8000/docs>.
Stop the server with `Ctrl+C`.

Alternative: press **F5** in VS Code and choose **EduGenie (FastAPI + uvicorn)** to run with the debugger.

> **First "Explain" request with the local model** downloads ~3 GB and can take several minutes.
> Later requests are fast. If the local model can't load, EduGenie automatically uses Gemini instead,
> and the result says which engine answered.

## 4. Test

**A. Automated tests (offline, no key needed)**
```bash
pip install -r requirements-dev.txt
pytest
```
Expected: `15 passed`. You can also use VS Code's **Testing** panel (beaker icon).

**B. Live check against real Gemini** (server running in one terminal, then in a second terminal):
```bash
python smoke_test.py
```
Expected: six `PASS` lines (Health, Q&A, Explain, Quiz, Summarize, Learning path).

**C. Manual check in the browser** (matches the project's functional test list)

| Task | Try | You should see |
|---|---|---|
| Ask a question | `Which is the largest ocean?` | Pacific Ocean with a short explanation |
| Explain a concept | `Photosynthesis` | A simple explanation and the engine used |
| Generate a quiz | `The Pythagoras Theorem` | 3 questions, 4 options each; wrong picks reveal the right answer; score at the end |
| Summarize text | Paste a long paragraph | A short summary plus key points |
| Learning path | `SQL` | Beginner / Intermediate / Advanced plan with time estimates and resources |

**D. Call the API directly** (PowerShell: use `curl.exe`, or the `/docs` page)
```bash
curl -X POST http://127.0.0.1:8000/qa -H "Content-Type: application/json" -d "{\"question\":\"Which is the largest ocean?\"}"
curl "http://127.0.0.1:8000/learn/recommendations?topic=SQL"
```

## API reference

| Method | Path | Body / query | Response |
|---|---|---|---|
| GET | `/` | - | Web UI |
| GET | `/health` | - | Status, model name, whether a key is configured |
| POST | `/qa` | `{"question": "..."}` | `{"question", "answer"}` |
| POST | `/explain` | `{"topic": "..."}` | `{"topic", "explanation", "engine"}` |
| POST | `/quiz` | `{"text": "topic or passage"}` | `{"quiz": [{"question", "options":[4], "answer"}]}` |
| POST | `/summarize` | `{"text": "..."}` | `{"summary"}` |
| GET | `/learn/recommendations` | `?topic=SQL` | `{"topic", "recommendation"}` |

Errors always look like `{"error": "message"}` with a suitable HTTP status (400 empty input, 413 too long, 422 bad request, 502 Gemini failure, 503 missing API key).

## Troubleshooting

| Problem | Fix |
|---|---|
| `GEMINI_API_KEY is not set` | Create `.env` (copy `.env.example`), add your key, restart `uvicorn` |
| `Gemini request failed: ... 404 ... model` | Set `GEMINI_MODEL` in `.env` to a current model name (default `gemini-2.5-flash`; see <https://ai.google.dev/gemini-api/docs/models>) |
| `429` / quota errors | Free-tier rate limit; wait a minute or use a lighter model |
| `uvicorn` not recognized | Activate the venv (`.venv\Scripts\Activate.ps1`) and re-run `pip install` |
| Explain is slow or fails to load | Set `EXPLAIN_BACKEND=gemini` in `.env` |
| Port 8000 busy | `uvicorn main:app --reload --port 8001` |
| Changed `.env` but nothing happens | Stop and restart the server |

Never commit `.env` (it is in `.gitignore`).
