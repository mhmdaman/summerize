from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import anthropic
import os
import json
from dotenv import load_dotenv
from summarizer import extract_video_id, fetch_video_meta, fetch_transcript

load_dotenv()

app = FastAPI(title="YouTube Summarizer API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

class SummarizeRequest(BaseModel):
    url: str
    detail: str = "standard"  # brief | standard | deep

DETAIL_PROMPTS = {
    "brief": "3-4 key points and 3-4 timestamp markers",
    "standard": "5-6 key points and 5-6 timestamp markers",
    "deep": "7-8 key points, 7-8 timestamps, and detailed notes per timestamp"
}

SYSTEM_PROMPT = """You are an expert YouTube video analyst. You will be given a video title, channel name, and optionally the real transcript with timestamps.

Respond ONLY with a valid JSON object in this exact format:
{
  "tldr": "2-3 sentence overall summary",
  "keyPoints": [
    {"num": 1, "point": "Key insight or takeaway"}
  ],
  "timestamps": [
    {"time": "0:00", "topic": "Topic name", "note": "Brief description"}
  ],
  "tags": ["tag1", "tag2", "tag3", "tag4", "tag5"],
  "sentiment": "Educational / Entertaining / Inspirational / Technical",
  "difficulty": "Beginner / Intermediate / Advanced"
}

No markdown, no backticks. Pure JSON only."""

@app.post("/summarize")
async def summarize(req: SummarizeRequest):
    video_id = extract_video_id(req.url)
    if not video_id:
        raise HTTPException(status_code=400, detail="Invalid YouTube URL")

    meta = await fetch_video_meta(video_id)
    transcript = fetch_transcript(video_id)

    transcript_section = ""
    if transcript:
        # Limit transcript to ~3000 chars to stay within token limits
        transcript_section = f"\n\nReal transcript (use these timestamps accurately):\n{transcript[:3000]}"
    else:
        transcript_section = "\n\n(No transcript available — generate plausible summary from title/channel.)"

    user_message = f"""Video: "{meta['title']}" by {meta['channel']}
URL: {req.url}
Detail level: {DETAIL_PROMPTS[req.detail]}{transcript_section}

Generate the structured summary now."""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1200,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}]
    )

    raw = message.content[0].text.strip()
    try:
        summary = json.loads(raw)
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Failed to parse Claude response")

    return {
        "videoId": video_id,
        "meta": meta,
        "thumbnail": f"https://img.youtube.com/vi/{video_id}/mqdefault.jpg",
        "summary": summary
    }

@app.get("/health")
def health():
    return {"status": "ok"}