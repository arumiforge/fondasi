#!/usr/bin/env python3
"""Build data/kaldik-madrasah-jateng from Keputusan Kakanwil Kemenag Jawa Tengah Nomor 1681 Tahun 2026 (R-06).

The decree's PDF (sources/kaldik-madrasah-jateng/) has a text layer only for the cover letter; the decree and its
Lampiran (calendar per month) were transcribed by hand into EVENTS below, each with a reference to its Pasal or
Lampiran month. The script then checks the transcription and writes the data set:

  * every date is valid and every range runs forward;
  * per month, the printed HK/HL/HE (hari kalender / libur / efektif) are recomputed: holidays = Sundays + days of
    holiday events + report-card Saturdays; a mismatch stops the build;
  * every holiday day is compared with data/libur-nasional (SKB 3 Menteri, the national layer that wins, F-025):
    field 'skb' per event, and SKB days the decree does not list in 'skb_days_not_in_this_calendar'.

Usage: python3 -I tools/converters/kaldik-madrasah-jateng.py
"""
import datetime as dt
import hashlib
import json
import os
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
OUT = os.path.join(ROOT, "data", "kaldik-madrasah-jateng")
SRC = "sources/kaldik-madrasah-jateng/20260701-JTG-Kaldik-Madrasah-2026-2027.pdf"
VERSION = "2026-06-29"  # signing date of the decree

ALL = ["RA", "MI", "MTs", "MA", "MAK"]
TKA_MA = ["MA", "MAK"]

# kind, start, end, label (as printed, plain), levels, ref, extra fields
EVENTS = [
    ("first_day", "2026-07-13", "2026-07-13", "Awal masuk tahun ajaran 2026/2027", ALL, "Pasal 4; Lampiran Juli", {}),
    ("orientation", "2026-07-13", "2026-07-18", "Pengenalan lingkungan madrasah", ALL, "Pasal 5 ayat (2); Lampiran Juli",
     {"note": "MI also runs the PAUD/RA-to-MI transition programme in the first two weeks (Pasal 5 ayat (3))"}),
    ("teacher_training", "2026-07-20", "2026-08-17", "Sulingjar untuk kepala dan guru (RA, MI, MTs, MA, MAK)", ALL,
     "Lampiran Juli–Agustus", {"note": "for heads and teachers; school days for pupils"}),
    ("public_holiday", "2026-08-17", "2026-08-17", "Proklamasi Kemerdekaan", ALL, "Pasal 15 ayat (2) a; Pasal 21 ayat (1) a",
     {"ceremony": True}),
    ("public_holiday", "2026-08-25", "2026-08-25", "Maulid Nabi Muhammad S.A.W.", ALL, "Pasal 21 ayat (1) b", {}),
    ("national_test", "2026-09-21", "2026-09-27", "Simulasi TKA dan AN jenjang MA/MAK", TKA_MA, "Lampiran September", {}),
    ("ceremony", "2026-10-01", "2026-10-01", "Hari Kesaktian Pancasila", ALL, "Pasal 15 ayat (2) b", {}),
    ("national_test", "2026-10-05", "2026-10-18", "Gladi bersih TKA dan AN jenjang MA/MAK", TKA_MA, "Lampiran Oktober", {}),
    ("ceremony", "2026-10-22", "2026-10-22", "Hari Santri", ALL, "Pasal 15 ayat (2) c", {}),
    ("national_test", "2026-10-26", "2026-10-29", "Pelaksanaan utama TKA dan AN jenjang MA/MAK", TKA_MA, "Lampiran Oktober", {}),
    ("ceremony", "2026-10-28", "2026-10-28", "Hari Sumpah Pemuda", ALL, "Pasal 15 ayat (2) d", {}),
    ("national_test", "2026-11-02", "2026-11-05", "Pelaksanaan utama TKA dan AN jenjang MA/MAK", TKA_MA, "Lampiran November", {}),
    ("ceremony", "2026-11-10", "2026-11-10", "Hari Pahlawan", ALL, "Pasal 15 ayat (2) e", {}),
    ("national_test", "2026-11-16", "2026-11-29", "Susulan TKA dan AN jenjang MA/MAK", TKA_MA, "Lampiran November", {}),
    ("summative", "2026-11-23", "2026-12-05", "Asesmen sumatif akhir semester (ASAS) gasal", ALL,
     "Pasal 12 ayat (1); Lampiran November–Desember", {}),
    ("report", "2026-12-19", "2026-12-19", "Penyerahan rapor murid semester gasal", ALL, "Pasal 14 ayat (1)", {}),
    ("semester_break", "2026-12-21", "2027-01-02", "Libur semester gasal", ALL, "Pasal 19 ayat (1); Lampiran Desember", {}),
    ("cuti_bersama", "2026-12-24", "2026-12-24", "Cuti bersama Kelahiran Yesus Kristus", ALL, "Pasal 21 ayat (1) c", {}),
    ("public_holiday", "2026-12-25", "2026-12-25", "Kelahiran Yesus Kristus", ALL, "Pasal 21 ayat (1) d", {}),
    ("public_holiday", "2027-01-01", "2027-01-01", "Tahun Baru 2027 Masehi", ALL, "Pasal 21 ayat (2) a", {"estimate": True}),
    ("ceremony", "2027-01-03", "2027-01-03", "Hari Amal Bakti (HAB) Kementerian Agama", ALL, "Pasal 16", {}),
    ("first_day", "2027-01-04", "2027-01-04", "Awal masuk semester genap", ALL, "Lampiran Januari", {}),
    ("public_holiday", "2027-01-05", "2027-01-05", "Isra Mikraj Nabi Muhammad S.A.W.", ALL, "Pasal 21 ayat (2) b", {"estimate": True}),
    ("public_holiday", "2027-02-06", "2027-02-06", "Tahun Baru Imlek 2578 Kongzili", ALL, "Pasal 21 ayat (2) c", {"estimate": True}),
    ("ramadan", "2027-02-08", "2027-02-10", "Libur awal Ramadan 1448 H", ALL, "Pasal 20 ayat (1); Lampiran Februari",
     {"estimate": True, "note": "one day before Ramadan and its first two days (1–2 Ramadan 1448 H)"}),
    ("ramadan", "2027-03-05", "2027-03-09", "Libur akhir bulan Ramadan 1448 H", ALL, "Pasal 20 ayat (2); Lampiran Maret",
     {"estimate": True}),
    ("public_holiday", "2027-03-08", "2027-03-08", "Hari Suci Nyepi (Tahun Baru Saka 1949)", ALL, "Pasal 21 ayat (2) d",
     {"estimate": True}),
    ("public_holiday", "2027-03-10", "2027-03-11", "Hari Raya Idul Fitri 1448 H", ALL, "Pasal 21 ayat (2) e", {"estimate": True}),
    ("eid_break", "2027-03-12", "2027-03-15", "Libur dalam rangka Hari Raya Idul Fitri 1448 H", ALL,
     "Pasal 20 ayat (3); Lampiran Maret",
     {"estimate": True, "note": "Pasal 20 ayat (3) gives 10–15 Maret 2027 including the two days of Idul Fitri"}),
    ("public_holiday", "2027-03-26", "2027-03-26", "Wafat Yesus Kristus", ALL, "Pasal 21 ayat (2) f", {"estimate": True}),
    ("public_holiday", "2027-03-28", "2027-03-28", "Kebangkitan Yesus Kristus (Paskah)", ALL, "Pasal 21 ayat (2) g",
     {"estimate": True}),
    ("school_exam", "2027-03-29", "2027-05-15", "Rentang waktu ujian madrasah (UM) tahun ajaran 2026/2027", ALL,
     "Lampiran Maret–Mei; Pasal 13 ayat (1)",
     {"estimate": True, "note": "the final UM dates follow the Direktur Jenderal Pendidikan Islam (Pasal 13 ayat (1))"}),
    ("ceremony", "2027-04-21", "2027-04-21", "Hari Kartini", ALL, "Pasal 15 ayat (2) f", {}),
    ("public_holiday", "2027-05-01", "2027-05-01", "Hari Buruh Internasional", ALL, "Pasal 21 ayat (2) h", {"estimate": True}),
    ("ceremony", "2027-05-02", "2027-05-02", "Hari Pendidikan Nasional", ALL, "Pasal 15 ayat (2) g", {}),
    ("public_holiday", "2027-05-06", "2027-05-06", "Kenaikan Yesus Kristus", ALL, "Pasal 21 ayat (2) i", {"estimate": True}),
    ("public_holiday", "2027-05-17", "2027-05-17", "Hari Raya Idul Adha 1448 H", ALL, "Pasal 21 ayat (2) j", {"estimate": True}),
    ("ceremony", "2027-05-20", "2027-05-20", "Hari Kebangkitan Nasional", ALL, "Pasal 15 ayat (2) h", {}),
    ("public_holiday", "2027-05-20", "2027-05-20", "Hari Raya Waisak 2571 BE", ALL, "Pasal 21 ayat (2) k", {"estimate": True}),
    ("summative", "2027-05-24", "2027-06-05", "Asesmen sumatif akhir tahun ajaran", ALL,
     "Pasal 12 ayat (2); Lampiran Mei–Juni", {}),
    ("public_holiday", "2027-06-01", "2027-06-01", "Hari Lahir Pancasila", ALL, "Pasal 15 ayat (2) i; Pasal 21 ayat (2) l",
     {"estimate": True, "ceremony": True}),
    ("public_holiday", "2027-06-06", "2027-06-06", "1 Muharam Tahun Baru Islam 1449 H", ALL, "Pasal 21 ayat (2) m",
     {"estimate": True}),
    ("report", "2027-06-19", "2027-06-19", "Penyerahan rapor murid semester genap", ALL, "Pasal 14 ayat (2)", {}),
    ("semester_break", "2027-06-21", "2027-07-10", "Libur akhir tahun ajaran", ALL, "Pasal 19 ayat (2); Lampiran Juni", {}),
    ("next_year", "2027-07-12", "2027-07-12", "Awal tahun ajaran 2027/2028", ALL, "Lampiran Juni", {"estimate": True}),
]

# printed in the Lampiran under each month: HK (hari kalender), HL (hari libur), HE (hari efektif)
MONTHS = {
    "2026-07": (31, 14, 17), "2026-08": (31, 7, 24), "2026-09": (30, 4, 26), "2026-10": (31, 4, 27),
    "2026-11": (30, 5, 25), "2026-12": (31, 15, 16), "2027-01": (31, 8, 23), "2027-02": (28, 8, 20),
    "2027-03": (31, 14, 17), "2027-04": (30, 4, 26), "2027-05": (31, 9, 22), "2027-06": (30, 15, 15),
}
SEMESTERS = {"gasal": ("2026-07", "2026-12", 184, 49, 135), "genap": ("2027-01", "2027-06", 181, 58, 123)}

HOLIDAY_KINDS = {"public_holiday", "cuti_bersama", "ramadan", "eid_break", "semester_break"}
YEAR_START, YEAR_END = dt.date(2026, 7, 13), dt.date(2027, 7, 10)
# the days before the first school day belong to the previous year's break (Lampiran Juli)
BEFORE_START = (dt.date(2026, 7, 1), dt.date(2026, 7, 12))


def d(s):
    return dt.date.fromisoformat(s)


def days(a, b):
    x = a
    while x <= b:
        yield x
        x += dt.timedelta(days=1)


def main():
    errors = []
    for kind, a, b, *_ in EVENTS:
        if d(a) > d(b):
            errors.append(f"range runs backwards: {kind} {a} {b}")

    # recompute HL per month: Sundays, days of holiday events, report-card Saturdays, days before the first school day
    off = set(days(*BEFORE_START))
    for kind, a, b, *_ in EVENTS:
        if kind in HOLIDAY_KINDS or (kind == "report" and d(a).weekday() == 5):
            off.update(days(d(a), d(b)))
    month_counts = {}
    for ym, (hk, hl, he) in MONTHS.items():
        y, m = map(int, ym.split("-"))
        first = dt.date(y, m, 1)
        last = (first.replace(day=28) + dt.timedelta(days=4)).replace(day=1) - dt.timedelta(days=1)
        all_days = list(days(first, last))
        hl_calc = sum(1 for x in all_days if x.weekday() == 6 or x in off)
        if (len(all_days), hl_calc, len(all_days) - hl_calc) != (hk, hl, he):
            errors.append(f"{ym}: printed HK/HL/HE {hk}/{hl}/{he}, computed {len(all_days)}/{hl_calc}/{len(all_days) - hl_calc}")
        month_counts[ym] = {"hk": hk, "hl": hl, "he": he}
    for name, (a, b, hk, hl, he) in SEMESTERS.items():
        ms = [v for k, v in MONTHS.items() if a <= k <= b]
        if (sum(x[0] for x in ms), sum(x[1] for x in ms), sum(x[2] for x in ms)) != (hk, hl, he):
            errors.append(f"semester {name}: month sums differ from the printed totals {hk}/{hl}/{he}")

    # national layer: SKB 3 Menteri (data/libur-nasional)
    skb = {}
    ln = json.load(open(os.path.join(ROOT, "data", "libur-nasional", "libur-nasional.json"), encoding="utf-8"))
    for year in ln["years"]:
        for day in year["days"]:
            skb[day["date"]] = (year["year"], day)
    events = []
    covered = set(off)
    for kind, a, b, label, levels, ref, extra in EVENTS:
        e = {"start": a, "end": b, "kind": kind, "label": label, "levels": levels, "ref": ref}
        e.update({k: v for k, v in extra.items() if k != "note"})
        if "note" in extra:
            e["note"] = extra["note"]
        if kind in HOLIDAY_KINDS - {"semester_break"}:
            hits = [skb[x.isoformat()] for x in days(d(a), d(b)) if x.isoformat() in skb]
            missing = [x.isoformat() for x in days(d(a), d(b)) if x.isoformat() not in skb]
            if hits and not missing:
                e["skb"] = "matches " + "; ".join(f"SKB {y} {h['ref']}" for y, h in hits)
            elif hits:
                e["skb"] = ("partly in the SKB: " + "; ".join(f"{h['date']} SKB {y} {h['ref']}" for y, h in hits)
                            + "; not in the SKB: " + ", ".join(missing))
            elif kind in ("public_holiday", "cuti_bersama"):
                e["skb"] = "not in the SKB on this date: " + ", ".join(missing)
        events.append(e)
    not_listed = []
    for date, (year, day) in sorted(skb.items()):
        x = d(date)
        if YEAR_START <= x <= YEAR_END and x not in covered and x.weekday() != 6:
            wd = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"][x.weekday()]
            kind = "cuti bersama" if day["kind"] == "cuti_bersama" else "libur nasional"
            not_listed.append(f"{date} {wd} {kind}: {day['label']}")

    if errors:
        sys.exit("transcription check failed:\n  " + "\n  ".join(errors))

    data = {
        "name": "Kalender pendidikan madrasah Provinsi Jawa Tengah",
        "province_code": "33",
        "kinds": ["first_day", "orientation", "teacher_training", "ceremony", "public_holiday", "cuti_bersama",
                  "ramadan", "eid_break", "national_test", "summative", "school_exam", "report", "semester_break",
                  "next_year"],
        "years": [{
            "academic_year": "2026/2027",
            "regulation": "Keputusan Kepala Kantor Wilayah Kementerian Agama Provinsi Jawa Tengah Nomor 1681 Tahun 2026 "
                          "tentang Pedoman Penyusunan Kalender Pendidikan Madrasah Tahun Ajaran 2026/2027 "
                          "(ditetapkan di Semarang, 29 Juni 2026)",
            "based_on": "Keputusan Direktur Jenderal Pendidikan Islam Nomor 4860 Tahun 2026 tentang Pedoman Kalender "
                        "Pendidikan Madrasah Tahun Ajaran 2026/2027",
            "applies_to": "RA, MI, MTs, MA and MAK in Jawa Tengah (Pasal 1 angka 2); kabupaten/kota offices may add "
                          "details (Pasal 23)",
            "source_file": SRC,
            "school_week": "six days: Saturdays are school days in the printed HE counts",
            "rules": {
                "first_day": "2026-07-13",
                "orientation": ["2026-07-13", "2026-07-18"],
                "class_plans_due": "2026-07-11 (Pasal 2)",
                "min_effective_weeks": 36,
                "min_effective_weeks_final_grades_even_semester": 14,
                "lessons_start": "07.00 WIB unless the kabupaten/kota office sets another time (Pasal 7)",
                "lesson_minutes": {"RA": 30, "MI": 35, "MTs": 40, "MA/MAK": 45},
                "ramadan_lesson_minutes": {"RA": "set by the madrasah", "MI": 30, "MTs": 30, "MA/MAK": 35},
                "summative_semester_1": ["2026-11-23", "2026-12-05"],
                "summative_year_end": ["2027-05-24", "2027-06-05"],
                "reports": ["2026-12-19", "2027-06-19"],
                "school_exam": "dates follow the Direktur Jenderal Pendidikan Islam (Pasal 13 ayat (1))",
                "tka_an": "Keputusan Mendikdasmen Nomor 56 Tahun 2026; for MTs and MI in 2027 the dates follow "
                          "Kemendikdasmen (Lampiran Maret–April, marked without dates)",
                "holidays_2027": "public holidays, cuti bersama and Ramadan days in 2027 follow the government's "
                                 "decision (Pasal 22)",
            },
            "month_counts": month_counts,
            "semester_counts": {k: {"hk": v[2], "hl": v[3], "he": v[4]} for k, v in SEMESTERS.items()},
            "skb_days_not_in_this_calendar": not_listed,
            "events": events,
        }],
        "notes": [
            "Transcribed from the official decree (PDF with the Kanwil cover letter B-1740/Kw.11.2/PP.00/07/2026); "
            "the spreadsheet that came with it (ayomadrasah.id) is not a source: it has leftover 2025 rows and wrong "
            "dates (e.g. Hari Pahlawan on 10 Oktober).",
            "HL per month is recomputed from Sundays, holiday events and the report-card Saturdays (19 Desember 2026, "
            "19 Juni 2027), which the Lampiran counts as days off; all twelve months match the printed HK/HL/HE.",
            "Dates marked estimate follow the decree's estimate; the national SKB (data set libur-nasional) wins "
            "where it differs (F-025).",
        ],
    }
    os.makedirs(OUT, exist_ok=True)
    body = json.dumps(data, ensure_ascii=False, indent=1) + "\n"
    with open(os.path.join(OUT, "kaldik-madrasah-jateng.json"), "w", encoding="utf-8") as f:
        f.write(body)
    src_path = os.path.join(ROOT, SRC)
    manifest = {
        "version": VERSION,
        "description": "Education calendar of madrasah (RA, MI, MTs, MA, MAK) in Jawa Tengah: 2026/2027 in full "
                       f"({len(events)} dated events from the decree and its Lampiran, with its rules and the printed "
                       "HK/HL/HE per month).",
        "status": "ready for 2026/2027",
        "source": "Kantor Wilayah Kementerian Agama Provinsi Jawa Tengah, Keputusan Nomor 1681 Tahun 2026 (raw PDF and "
                  "SOURCE.txt in sources/kaldik-madrasah-jateng/, received from the user, brief R-06)",
        "licence": "Public government document",
        "procedure": "Transcribed by hand into tools/converters/kaldik-madrasah-jateng.py, which recomputes HK/HL/HE "
                     "per month against the Lampiran, compares every holiday with libur-nasional and writes the JSON.",
        "source_sha256": hashlib.sha256(open(src_path, "rb").read()).hexdigest() if os.path.exists(src_path) else None,
        "counts": {"events": len(events), "skb_days_not_in_this_calendar": len(not_listed)},
        "files": ["kaldik-madrasah-jateng.json"],
    }
    with open(os.path.join(OUT, "manifest.json"), "w", encoding="utf-8") as f:
        f.write(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    print(f"wrote {len(events)} events; months checked: {len(month_counts)}; SKB days not listed: {len(not_listed)}")
    for e in events:
        if "skb" in e and not e["skb"].startswith("matches"):
            print("  skb:", e["start"], e["label"], "->", e["skb"])
    for x in not_listed:
        print("  not listed:", x)


if __name__ == "__main__":
    main()
