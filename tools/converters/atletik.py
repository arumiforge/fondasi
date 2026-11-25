#!/usr/bin/env python3
"""Build the athletics reference sets atletik-nomor, atletik-kelompok-umur and atletik-hasil (R-10, F-027).

Source: World Athletics Book C — C1.1 Competition Rules and C2.1 Technical Rules (edition with amendments effective
up to 2026-03-20, PDF of 2026-07-17) and the IAAF Scoring Tables for Combined Events (reprint 2016). Raw PDFs and
SOURCE.txt are in sources/atletik/. The rule numbers are not in the PDFs' text layer, so every fact cites the rule
number where the text itself names it, otherwise the section heading and the PDF page.

The facts are transcribed by hand below. The script checks what can be checked: the combined-events formula against
the worked example and table rows printed in the scoring tables, and the hurdle and implement tables for
completeness. Then it writes the three sets:

  python3 -I tools/converters/atletik.py data

Indonesian labels (`label`) are the usual PASI terms; they are to be checked against PASI and the school
championships' technical handbooks (brief R-10b). `label_en` is the World Athletics name as printed.
"""
import json
import math
import os
import sys

RULES = "WA C1.1/C2.1 (2026)"
TABLES = "IAAF Scoring Tables for Combined Events (2016)"
CATEGORIES = ["U18_W", "U20_W", "SENIOR_W", "U18_M", "U20_M", "SENIOR_M"]

# ------------------------------------------------------------------ age groups

AGE_GROUPS = {
    "name": "Kelompok umur atletik",
    "reference_rules": {
        "dec31": "Umur dihitung pada 31 Desember tahun lomba (World Athletics, PASI).",
        "birthday_reached": "Sudah berulang tahun ke-N pada hari lomba (Master).",
        "championship": "Tanggal acuan ditetapkan juknis kejuaraan (O2SN, POPDA/POPNAS, kejuaraan panitia).",
    },
    "groups": [
        {"code": "U18", "label": "U18", "label_en": "Under-18 (U18)", "min_age": 16, "max_age": 17,
         "reference": "dec31", "ref": f"{RULES}, Technical Rules, Age Categories (PDF p. 44)"},
        {"code": "U20", "label": "U20", "label_en": "Under-20 (U20)", "min_age": 18, "max_age": 19,
         "reference": "dec31", "ref": f"{RULES}, Technical Rules, Age Categories (PDF p. 44)"},
        {"code": "SENIOR", "label": "Senior", "label_en": "Senior", "min_age": None, "max_age": None,
         "reference": None, "ref": f"{RULES}, Technical Rules, Age Categories (PDF p. 44)",
         "note": "No age range in the rules: open to every athlete allowed by the competition's minimum age."},
        {"code": "MASTER", "label": "Master", "label_en": "Master", "min_age": 35, "max_age": None,
         "reference": "birthday_reached", "ref": f"{RULES}, Technical Rules, Age Categories (PDF p. 44)",
         "note": "Masters' five-year groups follow the World Athletics/WMA Handbook (not part of this set)."},
    ],
    "pending": [
        "PASI U14 and U16 (and their implements and hurdle heights): brief R-10b.",
        "O2SN SD/SMP/SMA, POPDA/POPNAS groups and their reference dates: brief R-10b.",
    ],
    "notes": [
        "Each championship stores its own reference rule (user decision 2026-11-26): an app keeps "
        "`reference` per championship, using these groups as defaults.",
        "Eligibility and minimum ages for participation follow each competition's technical regulations.",
    ],
}

# ------------------------------------------------------------------ events
# code, label (Indonesian), label_en (as printed), kind, group, result, extra
# kind: track | field | road | walk | relay | combined; result: time | distance | height | points

EVENTS = [
    ("60m", "Lari 60 m", "60m", "track", "sprint", "time", {"wind_seconds": 5, "lanes": True}),
    ("100m", "Lari 100 m", "100m", "track", "sprint", "time", {"wind_seconds": 10, "lanes": True}),
    ("200m", "Lari 200 m", "200m", "track", "sprint", "time", {"wind_seconds": 10, "lanes": True,
                                                              "wind_note": "measured for 10 s from when the first athlete enters the straight"}),
    ("400m", "Lari 400 m", "400m", "track", "sprint", "time", {"lanes": True}),
    ("800m", "Lari 800 m", "800m", "track", "middle", "time", {}),
    ("1500m", "Lari 1500 m", "1500m", "track", "middle", "time", {}),
    ("3000m", "Lari 3000 m", "3000m", "track", "long", "time", {}),
    ("5000m", "Lari 5000 m", "5000m", "track", "long", "time", {}),
    ("10000m", "Lari 10.000 m", "10,000m", "track", "long", "time", {}),
    ("100mH", "Lari gawang 100 m", "100m Hurdles", "track", "hurdles", "time",
     {"wind_seconds": 13, "lanes": True, "sexes": ["W"]}),
    ("110mH", "Lari gawang 110 m", "110m Hurdles", "track", "hurdles", "time",
     {"wind_seconds": 13, "lanes": True, "sexes": ["M"]}),
    ("300mH", "Lari gawang 300 m", "300m Hurdles", "track", "hurdles", "time", {"lanes": True}),
    ("400mH", "Lari gawang 400 m", "400m Hurdles", "track", "hurdles", "time", {"lanes": True}),
    ("2000mSC", "Lari halang rintang 2000 m", "2000m Steeplechase", "track", "steeplechase", "time",
     {"hurdle_jumps": 18, "water_jumps": 5}),
    ("3000mSC", "Lari halang rintang 3000 m", "3000m Steeplechase", "track", "steeplechase", "time",
     {"hurdle_jumps": 28, "water_jumps": 7}),
    ("4x100m", "Estafet 4 × 100 m", "4 × 100m", "relay", "relay", "time", {"lanes": True}),
    ("4x100mX", "Estafet 4 × 100 m campuran", "4 × 100m Mixed", "relay", "relay", "time", {"lanes": True, "sexes": ["X"]}),
    ("4x400m", "Estafet 4 × 400 m", "4 × 400m", "relay", "relay", "time", {}),
    ("4x400mX", "Estafet 4 × 400 m campuran", "4 × 400m Mixed", "relay", "relay", "time", {"sexes": ["X"]}),
    ("HJ", "Lompat tinggi", "High Jump", "field", "vertical_jump", "height", {"bar_raise_combined_cm": 3}),
    ("PV", "Lompat tinggi galah", "Pole Vault", "field", "vertical_jump", "height", {"bar_raise_combined_cm": 10}),
    ("LJ", "Lompat jauh", "Long Jump", "field", "horizontal_jump", "distance", {"wind_seconds": 5}),
    ("TJ", "Lompat jangkit", "Triple Jump", "field", "horizontal_jump", "distance", {"wind_seconds": 5}),
    ("SP", "Tolak peluru", "Shot Put", "field", "throw", "distance", {"implement": "Shot"}),
    ("DT", "Lempar cakram", "Discus Throw", "field", "throw", "distance", {"implement": "Discus"}),
    ("HT", "Lontar martil", "Hammer Throw", "field", "throw", "distance", {"implement": "Hammer"}),
    ("JT", "Lempar lembing", "Javelin Throw", "field", "throw", "distance", {"implement": "Javelin"}),
    ("5000mW", "Jalan cepat 5000 m", "5000m Race Walk", "walk", "race_walk", "time", {}),
    ("10000mW", "Jalan cepat 10.000 m", "10,000m Race Walk", "walk", "race_walk", "time", {}),
    ("10kmW", "Jalan cepat 10 km", "10km Race Walk", "walk", "race_walk", "time", {"road": True}),
    ("20kmW", "Jalan cepat 20 km", "20km Race Walk", "walk", "race_walk", "time", {"road": True}),
    ("HMW", "Jalan cepat half marathon", "Half Marathon Race Walk", "walk", "race_walk", "time", {"road": True}),
    ("MarW", "Jalan cepat marathon", "Marathon Race Walk", "walk", "race_walk", "time", {"road": True}),
    ("5km", "Lari jalan raya 5 km", "5km", "road", "road", "time", {}),
    ("10km", "Lari jalan raya 10 km", "10km", "road", "road", "time", {}),
    ("HM", "Half marathon", "Half Marathon", "road", "road", "time", {}),
    ("Mar", "Marathon", "Marathon", "road", "road", "time", {}),
    ("Pen", "Pancalomba", "Pentathlon", "combined", "combined", "points", {"sexes": ["M"]}),
    ("Hep", "Saptalomba", "Heptathlon", "combined", "combined", "points", {"sexes": ["W"]}),
    ("Dec", "Dasalomba", "Decathlon", "combined", "combined", "points", {}),
]

EVENT_REFS = {
    "track": f"{RULES}, Technical Rules: Hurdle Races (PDF p. 83), Steeplechase (PDF p. 86–87), Relays",
    "walk": f"{RULES}, Technical Rules, Race Walking standard distances",
    "road": f"{RULES}, Technical Rules, Road Races standard distances",
    "wind": f"{RULES}, Technical Rules, wind measurement periods (PDF p. 70–71) and Long/Triple Jump wind measurement (PDF p. 116)",
}

HURDLES = {
    "ref": f"{RULES}, Technical Rules, Hurdle Races (PDF p. 83–85)",
    "tolerance_m": 0.003,
    "note": "U20 110m Hurdles: hurdles up to 1.000 m are also acceptable (manufacturing variations).",
    "spacing": {  # start → first hurdle, between hurdles, last hurdle → finish; flights
        "110mH": {"first_m": 13.72, "between_m": 9.14, "last_m": 14.02, "flights": 10},
        "100mH": {"first_m": 13.00, "between_m": 8.50, "last_m": 10.50, "flights": 10},
        "300mH": {"first_m": 50.00, "between_m": 35.00, "last_m": 40.00, "flights": 7},
        "400mH": {"first_m": 45.00, "between_m": 35.00, "last_m": 40.00, "flights": 10},
    },
    "height_m": {  # by race and category
        "110mH": {"SENIOR_M": 1.067, "U20_M": 0.991, "U18_M": 0.914},
        "100mH": {"SENIOR_W": 0.838, "U20_W": 0.838, "U18_W": 0.762},
        "300mH": {"SENIOR_M": 0.914, "U20_M": 0.914, "U18_M": 0.838, "SENIOR_W": 0.762, "U20_W": 0.762, "U18_W": 0.762},
        "400mH": {"SENIOR_M": 0.914, "U20_M": 0.914, "U18_M": 0.838, "SENIOR_W": 0.762, "U20_W": 0.762, "U18_W": 0.762},
    },
}

STEEPLECHASE = {
    "ref": f"{RULES}, Technical Rules, Steeplechase Races (PDF p. 86–87)",
    "tolerance_m": 0.003,
    "height_m": {"SENIOR_M": 0.914, "U20_M": 0.914, "U18_M": 0.838,
                 "SENIOR_W": 0.762, "U20_W": 0.762, "U18_W": 0.762},
}

IMPLEMENTS = {
    "ref": f"{RULES}, Technical Rules, Official Implements (PDF p. 120)",
    "note": "Weights for other age groups (U14, U16, masters, para) are not in the rules: brief R-10b.",
    "weight_kg": {
        "Shot":    {"U18_W": 3.000, "U20_W": 4.000, "SENIOR_W": 4.000, "U18_M": 5.000, "U20_M": 6.000, "SENIOR_M": 7.260},
        "Discus":  {"U18_W": 1.000, "U20_W": 1.000, "SENIOR_W": 1.000, "U18_M": 1.500, "U20_M": 1.750, "SENIOR_M": 2.000},
        "Hammer":  {"U18_W": 3.000, "U20_W": 4.000, "SENIOR_W": 4.000, "U18_M": 5.000, "U20_M": 6.000, "SENIOR_M": 7.260},
        "Javelin": {"U18_W": 0.500, "U20_W": 0.600, "SENIOR_W": 0.600, "U18_M": 0.700, "U20_M": 0.800, "SENIOR_M": 0.800},
    },
}

COMBINED = {
    "ref": f"{RULES}, Technical Rules, Part IV Combined Events Competitions (PDF p. 144)",
    "events": {
        "Pen_M": {"categories": ["U18_M", "U20_M", "SENIOR_M"], "days": 1,
                  "order": [["LJ", "JT", "200m", "DT", "1500m"]]},
        "Dec_M": {"categories": ["U18_M", "U20_M", "SENIOR_M"], "days": 2,
                  "order": [["100m", "LJ", "SP", "HJ", "400m"], ["110mH", "DT", "PV", "JT", "1500m"]]},
        "Hep_W": {"categories": ["U18_W", "U20_W", "SENIOR_W"], "days": 2,
                  "order": [["100mH", "HJ", "SP", "200m"], ["LJ", "JT", "800m"]]},
        "Dec_W": {"categories": ["U20_W", "SENIOR_W"], "days": 2,
                  "order": [["100m", "DT", "PV", "JT", "400m"], ["100mH", "LJ", "SP", "HJ", "1500m"]],
                  "note": "The rules also allow the men's order for the women's decathlon."},
    },
    "rules": [
        "At least 30 minutes between events for each athlete where possible; at least 10 hours between the two days if possible.",
        "Long Jump and each throw: three trials only.",
        "Track events: one false start per race allowed; the athlete(s) responsible for any further false start are disqualified.",
        "Vertical jumps: uniform bar raises of 3 cm (High Jump) and 10 cm (Pole Vault).",
        "Without fully automatic timing, each athlete is timed by three timekeepers.",
    ],
}

# ------------------------------------------------------------------ results

ABBREVIATIONS = {
    "ref": f"{RULES}, Competition Rule 25.4 (PDF p. 23)",
    "codes": [
        ("DNS", "Tidak start", "Did not start"),
        ("DNF", "Tidak finis", "Did not finish (Running or Race Walking or Combined Events)"),
        ("NM", "Tidak ada lompatan/lemparan sah", "No valid trial recorded"),
        ("DQ", "Diskualifikasi (diikuti nomor aturan)", "Disqualified (followed by the applicable Rule number)"),
        ("O", "Berhasil (lompat tinggi, galah)", "Valid trial in High Jump and Pole Vault"),
        ("X", "Gagal", "Failed trial"),
        ("–", "Melewatkan (pass)", "Passed trial"),
        ("r", "Mundur dari lomba (nomor lapangan)", "Retired from competition (Field Events)"),
        ("Q", "Lolos karena urutan (lintasan) / karena limit (lapangan)", "Qualified by place in Track Events / by standard in Field Events"),
        ("q", "Lolos karena waktu (lintasan) / karena prestasi (lapangan)", "Qualified by time in Track Events / by performance in Field Events"),
        ("qR", "Diloloskan wasit", "Advanced to next round by Referee"),
        ("qJ", "Diloloskan juri banding", "Advanced to next round by Jury of Appeal"),
        ("qD", "Diloloskan lewat undian", "Advanced to next round by draw"),
        (">", "Lutut tertekuk (jalan cepat)", "Bent knee (Race Walking Events)"),
        ("~", "Kehilangan kontak (jalan cepat)", "Loss of contact (Race Walking Events)"),
        ("YC", "Kartu kuning (diikuti nomor aturan)", "Yellow Card (followed by the applicable Rule number)"),
        ("YRC", "Kartu kuning kedua (diikuti nomor aturan)", "Second Yellow Card (followed by the applicable Rule number)"),
    ],
    "notes": [
        "An athlete who did not start any trial or race is DNS; one who took trials keeps those results "
        "(Competition Rules, PDF p. 20).",
        "Leaving the course or a technical infringement in a race is generally shown as DNF rather than DQ "
        "(Competition Rules guidance, PDF p. 20).",
    ],
}

ROUNDING = {
    "fully_automatic": {
        "ref": f"{RULES}, Technical Rules, Fully Automatic Timing and Photo Finish System (PDF p. 75)",
        "track_up_to_10000m": "next longer 0.01 s unless exact (26:17.533 → 26:17.54)",
        "track_over_10000m": "next longer 0.1 s unless the time ends in two zeroes (59:26.322 → 59:26.4)",
        "outside_stadium": "next longer whole second unless the time ends in three zeroes (2:09:44.322 → 2:09:45)",
        "road_mile": "next longer 0.01 s",
        "decimals": {"track_up_to_10000m": 2, "track_over_10000m": 1, "outside_stadium": 0},
    },
    "hand": {
        "ref": f"{RULES}, Technical Rules, Hand Timing (PDF p. 73)",
        "track": "next longer 0.1 s unless exact (10.11 → 10.2)",
        "outside_stadium": "next longer whole second unless exact (2:09:44.3 → 2:09:45)",
        "road_mile": "next longer 0.1 s",
        "decimals": {"track": 1, "outside_stadium": 0},
    },
    "transponder": {
        "ref": f"{RULES}, Technical Rules, Transponder Timing (PDF p. 75–76)",
        "all": "next longer whole second unless the time ends in zero (2:09:44.3 → 2:09:45)",
    },
    "distance": {
        "ref": f"{RULES}, Technical Rules, Distance Measurement (jumps PDF p. 116, throws PDF p. 127)",
        "rule": "record to the nearest 0.01 m below the distance measured if it is not a whole centimetre",
        "decimals": 2,
        "direction": "down",
    },
    "wind": {
        "ref": f"{RULES}, Technical Rules, wind gauge reading (PDF p. 71)",
        "rule": "metres per second rounded to the next higher tenth in the positive direction unless the second "
                "decimal is zero (+2.03 → +2.1; −2.03 → −2.0)",
        "decimals": 1,
        "record_limit_mps": 2.0,
        "record_limit_ref": f"{RULES}, Competition Rules, World Records (PDF p. 32): a performance with a wind "
                            "average above 2 m/s in the direction of running is not ratified",
        "combined_events_limit": {"single_event_mps": 4.0, "average_mps": 2.0,
                                  "ref": f"{RULES}, Technical Rules (PDF p. 59)"},
    },
}

TIES = {
    "track": {
        "ref": f"{RULES}, Technical Rules, Ties (PDF p. 83)",
        "rules": [
            "If the judges cannot separate athletes for a place, it is a tie and stays a tie.",
            "Tie for a ranking position or the last qualifying place by time: compare the actual times to 0.001 s; "
            "if still equal, the tie stays and lots decide (ranking) or tied athletes advance if lanes allow, "
            "otherwise lots.",
            "Tie for the last qualifying place by place: tied athletes advance if lanes or positions allow, "
            "otherwise lots; this reduces the number qualifying on time.",
        ],
    },
    "field_horizontal_and_throws": {
        "ref": f"{RULES}, Technical Rule 25.22 (PDF p. 99)",
        "rule": "Equal best performances: the second best decides, then the third and so on; still equal → tie.",
    },
    "vertical_jumps": {
        "ref": f"{RULES}, Technical Rule 26.8 (PDF p. 102–103)",
        "rules": [
            "26.8.1 fewest jumps at the height last cleared;",
            "26.8.2 then fewest failures in the whole competition up to and including that height;",
            "26.8.3 then the same place, unless it is first place;",
            "26.8.4 for first place, a jump-off (Rule 26.9) unless the competition decided otherwise in advance; "
            "not in Combined Events.",
        ],
    },
}

# a, b, c per event (IAAF Scoring Tables for Combined Events, Formulae, PDF p. 22–23)
SCORING = {
    "ref": f"{TABLES}, Formulae (pages 22–23)",
    "formula": {
        "track": "P = a × (b − T)^c, T in seconds (e.g. 10.43)",
        "jumps": "P = a × (M − b)^c, M in centimetres (e.g. 808)",
        "throws": "P = a × (D − b)^c, D in metres (e.g. 16.69)",
        "rounding": "round P down to a whole number",
    },
    "manual_time": {
        "rule": "Hand times in events up to 400 m: add 0.24 s (below 400 m) or 0.14 s (400 m) to the time, or "
                "subtract it from b; no adjustment above 400 m.",
        "add_seconds": {"below_400m": 0.24, "400m": 0.14},
    },
    "parameters": {
        "M": {
            "100m":  ["track", 25.4347, 18.00, 1.81],
            "200m":  ["track", 5.8425, 38.00, 1.81],
            "400m":  ["track", 1.53775, 82.00, 1.81],
            "1500m": ["track", 0.03768, 480.00, 1.85],
            "110mH": ["track", 5.74352, 28.50, 1.92],
            "HJ":    ["jumps", 0.8465, 75.00, 1.42],
            "PV":    ["jumps", 0.2797, 100.00, 1.35],
            "LJ":    ["jumps", 0.14354, 220.00, 1.40],
            "SP":    ["throws", 51.39, 1.50, 1.05],
            "DT":    ["throws", 12.91, 4.00, 1.10],
            "JT":    ["throws", 10.14, 7.00, 1.08],
            "60m_indoor":   ["track", 58.0150, 11.50, 1.81],
            "1000m_indoor": ["track", 0.08713, 305.50, 1.85],
            "60mH_indoor":  ["track", 20.5173, 15.50, 1.92],
        },
        "W": {
            "200m":  ["track", 4.99087, 42.50, 1.81],
            "800m":  ["track", 0.11193, 254.00, 1.88],
            "100mH": ["track", 9.23076, 26.70, 1.835],
            "HJ":    ["jumps", 1.84523, 75.00, 1.348],
            "LJ":    ["jumps", 0.188807, 210.00, 1.41],
            "SP":    ["throws", 56.0211, 1.50, 1.05],
            "JT":    ["throws", 15.9803, 3.80, 1.04],
            "100m_decathlon":  ["track", 17.8570, 21.0, 1.81],
            "400m_decathlon":  ["track", 1.34285, 91.7, 1.81],
            "1500m_decathlon": ["track", 0.02883, 535, 1.88],
            "PV_decathlon":    ["jumps", 0.44125, 100, 1.35],
            "DT_decathlon":    ["throws", 12.3311, 3.00, 1.10],
            "60mH_indoor":     ["track", 20.0479, 17.00, 1.835],
        },
    },
    "notes": [
        "The pentathlon (men) uses the men's parameters of its events.",
        "Compute with exact decimals (performance as recorded after rounding), then round down; floating-point "
        "results such as 998.9999999 must be treated with a tiny tolerance or decimal arithmetic.",
    ],
}

# Rows printed in the scoring tables and the worked example, used to check the parameters.
CHECKS = [
    ("M", "100m", 10.40, 999, "worked example, p. 23"),
    ("M", "100m", 10.64, 942, "worked example (10.4 hand + 0.24), p. 23"),
    ("M", "SP", 7.72, 350, "men's shot put table"),
    ("M", "SP", 4.28, 150, "men's shot put table"),
    ("W", "JT", 57.18, 1000, "women's javelin table"),
    ("W", "JT", 46.87, 800, "women's javelin table"),
]


def points(sex, event, perf):
    kind, a, b, c = SCORING["parameters"][sex][event]
    x = (b - perf) if kind == "track" else (perf - b)
    if x <= 0:
        return 0
    return math.floor(a * x ** c + 1e-9)


def check():
    for sex, event, perf, expected, where in CHECKS:
        got = points(sex, event, perf)
        if got != expected:
            sys.exit(f"scoring check failed: {sex} {event} {perf} → {got}, table says {expected} ({where})")
    for race, heights in HURDLES["height_m"].items():
        sexes = {"110mH": "M", "100mH": "W"}.get(race)
        want = [c for c in CATEGORIES if sexes is None or c.endswith("_" + sexes)]
        if sorted(heights) != sorted(want):
            sys.exit(f"hurdle heights of {race} incomplete")
    for imp, w in IMPLEMENTS["weight_kg"].items():
        if sorted(w) != sorted(CATEGORIES):
            sys.exit(f"implement weights of {imp} incomplete")
    codes = [e[0] for e in EVENTS]
    if len(codes) != len(set(codes)):
        sys.exit("duplicate event code")
    for ce in COMBINED["events"].values():
        for day in ce["order"]:
            for ev in day:
                if ev not in codes:
                    sys.exit(f"combined event part {ev} is not an event code")


def write(out, name, obj):
    d = os.path.join(out, name)
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, name + ".json"), "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
        f.write("\n")


def main(out):
    check()
    events = []
    for code, label, label_en, kind, group, result, extra in EVENTS:
        e = {"code": code, "label": label, "label_en": label_en, "kind": kind, "group": group, "result": result,
             "sexes": extra.pop("sexes", ["M", "W"])}
        e.update(extra)
        events.append(e)
    write(out, "atletik-nomor", {
        "name": "Nomor lomba atletik",
        "categories": {
            "U18_W": "Putri U18", "U20_W": "Putri U20", "SENIOR_W": "Putri senior",
            "U18_M": "Putra U18", "U20_M": "Putra U20", "SENIOR_M": "Putra senior",
        },
        "events": events,
        "hurdles": HURDLES,
        "steeplechase": STEEPLECHASE,
        "implements": IMPLEMENTS,
        "combined_events": COMBINED,
        "refs": EVENT_REFS,
        "notes": [
            "sexes: M putra, W putri, X campuran. Events without wind_seconds have no wind reading.",
            "School events outside World Athletics (e.g. 80 m, lempar bola kasti, lompat jauh tanpa awalan) and "
            "U14/U16 specifications follow the championships' technical handbooks: brief R-10b.",
        ],
    })
    write(out, "atletik-kelompok-umur", AGE_GROUPS)
    write(out, "atletik-hasil", {
        "name": "Format dan aturan hasil atletik",
        "abbreviations": {"ref": ABBREVIATIONS["ref"], "notes": ABBREVIATIONS["notes"],
                          "codes": [{"code": c, "label": l, "label_en": e} for c, l, e in ABBREVIATIONS["codes"]]},
        "rounding": ROUNDING,
        "ties": TIES,
        "combined_events_scoring": dict(SCORING, checks=[
            {"sex": s, "event": e, "performance": p, "points": pts, "where": w} for s, e, p, pts, w in CHECKS]),
    })
    print(f"ok: {len(events)} events, {len(AGE_GROUPS['groups'])} age groups, "
          f"{len(ABBREVIATIONS['codes'])} result codes, {len(CHECKS)} scoring checks passed")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
