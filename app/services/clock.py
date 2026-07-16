"""Synchronous image-generation service. Runs in a thread-pool worker."""
import datetime
import io
import math
import random
import unicodedata
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from loguru import logger

from app.core.config import settings
from app.services.motivations import get_random_quote
from app.services.zmanim import _omer_text

try:
    from bidi import get_display
except ImportError:
    try:
        from bidi.algorithm import get_display
    except ImportError:
        get_display = None

def _strip_niqqud(text: str) -> str:
    return "".join(c for c in text if not unicodedata.combining(c))

def _rtl(text):
    if not text:
        return text
    text = _strip_niqqud(text)
    return get_display(text) if get_display else text

VALID_FONTS = {
    "DavidLibre-Bold", "FrankRuhlLibre-Bold", "FrankRuhlLibre",
    "Heebo-Bold", "NotoSansHebrew-Bold", "EFT-Tefilot-Bold", "EFT-Tefilot",
    "FbVilna-Bold", "FbVilna-Regular", "FbVilna-Light",
}
DEFAULT_FONT = "NotoSansHebrew-Bold"
TIME_FONT = "FbVilna-Regular"
FONT_EXTENSIONS = (".ttf", ".otf")

# ── Hebrew time tables ────────────────────────────────

HOURS = [
    "אַחַת", "שְׁתַּיִם", "שָׁלוֹשׁ", "אַרְבַּע", "חָמֵשׁ", "שֵׁשׁ",
    "שֶׁבַע", "שְׁמוֹנֶה", "תֵּשַׁע", "עֶשֶׂר", "אַחַת עֶשְׂרֵה", "שְׁתֵּים עֶשְׂרֵה"
]
MINUTE_PREFIX = [
    "", "וְדַקָּה אַחַת", "וּשְׁתֵּי דַקּוֹת", "וְשָׁלוֹשׁ דַקּוֹת",
    "וְאַרְבַּע דַקּוֹת", "וְחָמֵשׁ דַקּוֹת", "וְשֵׁשׁ דַקּוֹת", "וְשֶׁבַע דַקּוֹת",
    "וּשְׁמוֹנֶה דַקּוֹת", "וְתֵשַׁע דַקּוֹת", "וְעֶשֶׂר דַקּוֹת",
    "וְאַחַת עֶשְׂרֵה דַּקּוֹת", "וּשְׁתֵּים עֶשְׂרֵה דַּקּוֹת",
    "וּשְׁלוֹשׁ עֶשְׂרֵה דַּקּוֹת", "וְאַרְבַּע עֶשְׂרֵה דַּקּוֹת",
    "וָרֶבַע", "וְשֵׁשׁ עֶשְׂרֵה דַּקּוֹת", "וּשְׁבַע עֶשְׂרֵה דַּקּוֹת",
    "וּשְׁמוֹנֶה עֶשְׂרֵה דַּקּוֹת", "וּתְשַׁע עֶשְׂרֵה דַּקּוֹת",
    "וְעֶשְׂרִים דַקּוֹת", "וְעֶשְׂרִים וְאַחַת", "וְעֶשְׂרִים וּשְׁתַּיִם",
    "וְעֶשְׂרִים וְשָׁלוֹשׁ", "וְעֶשְׂרִים וְאַרְבַּע", "וְעֶשְׂרִים וְחָמֵשׁ",
    "וְעֶשְׂרִים וְשֵׁשׁ", "וְעֶשְׂרִים וְשֶׁבַע", "וְעֶשְׂרִים וּשְׁמוֹנֶה",
    "וְעֶשְׂרִים וְתֵשַׁע", "וּשְׁלוֹשִׁים", "וּשְׁלוֹשִׁים וְאַחַת",
    "וּשְׁלוֹשִׁים וּשְׁתַּיִם", "וּשְׁלוֹשִׁים וְשָׁלוֹשׁ", "וּשְׁלוֹשִׁים וְאַרְבַּע",
    "וּשְׁלוֹשִׁים וְחָמֵשׁ", "וּשְׁלוֹשִׁים וְשֵׁשׁ", "וּשְׁלוֹשִׁים וְשֶׁבַע",
    "וּשְׁלוֹשִׁים וּשְׁמוֹנֶה", "וּשְׁלוֹשִׁים וְתֵשַׁע", "וְאַרְבָּעִים",
    "וְאַרְבָּעִים וְאַחַת", "וְאַרְבָּעִים וּשְׁתַּיִם", "וְאַרְבָּעִים וְשָׁלוֹשׁ",
    "וְאַרְבָּעִים וְאַרְבַּע", "וְאַרְבָּעִים וְחָמֵשׁ", "וְאַרְבָּעִים וְשֵׁשׁ",
    "וְאַרְבָּעִים וְשֶׁבַע", "וְאַרְבָּעִים וּשְׁמוֹנֶה", "וְאַרְבָּעִים וְתֵשַׁע",
    "וַחֲמִשִּׁים", "וַחֲמִשִּׁים וְאַחַת", "וַחֲמִשִּׁים וּשְׁתַּיִם",
    "וַחֲמִשִּׁים וְשָׁלוֹשׁ", "וַחֲמִשִּׁים וְאַרְבַּע", "וַחֲמִשִּׁים וְחָמֵשׁ",
    "וַחֲמִשִּׁים וְשֵׁשׁ", "וַחֲמִשִּׁים וְשֶׁבַע", "וַחֲמִשִּׁים וּשְׁמוֹנֶה",
    "וַחֲמִשִּׁים וְתֵשַׁע",
]

PERIOD_WORDS = {
    "בַּבֹּקֶר", "בַּצָּהֳרַיִם", "אַחַר הַצָּהֳרַיִם",
    "בָּעֶרֶב", "בַּלַּיְלָה", "לִפְנוֹת בֹּקֶר",
}

MONTHS_HE = [
    "בְּיָנוּאָר", "בְּפֶבְּרוּאָר", "בְּמָרְץ", "בְּאַפְּרִיל",
    "בְּמַאי", "בְּיוּנִי", "בְּיוּלִי", "בְּאוֹגוּסְט",
    "בְּסֶפְּטֶמְבֶּר", "בְּאוֹקְטוֹבֶּר", "בְּנוֹבֶמְבֶּר", "בְּדֶצֶמְבֶּר",
]
DAYS_HE = [
    "יוֹם שֵׁנִי", "יוֹם שְׁלִישִׁי", "יוֹם רְבִיעִי",
    "יוֹם חֲמִישִׁי", "יוֹם שִׁישִּׁי", "שַׁבָּת", "יוֹם רִאשׁוֹן",
]

# ── Helpers ───────────────────────────────────────────

def get_israel_time() -> datetime.datetime:
    utc = datetime.datetime.utcnow()
    local = utc + datetime.timedelta(hours=3 if 3 <= utc.month <= 10 else 2)
    return local + datetime.timedelta(seconds=settings.display_lag)


def _find_font_file(name: str) -> Path | None:
    for ext in FONT_EXTENSIONS:
        path = settings.font_dir / f"{name}{ext}"
        if path.exists():
            return path
    return None


def get_font(size: int, font_name: str = DEFAULT_FONT) -> ImageFont.FreeTypeFont:
    name = font_name if font_name in VALID_FONTS else DEFAULT_FONT
    path = _find_font_file(name)
    if path:
        try:
            return ImageFont.truetype(str(path), size, layout_engine=ImageFont.Layout.BASIC)
        except Exception:
            pass
    for fallback in ("NotoSansHebrew-Bold", "FrankRuhlLibre"):
        fb = _find_font_file(fallback)
        if fb:
            try:
                return ImageFont.truetype(str(fb), size, layout_engine=ImageFont.Layout.BASIC)
            except Exception:
                pass
    return ImageFont.load_default()


def _png_bytes(img: Image.Image) -> bytes:
    buf = io.BytesIO()
    img.convert("1", dither=Image.Dither.NONE).save(buf, format="PNG", optimize=True)
    buf.seek(0)
    return buf.read()


def _get_time_period(h: int) -> str:
    if 6  <= h < 12: return "בַּבֹּקֶר"
    if 12 <= h < 16: return "בַּצָּהֳרַיִם"
    if 16 <= h < 18: return "אַחַר הַצָּהֳרַיִם"
    if 18 <= h < 21: return "בָּעֶרֶב"
    if 21 <= h < 24: return "בַּלַּיְלָה"
    if 0  <= h < 3:  return "בַּלַּיְלָה"
    return "לִפְנוֹת בֹּקֶר"


def _get_time_lines(h24: int, m: int) -> list[str]:
    h12 = h24 % 12 or 12
    period = _get_time_period(h24)
    mp = MINUTE_PREFIX[m]
    hp = HOURS[h12 - 1]
    if len(hp + mp) > 25:
        return [hp, mp, period]
    return [hp + " " + mp, period]

# ── Drawing ───────────────────────────────────────────

def _draw_weather_icon(draw: ImageDraw.Draw, cx: int, cy: int,
                       icon_key: str, size: int = 38) -> None:
    s = size

    def cloud(ox: int = 0, oy: int = 0, scale: float = 1.0) -> None:
        w, h = int(s * 1.4 * scale), int(s * 0.7 * scale)
        pts = []
        for a in range(180, 361, 8):
            pts.append((ox + cx + int(w / 2 * math.cos(math.radians(a))),
                        oy + cy + int(h / 2 * math.sin(math.radians(a)))))
        for centre, rx, dy in [
            (int(w * 0.25),  int(h * 0.6  * scale), int(h * 0.2)),
            (0,              int(h * 0.75 * scale), int(h * 0.3)),
            (-int(w * 0.25), int(h * 0.55 * scale), int(h * 0.1)),
        ]:
            for a in range(0, 181, 8):
                pts.append((ox + cx + centre + int(rx * math.cos(math.radians(a))),
                            oy + cy - dy     + int(rx * math.sin(math.radians(a)))))
        draw.polygon(pts, fill=255, outline=0)

    if icon_key == "sun":
        r = s // 2
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=255, outline=0, width=3)
        for a in range(0, 360, 45):
            rad = math.radians(a)
            draw.line([cx + (r + 4)  * math.cos(rad), cy + (r + 4)  * math.sin(rad),
                       cx + (r + 13) * math.cos(rad), cy + (r + 13) * math.sin(rad)],
                      fill=0, width=3)
    elif icon_key == "sun_cloud":
        sr = s // 3
        scx, scy = cx - s // 3, cy - s // 4
        draw.ellipse([scx - sr, scy - sr, scx + sr, scy + sr], fill=255, outline=0, width=2)
        for a in range(0, 360, 60):
            rad = math.radians(a)
            draw.line([scx + (sr + 3) * math.cos(rad), scy + (sr + 3) * math.sin(rad),
                       scx + (sr + 9) * math.cos(rad), scy + (sr + 9) * math.sin(rad)],
                      fill=0, width=2)
        cloud(s // 5, s // 5, 0.85)
    elif icon_key == "cloud":
        cloud()
    elif icon_key == "cloud_rain":
        cloud(0, -s // 5, 0.9)
        for ox in (-s // 3, -s // 8, s // 8, s // 3):
            draw.line([cx + ox, cy + s // 4, cx + ox - 4, cy + s // 2 + 4], fill=0, width=2)
    elif icon_key == "cloud_snow":
        cloud(0, -s // 5, 0.9)
        for ox in (-s // 3, -s // 8, s // 8, s // 3):
            x, y = cx + ox, cy + s // 3
            for a in (0, 60, 120):
                rad = math.radians(a)
                draw.line([x - 6 * math.cos(rad), y - 6 * math.sin(rad),
                           x + 6 * math.cos(rad), y + 6 * math.sin(rad)],
                          fill=0, width=2)
    elif icon_key == "thunder":
        cloud(0, -s // 4, 0.9)
        pts = [(cx + 4, cy + s // 6), (cx - 6, cy + s // 2),
               (cx + 2, cy + s // 2), (cx - 8, cy + s)]
        draw.line(pts, fill=0, width=3)


# ── Image generators ──────────────────────────────────

def _generate_night_image(font_name: str) -> bytes:
    W, H = 800, 480
    img = Image.new("L", (W, H), color=0)
    draw = ImageDraw.Draw(img)

    rng = random.Random(42)
    for _ in range(60):
        x = rng.randint(20, W - 20)
        y = rng.randint(20, H - 20)
        size = rng.choice([1, 1, 2, 2, 3])
        draw.ellipse([x - size, y - size, x + size, y + size], fill=255)

    mx, my, mr = 100, 90, 55
    draw.ellipse([mx - mr, my - mr, mx + mr, my + mr], fill=255)
    draw.ellipse([mx - mr + 16, my - mr - 12, mx + mr + 16, my - mr - 12 + mr * 2], fill=0)

    sleeping_path = settings.font_dir / "sleeping.png"
    if sleeping_path.exists():
        try:
            sleeping = Image.open(sleeping_path).convert("L")
            mask = sleeping.point(lambda p: 255 if p < 128 else 0)
            white_lines = Image.new("L", sleeping.size, 255)
            black_bg   = Image.new("L", sleeping.size, 0)
            result = Image.composite(white_lines, black_bg, mask)
            sw, sh = 380, 280
            result = result.resize((sw, sh), Image.LANCZOS)
            mask_r = mask.resize((sw, sh), Image.LANCZOS)
            img.paste(result, (W - sw - 20, (H - sh) // 2), mask=mask_r)
        except Exception as exc:
            logger.warning("sleeping image error: {}", exc)

    text_cx = (W - 380 - 40) // 2
    draw.text((text_cx, H // 2 - 30), _rtl("זְמַן לִישׁוֹן"),
              font=get_font(72, font_name), fill=255, anchor="mm")
    draw.text((text_cx, H // 2 + 55), _rtl("לַיְלָה טוֹב"),
              font=get_font(44, font_name), fill=180, anchor="mm")
    return _png_bytes(img)


def _generate_quiet_image(font_name: str) -> bytes:
    W, H = 800, 480
    img = Image.new("L", (W, H), color=255)
    draw = ImageDraw.Draw(img)
    PAD1, PAD2 = 8, 16
    draw.rectangle([PAD1, PAD1, W - PAD1, H - PAD1], outline=0, width=3)
    draw.rectangle([PAD2, PAD2, W - PAD2, H - PAD2], outline=0, width=1)
    draw.text((W // 2, H // 2 - 50), _rtl("לֹא לְהָעִיר אַף אֶחָד!"),
              font=get_font(72, font_name), fill=0, anchor="mm")
    draw.text((W // 2 - 60, H // 2 + 30), "z", font=get_font(72, font_name), fill=0, anchor="mm")
    draw.text((W // 2,      H // 2 + 20), "z", font=get_font(55, font_name), fill=0, anchor="mm")
    draw.text((W // 2 + 50, H // 2 + 10), "z", font=get_font(38, font_name), fill=0, anchor="mm")
    return _png_bytes(img)


def smart_banner(
    h24: int,
    events: dict | None,
    candle_time: str | None = None,
    havdalah_time: str | None = None,
) -> str:
    """
    Return the smart banner text based on priority:
    1. Eruv tavshilin
    2. Candle lighting (Friday / erev yom tov, before sunset)
    3. Havdalah / end of Shabbat/Yom Tov (Shabbat day)
    4. Omer count
    5. Random motivational quote
    """
    if events:
        # 1. Eruv tavshilin
        if events.get("eruv_tavshilin"):
            return "⚠ עֵרוּב תַּבְשִׁילִין הַיּוֹם!"

        # 2. Candle lighting — Friday or erev yom tov
        if candle_time and events.get("candles"):
            holiday = events.get("holiday", "")
            if events.get("is_yomtov") and not events.get("is_shabbat"):
                label = f"כְּנִיסַת {holiday}" if holiday else "כְּנִיסַת יוֹם טוֹב"
            else:
                label = "כְּנִיסַת שַׁבָּת"
            return f"{label}  {candle_time}"

        # 3. Havdalah — Shabbat or end of Yom Tov
        if havdalah_time and events.get("havdalah"):
            if events.get("is_yomtov") and not events.get("is_shabbat"):
                label = "יְצִיאַת יוֹם טוֹב"
            else:
                label = "יְצִיאַת שַׁבָּת"
            return f"{label}  {havdalah_time}"

        # 4. Omer
        omer_day = events.get("omer_day")
        if omer_day:
            return _omer_text(omer_day)

    # 5. Default: motivational quote
    return get_random_quote() or ""


def generate_clock_image(
    font_name:   str        = DEFAULT_FONT,
    sleep_time:  bool       = False,
    weather:     dict | None = None,
    jewish_date: str | None  = None,
    events:      dict | None = None,
) -> bytes:
    fn = font_name if font_name in VALID_FONTS else DEFAULT_FONT

    if sleep_time:
        return _generate_night_image(fn)

    now  = get_israel_time()
    h24, m = now.hour, now.minute

    if h24 == 6 or (h24 == 7 and m < 30):
        return _generate_quiet_image(fn)

    W, H = 800, 480
    img  = Image.new("L", (W, H), color=255)
    draw = ImageDraw.Draw(img)

    PAD1, PAD2 = 8, 16
    draw.rectangle([PAD1, PAD1, W - PAD1, H - PAD1], outline=0, width=3)
    draw.rectangle([PAD2, PAD2, W - PAD2, H - PAD2], outline=0, width=1)

    lines       = _get_time_lines(h24, m)
    time_lines  = [l for l in lines if l not in PERIOD_WORDS]
    period_line = next((l for l in lines if l in PERIOD_WORDS), "")

    font_large  = get_font(88, TIME_FONT)
    font_medium = get_font(58,  fn)
    font_small  = get_font(34,  fn)

    text_start_y = PAD2 + 20
    text_area_h  = H - 110 - text_start_y
    n            = len(time_lines)
    line_h       = 85
    total_h      = n * line_h
    ty           = text_start_y + (text_area_h - total_h) // 2 + 10

    for i, line in enumerate(time_lines):
        rtl_line = _rtl(line)
        f = font_large
        while True:
            bbox = draw.textbbox((0, 0), rtl_line, font=f)
            if (bbox[2] - bbox[0]) < (W - 60):
                break
            current_size = getattr(f, "size", 100)
            if current_size <= 40:
                break
            f = get_font(current_size - 6, TIME_FONT)
        draw.text((W // 2, ty + i * line_h), rtl_line, font=f, fill=0, anchor="mm")

    # ── Smart banner ─────────────────────────────────
    banner = smart_banner(
        h24          = h24,
        events       = events,
        candle_time  = events.get("candles")   if events else None,
        havdalah_time= events.get("havdalah")  if events else None,
    )
    if banner:
        rtl_banner = _rtl(banner)
        banner_font_size = 28
        banner_font = get_font(banner_font_size, fn)
        max_banner_w = W - 80
        while banner_font_size > 16:
            bbox = draw.textbbox((0, 0), rtl_banner, font=banner_font)
            if (bbox[2] - bbox[0]) <= max_banner_w:
                break
            banner_font_size -= 2
            banner_font = get_font(banner_font_size, fn)
        banner_y = ty + len(time_lines) * line_h + 10
        draw.text((W // 2, banner_y), rtl_banner, font=banner_font, fill=0, anchor="mm")

    sep_y = H - 105
    draw.line([(PAD2 + 8, sep_y), (W - PAD2 - 8, sep_y)], fill=0, width=1)
    bar_cy    = H - 52
    bar_left  = PAD2 + 8
    bar_right = W - PAD2 - 8
    bar_width = bar_right - bar_left
    div_x     = bar_left + bar_width // 3
    div_x2    = bar_left + 2 * bar_width // 3
    draw.line([(div_x,  H - 92), (div_x,  H - 15)], fill=0, width=1)
    draw.line([(div_x2, H - 92), (div_x2, H - 15)], fill=0, width=1)

    # ── Bottom bar: [Hebrew date + year] [period] [parsha/holiday/weather] ──
    day_name  = DAYS_HE[now.weekday()]
    if jewish_date and "\n" in jewish_date:
        date_str, year_str = jewish_date.split("\n", 1)
    else:
        date_str = jewish_date if jewish_date else f"{now.day} {MONTHS_HE[now.month - 1]}"
        year_str = None

    left_cx = (bar_left + div_x) // 2
    cell_w  = div_x - bar_left - 10

    def _fit_font(text: str, start: int, minimum: int = 18) -> ImageFont.FreeTypeFont:
        f = get_font(start, fn)
        while True:
            bbox = draw.textbbox((0, 0), text, font=f)
            if (bbox[2] - bbox[0]) <= cell_w:
                return f
            cur = getattr(f, "size", start)
            if cur <= minimum:
                return f
            f = get_font(cur - 2, fn)

    # Left cell: day + Hebrew date + year
    if year_str:
        day_font  = _fit_font(day_name, 26)
        date_font = _fit_font(date_str, 24)
        year_font = _fit_font(year_str, 20)
        draw.text((left_cx, bar_cy - 26), _rtl(day_name), font=day_font,  fill=0, anchor="mm")
        draw.text((left_cx, bar_cy),      _rtl(date_str), font=date_font, fill=0, anchor="mm")
        draw.text((left_cx, bar_cy + 22), _rtl(year_str), font=year_font, fill=0, anchor="mm")
    else:
        date_font = _fit_font(date_str, 30)
        draw.text((left_cx, bar_cy - 14), _rtl(day_name), font=font_small, fill=0, anchor="mm")
        draw.text((left_cx, bar_cy + 14), _rtl(date_str), font=date_font,  fill=0, anchor="mm")

    # Middle cell: time-of-day period
    mid_x = (div_x + div_x2) // 2
    if period_line:
        draw.text((mid_x, bar_cy), _rtl(period_line), font=font_small, fill=0, anchor="mm")

    # Right cell: parsha / holiday / weather
    # Priority: holiday name > parsha > weather
    right_start = div_x2
    right_end   = W - PAD2 - 8
    right_cx    = (right_start + right_end) // 2
    right_cell_w = right_end - right_start - 10

    def _fit_right(text: str, start: int) -> ImageFont.FreeTypeFont:
        f = get_font(start, fn)
        while True:
            bbox = draw.textbbox((0, 0), text, font=f)
            if (bbox[2] - bbox[0]) <= right_cell_w:
                return f
            cur = getattr(f, "size", start)
            if cur <= 16:
                return f
            f = get_font(cur - 2, fn)

    holiday_str = events.get("holiday") or events.get("fast") if events else None
    parsha_str  = events.get("parsha") if events else None

    if holiday_str:
        draw.text((right_cx, bar_cy - 10), _rtl(holiday_str),
                  font=_fit_right(holiday_str, 26), fill=0, anchor="mm")
        if parsha_str:
            combined = f"פר׳ {parsha_str}"
            draw.text((right_cx, bar_cy + 16), _rtl(combined),
                      font=_fit_right(combined, 18), fill=0, anchor="mm")
    elif parsha_str:
        draw.text((right_cx, bar_cy - 10), _rtl("פרשת"),
                  font=get_font(20, fn), fill=0, anchor="mm")
        draw.text((right_cx, bar_cy + 14), _rtl(parsha_str),
                  font=_fit_right(parsha_str, 26), fill=0, anchor="mm")
    elif weather:
        icon_x = right_start + (right_end - right_start) // 4
        text_x = right_start + 3 * (right_end - right_start) // 4
        _draw_weather_icon(draw, icon_x, bar_cy, weather.get("icon_key", "cloud"), size=34)
        draw.text((text_x, bar_cy - 14), f"{weather['temp']}°",
                  font=get_font(40, fn), fill=0, anchor="mm")
        draw.text((text_x, bar_cy + 16), _rtl(weather.get("desc", "")),
                  font=font_small, fill=0, anchor="mm")

    return _png_bytes(img)


def log_available_fonts() -> None:
    found = [f for f in VALID_FONTS if _find_font_file(f)]
    if found:
        logger.info("available fonts: {}", ", ".join(sorted(found)))
    else:
        logger.warning("no Hebrew font files found in {}", settings.font_dir)

    from PIL import features as _pil_features
    module = get_display.__module__ if get_display else "NONE (fallback identity)"
    sample = _rtl("שלום עולם")
    logger.info("bidi impl: {} | raqm available: {} | 'שלום עולם' -> '{}'",
                module, _pil_features.check("raqm"), sample)
