#!/usr/bin/env python3
"""THE WORLD TODAY — Sunday, 22 November 2026.

Renders one newspaper front page, 1024x1024, summing up 22 November 2026's
world news: 50 sourced stories (1 lead + 5 featured + 44 briefs), a UTC
timeline strip, and a visible date-check line. Deterministic: two runs write
byte-identical entry.png. Standard library + Pillow only; no network.
"""
import os
import sys
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
MARGIN = 24
CONTENT_W = W - 2 * MARGIN
PAPER = (247, 243, 232)
INK = (17, 17, 17)
RED = (163, 18, 18)
GRAY = (90, 86, 76)
LIGHT_RULE = (120, 114, 100)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
SERIF_B = os.path.join(FONT_DIR, "DejaVuSerif-Bold.ttf")
SERIF = os.path.join(FONT_DIR, "DejaVuSerif.ttf")
SANS = os.path.join(FONT_DIR, "DejaVuSans.ttf")
SANS_B = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_w):
    """Wrap text to max_w; returns list of lines."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(draw, x, y, text, fnt, max_w, max_lines, leading, fill=INK):
    """Draw wrapped text; raise if it needs more than max_lines."""
    lines = wrap(draw, text, fnt, max_w)
    if len(lines) > max_lines:
        raise ValueError("overflow: %r needs %d lines, allowed %d"
                         % (text[:40], len(lines), max_lines))
    for i, line in enumerate(lines):
        draw.text((x, y + i * leading), line, font=fnt, fill=fill)
    return y + len(lines) * leading


def rule(draw, x, y, w, width=2, fill=INK):
    draw.line([(x, y), (x + w, y)], fill=fill, width=width)


# ---------------------------------------------------------------- stories
LEAD = {
    "kicker": "CLIMATE  •  ANTALYA, TURKEY",
    "headline": "COP31 COLLAPSES WITHOUT A DEAL",
    "body": ("Two weeks of climate talks ended in Antalya on Sunday with no "
             "agreement, after the EU and about 130 other parties rejected a "
             "final text that said nothing about fossil fuels. Guterres said "
             "he was deeply disappointed."),
}

FEATURED = [
    {
        "kicker": "GULF  •  MANAMA, BAHRAIN",
        "headline": "Iran strikes U.S. bases in Bahrain",
        "body": ("Iran fired missiles and drones at U.S. positions on Saturday "
                 "night. Tehran claims it hit two Patriot radars; Bahrain says "
                 "a civilian plant was hit and two were hurt."),
    },
    {
        "kicker": "CONFLICT  •  BENGHAZI, LIBYA",
        "headline": "Russian warship sinks at Libyan port",
        "body": ("The corvette Merkury sank at its naval base after a suspected "
                 "Ukrainian sea-drone attack. A second ship was also reported "
                 "hit."),
    },
    {
        "kicker": "MEXICO  •  SINALOA",
        "headline": "Cartel boss 'El Chapo Isidro' captured",
        "body": ("Mexican special forces seized Fausto Isidro Meza Flores in "
                 "Guasave on Friday night. Eleven were killed in the raid, "
                 "among them four soldiers."),
    },
    {
        "kicker": "JUSTICE  •  THE HAGUE",
        "headline": "Court: Myanmar committed genocide",
        "body": ("The World Court ruled Myanmar committed genocide against the "
                 "Rohingya in 2017 — the first time it has held a state guilty "
                 "of genocide. The court ordered reparations."),
    },
    {
        "kicker": "DIPLOMACY  •  SHENZHEN, CHINA",
        "headline": "Trump, Xi and Putin meet in Shenzhen",
        "body": ("The three leaders held the first trilateral summit of the "
                 "nuclear powers and signed a four-point peace declaration. "
                 "It said nothing about Ukraine."),
    },
]

# (number, label, text, date) — 44 briefs, stories 7-50.
BRIEFS = [
    (7, "DYMER", "Russian strike on apartment block kills 10, 14 missing.", "22 NOV"),
    (8, "KRYVYI RIH", "Missile kills a boy, 7, and a woman, 20; 60 wounded.", "21 NOV"),
    (9, "WASHINGTON", "Democrats clinch 258 House seats, best since 1992.", "22 NOV"),
    (10, "MARKETS", "S&P 500 -3.7%, Nasdaq -5.3% as AI sell-off spreads.", "20 NOV"),
    (11, "ANTHROPIC", "Record $81.3bn IPO debut, then shares slide sharply.", "19 NOV"),
    (12, "HORMUZ", "Two supertankers hit mines and catch fire near strait.", "21 NOV"),
    (13, "GULF", "US denies Iran claim it damaged an F-16 over the Gulf.", "22 NOV"),
    (14, "TEHRAN", "Trump says no rush on Iran decision; may wait to 2027.", "20 NOV"),
    (15, "IRAN", "Electricity rationing resumes as cold season begins.", "22 NOV"),
    (16, "DOHA", "Qatari delegation holds talks in Tehran on ending war.", "21 NOV"),
    (17, "SPACE", "BepiColombo enters orbit around Mercury, a second ever.", "21 NOV"),
    (18, "BRUSSELS", "EU and Indonesia sign free-trade and investment deal.", "21 NOV"),
    (19, "POLAND", "Russian projectiles land; Warsaw calls it provocation.", "20 NOV"),
    (20, "FINLAND", "Drone strike sets Russian cargo ship ablaze; crew saved.", "21 NOV"),
    (21, "DENMARK", "Expels Russian defence attache over 'assassination plot'.", "21 NOV"),
    (22, "LATVIA", "Leader urges closing EU borders to all Russian citizens.", "21 NOV"),
    (23, "CRIMEA", "Ukraine strikes Kerch Bridge a third time in four days.", "20 NOV"),
    (24, "PARIS", "France seeks UN Security Council meeting on Kyiv strikes.", "20 NOV"),
    (25, "BERLIN", "Merz rejects a new Yalta over Europe's future.", "20 NOV"),
    (26, "LONDON", "UK-EU reset deal: 100,000 youth visas, fewer checks.", "20 NOV"),
    (27, "GREENLAND", "Denmark ratifies US security deal 109-0; two new bases.", "20 NOV"),
    (28, "PYONGYANG", "North Korea expanding Yongbyon enrichment plant.", "20 NOV"),
    (29, "GENEVA", "UN autonomous-weapons talks end with no binding ban.", "21 NOV"),
    (30, "COURTS", "Judge approves Bayer Roundup deal worth up to $7.25bn.", "21 NOV"),
    (31, "MATHS", "Researcher claims Claude AI proved Riemann hypothesis.", "21 NOV"),
    (32, "CIKANDE", "Candy-factory fire kills 3; dozens still missing.", "22 NOV"),
    (33, "BASRA", "Fire at power station kills 4 and injures 35.", "22 NOV"),
    (34, "KHARTOUM", "Drones hit homes and a UN building in Sudan capital.", "22 NOV"),
    (35, "JERUSALEM", "Netanyahu, Eisenkot resume talks to form government.", "22 NOV"),
    (36, "ISTANBUL", "Thousands march against seizure of Sozcu TV.", "22 NOV"),
    (37, "HAITI", "Police say 34 suspected gang members killed.", "20 NOV"),
    (38, "DHAKA", "Violence flares ahead of Hasina's planned return.", "20 NOV"),
    (39, "CARACAS", "US signs new military deal with Venezuela.", "20 NOV"),
    (40, "AMSTERDAM", "Dutch students walk out over conscription plans.", "20 NOV"),
    (41, "NEW YORK", "Mayor unveils plan to close Rikers Island by 2032.", "20 NOV"),
    (42, "GAMES", "Grand Theft Auto VI launches; $3.79bn in first-day sales.", "20 NOV"),
    (43, "TEXAS", "State executes Reinaldo Dennes after hour-long injection.", "20 NOV"),
    (44, "LOS ANGELES", "Palisades Fire arson trial ends in guilty verdict.", "20 NOV"),
    (45, "SENATE", "Bid to curb Trump's Iran war powers fails, 48-51.", "20 NOV"),
    (46, "SENATE", "Sweeping energy-permitting bill passes with Democrats.", "20 NOV"),
    (47, "GOLD", "Price slides to 14-month low under $3,600 an ounce.", "20 NOV"),
    (48, "HUNGER", "WFP plans to assist 91 million people in 2027.", "20 NOV"),
    (49, "BANDA SEA", "Earthquake rattles eastern Indonesia.", "21 NOV"),
    (50, "PERU", "Magnitude 6.8 quake strikes central Peru.", "21 NOV"),
]

TIMELINE = [
    ("05:00", "Dymer strike reported"),
    ("08:00", "Bahrain confirms two wounded"),
    ("11:00", "Democrats pass 258 seats"),
    ("14:00", "COP31 draft rejected"),
    ("16:00", "COP31 ends, no deal"),
    ("19:00", "Drones hit UN building, Khartoum"),
]

DATE_CHECK = ("DATE CHECK: every story on this page was checked against Sunday "
              "22 November 2026; all 50 events are dated 19-22 November 2026.")


def draw_globe(draw, cx, cy, r):
    """Simple line globe: circle, meridians, parallels, tilted ring."""
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(38, 74, 130),
                 width=3)
    for k in (0.45, 0.8):
        w = int(r * k)
        draw.ellipse([cx - w, cy - r, cx + w, cy + r], outline=(38, 74, 130),
                     width=2)
    for frac in (-0.5, 0.0, 0.5):
        yy = cy + int(r * frac)
        half = int((r * r - (r * frac) ** 2) ** 0.5)
        draw.line([(cx - half, yy), (cx + half, yy)], fill=(38, 74, 130),
                  width=2)
    draw.line([(cx, cy - r), (cx, cy + r)], fill=(38, 74, 130), width=2)
    # tilted ring
    draw.ellipse([cx - r - 12, cy - 26, cx + r + 12, cy + 6],
                 outline=(38, 74, 130), width=3)


def draw_stamp(img, cx, cy):
    """Red NO DEAL stamp, rotated, over the globe's lower half."""
    stamp = Image.new("RGBA", (210, 64), (0, 0, 0, 0))
    sd = ImageDraw.Draw(stamp)
    sd.rectangle([3, 3, 206, 60], outline=RED, width=4)
    sd.text((105, 32), "NO DEAL", font=font(SANS_B, 34), fill=RED,
            anchor="mm")
    stamp = stamp.rotate(-12, resample=Image.BICUBIC, expand=True)
    img.paste(stamp, (cx - stamp.width // 2, cy - stamp.height // 2), stamp)


def render():
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)

    # ---- masthead
    f_mast = font(SERIF_B, 58)
    draw.text((W // 2, 16), "THE WORLD TODAY", font=f_mast, fill=INK,
              anchor="ma")
    rule(draw, MARGIN, 82, CONTENT_W, width=3)
    f_sub = font(SANS_B, 17)
    draw.text((W // 2, 90), "SUNDAY, 22 NOVEMBER 2026  •  50 SOURCED STORIES",
              font=f_sub, fill=INK, anchor="ma")
    f_check = font(SANS_B, 12)
    draw.text((W // 2, 114), DATE_CHECK, font=f_check, fill=RED, anchor="ma")
    rule(draw, MARGIN, 134, CONTENT_W, width=2)

    # ---- lead story (left text, right globe)
    lead_x, lead_y, lead_w = MARGIN, 146, 640
    f_kick = font(SANS_B, 13)
    draw.text((lead_x, lead_y), LEAD["kicker"], font=f_kick, fill=RED)
    f_head = font(SERIF_B, 36)
    y = draw_wrapped(draw, lead_x, lead_y + 20, LEAD["headline"], f_head,
                     lead_w, 2, 40)
    f_body = font(SANS, 13)
    y = draw_wrapped(draw, lead_x, y + 5, LEAD["body"], f_body, lead_w, 3, 17)
    if y > 302:
        raise ValueError("lead block overflow: ends at %d" % y)
    draw_globe(draw, 856, 208, 58)
    draw_stamp(img, 856, 244)

    rule(draw, MARGIN, 310, CONTENT_W, width=2)

    # ---- UTC timeline strip
    f_tl = font(SANS_B, 12)
    draw.text((MARGIN, 318), "22 NOVEMBER 2026 — UTC TIMELINE",
              font=f_tl, fill=INK)
    tl_y = 350
    rule(draw, MARGIN, tl_y, CONTENT_W, width=2, fill=GRAY)
    n = len(TIMELINE)
    for i, (t, label) in enumerate(TIMELINE):
        x = MARGIN + int((i + 0.5) * CONTENT_W / n)
        draw.ellipse([x - 5, tl_y - 5, x + 5, tl_y + 5], fill=RED)
        f_time = font(SANS_B, 11)
        draw.text((x, tl_y + 8), t, font=f_time, fill=RED, anchor="ma")
        f_lab = font(SANS, 10)
        draw.text((x, tl_y + 22), label, font=f_lab, fill=INK, anchor="ma")
    rule(draw, MARGIN, 388, CONTENT_W, width=2)

    # ---- featured row 1: three columns
    col_w = (CONTENT_W - 2 * 24) // 3
    fy = 396
    for i, feat in enumerate(FEATURED[:3]):
        x = MARGIN + i * (col_w + 24)
        draw.text((x, fy), feat["kicker"], font=font(SANS_B, 11), fill=RED)
        y = draw_wrapped(draw, x, fy + 18, feat["headline"],
                         font(SERIF_B, 18), col_w, 2, 22)
        draw_wrapped(draw, x, y + 4, feat["body"], font(SANS, 12), col_w,
                     4, 15)
        if i < 2:
            draw.line([(x + col_w + 12, fy), (x + col_w + 12, fy + 124)],
                      fill=LIGHT_RULE, width=1)
    rule(draw, MARGIN, 530, CONTENT_W, width=1, fill=LIGHT_RULE)

    # ---- featured row 2: two columns
    col2_w = (CONTENT_W - 24) // 2
    fy2 = 538
    for i, feat in enumerate(FEATURED[3:]):
        x = MARGIN + i * (col2_w + 24)
        draw.text((x, fy2), feat["kicker"], font=font(SANS_B, 11), fill=RED)
        y = draw_wrapped(draw, x, fy2 + 18, feat["headline"],
                         font(SERIF_B, 20), col2_w, 1, 24)
        draw_wrapped(draw, x, y + 4, feat["body"], font(SANS, 12), col2_w,
                     3, 15)
        if i == 0:
            draw.line([(x + col2_w + 12, fy2),
                       (x + col2_w + 12, fy2 + 88)], fill=LIGHT_RULE, width=1)
    rule(draw, MARGIN, 636, CONTENT_W, width=2)

    # ---- briefs header
    draw.text((MARGIN, 644), "THE DAY IN BRIEF  —  STORIES 7–50",
              font=font(SANS_B, 13), fill=INK)

    # ---- briefs: 2 columns x 22 rows
    brief_col_w = (CONTENT_W - 24) // 2
    row_h = 15
    top = 664
    # vertical divider between the two brief columns, for scannability
    draw.line([(MARGIN + brief_col_w + 12, top - 4),
               (MARGIN + brief_col_w + 12, top + 22 * row_h)],
              fill=LIGHT_RULE, width=1)
    f_num = font(SANS_B, 11)
    f_lab = font(SANS_B, 11)
    f_txt = font(SANS, 11)
    f_date = font(SANS, 10)
    for idx, (num, label, text, date) in enumerate(BRIEFS):
        col = idx // 22
        row = idx % 22
        x = MARGIN + col * (brief_col_w + 24)
        y = top + row * row_h
        # measure full line; shrink font if needed, else fail loudly
        size = 11
        while size >= 9:
            fn, fl, ft, fd = (font(SANS_B, size), font(SANS_B, size),
                              font(SANS, size), font(SANS, 10))
            parts = [("%d." % num, fn), (label, fl), (text, ft),
                     (date, fd)]
            total = sum(draw.textlength(t, font=f) for t, f in parts) + 3 * 4
            if total <= brief_col_w:
                break
            size -= 1
        else:
            raise ValueError("brief %d too long even at 9px" % num)
        cx = x
        for txt, fnt in parts:
            fill = GRAY if txt == date else INK
            if txt == label:
                fill = RED
            draw.text((cx, y), txt, font=fnt, fill=fill)
            cx += draw.textlength(txt, font=fnt) + 4
        if y + row_h > 1000:
            raise ValueError("briefs overflow bottom at row %d" % row)

    # ---- footer
    rule(draw, MARGIN, 1004, CONTENT_W, width=2)
    draw.text((W // 2, 1010),
              "THE WORLD TODAY  •  SUNDAY 22 NOVEMBER 2026  •  50 STORIES",
              font=font(SANS, 10), fill=GRAY, anchor="ma")
    return img


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "out")
    os.makedirs(out_dir, exist_ok=True)
    img = render()
    path = os.path.join(out_dir, "entry.png")
    img.save(path, format="PNG", optimize=True)
    print("wrote %s (%d bytes)" % (path, os.path.getsize(path)))


if __name__ == "__main__":
    main()
