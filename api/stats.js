// api/stats.js
const fetch = require("node-fetch");

const YOUTUBE_API_KEY = "AIzaSyDNjsDrY3affjQUyEHJJLwtxPfyQDswXTc";

async function getChannelId(channelInput) {
    if (channelInput.includes("youtube.com/channel/")) {
        return channelInput.split("/channel/")[1];
    } else if (channelInput.includes("youtube.com/")) {
        // Search API for username or URL
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

module.exports = async (req, res) => {
    const channelInput = req.query.channel;
    if (!channelInput) {
        return res.status(400).json({ error: "Please provide a channel name or URL" });
    }

    try {
        const channelId = await getChannelId(channelInput);
        if (!channelId) return res.status(404).json({ error: "Channel not found" });

        const stats = await getChannelStats(channelId);
        if (!stats) return res.status(500).json({ error: "Failed to fetch stats" });

        return res.json(stats);
    } catch (err) {
        console.error(err);
        return res.status(500).json({ error: "Server error" });
    }
};
