from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
import os
import json
import re
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

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

class SummarizeRequest(BaseModel):
    url: str
    detail: str = "standard"

DETAIL_PROMPTS = {
    "brief": "2-3 sections with key concepts and 3 practice questions",
    "standard": "4-5 sections with examples, common mistakes and 5 practice questions",
    "deep": "6-8 detailed sections with step-by-step methods, common mistakes and 8 practice questions"
}

SYSTEM_PROMPT = """You are an expert educational content writer. You convert YouTube video content into comprehensive, structured study documents like textbook notes.

Respond ONLY with a valid JSON object in this exact format:
{
  "title": "Topic title",
  "introduction": "2-3 sentence overview of what this topic covers",
  "sections": [
    {
      "heading": "Section heading",
      "subsections": [
        {
          "subheading": "Subsection heading",
          "content": "Clear concise explanation in bullet points or short paragraphs",
          "keyTerms": ["term: definition", "formula: explanation"],
          "example": "A simple real-world example or analogy to understand this concept",
          "mnemonic": "A memory trick or mnemonic to remember this (if applicable)",
          "examQuestion": "A quick exam-style question to test understanding of this subsection"
        }
      ]
    }
  ],
  "keyConceptsSummary": ["concept 1", "concept 2", "concept 3"],
  "commonMistakes": ["mistake 1", "mistake 2", "mistake 3"],
  "practiceQuestions": [
    {"q": "Question here?", "a": "Answer here"}
  ],
  "quickRevisionSummary": "5-6 sentence paragraph covering all key points for last-minute revision"
}

Rules:
- No timestamps, no casual speech, no fillers
- Language must be clear, concise, and exam-oriented
- Structure like a textbook chapter
- Use bullet points or short paragraphs for content
- Bold key terms, definitions, and formulas using **term** syntax
- Add examples, mnemonics, and analogies wherever helpful
- Add a quick exam-style question at the end of each subsection
- No markdown, no backticks. Pure JSON only."""

@app.post("/summarize")
async def summarize(req: SummarizeRequest):
    video_id = extract_video_id(req.url)
    if not video_id:
        raise HTTPException(status_code=400, detail="Invalid YouTube URL")

    meta = await fetch_video_meta(video_id)
    transcript = fetch_transcript(video_id)

    if transcript:
        transcript_section = f"\n\nReal transcript:\n{transcript[:3000]}"
    else:
        transcript_section = "\n\n(No transcript available — generate plausible summary from title/channel.)"

    user_message = f"""Video: "{meta['title']}" by {meta['channel']}
URL: {req.url}
Detail level: {DETAIL_PROMPTS[req.detail]}{transcript_section}

Generate the structured study document now."""

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "deepseek/deepseek-v3.2",
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_message}
                ],
                "max_tokens": 4000
            },
            timeout=30
        )

    data = response.json()

    if "error" in data:
        raise HTTPException(status_code=500, detail=data["error"]["message"])

    raw = data["choices"][0]["message"]["content"].strip()
    raw = raw.replace("```json", "").replace("```", "").strip()

    json_match = re.search(r'\{.*\}', raw, re.DOTALL)
    if json_match:
        raw = json_match.group(0)

    try:
        summary = json.loads(raw)
    except json.JSONDecodeError:
        print("RAW MODEL OUTPUT:", raw[:500])
        raise HTTPException(status_code=500, detail="Failed to parse model response")

    return {
        "videoId": video_id,
        "meta": meta,
        "thumbnail": f"https://img.youtube.com/vi/{video_id}/mqdefault.jpg",
        "summary": summary
    }

@app.get("/health")
def health():
    return {"status": "ok"}
