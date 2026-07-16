"""Fetch and cache halachic times (zmanim) + Jewish calendar events for Safed.

Uses two hebcal.com endpoints:
  1. /zmanim   — sunrise, sunset, prayer times, etc.
  2. /hebcal   — holidays, Omer count, Shabbat candles/havdalah, parsha

Safed coordinates: 32.9646° N, 35.4956° E
"""

import datetime
import httpx
from loguru import logger

# ── Safed geo ────────────────────────────────────────
SAFED_LAT  = 32.9646
SAFED_LON  = 35.4956
SAFED_TZ   = "Asia/Jerusalem"

# ── API URLs ─────────────────────────────────────────
_ZMANIM_URL = (
    "https://www.hebcal.com/zmanim"
    "?cfg=json&latitude={lat}&longitude={lon}&tzid={tz}&date={date}"
)
_HEBCAL_URL = (
    "https://www.hebcal.com/hebcal"
    "?v=1&cfg=json&maj=on&min=on&mod=on&nx=on&year={y}&month={m}"
    "&ss=on&mf=on&c=on&latitude={lat}&longitude={lon}&tzid={tz}"
    "&i=off&s=on"   # i=off → diaspora off (Israel rules), s=on → parsha
)

_CACHE_TTL = 3600   # 1 hour (times don't change within a day)

_zmanim_cache: dict[str, dict] = {}
_events_cache: dict[str, dict] = {}

# ── Hebrew labels ─────────────────────────────────────
_ZMAN_LABELS: dict[str, str] = {
    "alotHaShachar":         "עֲלוֹת הַשַּׁחַר",
    "misheyakir":            "מִשֶּׁיַּכִּיר",
    "sunrise":               "הַנֵּץ הַחַמָּה",
    "sofZmanShmaMGA":        "סו\"ז ק\"ש (מג\"א)",
    "sofZmanShma":           "סו\"ז ק\"ש (גר\"א)",
    "sofZmanTfillaMGA":      "סו\"ז תְּפִלָּה (מג\"א)",
    "sofZmanTfilla":         "סו\"ז תְּפִלָּה (גר\"א)",
    "chatzot":               "חֲצוֹת",
    "minchaGedola":          "מִנְחָה גְּדוֹלָה",
    "minchaKetana":          "מִנְחָה קְטַנָּה",
    "plagHaMincha":          "פְּלַג הַמִּנְחָה",
    "sunset":                "שְׁקִיעַת הַחַמָּה",
    "beinHashmashos":        "בֵּין הַשְּׁמָשׁוֹת",
    "tzeit7083deg":          "צֵאת הַכּוֹכָבִים",
    "tzeit85deg":            "צֵאת (ר\"ת)",
}

# Zmanim to show on the calendar screen (ordered)
DISPLAY_ZMANIM = [
    "alotHaShachar",
    "sunrise",
    "sofZmanShma",
    "chatzot",
    "minchaGedola",
    "minchaKetana",
    "plagHaMincha",
    "sunset",
    "tzeit7083deg",
]

# Omer count words
_OMER_UNITS = [
    "", "אֶחָד", "שְׁנַיִם", "שְׁלֹשָׁה", "אַרְבָּעָה", "חֲמִשָּׁה",
    "שִׁשָּׁה", "שִׁבְעָה",
]
_OMER_WEEKS = [
    "", "שָׁבוּעַ אֶחָד", "שְׁנֵי שָׁבוּעוֹת", "שְׁלֹשָׁה שָׁבוּעוֹת",
    "אַרְבָּעָה שָׁבוּעוֹת", "חֲמִשָּׁה שָׁבוּעוֹת", "שִׁשָּׁה שָׁבוּעוֹת",
    "שִׁבְעָה שָׁבוּעוֹת",
]
_OMER_TENS = ["", "עֲשָׂרָה", "עֶשְׂרִים", "שְׁלֹשִׁים", "אַרְבָּעִים"]
_OMER_DAY_NUMS = [
    "", "א׳", "ב׳", "ג׳", "ד׳", "ה׳", "ו׳", "ז׳", "ח׳", "ט׳", "י׳",
    "י״א","י״ב","י״ג","י״ד","ט״ו","ט״ז","י״ז","י״ח","י״ט","כ׳",
    "כ״א","כ״ב","כ״ג","כ״ד","כ״ה","כ״ו","כ״ז","כ״ח","כ״ט","ל׳",
    "ל״א","ל״ב","ל״ג","ל״ד","ל״ה","ל״ו","ל״ז","ל״ח","ל״ט","מ׳",
    "מ״א","מ״ב","מ״ג","מ״ד","מ״ה","מ״ו","מ״ז","מ״ח","מ״ט",
]


def _fmt_time(iso: str) -> str:
    """'2026-04-15T18:45:00+03:00' → '18:45'"""
    try:
        t = datetime.datetime.fromisoformat(iso)
        return t.strftime("%H:%M")
    except Exception:
        return iso[11:16]


def _omer_text(day: int) -> str:
    """Return full Hebrew Omer count phrase for days 1-49."""
    if not 1 <= day <= 49:
        return ""
    weeks, rem = divmod(day, 7)
    parts = [f"הַיּוֹם {_OMER_DAY_NUMS[day]} יוֹם"]
    if weeks and rem:
        # e.g. שלושה שבועות ושני ימים
        day_word = _OMER_UNITS[rem] + (" יוֹם" if rem == 1 else " יָמִים")
        parts.append(f"שֶׁהֵם {_OMER_WEEKS[weeks]} וְ{day_word}")
    elif weeks:
        parts.append(f"שֶׁהֵם {_OMER_WEEKS[weeks]}")
    parts.append("לָעֹמֶר")
    return " ".join(parts)


async def get_zmanim(date: datetime.date, client: httpx.AsyncClient) -> dict:
    """Return dict of zman_key → 'HH:MM' for the given date."""
    key = f"zmanim:{date.isoformat()}"
    entry = _zmanim_cache.get(key, {})
    if entry.get("time") and (
        datetime.datetime.utcnow() - entry["time"]
    ).total_seconds() < _CACHE_TTL:
        return entry.get("data", {})

    try:
        url = _ZMANIM_URL.format(
            lat=SAFED_LAT, lon=SAFED_LON, tz=SAFED_TZ,
            date=date.isoformat(),
        )
        resp = await client.get(url, timeout=8)
        resp.raise_for_status()
        raw = resp.json().get("times", {})
        result = {k: _fmt_time(v) for k, v in raw.items() if v}
        _zmanim_cache[key] = {"data": result, "time": datetime.datetime.utcnow()}
        logger.info("zmanim OK [{}]: {} entries", date, len(result))
        return result
    except Exception as exc:
        logger.warning("zmanim error [{}]: {}", date, exc)
        return entry.get("data", {})


async def get_day_events(date: datetime.date, client: httpx.AsyncClient) -> dict:
    """
    Return structured dict with:
      holiday       – str | None   (e.g. "שַׁבָּת שָׁלוֹם", "פֶּסַח")
      fast          – str | None
      omer          – str | None   (full Hebrew phrase)
      omer_day      – int | None
      candles       – "HH:MM" | None
      havdalah      – "HH:MM" | None
      eruv_tavshilin– bool
      parsha        – str | None   (Hebrew parsha name)
      is_shabbat    – bool
      is_yomtov     – bool
    """
    key = f"events:{date.isoformat()}"
    entry = _events_cache.get(key, {})
    if entry.get("time") and (
        datetime.datetime.utcnow() - entry["time"]
    ).total_seconds() < _CACHE_TTL:
        return entry.get("data", {})

    result: dict = {
        "holiday": None, "fast": None, "omer": None, "omer_day": None,
        "candles": None, "havdalah": None, "eruv_tavshilin": False,
        "parsha": None, "is_shabbat": False, "is_yomtov": False,
    }

    try:
        url = _HEBCAL_URL.format(
            y=date.year, m=date.month,
            lat=SAFED_LAT, lon=SAFED_LON, tz=SAFED_TZ,
        )
        resp = await client.get(url, timeout=8)
        resp.raise_for_status()
        items = resp.json().get("items", [])

        date_str = date.isoformat()   # "2026-06-16"

        for item in items:
            item_date = item.get("date", "")[:10]
            if item_date != date_str:
                continue

            cat = item.get("category", "")
            title_en = item.get("title", "")
            title_he = item.get("hebrew", "") or title_en

            if cat == "candles":
                result["candles"] = _fmt_time(item.get("date", ""))
            elif cat == "havdalah":
                result["havdalah"] = _fmt_time(item.get("date", ""))
            elif cat == "parashat":
                result["parsha"] = title_he
            elif cat == "omer":
                # title like "49th day of the Omer"
                try:
                    day_num = int(title_en.split("th")[0].split("st")[0]
                                  .split("nd")[0].split("rd")[0].strip().split()[-1])
                    result["omer_day"] = day_num
                    result["omer"] = _omer_text(day_num)
                except Exception:
                    result["omer"] = title_he
            elif cat in ("holiday", "modern"):
                subcat = item.get("subcat", "")
                if "fast" in subcat or "fast" in title_en.lower():
                    result["fast"] = title_he
                    result["is_yomtov"] = True
                elif subcat == "shabbat" or "Shabbat" in title_en:
                    result["is_shabbat"] = True
                    result["holiday"] = title_he
                else:
                    result["holiday"] = title_he
                    result["is_yomtov"] = True
            elif cat == "erev-shabbat" or "Shabbat" in title_en:
                result["is_shabbat"] = True

            # Eruv tavshilin — appears when erev yom tov falls on Friday
            if "eruv" in title_en.lower() or "עירוב" in title_he:
                result["eruv_tavshilin"] = True

        _events_cache[key] = {"data": result, "time": datetime.datetime.utcnow()}
        logger.info("events OK [{}]: {}", date, {k: v for k, v in result.items() if v})
        return result

    except Exception as exc:
        logger.warning("events error [{}]: {}", date, exc)
        return entry.get("data", result)
