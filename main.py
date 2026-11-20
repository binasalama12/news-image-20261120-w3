#!/usr/bin/env python3
"""Friday 20 November 2026 - one day of world news, one picture.

Atlas Fidelity variant for wallet w3. A single-page broadsheet front
page: masthead, UTC timeline, region strip, one full-width hero
(Akvan), two smaller heroes, thirteen pictured stories in a 3/5/5
grid, a dot-matrix world map, thirty-two more briefs, a date check
and a sources footer. Everything is drawn from scratch with PIL -
flat scenes, no photographs, no imported artwork.
"""

import math
import random
from PIL import Image, ImageDraw, ImageFont

W, H = 1600, 1600
M = 44
PAPER = (247, 243, 233)
INK = (26, 24, 20)
RED = (168, 32, 40)
GREEN = (28, 84, 58)
GOLD = (176, 132, 40)
BLUE = (38, 84, 138)
TEAL = (24, 110, 110)
GREY = (96, 92, 84)
FAINT = (214, 208, 194)

FD = "/usr/share/fonts/truetype/dejavu/"
FL = "/usr/share/fonts/truetype/liberation/"


def _font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


def sans(size, bold=False):
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    return _font(FD + name, size)


def serif(size, bold=False, italic=False):
    if bold:
        name = "LiberationSerif-Bold.ttf"
    elif italic:
        name = "LiberationSerif-Italic.ttf"
    else:
        name = "LiberationSerif-Regular.ttf"
    return _font(FL + name, size)


def wrap(d, text, font, width):
    """Greedy word wrap to a pixel width."""
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if d.textlength(trial, font=font) <= width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def block(d, x, y, text, font, width, lh, color=INK, max_lines=None):
    """Draw wrapped text, return the y below it."""
    lines = wrap(d, text, font, width)
    if max_lines is not None and len(lines) > max_lines:
        lines = lines[:max_lines]
        while lines and d.textlength(lines[-1] + "…", font=font) > width:
            lines[-1] = lines[-1][:-1]
        if lines:
            lines[-1] = lines[-1].rstrip() + "…"
    for ln in lines:
        d.text((x, y), ln, font=font, fill=color)
        y += lh
    return y


def fit1(d, text, font, width):
    """Truncate one line with an ellipsis so it fits."""
    if d.textlength(text, font=font) <= width:
        return text
    while text and d.textlength(text + "…", font=font) > width:
        text = text[:-1]
    return text.rstrip() + "…"


def rule(d, y, x0=M, x1=W - M, color=INK, width=2):
    d.line([(x0, y), (x1, y)], fill=color, width=width)


def sky(d, x, y, w, h, top, bottom, bands=10):
    """Vertical gradient sky."""
    for i in range(bands):
        t = i / max(1, bands - 1)
        col = tuple(int(top[c] + (bottom[c] - top[c]) * t) for c in range(3))
        y0 = y + int(h * i / bands)
        y1 = y + int(h * (i + 1) / bands)
        d.rectangle([x, y0, x + w, y1], fill=col)


def speckle(im, seed=7, count=9000, amp=7):
    """Paper grain: faint random speckles over the page."""
    rnd = random.Random(seed)
    px = im.load()
    for _ in range(count):
        xx = rnd.randrange(W)
        yy = rnd.randrange(H)
        if rnd.random() < 0.5:
            n = rnd.randint(-amp, amp)
            r, g, b = px[xx, yy]
            px[xx, yy] = (max(0, min(255, r + n)),
                          max(0, min(255, g + n)),
                          max(0, min(255, b + n)))


def stars(d, x, y, w, h, seed, n=26):
    rnd = random.Random(seed)
    for _ in range(n):
        sx = x + rnd.randrange(w)
        sy = y + rnd.randrange(h)
        r = rnd.choice([1, 1, 2])
        d.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(240, 238, 220))


def kicker(d, x, y, num, place, topic, source, width, accent=RED, size=17):
    d.rectangle([x, y + 2, x + 7, y + size + 2], fill=accent)
    text = "%d · %s · %s" % (num, place, topic)
    d.text((x + 13, y), text, font=sans(size, True), fill=accent)
    if source:
        kw = d.textlength(text, font=sans(size, True))
        sw = d.textlength(source, font=sans(13, True))
        if 13 + kw + sw + 14 <= width:
            d.text((x + width - sw, y + 3), source, font=sans(13, True),
                   fill=GREY)
        else:
            sw2 = d.textlength(source, font=sans(11, True))
            if 13 + kw + sw2 + 10 <= width:
                d.text((x + width - sw2, y + 4), source, font=sans(11, True),
                       fill=GREY)


def scene(d, idx, x, y, w, h):
    """Flat drawn scene for story idx (1..16)."""
    if idx == 1:
        # Cyclone over the coast: dark storm sky, rain, spiral, waves.
        sky(d, x, y, w, h, (28, 48, 58), (96, 116, 122))
        rnd = random.Random(11)
        for _ in range(46):
            rx = x + rnd.randrange(w)
            ry = y + rnd.randrange(h)
            d.line([(rx, ry), (rx - 8, ry + 16)], fill=(200, 214, 218), width=2)
        cx, cy = x + w // 2, y + h // 2 - 6
        for r in (58, 44, 30, 16):
            d.arc([cx - r, cy - r, cx + r, cy + r], 20, 300,
                  fill=(240, 244, 244), width=4)
        for k in range(4):
            yy = y + h - 18 + k * 5
            pts = []
            for t in range(0, w + 20, 20):
                pts.append((x + t, yy + 5 * math.sin(t / 46.0 + k)))
            d.line(pts, fill=(225, 232, 232), width=3)
    elif idx == 2:
        # Night skyline, missile arc, burst over a tower.
        sky(d, x, y, w, h, (14, 16, 38), (44, 44, 74))
        stars(d, x, y, w, h // 2, 22, 22)
        rnd = random.Random(23)
        bx = x
        while bx < x + w:
            bw = rnd.randrange(26, 70)
            bh = rnd.randrange(h // 4, h // 2)
            d.rectangle([bx, y + h - bh, bx + bw, y + h], fill=(20, 22, 44))
            for wy in range(y + h - bh + 8, y + h - 6, 14):
                for wx in range(bx + 5, bx + bw - 4, 11):
                    if rnd.random() < 0.5:
                        d.rectangle([wx, wy, wx + 4, wy + 6], fill=(250, 210, 110))
            bx += bw + 6
        pts = []
        for t in range(0, 101, 5):
            px = x + w * 0.08 + (w * 0.78) * t / 100.0
            py = y + h * 0.78 - (h * 0.55) * math.sin(math.pi * t / 100.0)
            pts.append((px, py))
        d.line(pts, fill=(255, 150, 40), width=5)
        ex, ey = pts[-1]
        for a in range(0, 360, 30):
            r = 26 if a % 60 == 0 else 14
            d.line([(ex, ey),
                    (ex + r * math.cos(math.radians(a)),
                     ey + r * math.sin(math.radians(a)))],
                   fill=(255, 190, 60), width=4)
        d.ellipse([ex - 9, ey - 9, ex + 9, ey + 9], fill=(255, 220, 120))
    elif idx == 3:
        # Three flags over a summit skyline.
        sky(d, x, y, w, h, (120, 150, 190), (205, 215, 225))
        d.rectangle([x, y + h - 26, x + w, y + h], fill=(70, 78, 66))
        flags = [((200, 40, 40), "us"), ((200, 30, 30), "cn"),
                 ((230, 230, 230), "ru")]
        fw, fh = w // 6, h // 3
        for k, (col, kind) in enumerate(flags):
            fx = x + w // 8 + k * (w // 3)
            fy = y + h // 6
            d.line([(fx, fy), (fx, y + h - 26)], fill=INK, width=4)
            if kind == "us":
                for s in range(5):
                    d.rectangle([fx, fy + s * fh // 5,
                                 fx + fw, fy + (s + 1) * fh // 5],
                                fill=(200, 40, 40) if s % 2 == 0 else (245, 245, 245))
                d.rectangle([fx, fy, fx + fw // 2, fy + fh // 2], fill=(40, 60, 140))
            elif kind == "cn":
                d.rectangle([fx, fy, fx + fw, fy + fh], fill=(200, 30, 30))
                for sx, sy in [(10, 8), (26, 6), (30, 16), (24, 26), (10, 22)]:
                    d.ellipse([fx + sx, fy + sy, fx + sx + 7, fy + sy + 7],
                              fill=(250, 220, 60))
            else:
                d.rectangle([fx, fy, fx + fw, fy + fh // 3], fill=(245, 245, 245))
                d.rectangle([fx, fy + fh // 3, fx + fw, fy + 2 * fh // 3],
                            fill=(40, 90, 190))
                d.rectangle([fx, fy + 2 * fh // 3, fx + fw, fy + fh],
                            fill=(200, 40, 40))
    elif idx == 4:
        # Bridge arc over strait water at dusk.
        sky(d, x, y, w, h, (210, 150, 110), (120, 90, 110))
        d.rectangle([x, y + h * 0.62, x + w, y + h], fill=(50, 80, 110))
        d.arc([x - w // 5, y + h // 5, x + w * 6 // 5, y + h * 2],
              200, 340, fill=(30, 30, 34), width=6)
        for px in (0.2, 0.5, 0.8):
            d.line([(x + w * px, y + h * 0.30), (x + w * px, y + h * 0.62)],
                   fill=(30, 30, 34), width=5)
        d.ellipse([x + w * 0.62, y + h * 0.12, x + w * 0.62 + 8,
                   y + h * 0.12 + 8], fill=(255, 200, 80))
    elif idx == 5:
        # APEC hall: columns and a row of small flags.
        sky(d, x, y, w, h, (150, 170, 200), (220, 225, 230))
        d.rectangle([x + w // 8, y + h // 4, x + w * 7 // 8, y + h],
                    fill=(90, 100, 120))
        for k in range(5):
            cx = x + w // 8 + 14 + k * (w * 3 // 4) // 5
            d.rectangle([cx, y + h // 4 + 8, cx + 12, y + h - 8],
                        fill=(225, 225, 220))
        d.polygon([(x + w // 8 - 10, y + h // 4),
                   (x + w * 7 // 8 + 10, y + h // 4),
                   (x + w // 2, y + h // 12)], fill=(120, 40, 40))
        for k, col in enumerate([(200, 40, 40), (40, 90, 190), (40, 140, 80),
                                 (220, 170, 40), (140, 60, 160)]):
            fx = x + 8 + k * (w - 16) // 5
            d.rectangle([fx, y + h - 34, fx + 18, y + h - 12], fill=col)
    elif idx == 6:
        # Globe over a warming sea.
        sky(d, x, y, w, h, (60, 140, 130), (150, 205, 195))
        cx, cy, r = x + w // 2, y + h // 2, min(w, h) // 3
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(60, 120, 190))
        d.ellipse([cx - r // 2, cy - r // 2, cx + r // 3, cy - r // 6],
                  fill=(70, 150, 90))
        d.ellipse([cx - r // 6, cy + r // 4, cx + r // 2, cy + r // 2],
                  fill=(70, 150, 90))
        d.ellipse([cx - r - 6, cy - r - 6, cx + r + 6, cy + r + 6],
                  outline=(240, 240, 230), width=3)
        d.rectangle([x, y + h - 12, x + w, y + h], fill=(240, 200, 90))
    elif idx == 7:
        # Courthouse columns and scales.
        sky(d, x, y, w, h, (200, 200, 195), (235, 232, 220))
        for k in range(4):
            cx = x + 12 + k * (w - 24) // 4
            d.rectangle([cx, y + 12, cx + w // 8, y + h - 10],
                        fill=(225, 220, 205))
            d.rectangle([cx - 4, y + 6, cx + w // 8 + 4, y + 14],
                        fill=(180, 170, 150))
        d.rectangle([x, y + h - 10, x + w, y + h], fill=(120, 110, 95))
        mx, my = x + w // 2, y + h // 3
        d.line([(mx, my - 14), (mx, my + 14)], fill=GOLD, width=3)
        d.line([(mx - 16, my - 14), (mx + 16, my - 14)], fill=GOLD, width=3)
    elif idx == 8:
        # Falling market chart.
        sky(d, x, y, w, h, (30, 34, 44), (60, 64, 80))
        rnd = random.Random(81)
        for k in range(9):
            bx = x + 6 + k * (w - 12) // 9
            bh = rnd.randrange(h // 5, h // 2)
            d.rectangle([bx, y + h - bh, bx + (w - 12) // 11, y + h],
                        fill=(110, 116, 130))
        pts = []
        for k in range(9):
            pts.append((x + 8 + k * (w - 16) // 8,
                        y + h // 4 + k * h // 14 + (k % 3) * 4))
        d.line(pts, fill=(220, 60, 50), width=5)
        d.ellipse([pts[-1][0] - 6, pts[-1][1] - 6, pts[-1][0] + 6,
                   pts[-1][1] + 6], fill=(220, 60, 50))
    elif idx == 9:
        # Neon game city at night.
        sky(d, x, y, w, h, (24, 10, 50), (90, 30, 110))
        rnd = random.Random(91)
        bx = x
        while bx < x + w:
            bw = rnd.randrange(18, 46)
            bh = rnd.randrange(h // 3, h * 3 // 4)
            col = rnd.choice([(200, 60, 180), (60, 200, 220),
                              (250, 200, 60), (120, 80, 220)])
            d.rectangle([bx, y + h - bh, bx + bw, y + h], fill=col)
            bx += bw + 4
        d.ellipse([x + w - 34, y + 8, x + w - 10, y + 32], fill=(255, 220, 130))
    elif idx == 10:
        # Deep space: stars, ringed planet, probe dot.
        sky(d, x, y, w, h, (6, 8, 20), (20, 26, 52))
        stars(d, x, y, w, h, 101, 30)
        cx, cy = x + w // 2, y + h // 2
        d.ellipse([cx - 26, cy - 26, cx + 26, cy + 26], fill=(220, 170, 90))
        d.arc([cx - 44, cy - 12, cx + 44, cy + 12], 200, 340,
              fill=(230, 220, 200), width=3)
        d.ellipse([x + w - 16, y + 10, x + w - 10, y + 16], fill=(250, 250, 240))
    elif idx == 11:
        # Seoul tower and taegeuk.
        sky(d, x, y, w, h, (150, 185, 220), (225, 232, 240))
        tx = x + w // 2 - 8
        d.rectangle([tx, y + h // 4, tx + 16, y + h], fill=(70, 80, 95))
        d.ellipse([tx - 6, y + h // 6, tx + 22, y + h // 6 + 18],
                  fill=(200, 60, 60))
        d.rectangle([x + 10, y + h - 22, x + w - 10, y + h], fill=(120, 130, 120))
        cx, cy, r = x + w // 4, y + h // 2, 16
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(245, 245, 245),
                  outline=INK, width=2)
        d.pieslice([cx - r, cy - r, cx + r, cy + r], 270, 90, fill=(200, 50, 50))
        d.pieslice([cx - r, cy - r, cx + r, cy + r], 90, 270, fill=(50, 90, 180))
    elif idx == 12:
        # Drought: hot sun, cracked earth.
        sky(d, x, y, w, h, (240, 180, 110), (250, 220, 160))
        d.ellipse([x + w - 44, y + 8, x + w - 12, y + 40], fill=(255, 200, 60))
        d.rectangle([x, y + h * 0.55, x + w, y + h], fill=(170, 130, 80))
        rnd = random.Random(121)
        for _ in range(7):
            px = x + rnd.randrange(w)
            py = y + int(h * 0.55) + rnd.randrange(6)
            d.line([(px, py), (px + rnd.randrange(-14, 14),
                     py + rnd.randrange(10, 26))], fill=(90, 60, 35), width=2)
    elif idx == 13:
        # Nuclear site: cooling tower and atom.
        sky(d, x, y, w, h, (170, 175, 180), (220, 222, 225))
        tx = x + w // 2 - 22
        d.polygon([(tx, y + h // 5), (tx + 44, y + h // 5),
                   (tx + 34, y + h), (tx + 10, y + h)], fill=(200, 200, 195))
        d.rectangle([tx + 6, y + h // 5 - 8, tx + 38, y + h // 5],
                    fill=(160, 160, 155))
        cx, cy = x + w // 5, y + h // 2
        for a in (0, 60, 120):
            d.arc([cx - 18, cy - 18, cx + 18, cy + 18], a, a + 120,
                  fill=(40, 80, 160), width=3)
        d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=(40, 80, 160))
    elif idx == 14:
        # Two flags, restored channel.
        sky(d, x, y, w, h, (140, 175, 210), (215, 225, 235))
        for k, cols in enumerate([[(240, 200, 40), (40, 90, 190), (200, 50, 50)],
                                  [(200, 50, 50), (245, 245, 245),
                                   (40, 90, 190)]]):
            fx = x + w // 6 + k * (w // 2)
            fy = y + h // 5
            for s, col in enumerate(cols):
                d.rectangle([fx, fy + s * 12, fx + 52, fy + (s + 1) * 12],
                            fill=col)
            d.line([(fx, fy), (fx, y + h - 14)], fill=INK, width=3)
        d.arc([x + w // 2 - 30, y + h // 2, x + w // 2 + 30, y + h],
              200, 340, fill=GREEN, width=4)
    elif idx == 15:
        # Tanker in the strait.
        sky(d, x, y, w, h, (120, 170, 205), (200, 225, 235))
        d.rectangle([x, y + h * 0.6, x + w, y + h], fill=(40, 100, 150))
        d.rectangle([x + w // 6, y + h * 0.42, x + w * 5 // 6, y + h * 0.62],
                    fill=(150, 40, 40))
        for k, col in enumerate([(240, 200, 60), (60, 140, 90), (220, 220, 210)]):
            d.rectangle([x + w // 6 + 8 + k * 26, y + h * 0.28,
                         x + w // 6 + 30 + k * 26, y + h * 0.42], fill=col)
        d.ellipse([x + w * 0.72, y + h * 0.14, x + w * 0.72 + 22,
                   y + h * 0.14 + 22], fill=(120, 120, 115))
    else:
        # Cricket: green pitch, stumps, red ball.
        sky(d, x, y, w, h, (140, 190, 220), (210, 230, 240))
        d.rectangle([x, y + h * 0.45, x + w, y + h], fill=(70, 140, 80))
        d.rectangle([x + w // 4, y + h * 0.45, x + w * 3 // 4, y + h],
                    fill=(200, 180, 130))
        for k in range(3):
            sx = x + w // 2 - 8 + k * 8
            d.line([(sx, y + h * 0.5), (sx, y + h * 0.5 + 22)],
                   fill=(240, 220, 140), width=3)
        d.ellipse([x + w * 0.68, y + h * 0.62, x + w * 0.68 + 14,
                   y + h * 0.62 + 14], fill=(180, 40, 40))


TIMELINE = [
    ("Overnight", "Crimean Bridge hit a third time"),
    ("~06:00 UTC", "APEC leaders meet in Shenzhen"),
    ("~10:00 UTC", "Trilateral declaration issued"),
    ("~12:00 UTC", "Akvan makes landfall in Odisha"),
    ("~14:00 UTC", "Houthi missile hits Riyadh KAFD"),
    ("Late", "Wall Street slides; Dow -1,084"),
]

REGIONS = [
    ("EUROPE", 11, (38, 84, 138)),
    ("THE AMERICAS", 7, (28, 120, 80)),
    ("ASIA-PACIFIC", 19, (168, 32, 40)),
    ("MIDEAST", 4, (176, 132, 40)),
    ("AFRICA", 3, (24, 110, 110)),
    ("OCEANIA", 2, (120, 80, 160)),
    ("WORLD", 2, (96, 92, 84)),
]

HEROES = [
    {"num": 1, "place": "ODISHA", "topic": "STORM",
     "head": "Akvan comes ashore on the Odisha coast",
     "dek": "Cyclone Akvan crossed the coast near Gopalpur at noon, "
            "winds 90-100 km/h gusting to 110. Three hundred thousand "
            "people are out of harm's way, 423 rescue teams deployed, "
            "red alerts in 11 districts.",
     "src": "IMD · THE HINDU"},
    {"num": 2, "place": "RIYADH", "topic": "ATTACK",
     "head": "Houthi missile hits Riyadh's KAFD financial district",
     "dek": "A Houthi missile damaged a wealth-fund tower in the "
            "financial district, one of Riyadh's tallest. No casualties "
            "are reported, as air defences answered the strike.",
     "src": "ARAB NEWS · REUTERS"},
    {"num": 3, "place": "SHENZHEN", "topic": "DIPLOMACY",
     "head": "Trump, Xi and Putin issue a joint declaration",
     "dek": "No big peace deal from the trilateral's second day. Trump "
            "says the Iran war call waits until 2027, rates the summit "
            "'12 out of 10', and Putin may attend December's G20 in Miami.",
     "src": "REUTERS · AP"},
]

PICTURED = [
    {"num": 4, "place": "KERCH STRAIT", "topic": "WAR",
     "head": "Crimean Bridge hit a third time this week; rail halted",
     "dek": "A Ukrainian naval drone strike disrupted rail traffic on "
            "the bridge. Rail partly resumes; Putin vows retaliation, "
            "and Kyiv was hit by drones.",
     "src": "CLAIM · KYIV"},
    {"num": 5, "place": "SHENZHEN", "topic": "SUMMIT",
     "head": "APEC leaders meet in Shenzhen",
     "dek": "Leaders gather in China for the APEC summit. Xi urges "
            "APEC economies to back open trade and new technology.",
     "src": "AP"},
    {"num": 6, "place": "ANTALYA", "topic": "CLIMATE",
     "head": "COP31's final day: fossil fuels cut from the text",
     "dek": "A revised draft strips out every fossil-fuel phase-out "
            "pledge. Delegates push back as the final plenary meets today.",
     "src": "UNFCCC · AFP"},
    {"num": 7, "place": "THE HAGUE", "topic": "LAW",
     "head": "The world answers the genocide verdict",
     "dek": "Britain expels Myanmar's defence attache and seeks an "
            "urgent Security Council meeting. The Gambia hails a "
            "'historic' verdict.",
     "src": "AP · BBC"},
    {"num": 8, "place": "NEW YORK", "topic": "MARKETS",
     "head": "Anthropic's debut can't stop the slide",
     "dek": "The Dow fell 1,084 points, the S&P 2.02% and the Nasdaq "
            "2.25%, as the AI selloff bit a day after Anthropic's "
            "record debut.",
     "src": "BLOOMBERG"},
    {"num": 9, "place": "VICE CITY", "topic": "GAMES",
     "head": "GTA VI passes The Odyssey's $1.84bn",
     "dek": "Launch-day sales top The Odyssey's $1.80bn global run, "
            "Sensor Tower estimates. Reviews land; Rockstar calls it "
            "the highest-rated game ever.",
     "src": "SENSOR TOWER"},
    {"num": 10, "place": "SPACE", "topic": "SCIENCE",
     "head": "NASA confirms Voyager 1's light-day milestone",
     "dek": "The probe is now a full light-day from Earth - 16 billion "
            "miles out, the farthest any human-made object has ever "
            "travelled.",
     "src": "NASA · JPL"},
    {"num": 11, "place": "SEOUL", "topic": "LAW",
     "head": "South Korea clears ex-PM Han",
     "dek": "The Supreme Court overturns former prime minister Han "
            "Duck-soo's conviction, in the case tied to the 2024 "
            "martial-law declaration.",
     "src": "KOREA TIMES"},
    {"num": 12, "place": "SUVA", "topic": "CLIMATE",
     "head": "Fiji declares a national disaster over drought",
     "dek": "Fiji declares a national disaster over drought and water "
            "shortages. El Nino leaves water short across the islands.",
     "src": "AFP"},
    {"num": 13, "place": "VIENNA", "topic": "SECURITY",
     "head": "North Korea expands uranium enrichment at Yongbyon",
     "dek": "The UN watchdog reports growth at the nuclear site, in "
            "its latest assessment of the Yongbyon complex.",
     "src": "IAEA"},
    {"num": 14, "place": "CARACAS", "topic": "DIPLOMACY",
     "head": "US and Venezuela restore military cooperation",
     "dek": "The two countries sign an agreement to work together "
            "again, restoring a military channel closed for years.",
     "src": "REUTERS"},
    {"num": 15, "place": "HORMUZ", "topic": "CONFLICT",
     "head": "ADNOC vessel attacked in the Strait of Hormuz",
     "dek": "One crew member is missing after the strike on the ADNOC "
            "vessel in the strait.",
     "src": "REUTERS"},
    {"num": 16, "place": "WELLINGTON", "topic": "CRICKET",
     "head": "Day two at the Basin: Nicholls' 113 anchors New Zealand",
     "dek": "New Zealand build on Henry Nicholls' unbeaten 113 as "
            "India hunt early wickets, in the first Test at the Basin "
            "Reserve.",
     "src": "AP"},
]

BRIEFS = [
    "17 BRUSSELS — EU-UK summit opens",
    "18 NEW DELHI — Modi meets William and Kate",
    "19 DHAKA — Fire at the Yunus home; arson feared",
    "20 MUMBAI — Sensex +1.21%, Nifty +1.14% on the day",
    "21 TOKYO — Hayabusa2 gives up landing; mission rewritten",
    "22 BERLIN — Coalition of the Willing meets in Berlin",
    "23 BERLIN — Merz hosts Qatar's emir in Berlin",
    "24 NEW DELHI — Pakistan minister leads delegation to Delhi for SCO",
    "25 MANILA — Philippines-Chile trade deal signed",
    "26 MANILA — Musk plans Philippines projects",
    "27 HONG KONG — India beats Malaysia, Asian Hockey Trophy opens",
    "28 IPOH — Harimau Shakti exercise opens in Ipoh",
    "29 NEW DELHI — India's electronics exports jump 44%",
    "30 NEW DELHI — ICMR completes 100 tech transfers",
    "31 NEW DELHI — India unveils its first bird-flu vaccine",
    "32 GENEVA — World Children's Day marked worldwide",
    "33 EUROPE — Youth anti-war protests across Europe",
    "34 BRUSSELS — EU delays its methane rules by 24 months",
    "35 COLOGNE — Bayern Munich beat Koln 3-0",
    "36 U17 CUP — Argentina 0-2 Australia at the U17 Cup",
    "37 WASHINGTON — Jobless claims come in at 203,000",
    "38 STRASBOURG — NATO's assembly opens its 72nd session",
    "39 HANOI — Azerbaijan's Aliyev visits Vietnam",
    "40 MARKETS — Crude futures fall over 3%",
    "41 KHARTOUM — Sudan army: two-year El Obeid siege broken",
    "42 MOGADISHU — Somalia gives UAE ambassador 72 hours to leave",
    "43 SAN SALVADOR — Migrant boat capsizes off El Salvador; dozens missing",
    "44 PORT-AU-PRINCE — Haiti approves Salvadoran troop deal vs gangs",
    "45 ARABIAN SEA — Amur falcons cross the Arabian Sea",
    "46 NEW YORK — Al-Saadi appears in a New York court over a UK plot",
    "47 KYIV — Witkoff and Kushner brief Zelenskyy",
    "48 BEIJING — Xi urges APEC to back open trade, new tech",
]

# Coarse world map, '.' sea, '#' land (48 cols x 13 rows).
MAP_ROWS = [
    "................................................",
    "..############....................................",
    "..##############........####.......................",
    "...###########.........######....##########.........",
    "....########...........######..##############.......",
    ".....######....###......#####..################.....",
    "......####....#####.....####...###############......",
    ".......###....######....###.....##########..##......",
    "........##.....#####....##.......########...........",
    ".........#......####.............######...###.......",
    "...............###..............#####.....###.......",
    "...............##...............####......##........",
    "...............#................##.................",
]

PINS = {
    4: (0.52, 0.22), 5: (0.80, 0.42), 6: (0.50, 0.30),
    7: (0.47, 0.18), 8: (0.22, 0.28), 9: (0.20, 0.38),
    10: (0.17, 0.36), 11: (0.86, 0.32), 12: (0.95, 0.62),
    13: (0.49, 0.22), 14: (0.27, 0.48), 15: (0.66, 0.42),
    16: (0.96, 0.72),
}


def draw_map(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(22, 30, 48))
    rows = len(MAP_ROWS)
    cols = len(MAP_ROWS[0])
    cw, ch = w / cols, h / rows
    for r, row in enumerate(MAP_ROWS):
        for c, ch_ in enumerate(row):
            if ch_ == "#":
                cx = x + c * cw + cw / 2
                cy = y + r * ch + ch / 2
                d.ellipse([cx - 2, cy - 2, cx + 2, cy + 2],
                          fill=(180, 190, 205))
    for num, (fx, fy) in sorted(PINS.items()):
        px, py = x + fx * w, y + fy * h
        d.ellipse([px - 9, py - 9, px + 9, py + 9], fill=RED,
                  outline=(255, 255, 255), width=2)
        label = str(num)
        tw = d.textlength(label, font=sans(11, True))
        d.text((px - tw / 2, py - 6), label, font=sans(11, True),
               fill=(255, 255, 255))


def hero_panel(d, item, x, y, w, img_h, head_size, dek_size, accent=GREEN):
    scene(d, item["num"], x, y, w, img_h)
    yy = y + img_h + 8
    kicker(d, x, yy, item["num"], item["place"], item["topic"],
           item["src"], w, accent=accent)
    yy += 26
    yy = block(d, x, yy, item["head"], serif(head_size, True), w,
               head_size + 6, max_lines=2)
    yy = block(d, x, yy + 2, item["dek"], sans(dek_size), w, dek_size + 4,
               color=(52, 48, 42), max_lines=2)
    return yy


def pic_panel(d, item, x, y, w, img_h, head_size, dek_size):
    scene(d, item["num"], x, y, w, img_h)
    yy = y + img_h + 6
    kicker(d, x, yy, item["num"], item["place"], item["topic"],
           item["src"], w, size=15 if w >= 400 else 13)
    yy += 22
    yy = block(d, x, yy, item["head"], sans(head_size, True), w,
               head_size + 4, max_lines=2)
    yy = block(d, x, yy + 1, item["dek"], sans(dek_size), w, dek_size + 3,
               color=(52, 48, 42), max_lines=2)
    return yy


def main():
    im = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(im)

    # --- top bar + double rule ---
    d.text((M, 30), "ONE DAY OF WORLD NEWS, ONE PICTURE",
           font=sans(22, True), fill=RED)
    right = "48 STORIES - 7 REGIONS - EVERY ONE FROM THIS FRIDAY"
    d.text((W - M - d.textlength(right, font=sans(22, True)), 30), right,
           font=sans(22, True), fill=INK)
    rule(d, 62, width=3)
    rule(d, 68, width=1)

    # --- masthead, serif with double rule ---
    d.text((M, 76), "Friday 20 November 2026",
           font=serif(106, True), fill=INK)
    rule(d, 192, width=3)
    rule(d, 198, width=1)

    # --- UTC timeline ---
    ty = 208
    d.rectangle([M, ty, M + 118, ty + 58], fill=RED)
    d.text((M + 12, ty + 6), "THE DAY", font=sans(20, True),
           fill=(255, 255, 255))
    d.text((M + 12, ty + 30), "IN UTC", font=sans(20, True),
           fill=(255, 255, 255))
    col_w = (W - 2 * M - 130) / len(TIMELINE)
    for k, (when, what) in enumerate(TIMELINE):
        cx = M + 130 + k * col_w
        d.text((cx, ty + 2), when, font=sans(18, True), fill=RED)
        block(d, cx, ty + 26, what, sans(16), col_w - 12, 19, max_lines=2)
    rule(d, 272, width=1)

    # --- region strip ---
    ry = 280
    total = sum(c for _, c, _ in REGIONS)
    rx = M
    for name, count, col in REGIONS:
        seg = (W - 2 * M) * count / total
        d.rectangle([rx, ry, rx + seg, ry + 32], fill=col)
        label = "%s %d" % (name, count)
        size = 17
        while size > 11 and d.textlength(label, font=sans(size, True)) > seg - 6:
            size -= 1
        if d.textlength(label, font=sans(size, True)) > seg - 6:
            label = "%s %d" % (name[:2], count)
        tw = d.textlength(label, font=sans(size, True))
        d.text((rx + (seg - tw) / 2, ry + 8), label, font=sans(size, True),
               fill=(255, 255, 255))
        rx += seg

    # --- hero 1: full width (Akvan) ---
    y = hero_panel(d, HEROES[0], M, 322, W - 2 * M, 130, 40, 20)
    rule(d, y + 8, width=1)

    # --- heroes 2 + 3: two columns ---
    hy = y + 18
    hw = (W - 2 * M - 18) // 2
    y2 = hero_panel(d, HEROES[1], M, hy, hw, 96, 30, 17)
    y3 = hero_panel(d, HEROES[2], M + hw + 18, hy, hw, 96, 30, 17)
    y = max(y2, y3)
    rule(d, y + 8, width=1)

    # --- pictured row 1: 3 panels ---
    py = y + 18
    pw = (W - 2 * M - 2 * 18) // 3
    ends = []
    for k in range(3):
        ends.append(pic_panel(d, PICTURED[k], M + k * (pw + 18), py, pw,
                              64, 19, 14))
    y = max(ends)

    # --- pictured row 2: 5 panels ---
    py = y + 10
    pw5 = (W - 2 * M - 4 * 15) // 5
    ends = []
    for k in range(5):
        ends.append(pic_panel(d, PICTURED[3 + k], M + k * (pw5 + 15), py,
                              pw5, 52, 18, 13))
    y = max(ends)

    # --- pictured row 3: 5 panels ---
    py = y + 10
    ends = []
    for k in range(5):
        ends.append(pic_panel(d, PICTURED[8 + k], M + k * (pw5 + 15), py,
                              pw5, 52, 18, 13))
    y = max(ends)

    # --- map + briefs ---
    my = y + 12
    d.text((M, my), "WHERE IT HAPPENED", font=sans(20, True), fill=RED)
    bx = M + 580
    d.text((bx, my), "ALSO ON FRIDAY 20 NOVEMBER - 32 MORE STORIES",
           font=sans(18, True), fill=RED)
    map_y = my + 28
    draw_map(d, M, map_y, 560, 104)
    bcol_w = (W - M - bx - 2 * 14) // 3
    for col in range(3):
        cx = bx + col * (bcol_w + 14)
        for r in range(11):
            idx = col * 11 + r
            if idx >= len(BRIEFS):
                break
            txt = fit1(d, BRIEFS[idx], sans(11), bcol_w)
            d.text((cx, map_y + r * 11), txt, font=sans(11), fill=INK)

    # --- date check ---
    dy = map_y + 112
    d.rectangle([M, dy, M + 150, dy + 62], fill=RED)
    d.text((M + 14, dy + 12), "DATE", font=sans(18, True),
           fill=(255, 255, 255))
    d.text((M + 14, dy + 33), "CHECK", font=sans(18, True),
           fill=(255, 255, 255))
    d.rectangle([M, dy, W - M, dy + 62], outline=RED, width=2)
    check = ("Left out - they broke before Friday: the ICJ genocide "
             "ruling on Myanmar itself (Thursday 19 Nov) - Friday's news "
             "is the world's answer to it - Denmark's Greenland-US pact "
             "(19 Nov) - Anthropic's $81.34bn IPO (19 Nov); its first "
             "trading day was Thursday - Germany's electricity-tax cut "
             "(18 Nov) - the Crimean Bridge span collapse (17-18 Nov). "
             "Not yet: the trilateral's first meeting was 19 Nov; the "
             "joint declaration is Friday's.")
    block(d, M + 164, dy + 5, check, sans(14), W - 2 * M - 164, 18,
          max_lines=3)

    # --- footer ---
    fy = dy + 70
    d.text((M, fy), "Every story here happened, or was first reported, on "
                    "Friday 20 November 2026, in some time zone. Disputed "
                    "claims are attributed, not stated as fact.",
           font=serif(15, italic=True), fill=INK)
    d.text((M, fy + 20), "Sources: Reuters - AP - AFP - BBC - Bloomberg - "
                         "IMD - NASA - IAEA - The Hindu - Arab News - "
                         "Sensor Tower. Original drawings, drawn for this page.",
           font=sans(14), fill=GREY)

    speckle(im)
    im = im.resize((1024, 1024), Image.LANCZOS)
    im.save("entry.png")
    print("saved entry.png 1024x1024")


if __name__ == "__main__":
    main()
