from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests
from datetime import datetime
import re
import os

app = Flask(__name__, static_folder='.')
CORS(app)  # Allow frontend fetch

API_KEY = "AIzaSyDNjsDrY3affjQUyEHJJLwtxPfyQDswXTc"  # Your API key

# --- Helper to get channel ID ---
def get_channel_id(channel_input):
    channel_input = channel_input.strip()

    # 1️⃣ Full channel ID URL
    match = re.search(r"(?:youtube\.com\/channel\/)([a-zA-Z0-9_-]+)", channel_input)
    if match:
        return match.group(1)

    # 2️⃣ Custom URL (/c/Name or /user/Name)
    match = re.search(r"(?:youtube\.com\/(?:c|user)\/)([a-zA-Z0-9_-]+)", channel_input)
    if match:
        username = match.group(1)
        res = requests.get(
            f"https://www.googleapis.com/youtube/v3/search?part=snippet&type=channel&q={username}&key={API_KEY}"
        ).json()
        if "items" in res and res["items"]:
            return res["items"][0]["snippet"]["channelId"]

    # 3️⃣ Plain channel name
    res = requests.get(
        f"https://www.googleapis.com/youtube/v3/search?part=snippet&type=channel&q={channel_input}&key={API_KEY}"
    ).json()
    if "items" in res and res["items"]:
        return res["items"][0]["snippet"]["channelId"]

    return None

# --- API route ---
@app.route("/api/stats")
def stats():
    channel_input = request.args.get("channel")
    if not channel_input:
        return jsonify({"error": "No channel provided"}), 400

    channel_id = get_channel_id(channel_input)
    if not channel_id:
        return jsonify({"error": "Channel not found"}), 404

    url = f"https://www.googleapis.com/youtube/v3/channels?part=statistics,snippet&id={channel_id}&key={API_KEY}"
    res = requests.get(url).json()

    if "items" not in res or not res["items"]:
        return jsonify({"error": "Stats not found"}), 404

    data = res["items"][0]
    stats = data["statistics"]
    snippet = data["snippet"]

    return jsonify({
        "title": snippet.get("title", "-"),
        "subscribers": stats.get("subscriberCount", "0"),
        "views": stats.get("viewCount", "0"),
        "videos": stats.get("videoCount", "0"),
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

# --- Serve index.html ---
@app.route("/")
def index():
    return send_from_directory('.', 'index.html')

# --- Run app ---
if __name__ == "__main__":
    app.run(debug=True)
