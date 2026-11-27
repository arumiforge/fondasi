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
  python3 -I tools/converters/atletik.py data --tables sources/atletik/o2sn   # also check every O2SN table row

O2SN 2026 (R-10b part): eligibility, events, implements, Kids' Athletics courses and qualifying marks are transcribed
from the three Puspresnas guides with PDF page references; POPDA Jawa Tengah 2026 (events, implements, entry limits,
eligibility) from the Dispora Jateng juknis page images, and the POPNAS age rule as Kemenpora quotes it
(sources/atletik/popda-jateng/, sources/atletik/popnas/); the SMP and SMA/SMK scoring tables the guides link to are
checked row by row with --tables (needs pdftotext; not run in CI).

Indonesian labels (`label`) are the usual PASI terms; they are to be checked against PASI and the school
championships' technical handbooks (brief R-10b). `label_en` is the World Athletics name as printed.
"""
import json
import math
import os
import sys

RULES = "WA C1.1/C2.1 (2026)"
TABLES = "IAAF Scoring Tables for Combined Events (2016)"
# O2SN 2026 guides (Puspresnas, Kemendikdasmen, March 2026) and the scoring tables they link to (sources/atletik/o2sn/)
O2SN = {
    "SD": "Pedoman O2SN SD/MI/Sederajat 2026",
    "SMP": "Panduan O2SN SMP/MTs/Sederajat 2026",
    "SMA": "Panduan O2SN SMA/MA/SMK/MAK/Sederajat 2026",
    "SMP_TABLE": "Scoring Table Trilomba O2SN SMP (\"Licenced by IAAF & PASI Modification\")",
    "SMA_TABLE": "Scoring Tables Pancalomba O2SN SMA & SMK (WA tables, edition 2001, reprint 2016)",
}
# POPDA Jawa Tengah 2026 juknis (Dispora Jateng) and the POPNAS age rule as quoted by Kemenpora (sources/atletik/)
POPDA = "Juknis POPDA Tingkat Provinsi Jawa Tengah 2026 (Dispora Jateng, surat 400.3.9.2/371/2026, 27 Feb 2026)"
POPNAS = ("Peraturan Ketua Umum PP BAPOPSI Nomor 8 Tahun 2022, Bab V Pasal 14 ayat (1) huruf h, as quoted in Kemenpora "
          "Laporan Kinerja 2025 Sesdep 3 (PDF p. 40, printed p. 31)")
CATEGORIES = ["U18_W", "U20_W", "SENIOR_W", "U18_M", "U20_M", "SENIOR_M"]

# ------------------------------------------------------------------ age groups

AGE_GROUPS = {
    "name": "Kelompok umur atletik",
    "reference_rules": {
        "dec31": "Umur dihitung pada 31 Desember tahun lomba (World Athletics, PASI).",
        "birthday_reached": "Sudah berulang tahun ke-N pada hari lomba (Master).",
        "championship": "Tanggal acuan ditetapkan juknis kejuaraan (O2SN, POPDA/POPNAS, kejuaraan panitia).",
        "born_on_or_after": "Lahir pada tanggal batas atau sesudahnya (O2SN: `born_on_or_after`), ditambah syarat kelas.",
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
        # O2SN 2026 (Puspresnas): eligibility by birth date and grade, the same for every sport of the level.
        {"code": "O2SN_SD", "label": "O2SN SD/MI", "label_en": "O2SN primary (SD/MI) 2026", "min_age": None,
         "max_age": None, "reference": "born_on_or_after", "championship": "O2SN", "year": 2026,
         "born_on_or_after": "2014-01-01", "grades": [3, 4, 5], "school_year": "2026/2027",
         "levels": ["SD", "MI", "sederajat"],
         "ref": f"{O2SN['SD']}, Bab III B.1.d (PDF p. 18, printed p. 16)",
         "note": "The SD guide names school year 2026/2027 for the grades; the SMP and SMA guides name 2025/2026. "
                 "Stored as printed."},
        {"code": "O2SN_SMP", "label": "O2SN SMP/MTs", "label_en": "O2SN lower secondary (SMP/MTs) 2026",
         "min_age": None, "max_age": None, "reference": "born_on_or_after", "championship": "O2SN", "year": 2026,
         "born_on_or_after": "2011-01-01", "grades": [7, 8], "school_year": "2025/2026",
         "levels": ["SMP", "MTs", "sederajat"],
         "ref": f"{O2SN['SMP']}, Bab III B.1.d (PDF p. 20, printed p. 18)"},
        {"code": "O2SN_SMA", "label": "O2SN SMA/MA/SMK/MAK", "label_en": "O2SN upper secondary (SMA/MA/SMK/MAK) 2026",
         "min_age": None, "max_age": None, "reference": "born_on_or_after", "championship": "O2SN", "year": 2026,
         "born_on_or_after": "2008-01-01", "grades": [10, 11], "school_year": "2025/2026",
         "levels": ["SMA", "MA", "SMK", "MAK", "sederajat"],
         "ref": f"{O2SN['SMA']}, Bab III B.1.d (PDF p. 21, printed p. 17)"},
        # POPDA Jawa Tengah 2026: one rule for every sport and level (SD, SMP, SMA events by the athlete's school)
        {"code": "POPDA_JATENG_2026", "label": "POPDA Jawa Tengah 2026", "label_en": "POPDA Central Java 2026",
         "min_age": None, "max_age": None, "reference": "born_on_or_after", "championship": "POPDA Jawa Tengah",
         "year": 2026, "born_on_or_after": "2008-01-01", "printed": "tahun kelahiran maksimal 2008",
         "levels": ["SD", "SMP", "SMA"], "student": "pelajar aktif saat POPDA",
         "ref": f"{POPDA}, V.2 (PDF p. 3)",
         "note": "Printed as a birth-year limit; read as born in 2008 or later, as POPNAS (at most 18) and O2SN SMA "
                 "2026 (born on or after 2008-01-01) have it. Moves between regencies count only 6 months after the "
                 "Dapodik registration, except 2026 SD/SMP graduates (V.4)."},
        # POPNAS: the age rule of the national guideline, quoted by Kemenpora; the guideline itself was not found
        {"code": "POPNAS", "label": "POPNAS", "label_en": "POPNAS (national student games)", "min_age": None,
         "max_age": 18, "reference": "championship", "championship": "POPNAS", "year": None,
         "printed": "Berusia maksimal 18 tahun, lahir 1 Januari dan sesudahnya sesuai tahun penyelenggaraan POPNAS",
         "student": "pelajar aktif saat POPNAS", "confidence": "secondary",
         "ref": POPNAS,
         "note": "The quoted text does not say which year's 1 January counts; check each edition's Pedoman Umum. "
                 "A third-party copy of the 2025 conditions (Scribd, not used) gives born 1 January 2008 or later."},
    ],
    "pending": [
        "PASI U14 and U16 (and their implements and hurdle heights): no official PASI document reachable on "
        "2026-11-27 (pasi.or.id does not resolve; brief R-10b).",
        "POPNAS events, implements and the exact birth-date limit per edition: the Pedoman Umum and athletics "
        "technical handbook were not found on an official site (brief R-10b).",
    ],
    "notes": [
        "Each championship stores its own reference rule (user decision 2026-11-26): an app keeps "
        "`reference` per championship, using these groups as defaults.",
        "Eligibility and minimum ages for participation follow each competition's technical regulations.",
    ],
}

# ------------------------------------------------------------------ events
# code, label (Indonesian), label_en (as printed), kind, group, result, extra
# kind: track | field | road | walk | relay | combined | kids; result: time | distance | height | points

EVENTS = [
    ("60m", "Lari 60 m", "60m", "track", "sprint", "time", {"wind_seconds": 5, "lanes": True}),
    ("100m", "Lari 100 m", "100m", "track", "sprint", "time", {"wind_seconds": 10, "lanes": True}),
    ("200m", "Lari 200 m", "200m", "track", "sprint", "time", {"wind_seconds": 10, "lanes": True,
                                                              "wind_note": "measured for 10 s from when the first athlete enters the straight"}),
    ("400m", "Lari 400 m", "400m", "track", "sprint", "time", {"lanes": True}),
    ("80m", "Lari 80 m", "80m", "track", "sprint", "time", {"lanes": True, "championship": "POPDA Jawa Tengah SMP",
                                                            "note": "Not a World Athletics standard event."}),
    ("800m", "Lari 800 m", "800m", "track", "middle", "time", {}),
    ("1000m", "Lari 1000 m", "1000m", "track", "middle", "time", {}),
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
    ("3000mW", "Jalan cepat 3000 m", "3000m Race Walk", "walk", "race_walk", "time", {}),
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
    ("Tri", "Trilomba", "Triathlon (school)", "combined", "combined", "points", {"championship": "O2SN SMP"}),
    ("PenO2SN", "Pancalomba (O2SN SMA/SMK)", "Pentathlon (school)", "combined", "combined", "points",
     {"championship": "O2SN SMA"}),
    ("TriSD", "Trilomba SD", "Triathlon (school, primary)", "combined", "combined", "points",
     {"championship": "POPDA Jawa Tengah SD", "note": "The juknis does not name the three events."}),
    # Kids' Athletics team events of O2SN SD (labels as printed in the guide)
    ("KA_KANGA", "Gawang & Sprint (Kanga Escape)", "Kanga Escape", "kids", "kids_athletics", "time",
     {"team_size": 2}),
    ("KA_F1", "Formula 1", "Formula 1", "kids", "kids_athletics", "time", {"team_size": 2}),
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

# ------------------------------------------------------------------ O2SN 2026 (school championship)
# Facts as printed in the three guides; PDF page numbers (printed numbers differ, given where useful).

CHAMPIONSHIPS = {
    "O2SN_2026": {
        "name": "Olimpiade Olahraga Siswa Nasional (O2SN) 2026",
        "organiser": "Pusat Prestasi Nasional (Puspresnas), Sekretariat Jenderal, Kementerian Pendidikan Dasar dan "
                     "Menengah",
        "rules_basis": "PASI rules adapted from World Athletics; the SD and SMA guides name WA edition 2026, the SMP "
                       "guide edition 2025 (as printed)",
        "levels": {
            "SD": {
                "age_group": "O2SN_SD",
                "sport_label": "Kids' Athletics",
                "events": {"M": ["KA_KANGA", "KA_F1"], "W": ["KA_KANGA", "KA_F1"]},
                "entries": "1 putra and 1 putri per contingent; each athlete takes part in both events",
                "events_ref": f"{O2SN['SD']}, Lampiran A.1.c and A.2.a.6–7 (PDF p. 26)",
                "teams_note": "A team has 2 athletes (PDF p. 27); the guide does not say whether a team is the "
                              "contingent's putra and putri together.",
                "surface": "synthetic track only, no earth or gravel (PDF p. 27)",
                "ranking": "by time per event; place points from the number of teams down to 1 (38, 37, 36 … with "
                           "38 teams); highest total wins (PDF p. 27, 29)",
                "ties": "equal totals for a position are a tie (\"hasil sama\", PDF p. 29)",
                "footwear": "barefoot, shoes or spikes allowed (PDF p. 27)",
                "events_detail": {
                    "KA_KANGA": {
                        "description": "Shuttle relay over hurdles out and flat sprint back; the first runner hands "
                                       "a relay ring to the second behind the flag; time from start until the second "
                                       "runner finishes",
                        "lanes_per_team": 2, "distance_m": 40, "hurdles": 4, "hurdle_height_m": 0.50,
                        "hurdle_spacing_m": 6.0, "start_to_first_hurdle_m": 11.0, "last_hurdle_to_flag_m": 11.0,
                        "equipment": ["1 stopwatch", "1 event card", "4 hurdles", "2 flag posts", "1 relay ring"],
                        "ref": f"{O2SN['SD']}, Lampiran A.2.d.1 (PDF p. 27–28)",
                        "figure_note": "The 11 m distances are read from the figure on PDF p. 28 (11 + 6 + 6 + 6 + "
                                       "11 = 40 m); the text gives 40 m, 4 hurdles, 50 cm, 6 m apart.",
                    },
                    "KA_F1": {
                        "description": "Relay round a course of about 80 m with sprint, hurdles and slalom; each "
                                       "runner starts with a forward or sideways roll on a mat; 1–2 teams per start",
                        "course_m": 80, "hurdles": 9, "hurdle_height_m": None, "slalom_poles": 10,
                        "slalom_spacing_m": 1.0, "mats": 3, "cones": 30,
                        "ref": f"{O2SN['SD']}, Lampiran A.2.d.2 (PDF p. 28–29)",
                        "note": "Hurdle height is not stated for Formula 1.",
                    },
                },
            },
            "SMP": {
                "age_group": "O2SN_SMP",
                "sport_label": "Atletik",
                "combined": "Tri",
                "events": {"M": ["60m", "LJ", "SP"], "W": ["60m", "LJ", "SP"]},
                "entries": "1 putra and 1 putri per contingent; each athlete takes part in all three events",
                "events_ref": f"{O2SN['SMP']}, Lampiran A.1.c and A.2.a.6–7 (PDF p. 28)",
                "trials": {"LJ": 3, "SP": 3},
                "trials_ref": f"{O2SN['SMP']}, Lampiran A.2.d.2 (PDF p. 30)",
                "implements_kg": {"SP": {"M": 4.0, "W": 3.0}},
                "implements_ref": f"{O2SN['SMP']}, Lampiran A.2.c.3 (PDF p. 29)",
                "timing": "fully automatic timing/photo finish, backed up by digital hand stopwatches (PDF p. 29)",
                "ranking": "highest total of the three events' points (Trilomba table); equal totals are a tie "
                           "(PDF p. 31–32)",
                "qualifying": {  # QET for the national round, from the province (table image, PDF p. 29)
                    "M": {"60m": 8.51, "LJ": 4.60, "SP": 7.37},
                    "W": {"60m": 10.14, "LJ": 3.68, "SP": 5.91},
                    "units": {"60m": "s", "LJ": "m", "SP": "m"},
                    "ref": f"{O2SN['SMP']}, Lampiran A.2.a.10 (PDF p. 29, table image)",
                },
            },
            "SMA": {
                "age_group": "O2SN_SMA",
                "sport_label": "Atletik",
                "combined": "PenO2SN",
                "events": {"M": ["100m", "LJ", "SP", "JT", "400m"], "W": ["100m", "LJ", "SP", "JT", "400m"]},
                "events_order_note": "Listed in this order in the guide; the competition order is not stated.",
                "entries": "1 putra and 1 putri per contingent; each athlete takes part in all five events",
                "events_ref": f"{O2SN['SMA']}, Lampiran A.1.c and A.2.a.6–7 (PDF p. 30)",
                "trials": {"LJ": 3, "SP": 3, "JT": 3},
                "trials_ref": f"{O2SN['SMA']}, Lampiran A.4.b (PDF p. 32)",
                "implements_kg": {"SP": {"M": 5.0, "W": 3.0}, "JT": {"M": 0.700, "W": 0.500}},
                "implements_ref": f"{O2SN['SMA']}, Lampiran A.3.c (PDF p. 32)",
                "timing": "fully automatic timing/photo finish, backed up by digital hand stopwatches (PDF p. 32)",
                "ranking": "highest total of the five events' points (Pancalomba table); equal totals are a tie "
                           "(PDF p. 34)",
                "qualifying": {  # QET for the national round (table image, PDF p. 31)
                    "M": {"100m": 13.31, "LJ": 4.59, "SP": 7.77, "JT": 26.75, "400m": 64.86},
                    "W": {"100m": 17.34, "LJ": 3.36, "SP": 6.00, "JT": 13.78, "400m": 94.37},
                    "units": {"100m": "s", "400m": "s", "LJ": "m", "SP": "m", "JT": "m"},
                    "ref": f"{O2SN['SMA']}, Lampiran A.2.a.10 (PDF p. 31, table image)",
                    "note": "Athletes who do not meet the QET may not enter the national round.",
                },
            },
        },
        "common": [
            "Eligibility (birth date, grades) is in atletik-kelompok-umur (O2SN_SD, O2SN_SMP, O2SN_SMA).",
            "Not a past national champion of a PB PASI event (all levels) nor an international champion of a World "
            "Athletics event (SMP, SMA); details and other conditions in each guide's Bab III and Lampiran A.2.a.",
            "Lanes and order by draw (WA rule cited as 'Pasal 141'); protests within 30 minutes of the official "
            "result; appeal in writing with a deposit of Rp1.000.000 within 30 minutes.",
            "Roll call (SMP, SMA): track events first call 30 min and last call 20 min before the start, entry to "
            "the arena 15 min before; jumps and throws 60 / 40 / 30 min.",
            "Medals for places 1–3 of the combined result (SD: Kids' Athletics total); certificates for places 1–3 "
            "per event and 4–8 overall.",
        ],
    },
    "POPDA_JATENG_2026": {
        "name": "Pekan Olahraga Pelajar Daerah (POPDA) Tingkat Provinsi Jawa Tengah 2026",
        "organiser": "Dinas Kepemudaan dan Olahraga Provinsi Jawa Tengah",
        "dates": {"start": "2026-09-01", "end": "2026-09-06", "competition": ["2026-09-02", "2026-09-05"],
                  "technical_meeting": "2026-09-01", "venue_city": "Kota Semarang", "ref": f"{POPDA}, IV (PDF p. 3)"},
        "rules_basis": "World Athletics Competition and Technical Rules 2026 Edition, adapted to local conditions "
                       "(printed \"World Atletics\")",
        "levels": {
            "SD": {
                "age_group": "POPDA_JATENG_2026",
                "sport_label": "Atletik",
                "events": {"M": ["60m", "1000m", "LJ", "SP"], "W": ["60m", "1000m", "LJ", "SP"]},
                "combined": "TriSD",
                "implements_kg": {"SP": {"M": 3.0, "W": 2.0}},
            },
            "SMP": {
                "age_group": "POPDA_JATENG_2026",
                "sport_label": "Atletik",
                "events": {"M": ["80m", "400m", "1500m", "4x100m", "SP", "LJ"],
                           "W": ["80m", "400m", "1500m", "4x100m", "SP", "LJ"]},
                "implements_kg": {"SP": {"M": 4.0, "W": 3.0}},
            },
            "SMA": {
                "age_group": "POPDA_JATENG_2026",
                "sport_label": "Atletik",
                "events": {"M": ["100m", "800m", "3000m", "3000mW", "4x100m", "SP", "LJ", "HJ", "JT"],
                           "W": ["100m", "800m", "3000m", "3000mW", "4x100m", "SP", "LJ", "HJ", "JT"]},
                "implements_kg": {"SP": {"M": 5.0, "W": None}, "JT": {"M": 0.700, "W": 0.600}},
                "implements_note": "SMA putri shot printed \"24 kg\": see errata.",
            },
        },
        "events_count": {"M": 20, "W": 20, "ref": f"{POPDA}, VI table (PDF p. 3) and VII.2 (PDF p. 5)"},
        "events_ref": f"{POPDA}, VII.2 Atletik, table of events (PDF p. 5)",
        "implements_ref": f"{POPDA}, VII.2 Ketentuan 7 (PDF p. 5)",
        "entries": [
            "One athlete enters at most two individual events (Ketentuan 4).",
            "Trilomba: at most 1 athlete per kabupaten/kota, who may not enter any other individual event "
            "(Ketentuan 5).",
            "Quota per kabupaten/kota; at most 2 athletes of the same kabupaten/kota per event (Ketentuan 6).",
            "An athlete takes part in one sport only (V.5).",
        ],
        "entries_ref": f"{POPDA}, VII.2 Ketentuan 4–6 (PDF p. 5), V.5 (PDF p. 3)",
        "registration": "SIMPORA, 1 July – 20 August 2026; offline verification 24 August 2026 (VIII, PDF p. 18)",
        "exhibition": "An event with fewer than 5 kabupaten/kota taking part is an exhibition event: medals and "
                      "certificates are given but do not count for the overall standing (IX, PDF p. 18).",
        "overall_standing": "By medals (gold, silver, bronze); the winning kabupaten/kota receives a trophy "
                            "(IX–X, PDF p. 18).",
        "errata": [
            {"field": "levels.SMA.implements_kg.SP.W", "printed": "24 kg", "value": None, "status": "unresolved",
             "page": "PDF p. 5, VII.2 Ketentuan 7",
             "reason": "A 24 kg shot is impossible; the juknis does not show whether 3 kg (World Athletics U18) or "
                       "4 kg (U20, senior) is meant. Ask the organiser or the technical meeting minutes (F-031)."},
        ],
        "not_stated": ["the three events of Trilomba SD", "hurdles (no hurdle events)", "trials per field event",
                       "qualifying marks"],
        "common": [
            "Eligibility is in atletik-kelompok-umur (POPDA_JATENG_2026).",
            "The levels follow the athlete's school (SD, SMP, SMA); the juknis gives no separate age band per level.",
        ],
    },
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
            "60m_o2sn_smp":    ["track", 46.0849, 13.00, 1.81],
        },
    },
    "notes": [
        "The pentathlon (men) uses the men's parameters of its events.",
        "Compute with exact decimals (performance as recorded after rounding), then round down; floating-point "
        "results such as 998.9999999 must be treated with a tiny tolerance or decimal arithmetic.",
    ],
}

# O2SN scoring tables (sources/atletik/o2sn/). Each event: the parameter set used (sex, key in SCORING) and the
# table's printed range. `--tables` checks every printed row against these (see verify_tables).
O2SN_SCORING = {
    "SMP": {
        "ref": f"{O2SN['SMP_TABLE']}, linked from {O2SN['SMP']} Lampiran A.2.c.6 (PDF p. 29)",
        "max_points": 1500,
        "events": {
            "M": {"60m": "60m_indoor", "LJ": "LJ", "SP": "SP"},
            "W": {"60m": "60m_o2sn_smp", "LJ": "LJ", "SP": "SP"},
        },
        "notes": [
            "Points are capped at 1500 (the formula gives 1503 for 5.46 s men's 60 m and 1501 for a 7.94 m women's "
            "long jump; the table prints 1500).",
            "Men's shot put (4 kg) and both long jumps use the World Athletics parameters unchanged.",
            "Women's 60 m has no World Athletics parameters; a = 46.0849, b = 13.00, c = 1.81 reproduce all 628 "
            "printed rows below the cap (derived from the table, not printed in it).",
        ],
    },
    "SMA": {
        "ref": f"{O2SN['SMA_TABLE']}, linked from {O2SN['SMA']} Lampiran A.3.f (PDF p. 32)",
        "max_points": None,
        "events": {
            "M": {"100m": "100m", "400m": "400m", "LJ": "LJ", "SP": "SP", "JT": "JT"},
            "W": {"100m": "100m_decathlon", "400m": "400m_decathlon", "LJ": "LJ", "SP": "SP", "JT": "JT"},
        },
        "hand_timing": "separate 1/10 s tables for 100 m and 400 m (\"alternatif pada seleksi daerah\") equal the "
                       "World Athletics hand-time rule: +0.24 s (100 m), +0.14 s (400 m)",
        "notes": [
            "The guide calls the table 'modified', but every printed row equals the World Athletics formula; the "
            "women's 100 m and 400 m use the women's decathlon parameters.",
        ],
    },
}

# Rows printed in the scoring tables and the worked example, used to check the parameters.
CHECKS = [
    ("M", "100m", 10.40, 999, "worked example, p. 23"),
    ("M", "100m", 10.64, 942, "worked example (10.4 hand + 0.24), p. 23"),
    ("M", "SP", 7.72, 350, "men's shot put table"),
    ("M", "SP", 4.28, 150, "men's shot put table"),
    ("W", "JT", 57.18, 1000, "women's javelin table"),
    ("W", "JT", 46.87, 800, "women's javelin table"),
    # O2SN tables (sources/atletik/o2sn/): Trilomba SMP and Pancalomba SMA/SMK
    ("M", "60m_indoor", 6.83, 944, "O2SN SMP table, putra 60 m"),
    ("M", "LJ", 5.41, 463, "O2SN SMP table, putra lompat jauh"),
    ("M", "SP", 14.35, 750, "O2SN SMP table, putra tolak peluru (4 kg)"),
    ("W", "60m_o2sn_smp", 8.56, 684, "O2SN SMP table, putri 60 m"),
    ("W", "60m_o2sn_smp", 7.16, 1123, "O2SN SMP table, putri 60 m"),
    ("W", "LJ", 3.87, 279, "O2SN SMP table, putri lompat jauh"),
    ("M", "100m", 12.73, 515, "O2SN SMA table, laki-laki 100 m"),
    ("M", "400m", 52.00, 725, "O2SN SMA table, laki-laki 400 m"),
    ("M", "JT", 68.04, 860, "O2SN SMA table, lempar lembing laki-laki"),
    ("W", "100m_decathlon", 15.63, 374, "O2SN SMA table, perempuan 100 m"),
    ("W", "400m_decathlon", 59.37, 725, "O2SN SMA table, perempuan 400 m"),
    ("W", "LJ", 6.11, 883, "O2SN SMA table, perempuan lompat jauh"),
]


def points(sex, event, perf):
    kind, a, b, c = SCORING["parameters"][sex][event]
    x = (b - perf) if kind == "track" else (perf - b)
    if x <= 0:
        return 0
    return math.floor(a * x ** c + 1e-9)


def printed_points(sex, event, perf, add=0.0):
    """Points for a performance as printed in a table: jumps in metres (converted to cm), times in seconds."""
    kind = SCORING["parameters"][sex][event][0]
    return points(sex, event, round(perf * 100) if kind == "jumps" else perf + add)


def check():
    for sex, event, perf, expected, where in CHECKS:
        got = printed_points(sex, event, perf)
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
    groups = {g["code"] for g in AGE_GROUPS["groups"]}
    for champ in CHAMPIONSHIPS.values():
        for level, spec in champ["levels"].items():
            if spec["age_group"] not in groups:
                sys.exit(f"{level}: unknown age group {spec['age_group']}")
            for sex, evs in spec["events"].items():
                for ev in evs + [spec.get("combined")] * bool(spec.get("combined")):
                    if ev not in codes:
                        sys.exit(f"{level} {sex}: {ev} is not an event code")
            for sex, q in spec.get("qualifying", {}).items():
                if sex in ("M", "W") and sorted(q) != sorted(spec["events"][sex]):
                    sys.exit(f"{level} {sex}: qualifying marks do not cover the events")
        if "events_count" in champ:  # the number of events per sex printed in the handbook
            for sex in ("M", "W"):
                n = sum(len(spec["events"][sex]) + bool(spec.get("combined")) for spec in champ["levels"].values())
                if n != champ["events_count"][sex]:
                    sys.exit(f"{champ['name']} {sex}: {n} events, the handbook counts {champ['events_count'][sex]}")
    for level, sc in O2SN_SCORING.items():
        spec = CHAMPIONSHIPS["O2SN_2026"]["levels"][level]
        for sex, evs in sc["events"].items():
            if sorted(evs) != sorted(spec["events"][sex]):
                sys.exit(f"O2SN {level} {sex}: scoring events differ from the events")
            for key in evs.values():
                if key not in SCORING["parameters"][sex]:
                    sys.exit(f"O2SN {level} {sex}: no parameters {key}")


TABLE_SECTIONS = {  # printed heading → (level, sex, event, hand-time seconds added)
    "SMP": {"Putra 60 Meter": ("M", "60m", 0), "Putra Lompat Jauh": ("M", "LJ", 0),
            "Putra Tolak Peluru": ("M", "SP", 0), "Putri 60 Meter": ("W", "60m", 0),
            "Putri Lompat Jauh": ("W", "LJ", 0), "Putri Tolak Peluru": ("W", "SP", 0)},
    "SMA": {"Laki-laki 100 Meter": ("M", "100m", 0), "Laki-laki 100 Meter - 1/10 sec": ("M", "100m", 0.24),
            "Laki-laki 400 Meter": ("M", "400m", 0), "Laki-laki 400 Meter - 1/10 sec": ("M", "400m", 0.14),
            "Laki-laki Lompat Jauh": ("M", "LJ", 0), "Laki-laki Tolak Peluru": ("M", "SP", 0),
            "Lempar Lembing Laki-laki": ("M", "JT", 0),
            "Perempuan 100 Meter": ("W", "100m", 0), "Perempuan 100 Meter - 1/10 sec": ("W", "100m", 0.24),
            "Perempuan 400 Meter": ("W", "400m", 0), "Perempuan 400 Meter - 1/10 sec": ("W", "400m", 0.14),
            "Perempuan Tolak Peluru": ("W", "SP", 0), "Perempuan Lompat Jauh": ("W", "LJ", 0),
            "Perempuan Lempar Lembing": ("W", "JT", 0)},
}
TABLE_FILES = {"SMP": "Scoring-Table-Trilomba-O2SN-SMP.pdf", "SMA": "Scoring-Table-Pancalomba-O2SN-SMA-SMK.pdf"}
TABLE_ROWS = {"SMP": 5493, "SMA": 12102}  # rows printed (and checked) per table


def parse_table_text(text):
    """Rows per heading from `pdftotext -layout` output; numbers only, strict patterns."""
    import re
    out, cur = {}, None
    head = re.compile(r"^(Putra|Putri|Laki-laki|Perempuan|Lempar Lembing Laki-laki)\s*(.*?)(\s+Multi-Event Table)?$")
    for line in text.split("\n"):
        h = re.sub(r"\s+", " ", line).strip()
        m = head.match(h)
        if m and not re.search(r"\d+[.,]\d+\s+\d", h):
            cur = h.replace(" Multi-Event Table", "")
            out.setdefault(cur, [])
            continue
        if cur is not None:
            out[cur] += [(float(a), int(b)) for a, b in re.findall(r"(\d+\.\d+)\s+(\d{1,4})(?=\s|\||$)", line)]
    return out


def verify_tables(src):
    """Check every printed row of the O2SN scoring tables (needs pdftotext); not run in CI."""
    import subprocess
    for level, fname in TABLE_FILES.items():
        text = subprocess.run(["pdftotext", "-layout", os.path.join(src, fname), "-"], check=True,
                              capture_output=True, text=True).stdout
        sections = parse_table_text(text)
        if sorted(sections) != sorted(TABLE_SECTIONS[level]):
            sys.exit(f"{fname}: headings {sorted(sections)} differ from the expected ones")
        cap = O2SN_SCORING[level]["max_points"]
        total = 0
        for heading, rows in sections.items():
            sex, event, add = TABLE_SECTIONS[level][heading]
            key = O2SN_SCORING[level]["events"][sex][event]
            for perf, printed in rows:
                got = printed_points(sex, key, perf, add)
                if cap:
                    got = min(got, cap)
                if got != printed:
                    sys.exit(f"{fname} {heading}: {perf} → {got}, table prints {printed}")
            total += len(rows)
        if total != TABLE_ROWS[level]:
            sys.exit(f"{fname}: {total} rows read, expected {TABLE_ROWS[level]}")
        print(f"ok: {fname}: all {total} rows match")


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
        "championships": CHAMPIONSHIPS,
        "refs": EVENT_REFS,
        "notes": [
            "sexes: M putra, W putri, X campuran. Events without wind_seconds have no wind reading.",
            "O2SN 2026 (SD Kids' Athletics, SMP Trilomba, SMA/SMK Pancalomba) is under `championships`, with "
            "implements, trials and qualifying marks per level; its scoring is in atletik-hasil.",
            "POPDA Jawa Tengah 2026 is under `championships` (events and implements per level, entry limits, "
            "exhibition rule, errata); its eligibility is in atletik-kelompok-umur.",
            "PASI U14/U16 and POPNAS events and implements: no official document reachable yet (brief R-10b).",
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
        "championship_scoring": {"O2SN_2026": {
            level: dict(sc, rows_checked=TABLE_ROWS[level], table_file=f"sources/atletik/o2sn/{TABLE_FILES[level]}")
            for level, sc in O2SN_SCORING.items()}},
    })
    print(f"ok: {len(events)} events, {len(AGE_GROUPS['groups'])} age groups, "
          f"{len(ABBREVIATIONS['codes'])} result codes, {len(CHECKS)} scoring checks passed")


if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) == 3 and args[1] == "--tables":
        check()
        verify_tables(args[2])
        args = args[:1]
    if len(args) != 1:
        sys.exit(__doc__)
    main(args[0])
