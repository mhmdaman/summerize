# 🦆 GRUMPYDUCK- SUMMERIZER

An AI-powered YouTube video study notes generator. Paste any YouTube URL and get structured, exam-ready study notes — complete with key terms, examples, memory tricks, and practice questions.

## 🚀 Live Demo
[Coming soon]

## 📸 Preview
<!-- Add a screenshot here -->

## ✨ Features
- 📝 Converts YouTube videos into structured study notes
- 🔑 Highlights key terms, definitions, and formulas
- 💡 Adds examples, analogies, and memory tricks
- ❓ Generates exam-style questions per section
- 📋 Practice Q&A tab for revision
- ⚡ Quick revision summary
- 🖨️ Download notes as PDF
- 🎨 Doodle-style UI

## 🛠️ Tech Stack
- **Backend** — Python, FastAPI, uvicorn
- **AI** — OpenRouter API (DeepSeek)
- **Transcript** — youtube-transcript-api
- **Frontend** — Vanilla HTML, CSS, JavaScript

## ⚙️ Setup

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/yt-summarizer.git
cd yt-summarizer
```

### 2. Backend
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp ../.env.example .env
# Add your OpenRouter API key to .env
uvicorn main:app --reload
```

### 3. Frontend
```bash
cd frontend
python -m http.server 3000
# Open http://localhost:3000
```

## 🔑 Environment Variables
Create a `.env` file inside the `backend` folder:
```
OPENROUTER_API_KEY=your_key_here
```
Get your free API key at [openrouter.ai](https://openrouter.ai)

## 📁 Project Structure
```
yt-summarizer/
├── backend/
│   ├── main.py          # FastAPI app
│   ├── summarizer.py    # Transcript fetcher
│   └── requirements.txt
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── script.js
├── .env.example
├── .gitignore
└── README.md
```

## 🙌 Made by
Muhammed Aman — B.Tech CSE (Cyber Security), MITS Kochi

---
> "Why watch a lecture twice when GRUMPYDUCK can summarize it once?" 🦆
