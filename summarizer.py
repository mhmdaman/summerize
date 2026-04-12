from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
import httpx
import re

def extract_video_id(url: str) -> str | None:
    patterns = [
        r"(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})",
        r"youtube\.com\/shorts\/([a-zA-Z0-9_-]{11})"
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

async def fetch_video_meta(video_id: str) -> dict:
    url = f"https://www.youtube.com/oembed?url=https://youtube.com/watch?v={video_id}&format=json"
    async with httpx.AsyncClient() as client:
        try:
            res = await client.get(url, timeout=5)
            data = res.json()
            return {"title": data.get("title", "Unknown"), "channel": data.get("author_name", "Unknown")}
        except Exception:
            return {"title": "Unknown", "channel": "Unknown"}

def fetch_transcript(video_id: str) -> str:
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        # Join transcript chunks with timestamps
        lines = []
        for entry in transcript:
            mins = int(entry["start"] // 60)
            secs = int(entry["start"] % 60)
            lines.append(f"[{mins}:{secs:02d}] {entry['text']}")
        return "\n".join(lines)
    except (TranscriptsDisabled, NoTranscriptFound):
        return ""
    except Exception:
        return ""