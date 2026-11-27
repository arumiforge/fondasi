#!/usr/bin/env python3
"""Build the athletics records set atletik-rekor (R-11, F-037).

Sources (raw files and SOURCE.txt in sources/atletik-rekor/):
  pasi/       PASI national record tables, www.pbpasi.org: senior men/women, U20 men/women, U18 boys/girls
  wa/         World Athletics record lists (worldathletics.org/records/by-category/...): world records, world U20
              records, world U18 best performances, Asian records; one <table> per page and sex tab, saved by
              tools/converters/atletik-rekor-fetch.mjs
  wikipedia/  "List of Indonesian records in athletics" (CC BY-SA), used only to cross-check the PASI senior tables

Everything is untrusted input: the HTML is read with strict patterns, never executed. Values stay as printed
(`*_printed`) beside the normalised ones. Where a printed value has only one possible reading (a time printed as
"43:12:00" for 10 km walk), the normalised value follows it and the case goes to `errata` with `resolved`; where it
cannot be told (a record date before the holder's birth date, two different birth dates for one athlete), the value
stays as printed and the erratum is `unresolved` (F-031).

  python3 -I tools/converters/atletik-rekor.py sources/atletik-rekor data
"""
import datetime
import glob
import html
import json
import os
import re
import sys

VERSION = "2026-11-27"  # fetch date of the PASI and World Athletics lists
SEXES = {"men": "M", "women": "W", "mixed": "X"}

LISTS = [
    # id, label, label_en, body, age group, sources
    ("nasional-senior", "Rekor nasional Indonesia", "Indonesian national records", "PASI", "SENIOR",
     {"M": "tabel_rekor_men", "W": "tabel_rekor_women"}),
    ("nasional-u20", "Rekor nasional Indonesia U20", "Indonesian national U20 records", "PASI", "U20",
     {"M": "tabel_rekor_u20men", "W": "tabel_rekor_u20women"}),
    ("nasional-u18", "Rekor nasional Indonesia U18", "Indonesian national U18 records", "PASI", "U18",
     {"M": "tabel_rekor_u18boys", "W": "tabel_rekor_u18girls"}),
    ("dunia-senior", "Rekor dunia", "World Records", "World Athletics", "SENIOR", "world-records"),
    ("dunia-u20", "Rekor dunia U20", "World U20 Records", "World Athletics", "U20", "world-u20-records"),
    ("dunia-u18", "Prestasi terbaik dunia U18", "World U18 Best Performances", "World Athletics", "U18",
     "world-u18-best-performances"),
    ("asia-senior", "Rekor Asia", "Asian Records", "World Athletics (Asian Athletics Association)", "SENIOR",
     "asian-records"),
]
LIST_NOTES = {
    "dunia-u18": "World Athletics tidak mengesahkan rekor dunia U18; daftar ini prestasi terbaik yang diakui.",
    "nasional-senior": "Tabel PASI tidak memisahkan rekor dalam ruangan; nomor jalan raya dan lintasan dicetak "
                       "dalam satu tabel.",
}
MAX_AGE = {"U18": 17, "U20": 19}  # age on 31 December of the record year (World Athletics age categories)

MONTHS = {m: i + 1 for i, m in enumerate("jan feb mar apr may jun jul aug sep oct nov dec".split())}
MONTHS.update({"mei": 5, "agu": 8, "agt": 8, "okt": 10, "des": 12, "sept": 9})

# Province names as PASI prints them -> wilayah code (data/wilayah). Teams that are not a province map to None.
PROVINCES = {
    "ACEH": "11", "SUMATRA UTARA": "12", "SUMATERA UTARA": "12", "TIM SUMATERA UTARA": "12",
    "SUMATRA BARAT": "13", "SUMATERA BARAT": "13", "RIAU": "14", "JAMBI": "15", "SUMATRA SELATAN": "16",
    "SUMATERA SELATAN": "16", "BENGKULU": "17", "LAMPUNG": "18", "BANGKA BELITUNG": "19", "DKI JAKARTA": "31",
    "JAWA BARAT": "32", "JAWA TENGAH": "33", "JATENG TEAM": "33", "DI YOGYAKARTA": "34", "JAWA TIMUR": "35",
    "JATIM": "35", "BALI": "51", "NUSA TENGGARA BARAT": "52", "NUSA TENGGARA TIMUR": "53",
    "KALIMANTAN BARAT": "61", "KALIMANTAN TENGAH": "62", "KALIMANTAN SELATAN": "63", "SULAWESI UTARA": "71",
    "SULAWESI SELATAN": "73", "MALUKU": "81", "PAPUA": "91", "INDONESIA TEAM": None,
}
PROVINCE_NOTES = {"PAPUA": "Papua sebelum pemekaran 2022 (kode 91 sekarang)",
                  "INDONESIA TEAM": "tim nasional", "JATENG TEAM": "tim Jawa Tengah",
                  "TIM SUMATERA UTARA": "tim Sumatera Utara"}

errata = []


def erratum(rec_id, field, printed, reason, value=None, resolved=False):
    errata.append({"record": rec_id, "field": field, "printed": printed, "value": value,
                   "status": "resolved" if resolved else "unresolved", "reason": reason})


# ------------------------------------------------------------------ HTML

def cell_text(c):
    c = re.sub(r"<br\s*/?>", " ", c)
    c = re.sub(r"<[^>]+>", "", c)
    return re.sub(r"\s+", " ", html.unescape(c)).strip()


def table_rows(s):
    i, j = s.find("<table"), s.find("</table>")
    if i < 0 or j < 0 or s.count("<table") != 1:
        raise SystemExit("expected exactly one <table>")
    t = s[i:j]
    out = []
    for attrs, body in re.findall(r"<tr([^>]*)>(.*?)</tr>", t, re.S):
        out.append((attrs, [cell_text(c) for c in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", body, re.S)]))
    return out


# ------------------------------------------------------------------ events

def fmt_m(n):
    return f"{n:,}".replace(",", ".") if n >= 10000 else str(n)


def num(s):
    s = s.replace(",", "") if re.fullmatch(r"\d{1,3}(,\d{3})+", s) else s
    s = s.replace(".", "") if re.fullmatch(r"\d{1,3}(\.\d{3})+", s) else s
    return int(s)


def dec(s):
    return float(s.replace(",", "."))


def id_dec(x):
    return (f"{x:g}").replace(".", ",")


NOMOR = None  # codes of data/atletik-nomor, filled in main()


def event(printed):
    """Return (code, label, label_en, result, distance_m, extra) for a printed discipline name."""
    n = printed.strip()
    extra = {}
    low = n.lower()
    if "short track" in low:
        extra["short_track"] = True
        low = low.replace("short track", "").strip()
    m = re.search(r"\(([^)]*)\)", low)
    spec = None
    if m:
        spec = m.group(1).strip()
        low = (low[:m.start()] + low[m.end():]).strip()
    low = re.sub(r"\s+", " ", low.replace(" - ", " ")).strip()
    for age in ("boys", "u20", "u18"):
        if low.endswith(" " + age):
            extra["combined_age_table"] = age.upper() if age != "boys" else "U18"
            low = low[: -len(age) - 1]
    if spec in ("road", "track"):
        extra["surface"] = spec
        spec = None
    if spec:
        mk = re.fullmatch(r"([\d.,]+)\s*(kg|g|gr|cm)", spec)
        if mk:
            unit = {"gr": "g"}.get(mk.group(2), mk.group(2))
            extra["implement"] = f"{id_dec(dec(mk.group(1)))} {unit}"
        elif re.fullmatch(r"0[.,]\d+", spec):  # WA prints the steeplechase barrier height in metres: (0.84)
            extra["implement"] = f"{id_dec(dec(spec) * 100)} cm"
        else:
            raise SystemExit(f"unknown specification in {printed!r}")
        extra["implement_printed"] = spec

    def out(code, label, label_en, result, dist=None):
        return code, label, label_en, result, dist, extra

    mixed = bool(re.search(r"\bmix(ed)?\b", low))
    low = re.sub(r"\s*\bmix(ed)?\b", "", low).strip()
    mm = re.fullmatch(r"4 ?x ?(\d+) ?(m|metres)( relay)?", low)
    if mm:
        d = int(mm.group(1))
        code = f"4x{d}m" + ("X" if mixed else "")
        return out(code, f"Estafet 4 × {d} m" + (" campuran" if mixed else ""),
                   f"4 × {d}m" + (" Mixed" if mixed else ""), "time", 4 * d)
    if mixed:
        raise SystemExit(f"unexpected mixed event {printed!r}")
    if low == "distance medley":
        return out("DMR", "Estafet medley jarak jauh", "Distance Medley", "time", 4000)
    if low == "road relay":
        return out("RoadRelay", "Estafet jalan raya (ekiden)", "Road Relay", "time", 42195)
    if low == "sprint medley 1000m":
        return out("SMR1000", "Estafet medley sprint 1000 m", "Sprint Medley 1000m", "time", 1000)
    mm = re.fullmatch(r"([\d.,]+) ?(m|metres) hurdles", low)
    if mm:
        d = num(mm.group(1))
        return out(f"{d}mH", f"Lari gawang {d} m", f"{d}m Hurdles", "time", d)
    mm = re.fullmatch(r"([\d.,]+) ?(m|metres) steeplechase", low)
    if mm:
        d = num(mm.group(1))
        return out(f"{d}mSC", f"Lari halang rintang {d} m", f"{d}m Steeplechase", "time", d)
    mm = re.fullmatch(r"([\d.,]+) ?(m|metres|km|kilometres) (race )?walk", low)
    if mm:
        d = num(mm.group(1))
        if mm.group(2).startswith("k"):
            return out(f"{d}kmW", f"Jalan cepat {d} km", f"{d}km Race Walk", "time", d * 1000)
        return out(f"{d}mW", f"Jalan cepat {fmt_m(d)} m", f"{d:,}m Race Walk", "time", d)
    if low in ("half marathon walk", "half marathon race walk"):
        return out("HMW", "Jalan cepat half marathon", "Half Marathon Race Walk", "time", 21097.5)
    if low == "marathon race walk":
        return out("MarW", "Jalan cepat marathon", "Marathon Race Walk", "time", 42195)
    mm = re.fullmatch(r"(\d+) ?(km|kilometres)( road)?", low)
    if mm:
        d = int(mm.group(1))
        return out(f"{d}km", f"Lari jalan raya {d} km", f"{d}km Road", "time", d * 1000)
    if low == "half marathon":
        return out("HM", "Half marathon", "Half Marathon", "time", 21097.5)
    if low == "marathon":
        return out("Mar", "Marathon", "Marathon", "time", 42195)
    if low == "mile road":
        return out("MileRoad", "Lari jalan raya 1 mil", "Mile Road", "time", 1609.344)
    if low == "mile":
        return out("Mile", "Lari 1 mil", "Mile", "time", 1609.344)
    if low == "one hour":
        return out("1h", "Lari 1 jam", "One Hour", "distance")
    mm = re.fullmatch(r"([\d.,]+) ?(m|metres)", low)
    if mm:
        d = num(mm.group(1))
        return out(f"{d}m", f"Lari {fmt_m(d)} m", f"{d:,}m", "time", d)
    field = {"high jump": ("HJ", "Lompat tinggi", "High Jump", "height"),
             "pole vault": ("PV", "Lompat tinggi galah", "Pole Vault", "height"),
             "long jump": ("LJ", "Lompat jauh", "Long Jump", "distance"),
             "triple jump": ("TJ", "Lompat jangkit", "Triple Jump", "distance"),
             "shot put": ("SP", "Tolak peluru", "Shot Put", "distance"),
             "discus throw": ("DT", "Lempar cakram", "Discus Throw", "distance"),
             "hammer throw": ("HT", "Lontar martil", "Hammer Throw", "distance"),
             "javelin throw": ("JT", "Lempar lembing", "Javelin Throw", "distance"),
             "pentathlon": ("Pen", "Pancalomba", "Pentathlon", "points"),
             "heptathlon": ("Hep", "Saptalomba", "Heptathlon", "points"),
             "octathlon": ("Oct", "Oktalomba", "Octathlon", "points"),
             "decathlon": ("Dec", "Dasalomba", "Decathlon", "points")}
    for key in ("javelin throw old rule", "javelin throw new rule"):
        if low == key:
            extra["javelin_rule"] = key.split()[2]  # PASI keeps the pre-1986 men's javelin separately
            low = "javelin throw"
    if low in field:
        return out(*field[low])
    raise SystemExit(f"unknown discipline {printed!r}")


# ------------------------------------------------------------------ marks and dates

def parse_time(s):
    """'10.03' / '1:49.93' / '01:49.93' / '1:04:48' -> seconds, or None."""
    m = re.fullmatch(r"(?:(\d{1,2}):)?(?:(\d{1,2}):)?(\d{1,2}(?:\.\d{1,2})?)", s)
    if not m:
        return None
    parts = [p for p in m.groups() if p is not None]
    v = 0.0
    for p in parts:
        v = v * 60 + float(p)
    return round(v, 2)


def plausible(sec, dist):
    """Average speed between 0.5 and 11 m/s (covers every track, road and walk record)."""
    return dist is None or sec is None or 0.5 <= dist / sec <= 11.0


def mark(printed, result, dist, rec_id):
    """Normalise a printed mark. Returns (value, flags)."""
    s = printed.strip()
    flags = {}
    if s.endswith("*"):
        flags["pending"] = True
        s = s[:-1].strip()
    for suf, key in ((" Mx", "mixed_race"), (" Wo", "women_only_race")):
        if s.endswith(suf):
            flags[key] = True
            s = s[: -len(suf)].strip()
    if result == "time":
        if s.endswith("h"):
            flags["hand_timed"] = True
            s = s[:-1]
        v = parse_time(s)
        if v is not None and plausible(v, dist):
            return v, flags
        # '11.56.0', '53.21.0': a trailing '.0' after the hundredths
        m = re.fullmatch(r"(\d{1,2}\.\d{2})\.0", s)
        if m and plausible(parse_time(m.group(1)), dist):
            v = parse_time(m.group(1))
            erratum(rec_id, "mark", printed, "a trailing \".0\" after the hundredths; read as " + m.group(1), v, True)
            return v, flags
        # '43:12:00' for 10 km walk: h:mm:ss would be 43 hours; the only reading is mm:ss.cc
        m = re.fullmatch(r"(\d{1,2}):(\d{2}):(\d{2})", s)
        if m and plausible(parse_time(f"{m.group(1)}:{m.group(2)}.{m.group(3)}"), dist):
            v = parse_time(f"{m.group(1)}:{m.group(2)}.{m.group(3)}")
            erratum(rec_id, "mark", printed, "printed as h:mm:ss, which is not possible for the distance; read as "
                    f"{m.group(1)}:{m.group(2)}.{m.group(3)}", v, True)
            return v, flags
        # '1:35.35' for 20 km walk: m:ss.cc would be 95 s; the only reading is h:mm:ss
        m = re.fullmatch(r"(\d{1,2}):(\d{2})\.(\d{2})", s)
        if m and plausible(parse_time(f"{m.group(1)}:{m.group(2)}:{m.group(3)}"), dist):
            v = parse_time(f"{m.group(1)}:{m.group(2)}:{m.group(3)}")
            erratum(rec_id, "mark", printed, "printed as m:ss.cc, which is not possible for the distance; read as "
                    f"{m.group(1)}:{m.group(2)}:{m.group(3)}", v, True)
            return v, flags
        raise SystemExit(f"{rec_id}: cannot read time {printed!r}")
    if result == "points":
        m = re.fullmatch(r"(\d{1,2})[,.]?(\d{3})(?: pts)?", s)
        if not m:
            raise SystemExit(f"{rec_id}: cannot read points {printed!r}")
        return int(m.group(1) + m.group(2)), flags
    if re.fullmatch(r"\d{5}", s):  # One Hour: metres covered, printed without a unit
        return int(s), flags
    m = re.fullmatch(r"(\d{1,3}(?:\.\d{1,2})?) ?(m|cm)?", s)
    if not m:
        raise SystemExit(f"{rec_id}: cannot read distance {printed!r}")
    v = float(m.group(1))
    if m.group(2) == "cm":
        v = v / 100
    elif m.group(2) is None and "." not in m.group(1) and v > 100:
        raise SystemExit(f"{rec_id}: distance without unit {printed!r}")
    return round(v, 2), flags


def yy(y):
    y = int(y)
    return 2000 + y if y <= 26 else 1900 + y


def pasi_date(s, rec_id, field):
    """'19-May-19', '12-Okt-04', '13‐14 Jun-93' (two days), '2003' (year only). Returns (iso or None, extra)."""
    s = s.strip().replace("‐", "-")
    if not s:
        return None, {}
    if re.fullmatch(r"\d{4}", s):
        return None, {"year": int(s)}
    m = re.fullmatch(r"(\d{1,2})(?:\s*-\s*(\d{1,2}))?[ -]([A-Za-z]{3,4})-(\d{2})", s)
    if not m or m.group(3).lower() not in MONTHS:
        raise SystemExit(f"{rec_id}: cannot read {field} {s!r}")
    month, year = MONTHS[m.group(3).lower()], yy(m.group(4))
    first = datetime.date(year, month, int(m.group(1)))
    extra = {"year": year}
    if m.group(2):
        extra["end"] = datetime.date(year, month, int(m.group(2))).isoformat()
    return first.isoformat(), extra


def wa_date(s, rec_id, field):
    s = s.strip()
    if not s:
        return None
    m = re.fullmatch(r"(\d{2}) ([A-Z]{3}) (\d{4})", s)
    if not m:
        raise SystemExit(f"{rec_id}: cannot read {field} {s!r}")
    return datetime.date(int(m.group(3)), MONTHS[m.group(2).lower()], int(m.group(1))).isoformat()


# ------------------------------------------------------------------ PASI

def pasi(src, list_id, age, sex, page):
    path = os.path.join(src, "pasi", page + ".html")
    s = open(path, encoding="utf-8").read()
    heading = [cell_text(h) for h in re.findall(r"<h2[^>]*>(.*?)</h2>", s, re.S) if "RECORD" in h.upper()]
    rows = table_rows(s)
    if rows[0][1] != ["Dicipline", "Record", "Athlete", "DoB", "Province", "Competition", "Date", "Venue"]:
        raise SystemExit(f"{page}: unexpected header {rows[0][1]}")
    records, updated = [], None
    for _, c in rows[1:]:
        if len(c) == 8 and not any(c[:7]) and re.match(r"Updated? ", c[7]):
            d = re.fullmatch(r"Updated? (\d{1,2}) ([A-Za-z]{3}) (\d{4})", c[7])
            updated = {"printed": c[7], "date": datetime.date(int(d.group(3)), MONTHS[d.group(2).lower()],
                                                               int(d.group(1))).isoformat()}
            continue
        if len(c) == 8:
            n = sum(1 for r in records if r["list"] == list_id and r["sex"] == sex) + 1
            rec_id = f"{list_id}/{sex}/{n:02d}"
            code, label, label_en, result, dist, extra = event(c[0])
            value, flags = mark(c[1], result, dist, rec_id)
            date, dextra = pasi_date(c[6], rec_id, "date")
            rec = {"id": rec_id, "list": list_id, "sex": "X" if code.endswith("X") else sex,
                   "event": code, "event_in_atletik_nomor": code in NOMOR, "event_printed": c[0],
                   "label": label, "label_en": label_en, **extra, "result": result,
                   "mark": value, "mark_printed": c[1], **flags, "wind": None,
                   "holders": [], "team": None, "competition": c[5] or None, "date": date,
                   "date_printed": c[6], "venue": c[7] or None}
            if "end" in dextra:
                rec["date_end"] = dextra["end"]
            province = c[4].strip()
            if province not in PROVINCES:
                if province:
                    raise SystemExit(f"{rec_id}: unknown province {province!r}")
            rec["province_printed"] = province or None
            rec["province"] = PROVINCES.get(province)
            if province in PROVINCE_NOTES:
                rec["province_note"] = PROVINCE_NOTES[province]
            if code.startswith("4x"):
                rec["team"] = province or None
            rec["holders"].append(holder(c[2], c[3], None, rec_id))
            records.append(rec)
        elif len(c) in (2, 3) and records:  # relay member: name, DoB[, province]
            records[-1]["holders"].append(holder(c[0], c[1], c[2] if len(c) == 3 else None, records[-1]["id"]))
        elif len(c) == 1 and records:  # combined events: the splits line under the total
            records[-1]["splits_printed"] = c[0]
        else:
            raise SystemExit(f"{page}: unexpected row {c}")
    if not updated:
        raise SystemExit(f"{page}: no 'Update' line")
    for r in records:
        check_pasi(r, age)
    return records, {"heading": heading[0] if heading else None, "updated": updated}


def holder(name, dob, province, rec_id):
    h = {"name": name.strip()}
    iso, extra = pasi_date(dob, rec_id, "dob")
    h["dob"] = iso
    if iso is None and "year" in extra:
        h["birth_year"] = extra["year"]
    h["dob_printed"] = dob.strip() or None
    if province:
        h["province_printed"] = province
        h["province"] = PROVINCES.get(province)
    return h


def age_on(h, date):
    """Age on `date` (ISO); with only a birth year, the lowest possible age."""
    if h["dob"]:
        b, d = datetime.date.fromisoformat(h["dob"]), datetime.date.fromisoformat(date)
        return d.year - b.year - ((d.month, d.day) < (b.month, b.day))
    if h.get("birth_year"):
        return int(date[:4]) - h["birth_year"] - 1
    return None


def check_pasi(r, age):
    for h in r["holders"]:
        if not r["date"]:
            continue
        a = age_on(h, r["date"])
        if a is None:
            continue
        if h["dob"] and h["dob"] >= r["date"]:
            erratum(r["id"], "date", r["date_printed"],
                    f"the record date is not after {h['name']}'s printed birth date {h['dob_printed']}")
        elif a < 12:
            erratum(r["id"], "date", r["date_printed"],
                    f"{h['name']} would be {a} at the record (birth date printed {h['dob_printed']})")
        elif age in MAX_AGE and a > MAX_AGE[age]:
            # PASI counts the age on the day of the record (several U18 holders are 18 on 31 December),
            # so only a holder older than the group on the day itself is listed.
            erratum(r["id"], "date", r["date_printed"],
                    f"{h['name']} (birth date printed {h['dob_printed'] or h.get('birth_year')}) is {a} on the day "
                    f"of the record, older than {age} allows")
    if r["result"] == "points" and r.get("splits_printed"):
        sp = r["splits_printed"]
        n = len(re.findall(r"\(", sp)) if "(" in sp.strip("()") else len(re.split(r"\s+-\s+", sp.strip("()")))
        want = {"Dec": 10, "Hep": 7, "Pen": 5}.get(r["event"])
        if want and n != want:
            erratum(r["id"], "splits_printed", sp, f"the splits line names {n} events, the {r['label_en']} has {want}")


def check_people(records):
    """The same athlete printed with different birth dates across the PASI tables."""
    seen = {}
    for r in records:
        for h in r["holders"]:
            if not h["dob"]:
                continue
            key = re.sub(r"[^a-z]", "", h["name"].lower())
            seen.setdefault(key, {}).setdefault(h["dob"], set()).add((r["id"], h["dob_printed"]))
    for key, dobs in sorted(seen.items()):
        if len(dobs) > 1:
            errata.append({"record": sorted({i for v in dobs.values() for i, _ in v}), "field": "dob",
                           "printed": sorted({p for v in dobs.values() for _, p in v}), "value": None,
                           "status": "unresolved",
                           "reason": "one athlete, printed with different birth dates in the PASI tables"})


# ------------------------------------------------------------------ World Athletics

def wa(src, list_id, slug):
    records = []
    for tab, sex in SEXES.items():
        path = os.path.join(src, "wa", f"{slug}--{tab}.html")
        rows = table_rows(open(path, encoding="utf-8").read())
        if rows[0][1] != ["Discipline", "Progression", "Perf", "Wind", "Competitor", "DOB", "", "Venue", "Date"]:
            raise SystemExit(f"{path}: unexpected header {rows[0][1]}")
        for attrs, c in rows[1:]:
            n = sum(1 for r in records if r["sex"] == sex) + 1
            rec_id = f"{list_id}/{sex}/{n:02d}"
            code, label, label_en, result, dist, extra = event(c[0])
            if sex == "X" and not code.endswith("X"):
                raise SystemExit(f"{rec_id}: mixed tab with {c[0]!r}")
            value, flags = mark(c[2], result, dist, rec_id)
            venue = c[7]
            indoor = venue.endswith("(i)")
            team = "teamRecord" in attrs
            rec = {"id": rec_id, "list": list_id, "sex": sex, "event": code,
                   "event_in_atletik_nomor": code in NOMOR, "event_printed": c[0], "label": label,
                   "label_en": label_en, **extra, "result": result, "mark": value, "mark_printed": c[2], **flags,
                   "wind": float(c[3]) if c[3] else None, "indoor": indoor,
                   "holders": [] if team else [{"name": c[4], "dob": wa_date(c[5], rec_id, "dob"),
                                                "dob_printed": c[5] or None}],
                   "team": c[4] if team else None, "country": c[6] or None,
                   "date": wa_date(c[8], rec_id, "date"), "date_printed": c[8],
                   "venue": venue[:-3].strip() if indoor else venue}
            records.append(rec)
    return records


def mark_current(records):
    """Several rows for one discipline (ties, or a chain of marks awaiting ratification): flag the best.
    Mixed-race and women-only marks of road events are separate records, so they are compared apart."""
    groups = {}
    for r in records:
        key = (r["list"], r["sex"], r["event_printed"], r.get("indoor", False), r.get("mixed_race", False),
               r.get("women_only_race", False))
        groups.setdefault(key, []).append(r)
    for rows in groups.values():
        better = min if rows[0]["result"] == "time" else max
        best = better(r["mark"] for r in rows)
        for r in rows:
            r["current"] = r["mark"] == best


# ------------------------------------------------------------------ Wikipedia cross-check

def wiki_check(src, records):
    path = os.path.join(src, "wikipedia", "List_of_Indonesian_records_in_athletics.wikitext")
    if not os.path.exists(path):
        return []
    text = open(path, encoding="utf-8").read()
    outdoor = text[text.find("==Outdoor=="):text.find("==Indoor==")]
    diffs = []
    for sex, start, end in (("M", "===Men===", "===Women==="), ("W", "===Women===", "===Mixed===")):
        part = outdoor[outdoor.find(start):outdoor.find(end)]
        for row in part.split("\n|-")[1:]:
            first = row.split("\n")[0]
            if row.startswith("style") and ("pink" in first or "f6f5ce" in first.lower()):
                continue  # Wikipedia marks it "not ratified or later rescinded" or "not kept by PASI"
            cells = [c[1:].strip() for c in row.split("\n") if c.startswith("|") and not c.startswith("|}")]
            cells = [c for c in cells if not c.startswith("style") and not c.startswith("-")]
            if len(cells) < 4 or cells[0].startswith("colspan"):
                continue
            ev = re.sub(r"^rowspan=\d+\|", "", cells[0])
            ev = re.sub(r"\[\[[^|\]]*\|([^\]]*)\]\]|\[\[([^\]]*)\]\]", lambda m: m.group(1) or m.group(2), ev)
            mk = re.sub(r"\{\{[^}]*\}\}|<[^>]+>|\s+$", "", re.sub(r"^rowspan=\d+\|", "", cells[1])).strip()
            date = cells[3]
            mine = [r for r in records if r["list"] == "nasional-senior" and r["sex"] == sex
                    and norm_ev(r["event_printed"]) == norm_ev(ev)]
            if not mine:
                continue
            r = mine[0]
            try:
                wd = datetime.datetime.strptime(re.sub(r"\[\[|\]\]", "", date).strip(), "%d %B %Y").date().isoformat()
            except ValueError:
                wd = None
            wmark = re.sub(r"\s*(m|pts)$", "", mk).replace(",", "")
            pm = r["mark"]
            n0 = len(errata)
            try:
                wv = mark(wmark, r["result"], None, "wikipedia")[0] if r["result"] != "time" else parse_time(wmark)
            except SystemExit:
                wv = None
            del errata[n0:]  # the cross-check never adds errata
            if wv is not None and pm is not None and abs(wv - pm) > 0.005:
                diffs.append({"record": r["id"], "field": "mark", "pasi": r["mark_printed"], "wikipedia": mk})
            if wd and r["date"] and wd != r["date"]:
                diffs.append({"record": r["id"], "field": "date", "pasi": r["date_printed"], "wikipedia": date})
    return diffs


def norm_ev(s):
    s = s.lower().replace(",", "").replace(" metres", " m").replace("–", "-")
    s = re.sub(r"\(.*?\)", "", s)
    s = s.replace("race walk", "walk").replace("- walk", "walk").replace("throw", "").replace(" ", "")
    s = s.replace("×", "x").replace("relay", "").replace("kilometres", "km").replace("km(road)", "km")
    return s.replace("road", "").replace("track", "")


# ------------------------------------------------------------------ main

def main():
    global NOMOR
    if len(sys.argv) != 3:
        raise SystemExit("usage: atletik-rekor.py <sources/atletik-rekor> <data>")
    src, data = sys.argv[1:]
    NOMOR = {e["code"] for e in json.load(open(os.path.join(data, "atletik-nomor", "atletik-nomor.json")))["events"]}
    records, lists = [], []
    for list_id, label, label_en, body, age, source in LISTS:
        entry = {"id": list_id, "label": label, "label_en": label_en, "body": body, "age_group": age}
        if list_id in LIST_NOTES:
            entry["note"] = LIST_NOTES[list_id]
        if isinstance(source, dict):
            entry["pages"] = []
            for sex, page in source.items():
                recs, meta = pasi(src, list_id, age, sex, page)
                records += recs
                entry["pages"].append({"sex": sex, "url": f"https://www.pbpasi.org/{page}/",
                                       "heading": meta["heading"], "updated": meta["updated"]["date"],
                                       "updated_printed": meta["updated"]["printed"]})
            entry["confidence"] = "official"
        else:
            records += wa(src, list_id, source)
            entry["pages"] = [{"url": f"https://worldathletics.org/records/by-category/{source}",
                               "fetched": VERSION}]
            entry["confidence"] = "official"
        lists.append(entry)
    check_people([r for r in records if r["list"].startswith("nasional")])
    mark_current(records)
    cross = wiki_check(src, records)

    out = {
        "name": "Rekor atletik",
        "lists": lists,
        "legend": {
            "pending": "Menunggu pengesahan (World Athletics: *).",
            "hand_timed": "Waktu manual (h).",
            "indoor": "Dicapai di dalam ruangan ((i)).",
            "short_track": "Lintasan pendek (dalam ruangan, 200 m).",
            "mixed_race": "Lomba campuran putra-putri (Mx).",
            "women_only_race": "Lomba khusus putri (Wo).",
            "current": "Prestasi terbaik baris-baris satu nomor (ada rangkaian rekor yang menunggu pengesahan "
                       "atau rekor yang sama).",
        },
        "records": records,
        "errata": errata,
        "cross_check_wikipedia": cross,
        "not_included": [
            "Rekor kejuaraan O2SN, POPDA dan POPNAS: penyelenggara tidak menerbitkan daftar rekor yang terjangkau "
            "(2026-11-27). Ditambahkan bila juknis atau buku hasil memuatnya.",
            "Rekor kejuaraan yang diselenggarakan pengguna: belum ada daftar dari pengguna.",
            "Rekor nasional U16 dan U14: PASI tidak menerbitkan tabelnya di pbpasi.org.",
        ],
    }
    target = os.path.join(data, "atletik-rekor")
    os.makedirs(target, exist_ok=True)
    with open(os.path.join(target, "atletik-rekor.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
        f.write("\n")
    counts = {l["id"]: sum(1 for r in records if r["list"] == l["id"]) for l in lists}
    manifest = {
        "version": VERSION,
        "description": "Athletics records: Indonesian national records (senior, U20, U18) from PASI; world records, "
                       "world U20 records, world U18 best performances and Asian records from World Athletics. Per "
                       "record: event (atletik-nomor code), mark as printed and normalised (seconds, metres or "
                       "points), wind, holders with birth date as published, province (wilayah code) or country, "
                       "competition, date, venue, indoor/pending/hand-timed flags; errata and a Wikipedia "
                       "cross-check.",
        "status": "ready for national (PASI) and World Athletics lists; championship records (O2SN, POPDA, POPNAS, "
                  "the user's championships) and U16/U14 national records not published (F-037)",
        "source": "PASI national record tables at www.pbpasi.org (senior men updated 23 Jun 2025, senior women "
                  "9 Dec 2024, U20 and U18 5 Dec 2023), World Athletics record lists at worldathletics.org/records "
                  "(fetched 2026-11-27); English Wikipedia list of Indonesian records (CC BY-SA) for the "
                  "cross-check only. Raw files and SOURCE.txt in sources/atletik-rekor/",
        "licence": "PASI and World Athletics publish the records publicly; facts with references (F-027, F-037). "
                   "Holders' names and birth dates appear only as the federations publish them (F-037)",
        "procedure": "node tools/converters/atletik-rekor-fetch.mjs sources/atletik-rekor/wa (World Athletics "
                     "pages need a browser); curl for the PASI pages; then python3 -I tools/converters/atletik-rekor.py "
                     "sources/atletik-rekor data and tools/data-check --write",
        "counts": {"records": len(records), **counts, "errata": len(errata), "cross_check_differences": len(cross)},
        "files": ["atletik-rekor.json"],
    }
    with open(os.path.join(target, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(json.dumps(manifest["counts"]))


if __name__ == "__main__":
    main()
