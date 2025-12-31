// api/stats.js
import fetch from "node-fetch";

const YOUTUBE_API_KEY = "AIzaSyDNjsDrY3affjQUyEHJJLwtxPfyQDswXTc";

// Helper: Get channel ID from input
async function getChannelId(channelInput) {
  if (channelInput.includes("youtube.com/channel/")) {
    return channelInput.split("/channel/")[1];
  } else if (channelInput.includes("youtube.com/")) {
    // Search API to find channel ID from URL/username
    const searchUrl = `https://www.googleapis.com/youtube/v3/search?part=snippet&q=${encodeURIComponent(channelInput)}&type=channel&key=${YOUTUBE_API_KEY}`;
    const r = await fetch(searchUrl);
    const data = await r.json();
    if (data.items && data.items.length > 0) {
      return data.items[0].snippet.channelId;
    } else {
      return null;
    }
  } else {
    // Direct channel ID
    return channelInput;
  }
}

// Helper: Fetch stats
async function getChannelStats(channelId) {
  const url = `https://www.googleapis.com/youtube/v3/channels?part=snippet,statistics&id=${channelId}&key=${YOUTUBE_API_KEY}`;
  const r = await fetch(url);
  const data = await r.json();
  if (!data.items || data.items.length === 0) return null;

  const item = data.items[0];
  const stats = item.statistics;
  const snippet = item.snippet;

  return {
    title: snippet.title || "-",
    subscribers: parseInt(stats.subscriberCount || 0),
    views: parseInt(stats.viewCount || 0),
    videos: parseInt(stats.videoCount || 0),
    last_updated: new Date().toLocaleTimeString()
  };
}

// Vercel serverless handler
export default async function handler(req, res) {
  const channelInput = req.query.channel;
  if (!channelInput) {
    res.status(400).json({ error: "Please provide a channel name or URL" });
    return;
  }

  try {
    const channelId = await getChannelId(channelInput);
    if (!channelId) {
      res.status(404).json({ error: "Channel not found" });
      return;
    }

    const stats = await getChannelStats(channelId);
    if (!stats) {
      res.status(500).json({ error: "Failed to fetch channel stats" });
      return;
    }

    res.status(200).json(stats);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "Server error" });
  }
}
