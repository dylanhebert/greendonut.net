import json
import os

from flask import Flask, render_template, send_from_directory

app = Flask(__name__)


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
    },
    {
        "name": "Chatty Foods",
        "description": "Recipes and food tips collected from cooking conversations with AI.",
        "url": "https://chattyfoods.greendonut.net",
        "image": "chattyfoods-banner.svg",
        "color": "emerald",
    },
    {
        "name": "Green Flips",
        "description": "Real-time Grand Exchange flip tracker for Old School RuneScape.",
        "url": "https://flips.greendonut.net",
        "image": "greenflips-banner.svg",
        "icon": "greenflips-icon.svg",
        "color": "amber",
    },
]

SOCIAL_LINKS = [
    {"name": "GitHub", "url": "https://github.com/dylanhebert"},
]

GAME_DEV = [
    {
        "name": "Dead High",
        "game": "Call of Duty: Black Ops III",
        "description": "A custom zombies map set at Wellington High School. Features a full original storyline, custom wonder weapons, quest lines, and its own save & leaderboard systems.",
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
    },
    {
        "name": "Zombie Royale",
        "game": "Call of Duty: Black Ops III",
        "description": "A battle royale mode for zombies. Survive a shrinking circle across three phases on any map — solo or co-op.",
        "players": "7,400+",
        "url": "https://steamcommunity.com/sharedfiles/filedetails/?id=2873503816",
        "image": "mods/zr_thumbnail_wide.jpg",
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
