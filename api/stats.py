# api/stats.py
from flask import Flask, request, jsonify
import requests
import os
from datetime import datetime

app = Flask(__name__)

# ⚠️ Replace with your actual YouTube API key
YOUTUBE_API_KEY = "AIzaSyDNjsDrY3affjQUyEHJJLwtxPfyQDswXTc"

def get_channel_id(channel_input):
    """
    Determines the channel ID from user input.
    Supports:
      - Full channel URL
      - Channel username
      - Direct channel ID
    """
    if "youtube.com/channel/" in channel_input:
        return channel_input.split("/channel/")[-1]
    elif "youtube.com/" in channel_input:
        # Use search API to get channel ID from username or URL
        search_url = "https://www.googleapis.com/youtube/v3/search"
        params = {
            "part": "snippet",
            "q": channel_input,
            "type": "channel",
            "key": YOUTUBE_API_KEY
        }
        r = requests.get(search_url, params=params).json()
        if "items" in r and len(r["items"]) > 0:
            return r["items"][0]["snippet"]["channelId"]
        else:
            return None
    else:
        # Assume direct channel ID
        return channel_input

def get_channel_stats(channel_id):
    """
    Fetches stats for a channel using YouTube Data API v3
    """
    url = "https://www.googleapis.com/youtube/v3/channels"
    params = {
        "part": "snippet,statistics",
        "id": channel_id,
        "key": YOUTUBE_API_KEY
    }
    r = requests.get(url, params=params)
    data = r.json()
    if "items" not in data or len(data["items"]) == 0:
        return None

    item = data["items"][0]
    stats = item["statistics"]
    snippet = item["snippet"]

    return {
        "title": snippet.get("title", "-"),
        "subscribers": int(stats.get("subscriberCount", 0)),
        "views": int(stats.get("viewCount", 0)),
        "videos": int(stats.get("videoCount", 0)),
        "last_updated": datetime.now().strftime("%H:%M:%S")
    }

@app.route("/api/stats")
def stats():
    channel_input = request.args.get("channel")
    if not channel_input:
        return jsonify({"error": "Please provide a channel name or URL"}), 400

    channel_id = get_channel_id(channel_input)
    if not channel_id:
        return jsonify({"error": "Could not find channel"}), 404

    stats = get_channel_stats(channel_id)
    if not stats:
        return jsonify({"error": "Failed to fetch channel stats"}), 500

    return jsonify(stats)

if __name__ == "__main__":
    app.run(debug=True)
