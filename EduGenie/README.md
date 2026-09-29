# EduGenie — Google Gemini Powered Learning Assistant

EduGenie is a FastAPI + HTML/CSS/JavaScript educational assistant based on the supplied project document.

## Features

- Q&A
- Beginner-friendly topic explanation
- 3-question MCQ quiz with 4 options
- Passage summarization
- Beginner-to-advanced learning path
- `/health` endpoint
- Responsive browser UI

## Architecture

```text
EduGenie/
├── main.py
├── config.py
├── gemini_client.py
├── qna.py
├── explanation_module.py
├── quiz_module.py
├── summary_module.py
├── learning_path.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
├── templates/
│   └── index.html
└── static/
    ├── style.css
    └── app.js
```

## Why the model setting is configurable

The supplied document names Gemini 1.5 Pro. That model choice is outdated for a new implementation. The application therefore uses an environment variable and defaults to a current Gemini model. Change `GEMINI_MODEL` in `.env` if your Google AI account exposes a different model.

The supplied document also specifies LaMini-Flan-T5-783M for local explanations. The implementation keeps that option behind `ENABLE_LOCAL_EXPLAINER=true`. The default is `false` so the project remains lightweight and does not require a large local model download.

## Windows VS Code setup

### 1. Open the project

Open the `EduGenie` folder in VS Code.

### 2. Create a virtual environment

Open the VS Code terminal:

```powershell
python -m venv .venv
.venv\Scripts\activate
```

If PowerShell blocks activation, run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.venv\Scripts\activate
```

### 3. Install packages

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure Gemini

Copy `.env.example` to `.env`:

```powershell
copy .env.example .env
```

Open `.env` and replace:

```text
GEMINI_API_KEY=PASTE_YOUR_GEMINI_API_KEY_HERE
```

with your Google Gemini API key.

Do not commit `.env` to Git.

### 5. Start the server

```powershell
uvicorn main:app --reload
```

Open:

```text
http://127.0.0.1:8000
```

## Test the backend

Open:

```text
http://127.0.0.1:8000/docs
```

Try:
- `GET /health`
- `POST /qa`
- `POST /explain`
- `POST /quiz`
- `POST /summarize`
- `POST /learn/recommendations`

Example JSON:

```json
{
  "text": "Explain photosynthesis in simple English."
}
```

## Test from the browser

1. Select `Ask a Question`.
2. Enter `Which is the largest ocean?`.
3. Click `Generate`.
4. Try `Explain a Topic`.
5. Try `Generate Quiz` with a short passage.
6. Try `Summarize` with a paragraph.
7. Try `Learning Path` with `SQL`.

## Optional local LaMini explainer

The supplied design specifies `MBZUAI/LaMini-Flan-T5-783M` for explanations.

1. Install the optional packages:

```powershell
pip install torch transformers
```

2. Edit `.env`:

```text
ENABLE_LOCAL_EXPLAINER=true
LOCAL_MODEL=MBZUAI/LaMini-Flan-T5-783M
```

The first local explanation can take longer because the model needs to be downloaded and loaded. If the local model fails, EduGenie automatically falls back to Gemini.

## Troubleshooting

### `GEMINI_API_KEY is missing`

Make sure `.env` exists in the project root and contains a valid key.

### `404 model not found`

Change `GEMINI_MODEL` in `.env` to a model available to your account. Restart Uvicorn after changing `.env`.

### Port 8000 is already in use

Run:

```powershell
uvicorn main:app --reload --port 8001
```

Use:

```text
http://127.0.0.1:8001
```

### Changes are not visible

Stop Uvicorn with `Ctrl+C`, restart it, and refresh the browser.

## Security

- Keep the Gemini API key only in `.env`.
- Never place the API key in `static/app.js`.
- Never commit `.env` to Git.
