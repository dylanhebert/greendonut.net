import json
import os

from flask import Flask, render_template, send_from_directory

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
        "color": "red",
        "tech": ["Django", "SQLite", "Plotly", "Steam OAuth"],
        "features": [
            "40+ leaderboard categories",
            "Real-time active game tracking",
            "Steam-authenticated player profiles",
            "Detailed per-game statistics",
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


@app.route("/")
def index():
    return render_template("index.html", projects=PROJECTS, social_links=SOCIAL_LINKS, game_dev=GAME_DEV, music=load_music())


@app.route("/robots.txt")
def robots():
    return send_from_directory(app.static_folder, "robots.txt")


if __name__ == "__main__":
    app.run(debug=True)
