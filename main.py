"""THE WORLD TODAY - Tuesday 24 November 2026.

A pure Python 3.13 stdlib program that draws a 1024x1024 newspaper
front page summing up the world news of Tuesday 24 November 2026 and
writes it as /output/entry.png. No network, no randomness, no clock:
two runs write byte-identical files.

The page is drawn with a hand-designed 8x12 bitmap font and simple
flat-shape illustrations (a warship, a jet, a chip, a factory, a
gavel, scales of justice, a globe). The PNG is encoded by hand with
zlib and struct.
"""

import os
import struct
import zlib

W = 1024
H = 1024

PAPER = (253, 251, 244)
INK = (18, 18, 18)
RED = (176, 32, 32)
BLUE = (36, 88, 148)
SKY = (208, 226, 240)
SEA = (44, 96, 158)
TEAL = (18, 104, 102)
GOLD = (198, 148, 38)
GREY = (112, 112, 108)
LIGHT = (232, 227, 212)
GREEN = (46, 122, 62)
DARK = (44, 48, 58)
BROWN = (122, 82, 42)
ORANGE = (214, 110, 30)

# ---------------------------------------------------------------- font
# Each glyph is 12 rows of 8 cells ('#' = ink, '.' = empty).
# Capitals fill rows 1..10. Lowercase letters sit on the x-height
# (rows 4..10); ascenders reach row 1, descenders reach row 11.
# Digit 0 carries a slash so it never reads as O; digits 2 and 7
# carry full top bars; lowercase c is x-height only.

FONT = {
    "A": ("........", "..####..", ".##..##.", "##....##", "##....##",
          "########", "##....##", "##....##", "##....##", "##....##",
          "##....##", "........"),
    "B": ("........", "######..", "##....##", "##....##", "##....##",
          "######..", "##....##", "##....##", "##....##", "##....##",
          "######..", "........"),
    "C": ("........", "..####..", ".##..##.", "##....##", "##......",
          "##......", "##......", "##......", "##....##", ".##..##.",
          "..####..", "........"),
    "D": ("........", "#####...", "##...##.", "##....##", "##....##",
          "##....##", "##....##", "##....##", "##....##", "##...##.",
          "#####...", "........"),
    "E": ("........", "########", "##......", "##......", "##......",
          "#####...", "##......", "##......", "##......", "##......",
          "########", "........"),
    "F": ("........", "########", "##......", "##......", "##......",
          "#####...", "##......", "##......", "##......", "##......",
          "##......", "........"),
    "G": ("........", "..####..", ".##..##.", "##....##", "##......",
          "##..####", "##....##", "##....##", "##....##", ".##..##.",
          "..###...", "........"),
    "H": ("........", "##....##", "##....##", "##....##", "##....##",
          "########", "##....##", "##....##", "##....##", "##....##",
          "##....##", "........"),
    "I": ("........", "..####..", "...##...", "...##...", "...##...",
          "...##...", "...##...", "...##...", "...##...", "...##...",
          "..####..", "........"),
    "J": ("........", "...####.", "....##..", "....##..", "....##..",
          "....##..", "....##..", "....##..", "##..##..", "##..##..",
          ".####...", "........"),
    "K": ("........", "##....##", "##...##.", "##..##..", "##.##...",
          "####....", "##.##...", "##..##..", "##...##.", "##....##",
          "##....##", "........"),
    "L": ("........", "##......", "##......", "##......", "##......",
          "##......", "##......", "##......", "##......", "##......",
          "########", "........"),
    "M": ("........", "##....##", "###..###", "##.##.##", "##.##.##",
          "##....##", "##....##", "##....##", "##....##", "##....##",
          "##....##", "........"),
    "N": ("........", "##....##", "###...##", "##.#..##", "##..#.##",
          "##...###", "##....##", "##....##", "##....##", "##....##",
          "##....##", "........"),
    "O": ("........", "..####..", ".##..##.", "##....##", "##....##",
          "##....##", "##....##", "##....##", "##....##", ".##..##.",
          "..####..", "........"),
    "P": ("........", "######..", "##....##", "##....##", "##....##",
          "######..", "##......", "##......", "##......", "##......",
          "##......", "........"),
    "Q": ("........", "..####..", ".##..##.", "##....##", "##....##",
          "##....##", "##....##", "##..#.##", "##...###", ".##..##.",
          "..###.##", "........"),
    "R": ("........", "######..", "##....##", "##....##", "##....##",
          "######..", "##.##...", "##..##..", "##...##.", "##....##",
          "##....##", "........"),
    "S": ("........", "..####..", ".##..##.", "##....##", "##......",
          ".####...", ".....##.", "......##", "##....##", ".##..##.",
          "..####..", "........"),
    "T": ("........", "########", "...##...", "...##...", "...##...",
          "...##...", "...##...", "...##...", "...##...", "...##...",
          "...##...", "........"),
    "U": ("........", "##....##", "##....##", "##....##", "##....##",
          "##....##", "##....##", "##....##", "##....##", ".##..##.",
          "..####..", "........"),
    "V": ("........", "##....##", "##....##", "##....##", "##....##",
          "##....##", "##....##", ".##..##.", ".##..##.", "..####..",
          "...##...", "........"),
    "W": ("........", "##....##", "##....##", "##....##", "##....##",
          "##.##.##", "##.##.##", "###..###", "###..###", "##....##",
          "##....##", "........"),
    "X": ("........", "##....##", "##....##", ".##..##.", "..####..",
          "...##...", "..####..", ".##..##.", "##....##", "##....##",
          "##....##", "........"),
    "Y": ("........", "##....##", "##....##", "##....##", ".##..##.",
          "..####..", "...##...", "...##...", "...##...", "...##...",
          "...##...", "........"),
    "Z": ("........", "########", "......##", ".....##.", "....##..",
          "...##...", "..##....", ".##.....", "##......", "##......",
          "########", "........"),
    "0": ("........", "..####..", ".##..##.", "##...###", "##..####",
          "##.##.##", "####..##", "###...##", "##....##", ".##..##.",
          "..####..", "........"),
    "1": ("........", "...##...", "..###...", "...##...", "...##...",
          "...##...", "...##...", "...##...", "...##...", "...##...",
          "..####..", "........"),
    "2": ("........", "..####..", ".##..##.", "......##", ".....##.",
          "....##..", "...##...", "..##....", ".##.....", "##......",
          "########", "........"),
    "3": ("........", "..####..", ".##..##.", "......##", "......##",
          "...###..", "......##", "......##", "##....##", ".##..##.",
          "..####..", "........"),
    "4": ("........", "....##..", "...###..", "..##.#..", ".##..#..",
          "##...#..", "########", ".....#..", ".....#..", ".....#..",
          ".....#..", "........"),
    "5": ("........", "########", "##......", "##......", "######..",
          ".....##.", "......##", "......##", "##....##", ".##..##.",
          "..####..", "........"),
    "6": ("........", "..####..", ".##..##.", "##......", "##......",
          "######..", "##....##", "##....##", "##....##", ".##..##.",
          "..####..", "........"),
    "7": ("........", "########", "......##", ".....##.", "....##..",
          "...##...", "...##...", "..##....", "..##....", "..##....",
          "..##....", "........"),
    "8": ("........", "..####..", ".##..##.", "##....##", "##....##",
          "..####..", "##....##", "##....##", "##....##", ".##..##.",
          "..####..", "........"),
    "9": ("........", "..####..", ".##..##.", "##....##", "##....##",
          ".######.", "......##", "......##", "##....##", ".##..##.",
          "..####..", "........"),
    "a": ("........", "........", "........", "........", "..####..",
          ".##..##.", "......##", "..######", "##....##", "##....##",
          ".######.", "........"),
    "b": ("........", "##......", "##......", "##......", "##......",
          "######..", "##....##", "##....##", "##....##", "##....##",
          "######..", "........"),
    "c": ("........", "........", "........", "........", "..####..",
          ".##..##.", "##......", "##......", "##......", ".##..##.",
          "..####..", "........"),
    "d": ("........", "......##", "......##", "......##", "......##",
          "..######", "##....##", "##....##", "##....##", "##....##",
          "..######", "........"),
    "e": ("........", "........", "........", "........", "..####..",
          ".##..##.", "##....##", "########", "##......", ".##..##.",
          "..####..", "........"),
    "f": ("........", "...###..", "..##....", "..##....", "..##....",
          "#######.", "..##....", "..##....", "..##....", "..##....",
          "..##....", "........"),
    "g": ("........", "........", "........", "........", "..######",
          "##....##", "##....##", "##....##", "##....##", "..######",
          "......##", "..####.."),
    "h": ("........", "##......", "##......", "##......", "##......",
          "######..", "##....##", "##....##", "##....##", "##....##",
          "##....##", "........"),
    "i": ("........", "...##...", "........", "...##...", "...##...",
          "...##...", "...##...", "...##...", "...##...", "...##...",
          "..####..", "........"),
    "j": ("........", "....##..", "........", "....##..", "....##..",
          "....##..", "....##..", "....##..", "....##..", "##..##..",
          ".####...", "........"),
    "k": ("........", "##......", "##......", "##......", "##......",
          "##...##.", "##..##..", "####....", "##..##..", "##...##.",
          "##....##", "........"),
    "l": ("........", "..##....", "..##....", "..##....", "..##....",
          "..##....", "..##....", "..##....", "..##....", "..##....",
          ".####...", "........"),
    "m": ("........", "........", "........", "........", "........",
          "###.###.", "##.#.##.", "##.#.##.", "##.#.##.", "##.#.##.",
          "##.#.##.", "........"),
    "n": ("........", "........", "........", "........", "........",
          "######..", "##....##", "##....##", "##....##", "##....##",
          "##....##", "........"),
    "o": ("........", "........", "........", "........", "..####..",
          ".##..##.", "##....##", "##....##", "##....##", ".##..##.",
          "..####..", "........"),
    "p": ("........", "........", "........", "........", "........",
          "######..", "##....##", "##....##", "##....##", "######..",
          "##......", "##......"),
    "q": ("........", "........", "........", "........", "........",
          "..######", "##....##", "##....##", "##....##", "..######",
          "......##", "......##"),
    "r": ("........", "........", "........", "........", "........",
          "##.###..", "###..##.", "##......", "##......", "##......",
          "##......", "........"),
    "s": ("........", "........", "........", "........", "..####..",
          ".##..##.", "##......", "..####..", "......##", ".##..##.",
          "..####..", "........"),
    "t": ("........", "...##...", "...##...", "...##...", "...##...",
          "######..", "...##...", "...##...", "...##...", "...##...",
          "..###...", "........"),
    "u": ("........", "........", "........", "........", "........",
          "##....##", "##....##", "##....##", "##....##", "##....##",
          ".######.", "........"),
    "v": ("........", "........", "........", "........", "........",
          "##....##", "##....##", "##....##", "##....##", ".##..##.",
          "..####..", "........"),
    "w": ("........", "........", "........", "........", "........",
          "##....##", "##....##", "##.##.##", "##.##.##", "###..###",
          "##....##", "........"),
    "x": ("........", "........", "........", "........", "........",
          "##....##", ".##..##.", "..####..", ".##..##.", "##....##",
          "##....##", "........"),
    "y": ("........", "........", "........", "........", "........",
          "##....##", "##....##", "##....##", ".##..##.", "..####..",
          "...##...", "..##...."),
    "z": ("........", "........", "........", "........", "........",
          "########", ".....##.", "....##..", "...##...", "..##....",
          "########", "........"),
    " ": ("........", "........", "........", "........", "........",
         "........", "........", "........", "........", "........",
         "........", "........"),
    ".": ("........", "........", "........", "........", "........",
         "........", "........", "........", "........", "..##....",
         "..##....", "........"),
    ",": ("........", "........", "........", "........", "........",
         "........", "........", "........", "........", "..##....",
         "..##....", ".##....."),
    "'": ("........", "...##...", "...##...", "..##....", "........",
         "........", "........", "........", "........", "........",
         "........", "........"),
    "-": ("........", "........", "........", "........", "........",
         "........", ".######.", "........", "........", "........",
         "........", "........"),
    ":": ("........", "........", "........", "........", "..##....",
         "..##....", "........", "........", "..##....", "..##....",
         "........", "........"),
    "!": ("........", "...##...", "...##...", "...##...", "...##...",
          "...##...", "...##...", "...##...", "...##...", "........",
          "..##....", "........"),
    "?": ("........", "..####..", ".##..##.", "......##", ".....##.",
          "....##..", "...##...", "........", "...##...", "...##...",
          "........", "........"),
    "(": ("........", "....##..", "...##...", "..##....", "..##....",
         "..##....", "..##....", "..##....", "..##....", "...##...",
         "....##..", "........"),
    ")": ("........", "..##....", "...##...", "....##..", "....##..",
         "....##..", "....##..", "....##..", "....##..", "...##...",
         "..##....", "........"),
    "/": ("........", "......##", ".....##.", ".....##.", "....##..",
         "...##...", "...##...", "..##....", ".##.....", ".##.....",
         "##......", "........"),
    "&": ("........", "..####..", ".##..##.", ".##..##.", "..####..",
         ".##.##..", "##..##..", "##...##.", ".##..##.", "..####.#",
         "........", "........"),
}

# ---------------------------------------------------------------- canvas

PIX = bytearray(W * H * 3)


def fill(color):
    r, g, b = color
    PIX[0::3] = bytes([r]) * (W * H)
    PIX[1::3] = bytes([g]) * (W * H)
    PIX[2::3] = bytes([b]) * (W * H)


def px(x, y, color):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        PIX[i], PIX[i + 1], PIX[i + 2] = color


def rect(x, y, w, h, color):
    x0 = max(0, x)
    y0 = max(0, y)
    x1 = min(W, x + w)
    y1 = min(H, y + h)
    for yy in range(y0, y1):
        base = (yy * W + x0) * 3
        for xx in range(x0, x1):
            i = base + (xx - x0) * 3
            PIX[i], PIX[i + 1], PIX[i + 2] = color


def hline(x, y, length, color, thick=1):
    rect(x, y, length, thick, color)


def vline(x, y, length, color, thick=1):
    rect(x, y, thick, length, color)


def line(x0, y0, x1, y1, color, thick=1):
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    while True:
        rect(x0 - thick // 2, y0 - thick // 2, thick, thick, color)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy


def circle(cx, cy, r, color):
    for yy in range(cy - r, cy + r + 1):
        for xx in range(cx - r, cx + r + 1):
            if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                px(xx, yy, color)


def disc(cx, cy, r, color):
    circle(cx, cy, r, color)


def triangle(x1, y1, x2, y2, x3, y3, color):
    ys = sorted([y1, y2, y3])
    for yy in range(ys[0], ys[2] + 1):
        xs = []
        for (ax, ay, bx, by) in ((x1, y1, x2, y2), (x2, y2, x3, y3),
                                 (x3, y3, x1, y1)):
            if ay == by:
                continue
            if min(ay, by) <= yy <= max(ay, by):
                t = (yy - ay) / (by - ay)
                xs.append(ax + t * (bx - ax))
        if len(xs) >= 2:
            xa, xb = int(min(xs)), int(max(xs))
            hline(xa, yy, xb - xa + 1, color)


def polygon(points, color):
    ys = [p[1] for p in points]
    for yy in range(min(ys), max(ys) + 1):
        xs = []
        n = len(points)
        for k in range(n):
            ax, ay = points[k]
            bx, by = points[(k + 1) % n]
            if ay == by:
                continue
            if min(ay, by) <= yy < max(ay, by):
                t = (yy - ay) / (by - ay)
                xs.append(ax + t * (bx - ax))
        if len(xs) >= 2:
            xs.sort()
            for j in range(0, len(xs) - 1, 2):
                xa, xb = int(xs[j]), int(xs[j + 1])
                hline(xa, yy, xb - xa + 1, color)


# ---------------------------------------------------------------- text

def text_width(s, scale):
    return len(s) * 9 * scale - scale


def draw_text(x, y, s, scale, color):
    for ci, ch in enumerate(s):
        glyph = FONT.get(ch)
        if glyph is None:
            continue
        gx = x + ci * 9 * scale
        for row in range(12):
            bits = glyph[row]
            for col in range(8):
                if bits[col] == "#":
                    rect(gx + col * scale, y + row * scale,
                         scale, scale, color)


def draw_text_center(cx, y, s, scale, color):
    draw_text(cx - text_width(s, scale) // 2, y, s, scale, color)


def wrap(s, max_width, scale):
    """Greedy word wrap; returns a list of lines that fit max_width."""
    unit = 9 * scale
    words = s.split(" ")
    lines = []
    cur = ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if len(trial) * unit - scale <= max_width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_para(x, y, s, scale, color, max_width, step):
    lines = wrap(s, max_width, scale)
    for i, ln in enumerate(lines):
        draw_text(x, y + i * step, ln, scale, color)
    return len(lines)

# ---------------------------------------------------------------- pictures


def draw_ship(x, y, w, h):
    """Warship on the sea, drones above. Panel x,y,w,h."""
    rect(x, y, w, h, SKY)
    sea_y = y + int(h * 0.62)
    rect(x, sea_y, w, h - int(h * 0.62), SEA)
    # waves
    for wy in (sea_y + 14, sea_y + 34, sea_y + 54):
        for wx in range(x + 8, x + w - 8, 46):
            hline(wx, wy, 26, PAPER, 2)
    # hull
    hy = sea_y - 26
    polygon([(x + 30, hy), (x + w - 26, hy), (x + w - 58, hy + 30),
             (x + 52, hy + 30)], DARK)
    rect(x + 34, hy - 6, w - 66, 6, RED)
    # superstructure + funnel + mast
    rect(x + 108, hy - 44, 92, 44, INK)
    rect(x + 216, hy - 58, 26, 58, DARK)
    vline(x + 150, hy - 78, 36, INK, 3)
    # bridge windows
    for wx in range(x + 116, x + 192, 18):
        rect(wx, hy - 38, 10, 8, SKY)
    # smoke
    for cx, cy, r in ((x + 229, hy - 70, 9), (x + 240, hy - 84, 12),
                      (x + 254, hy - 98, 9)):
        disc(cx, cy, r, GREY)
    # drones: small dark crosses with rotors
    for dx, dy in ((x + 60, y + 22), (x + 150, y + 14), (x + 250, y + 26)):
        rect(dx - 5, dy - 2, 10, 4, INK)
        rect(dx - 2, dy - 5, 4, 10, INK)
        hline(dx - 9, dy - 8, 18, INK, 2)
    # blast burst at the bow
    bx, by = x + w - 44, hy + 8
    for ang in range(0, 360, 45):
        import math
        ex = bx + int(16 * math.cos(math.radians(ang)))
        ey = by + int(16 * math.sin(math.radians(ang)))
        line(bx, by, ex, ey, ORANGE, 3)
    disc(bx, by, 7, GOLD)


def draw_jet(x, y, w, h):
    """Jet over an island. Panel x,y,w,h."""
    rect(x, y, w, h, SKY)
    # island bottom right
    polygon([(x + 150, y + h), (x + 178, y + h - 26), (x + 232, y + h - 34),
             (x + w - 8, y + h - 22), (x + w - 8, y + h)], GREEN)
    rect(x + 196, y + h - 44, 16, 12, PAPER)
    rect(x + 222, y + h - 40, 12, 10, PAPER)
    # sea strip
    rect(x, y + h - 12, w, 12, SEA)
    # jet: fuselage, wings, tail
    jx, jy = x + 52, y + 26
    polygon([(jx, jy + 6), (jx + 96, jy + 10), (jx + 112, jy + 14),
             (jx + 96, jy + 18), (jx, jy + 20)], INK)
    polygon([(jx + 34, jy + 10), (jx + 62, jy - 12), (jx + 74, jy + 10)],
            DARK)
    polygon([(jx + 40, jy + 18), (jx + 58, jy + 34), (jx + 72, jy + 18)],
            DARK)
    polygon([(jx + 6, jy + 8), (jx + 18, jy - 8), (jx + 26, jy + 8)], DARK)
    disc(jx + 104, jy + 13, 3, RED)
    # red dashed line from jet toward the island (flight path)
    for t in range(0, 9):
        px(x + 130 + t * 12, y + 40 + t * 3, RED)
        px(x + 131 + t * 12, y + 40 + t * 3, RED)
        px(x + 130 + t * 12, y + 41 + t * 3, RED)
    # shelter arrow pointing down to the island
    line(x + 236, y + 12, x + 236, y + 34, RED, 3)
    triangle(x + 228, y + 32, x + 244, y + 32, x + 236, y + 44, RED)


def draw_chip(x, y, w, h):
    """A processor chip with gold pins and a rising arrow."""
    rect(x, y, w, h, LIGHT)
    cx, cy = x + 96, y + h // 2
    # pins
    for k in range(5):
        rect(cx - 40, cy - 26 + k * 13, 12, 5, GOLD)
        rect(cx + 28, cy - 26 + k * 13, 12, 5, GOLD)
        rect(cx - 26 + k * 13, cy - 34, 5, 10, GOLD)
        rect(cx - 26 + k * 13, cy + 24, 5, 10, GOLD)
    # chip body
    rect(cx - 28, cy - 28, 56, 56, GREEN)
    rect(cx - 28, cy - 28, 56, 5, (28, 88, 46))
    rect(cx - 18, cy - 18, 36, 36, (22, 74, 40))
    rect(cx - 9, cy - 9, 18, 18, GOLD)
    # rising arrow on the right
    ax = x + w - 52
    line(ax, y + h - 14, ax, y + 18, RED, 4)
    triangle(ax - 10, y + 26, ax + 10, y + 26, ax, y + 10, RED)


def draw_factory(x, y, w, h):
    """A plant with a chimney, and a red STOP sign."""
    rect(x, y, w, h, LIGHT)
    # factory block with sawtooth roof
    bx, by = x + 18, y + h - 44
    rect(bx, by, 130, 44, GREY)
    polygon([(bx, by), (bx + 32, by - 14), (bx + 64, by),
             (bx + 96, by - 14), (bx + 130, by)], DARK)
    # windows
    for wx in (bx + 12, bx + 46, bx + 80, bx + 108):
        rect(wx, by + 12, 14, 14, SKY)
    # chimney
    rect(bx + 132, by - 26, 18, 70, DARK)
    disc(bx + 141, by - 32, 6, (150, 150, 146))
    # red octagon STOP sign
    sx, sy, r = x + w - 52, y + 32, 28
    pts = []
    import math
    for k in range(8):
        a = math.radians(22.5 + k * 45)
        pts.append((sx + int(r * math.cos(a)), sy + int(r * math.sin(a))))
    polygon(pts, RED)
    draw_text_center(sx, sy - 6, "STOP", 1, PAPER)


def draw_court(x, y, w, h):
    """A courthouse: pediment, columns and steps."""
    rect(x, y, w, h, LIGHT)
    # steps at the bottom
    rect(x + 34, y + h - 14, w - 68, 6, DARK)
    rect(x + 26, y + h - 8, w - 52, 6, GREY)
    # columns
    for cx in (x + 48, x + 94, x + 140, x + 186):
        rect(cx - 3, y + 28, 20, 4, DARK)
        rect(cx, y + 32, 14, 26, GREY)
        rect(cx - 3, y + 58, 20, 4, DARK)
    # entablature and pediment
    rect(x + 30, y + 20, w - 60, 8, DARK)
    triangle(x + 30, y + 20, x + w - 30, y + 20, x + w // 2, y + 2, DARK)
    disc(x + w // 2, y + 15, 4, GOLD)


def draw_scales(x, y, w, h):
    """Scales of justice with an exit arrow."""
    rect(x, y, w, h, LIGHT)
    cx, cy = x + 108, y + 12
    # post and base
    vline(cx, cy, 52, INK, 4)
    rect(cx - 26, cy + 52, 52, 6, INK)
    # crossbar
    hline(cx - 52, cy + 6, 104, INK, 4)
    disc(cx, cy + 6, 5, GOLD)
    # pans
    for side in (-1, 1):
        px0 = cx + side * 52
        line(px0, cy + 8, px0 - 16, cy + 32, INK, 2)
        line(px0, cy + 8, px0 + 16, cy + 32, INK, 2)
        vline(px0, cy + 8, 10, INK, 2)
        polygon([(px0 - 20, cy + 32), (px0 + 20, cy + 32),
                 (px0, cy + 48)], GOLD)
    # exit arrow bottom right
    ax, ay = x + w - 58, y + h - 26
    hline(ax, ay, 34, TEAL, 4)
    triangle(ax + 32, ay - 8, ax + 32, ay + 8, ax + 46, ay, TEAL)
    rect(ax - 40, ay - 14, 30, 28, (200, 220, 214))
    rect(ax - 34, ay - 8, 18, 16, TEAL)


def draw_globe(x, y, r):
    """Small globe: circle, meridians, equator."""
    disc(x, y, r, BLUE)
    # land blobs
    disc(x - r // 3, y - r // 4, r // 3, GREEN)
    disc(x + r // 3, y + r // 4, r // 4, GREEN)
    disc(x + r // 5, y - r // 2, r // 5, GREEN)
    # meridians and equator
    for a in range(0, 360, 6):
        import math
        px(x + int((r - 1) * math.cos(math.radians(a))),
           y + int((r - 1) * math.sin(math.radians(a))), PAPER)
    hline(x - r + 2, y, 2 * r - 4, PAPER, 1)
    for k in range(-2, 3):
        vline(x + k * r // 3, y - r + 3, 2 * r - 6, PAPER, 1)

# ---------------------------------------------------------------- page


def card(x, y, w, h, kicker, headline, summary, picture):
    rect(x, y, w, h, PAPER)
    rect(x, y, w, h, INK)  # placeholder, overwritten below
    rect(x + 2, y + 2, w - 4, h - 4, PAPER)
    # thin frame
    rect(x, y, w, 2, INK)
    rect(x, y + h - 2, w, 2, INK)
    rect(x, y, 2, h, INK)
    rect(x + w - 2, y, 2, h, INK)
    # illustration
    picture(x + 12, y + 12, w - 24, 76)
    # kicker
    draw_text(x + 12, y + 100, kicker, 1, RED)
    # headline, scale 2, 28 px line step
    lines = wrap(headline, w - 24, 2)
    hy = y + 118
    for i, ln in enumerate(lines):
        draw_text(x + 12, hy + i * 28, ln, 2, INK)
    # summary, scale 1, 14 px line step
    sy = hy + len(lines) * 28 + 8
    draw_para(x + 12, sy, summary, 1, INK, w - 24, 14)


def build():
    fill(PAPER)
    # outer border
    rect(14, 14, W - 28, 3, INK)
    rect(14, H - 17, W - 28, 3, INK)
    rect(14, 14, 3, H - 28, INK)
    rect(W - 17, 14, 3, H - 28, INK)

    # ---- masthead
    draw_text_center(W // 2, 34, "THE WORLD TODAY", 5, INK)
    draw_text_center(W // 2, 106, "TUESDAY 24 NOVEMBER 2026", 2, RED)
    rect(28, 140, W - 56, 4, RED)
    rect(28, 148, W - 56, 1, INK)

    # ---- lead story
    lx, ly, lw, lh = 28, 162, W - 56, 232
    rect(lx, ly, lw, 2, INK)
    draw_ship(lx, ly + 10, 372, lh - 22)
    tx = lx + 392
    draw_text(tx, ly + 12, "LEAD STORY", 1, RED)
    lead_head = "UKRAINE SINKS RUSSIAN WARSHIP OFF LIBYA"
    lines = wrap(lead_head, lw - 392 - 12, 3)
    hy = ly + 34
    for i, ln in enumerate(lines):
        draw_text(tx, hy + i * 46, ln, 3, INK)
    lead_sum = ("Ukrainian drones strike a Russian naval vessel in "
                "Libyan waters. Kyiv's war spreads beyond Europe.")
    draw_para(tx, hy + len(lines) * 46 + 10, lead_sum, 1, INK,
              lw - 392 - 12, 16)
    rect(lx, ly + lh - 2, lw, 2, INK)

    # ---- story cards, row 1
    cy1 = 408
    cw = 304
    gap = 28
    card(28, cy1, cw, 264, "KOREAS",
         "NORTH KOREAN AIRCRAFT OVER SOUTH KOREA",
         "Suspected North Korean aircraft near Ulleung island; "
         "residents told to shelter.", draw_jet)
    card(28 + cw + gap, cy1, cw, 264, "TECH",
         "NVIDIA BRINGS BACK HUANG AS CEO",
         "Jensen Huang returns as chief executive after President "
         "Trump intervenes.", draw_chip)
    card(28 + 2 * (cw + gap), cy1, cw, 264, "USA",
         "TRUMP HALTS IOWA EXPLOSIVES BLAST",
         "The planned detonation at an Iowa plant is paused pending "
         "a court ruling.", draw_factory)

    # ---- row 2: two cards + In brief
    cy2 = 684
    card(28, cy2, cw, 264, "BANGLADESH",
         "BANGLADESH TO ARREST HASINA ON RETURN",
         "Dhaka says ex-PM Sheikh Hasina will be arrested if she "
         "comes back from India.", draw_court)
    card(28 + cw + gap, cy2, cw, 264, "THE HAGUE",
         "TAJIKISTAN QUITS THE ICC",
         "Tajikistan becomes the fourth country to leave the "
         "International Criminal Court.", draw_scales)

    bx = 28 + 2 * (cw + gap)
    bw = cw
    rect(bx, cy2, bw, 264, PAPER)
    rect(bx, cy2, bw, 2, INK)
    rect(bx, cy2 + 262, bw, 2, INK)
    rect(bx, cy2, 2, 264, INK)
    rect(bx + bw - 2, cy2, 2, 264, INK)
    draw_globe(bx + 34, cy2 + 28, 16)
    draw_text(bx + 60, cy2 + 18, "IN BRIEF", 2, RED)
    rect(bx + 12, cy2 + 50, bw - 24, 2, RED)
    briefs = [
        "Acropolis Museum reopens after a 7-year restoration.",
        "Israeli strikes kill an UNRWA worker and two others in Gaza.",
        "Denmark to ban school phones after poor PISA results.",
        "US, Mexico, Costa Rica, Jamaica host 2031 Women's World Cup; UK gets 2035.",
        "Magnitude 4.1 earthquake strikes Pakistan.",
        "Five killed in a suspected gas leak in Germany.",
    ]
    by = cy2 + 58
    for item in briefs:
        rect(bx + 12, by + 4, 7, 7, RED)
        n = draw_para(bx + 28, by, item, 1, INK, bw - 40, 13)
        by += n * 13 + 4

    # ---- footer
    draw_text_center(W // 2, 962,
                     "ALL STORIES FIRST REPORTED TUESDAY 24 NOVEMBER 2026",
                     1, GREY)


def png_bytes():
    raw = b"".join(
        b"\x00" + bytes(PIX[y * W * 3:(y + 1) * W * 3])
        for y in range(H))
    comp = zlib.compress(raw, 9)

    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        return out + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", comp) + chunk(b"IEND", b""))


def main():
    build()
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, "entry.png")
    with open(path, "wb") as f:
        f.write(png_bytes())


if __name__ == "__main__":
    main()
