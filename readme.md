# Summerizer

AI-powered YouTube video summarizer built with FastAPI + Claude API.

## Setup

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp ../.env.example .env       # add your Anthropic API key
uvicorn main:app --reload
```

### Frontend
Open `frontend/index.html` in your browser or serve with:
```bash
cd frontend
python -m http.server 3000
```

## Tech Stack
- FastAPI (Python backend)
- Deepseek API (summarization)
- youtube-transcript-api (real transcripts)
- Vanilla JS frontend
