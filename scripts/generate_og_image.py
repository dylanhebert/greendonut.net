"""Generate OG image for greendonut.net"""
from PIL import Image, ImageDraw, ImageFont
import os

WIDTH, HEIGHT = 1200, 630

# Colors from dark theme
BG_COLOR = (10, 10, 10)  # #0a0a0a
GREEN_FROM = (74, 222, 128)  # #4ade80
TEXT_MUTED = (115, 115, 115)  # #737373
TEXT_SECONDARY = (163, 163, 163)  # #a3a3a3

# Nav gradient colors: pink, amber, green, blue, purple
GRADIENT_COLORS = [
    (251, 113, 133),  # #fb7185
    (251, 191, 36),   # #fbbf24
    (52, 211, 153),   # #34d399
    (96, 165, 250),   # #60a5fa
    (167, 139, 250),  # #a78bfa
]


def lerp_color(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))


def gradient_color_at(x, width, colors):
    segments = len(colors) - 1
    pos = (x / width) * segments
    idx = min(int(pos), segments - 1)
    t = pos - idx
    return lerp_color(colors[idx], colors[idx + 1], t)


def load_font(size, bold=False):
    font_names = [
        "C:/Windows/Fonts/segoeui.ttf" if not bold else "C:/Windows/Fonts/segoeuib.ttf",
        "C:/Windows/Fonts/arial.ttf" if not bold else "C:/Windows/Fonts/arialbd.ttf",
    ]
    for name in font_names:
        try:
            return ImageFont.truetype(name, size)
        except (OSError, IOError):
            continue
    return ImageFont.load_default()


# Create image
img = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
draw = ImageDraw.Draw(img)

# Subtle radial vignette
for y in range(HEIGHT):
    for x in range(WIDTH):
        dx = (x - WIDTH / 2) / (WIDTH / 2)
        dy = (y - HEIGHT / 2) / (HEIGHT / 2)
        dist = (dx * dx + dy * dy) ** 0.5
        if dist > 0.6:
            darken = int((dist - 0.6) * 30)
            r, g, b = img.getpixel((x, y))
            img.putpixel((x, y), (max(0, r - darken), max(0, g - darken), max(0, b - darken)))

# Colorful gradient lines at top and bottom
LINE_HEIGHT = 4
for x in range(WIDTH):
    color = gradient_color_at(x, WIDTH, GRADIENT_COLORS)
    for y_off in range(LINE_HEIGHT):
        img.putpixel((x, y_off), color)
        img.putpixel((x, HEIGHT - 1 - y_off), color)

# --- Calculate layout to vertically center everything ---
LOGO_SIZE = 240
GAP_LOGO_TITLE = 5
GAP_TITLE_SUBTITLE = 50

font_the = load_font(52, bold=False)
font_title = load_font(96, bold=True)
font_subtitle = load_font(32, bold=False)

the_text = "the"
title_text = "Green Donut"
subtitle_text = "A developer and creator of some other things."

the_ascent, _ = font_the.getmetrics()
title_ascent, _ = font_title.getmetrics()

the_bbox = draw.textbbox((0, 0), the_text, font=font_the)
the_width = the_bbox[2] - the_bbox[0]

title_bbox = draw.textbbox((0, 0), title_text, font=font_title)
title_width = title_bbox[2] - title_bbox[0]
title_height = title_bbox[3] - title_bbox[1]

subtitle_bbox = draw.textbbox((0, 0), subtitle_text, font=font_subtitle)
subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
subtitle_height = subtitle_bbox[3] - subtitle_bbox[1]

total_content_height = LOGO_SIZE + GAP_LOGO_TITLE + title_height + GAP_TITLE_SUBTITLE + subtitle_height
content_top = (HEIGHT - total_content_height) // 2

# --- Draw everything ---

# Logo
logo_path = os.path.join("static", "images", "greendonutlogo.png")
if os.path.exists(logo_path):
    logo = Image.open(logo_path).convert("RGBA")
    logo = logo.resize((LOGO_SIZE, LOGO_SIZE), Image.LANCZOS)
    logo_x = (WIDTH - LOGO_SIZE) // 2
    logo_y = content_top
    img.paste(logo, (logo_x, logo_y), logo)

# Title row
spacing = 20
total_width = the_width + spacing + title_width
start_x = (WIDTH - total_width) // 2
title_y = content_top + LOGO_SIZE + GAP_LOGO_TITLE

baseline_offset = title_ascent - the_ascent
the_y = title_y + baseline_offset

draw.text((start_x, the_y), the_text, fill=TEXT_MUTED, font=font_the)

title_x = start_x + the_width + spacing
draw.text((title_x, title_y), title_text, fill=GREEN_FROM, font=font_title)

# Subtitle
subtitle_x = (WIDTH - subtitle_width) // 2
subtitle_y = title_y + title_height + GAP_TITLE_SUBTITLE
draw.text((subtitle_x, subtitle_y), subtitle_text, fill=TEXT_SECONDARY, font=font_subtitle)

# Save
output_path = os.path.join("static", "images", "og-image.png")
img.save(output_path, "PNG", optimize=True)
print(f"OG image saved to {output_path}")
print(f"Size: {WIDTH}x{HEIGHT}")
