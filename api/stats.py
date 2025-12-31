import os
from fastapi import FastAPI
from googleapiclient.discovery import build
from datetime import datetime

app = FastAPI()

API_KEY = os.environ.get("YOUTUBE_API_KEY")
CHANNEL_ID = os.environ.get("CHANNEL_ID")

youtube = build(
    "youtube",
    "v3",
    developerKey=API_KEY,
    cache_discovery=False,
    static_discovery=False
)

@app.get("/")
def root():
    return {"status": "YouTube Stats API is running"}

@app.get("/api/stats")
def stats():
    response = youtube.channels().list(
        part="snippet,statistics",
        id=CHANNEL_ID
    ).execute()

    item = response["items"][0]
    stats = item["statistics"]

    return {
        "channel_name": item["snippet"]["title"],
        "subscribers": int(stats["subscriberCount"]),
        "total_views": int(stats["viewCount"]),
        "total_videos": int(stats["videoCount"]),
        "last_updated": datetime.utcnow().isoformat() + "Z"
    }
