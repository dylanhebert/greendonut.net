import json
import os
import time
import urllib.request
import urllib.parse

from flask import Flask, jsonify, render_template, send_from_directory

app = Flask(__name__)


@app.context_processor
def cache_bust():
    def versioned_static(filename):
        filepath = os.path.join(app.static_folder, filename)
        try:
            mtime = int(os.path.getmtime(filepath))
        except OSError:
            mtime = 0
        return f"/static/{filename}?v={mtime}"
    return dict(versioned_static=versioned_static)


def load_music():
    json_path = os.path.join(os.path.dirname(__file__), "data", "music.json")
    with open(json_path) as f:
        tracks = json.load(f)
    audio_dir = os.path.join(os.path.dirname(__file__), "static", "audio")
    return [t for t in tracks if os.path.isfile(os.path.join(audio_dir, t["file"]))]

PROJECTS = [
    {
        "name": "Dead High Stats",
        "description": "Call of Duty Zombies high round leaderboard tracker and statistics.",
        "url": "https://deadhighstats.com",
        "image": "deadhighstats.jpg",
        "icon": "deadhighstats-icon.png",
        "color": "red",
        "tech": ["Django", "PostgreSQL", "Plotly", "Steam OAuth"],
        "features": [
            "40+ leaderboard categories",
            "Real-time active game tracking",
            "Steam-authenticated player profiles",
            "Detailed per-game statistics",
        ],
    },
    {
        "name": "GreenMD",
        "description": "A dark-mode markdown viewer for Windows, built for watching AI-written docs rewrite themselves in real time.",
        "url": "https://github.com/dylanhebert/GreenMD",
        "image": "greenmd-banner.svg",
        "icon": "greenmd-icon.png",
        "color": "greenmd",
        "tech": ["C#", "WPF", "WebView2", "Markdig"],
        "features": [
            "Live reload that keeps your reading position",
            "Change marks show what changed since you last looked",
            "Tabs, split panes, and multi-folder workspaces",
            "Paste screenshots straight into notes",
        ],
    },
    {
        "name": "Showtime Snooper",
        "description": "Cinema seat watcher that alerts when enough seats open up side by side where you want to sit.",
        "url": "https://showtimes.greendonut.net",
        "image": "showtimesnooper-banner.svg",
        "icon": "showtimesnooper-icon.svg",
        "color": "gold",
        "tech": ["Flask", "SQLite", "HTMX", "Pushover", "Gunicorn"],
        "features": [
            "Alerts on adjacent seats opening in your zone",
            "Real auditorium maps with drag-select seat picker",
            "Polite background polling on a request budget",
            "Public demo built from synthetic data",
        ],
    },
    {
        "name": "Concert Snooper",
        "description": "Concert watcher that follows your artists and venues and alerts the moment shows are announced or go on sale.",
        "url": "https://concerts.greendonut.net",
        "image": "concertsnooper-banner.svg",
        "icon": "concertsnooper-icon.svg",
        "color": "magenta",
        "tech": ["Flask", "SQLite", "Spotify API", "Ticketmaster API", "Gunicorn"],
        "features": [
            "One-tap Spotify import of your artists",
            "Merges five ticket sources into one feed",
            "Announce, onsale-scheduled, and on-sale-now alerts",
            "Openers matched too, not just headliners",
        ],
    },
    {
        "name": "Green Flips",
        "description": "Real-time Grand Exchange flip tracker for Old School RuneScape.",
        "url": "https://flips.greendonut.net",
        "image": "greenflips-banner.svg",
        "icon": "greenflips-icon.svg",
        "color": "amber",
        "tech": ["FastAPI", "HTMX", "SQLite", "Plotly", "Claude AI", "Discord.py"],
        "features": [
            "Real-time OSRS flip opportunities",
            "AI-powered daily investment picks",
            "Interactive price history charts",
            "Discord bot with live alerts",
        ],
    },
    {
        "name": "Chatty Foods",
        "description": "Recipes and food tips collected from cooking conversations with AI.",
        "url": "https://chattyfoods.greendonut.net",
        "image": "chattyfoods-banner.svg",
        "icon": "chattyfoods-icon.svg",
        "color": "emerald",
        "tech": ["Flask", "SQLite", "Tailwind CSS", "Claude AI"],
        "features": [
            "Recipe and food tip management",
            "AI conversation extraction workflow",
            "Full-text search and categories",
            "Discord webhook notifications",
        ],
    },
    {
        "name": "Green Stonks",
        "description": "Swing-trading dashboard and stock screener with real-time scoring and AI-powered analysis.",
        "color": "emerald",
        "private": True,
        "icon": "greenstonks-icon.svg",
        "tech": ["FastAPI", "HTMX", "SQLite", "TradingView Charts", "Claude AI", "Alpaca API"],
        "features": [
            "Real-time multi-factor stock scoring",
            "AI-powered trade analysis",
            "Automated autopilot trading",
            "Portfolio tracking with SPY benchmark",
        ],
    },
]

SOCIAL_LINKS = [
    {"name": "GitHub", "url": "https://github.com/dylanhebert"},
]

GAME_DEV = [
    {
        "name": "Dead High",
        "game": "Call of Duty: Black Ops III",
        "description": "A fully custom Call of Duty zombies experience set at Wellington High School during a 5G-triggered outbreak.",
        "steam_id": "885119667",
        "total_players": "263,000+",
        "players": "128,000+",
        "url": "https://steamcommunity.com/sharedfiles/filedetails/?id=885119667",
        "logo_clean": "mods/deadhigh2.png",
        "logo_dirty": "mods/deadhigh1.png",
        "slideshow": [
            "mods/deadhigh_steam_2.jpg",
            "mods/deadhigh_steam_7.jpg",
            "mods/deadhigh_steam_9_1.jpg",
            "mods/deadhigh_steam_10.jpg",
            "mods/deadhigh_steam_13.jpg",
        ],
        "tech": ["GSC", "Radiant", "Lua", "C++", "Blender", "Maya"],
        "features": [
            "Original storyline with custom wonder weapons",
            "Multi-step Easter egg quest lines",
            "Custom GobbleGums, ammo tiers, and weapon mastery",
            "Built-in save system and online leaderboards",
        ],
    },
    {
        "name": "Zombie Royale",
        "game": "Call of Duty: Black Ops III",
        "description": "A battle royale mode for zombies. Survive a shrinking circle across three phases on any map — solo or co-op.",
        "steam_id": "2873503816",
        "total_players": "22,000+",
        "players": "7,400+",
        "url": "https://steamcommunity.com/sharedfiles/filedetails/?id=2873503816",
        "image": "mods/zr_thumbnail_wide.jpg",
        "tech": ["GSC", "Radiant", "Lua", "C++"],
        "features": [
            "Three-phase collapse with shrinking circle",
            "Works on any stock or custom map",
            "4 special modes after first victory",
            "Solo and co-op support",
        ],
    },
]


_steam_cache = {"data": {}, "fetched_at": 0}
_STEAM_CACHE_TTL = 6 * 60 * 60  # 6 hours


def _fetch_steam_stats():
    """Fetch live subscriber counts from the Steam Workshop API."""
    ids = [mod["steam_id"] for mod in GAME_DEV]
    body = urllib.parse.urlencode(
        {"itemcount": len(ids)}
        | {f"publishedfileids[{i}]": sid for i, sid in enumerate(ids)}
    ).encode()
    req = urllib.request.Request(
        "https://api.steampowered.com/ISteamRemoteStorage/GetPublishedFileDetails/v1/",
        data=body,
    )
    with urllib.request.urlopen(req, timeout=5) as resp:
        data = json.loads(resp.read())
    result = {}
    for item in data["response"]["publishedfiledetails"]:
        result[item["publishedfileid"]] = {
            "total_players": item["lifetime_subscriptions"],
            "subscribers": item["subscriptions"],
        }
    return result


def _get_steam_stats():
    """Return cached stats, refreshing from Steam if stale."""
    now = time.time()
    if now - _steam_cache["fetched_at"] < _STEAM_CACHE_TTL and _steam_cache["data"]:
        return _steam_cache["data"]
    try:
        _steam_cache["data"] = _fetch_steam_stats()
        _steam_cache["fetched_at"] = now
    except Exception:
        # On failure, return whatever we last had (or fallback values)
        if not _steam_cache["data"]:
            _steam_cache["data"] = {
                mod["steam_id"]: {
                    "total_players": mod["total_players"],
                    "subscribers": mod["players"],
                }
                for mod in GAME_DEV
            }
    return _steam_cache["data"]


@app.route("/api/steam-stats")
def steam_stats():
    return jsonify(_get_steam_stats())


@app.route("/")
def index():
    return render_template("index.html", projects=PROJECTS, social_links=SOCIAL_LINKS, game_dev=GAME_DEV, music=load_music())


@app.route("/robots.txt")
def robots():
    return send_from_directory(app.static_folder, "robots.txt")


if __name__ == "__main__":
    app.run(debug=True)
