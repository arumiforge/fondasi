#!/usr/bin/env python3
"""Build data/libur-nasional/libur-nasional.json from the SKB 3 Menteri on national holidays and cuti bersama.

The PDFs (sources/libur-nasional/) are scans without a text layer, so their Lampiran tables are transcribed by hand
below, exactly as printed (date, weekday, keterangan). This script is the documented procedure: it expands date
ranges into one row per day and refuses to write when a printed weekday does not match the date.

  python3 -I tools/converters/libur-nasional.py data/libur-nasional/libur-nasional.json

Adding a year: transcribe its Lampiran A and B into DECREES, keep the raw PDF and SOURCE.txt, run this,
bump the manifest version to the decree's signing date, tools/data-check --write.
"""
import datetime
import json
import sys

MONTHS = {"Januari": 1, "Februari": 2, "Maret": 3, "April": 4, "Mei": 5, "Juni": 6, "Juli": 7, "Agustus": 8,
          "September": 9, "Oktober": 10, "November": 11, "Desember": 12}
WEEKDAYS = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]

# (days, month, printed weekdays, keterangan) — `days` lists every day the row covers.
DECREES = [
    {
        "year": 2026,
        "decree": "Keputusan Bersama Menteri Agama, Menteri Ketenagakerjaan, dan Menteri Pendayagunaan Aparatur "
                  "Negara dan Reformasi Birokrasi Nomor 1497 Tahun 2025, Nomor 2 Tahun 2025, Nomor 5 Tahun 2025 "
                  "tentang Hari Libur Nasional dan Cuti Bersama Tahun 2026",
        "signed": "2025-09-19",
        "source_file": "sources/libur-nasional/SKB-Libur-Nasional-dan-Cuti-Bersama-Tahun-2026.pdf",
        "libur": [
            ([1], "Januari", ["Kamis"], "Tahun Baru 2026 Masehi"),
            ([16], "Januari", ["Jumat"], "Isra Mikraj Nabi Muhammad S.A.W."),
            ([17], "Februari", ["Selasa"], "Tahun Baru Imlek 2577 Kongzili"),
            ([19], "Maret", ["Kamis"], "Hari Suci Nyepi (Tahun Baru Saka 1948)"),
            ([21, 22], "Maret", ["Sabtu", "Minggu"], "Idul Fitri 1447 Hijriah"),
            ([3], "April", ["Jumat"], "Wafat Yesus Kristus"),
            ([5], "April", ["Minggu"], "Kebangkitan Yesus Kristus (Paskah)"),
            ([1], "Mei", ["Jumat"], "Hari Buruh Internasional"),
            ([14], "Mei", ["Kamis"], "Kenaikan Yesus Kristus"),
            ([27], "Mei", ["Rabu"], "Idul Adha 1447 Hijriah"),
            ([31], "Mei", ["Minggu"], "Hari Raya Waisak 2570 BE"),
            ([1], "Juni", ["Senin"], "Hari Lahir Pancasila"),
            ([16], "Juni", ["Selasa"], "1 Muharam Tahun Baru Islam 1448 Hijriah"),
            ([17], "Agustus", ["Senin"], "Proklamasi Kemerdekaan"),
            ([25], "Agustus", ["Selasa"], "Maulid Nabi Muhammad S.A.W."),
            ([25], "Desember", ["Jumat"], "Kelahiran Yesus Kristus"),
        ],
        "cuti": [
            ([16], "Februari", ["Senin"], "Tahun Baru Imlek 2577 Kongzili"),
            ([18], "Maret", ["Rabu"], "Hari Suci Nyepi (Tahun Baru Saka 1948)"),
            ([20, 23, 24], "Maret", ["Jumat", "Senin", "Selasa"], "Idul Fitri 1447 Hijriah"),
            ([15], "Mei", ["Jumat"], "Kenaikan Yesus Kristus"),
            ([28], "Mei", ["Kamis"], "Idul Adha 1447 Hijriah"),
            ([24], "Desember", ["Kamis"], "Kelahiran Yesus Kristus"),
        ],
    },
    {
        "year": 2027,
        "decree": "Keputusan Bersama Menteri Agama, Menteri Ketenagakerjaan, dan Menteri Pendayagunaan Aparatur "
                  "Negara dan Reformasi Birokrasi Nomor 1205 Tahun 2026, Nomor 3 Tahun 2026, Nomor 2 Tahun 2026 "
                  "tentang Hari Libur Nasional dan Cuti Bersama Tahun 2027",
        "signed": "2026-09-15",
        "source_file": "sources/libur-nasional/SKB-Libur-Nasional-dan-Cuti-Bersama-Tahun-2027.pdf",
        "libur": [
            ([1], "Januari", ["Jumat"], "Tahun Baru 2027 Masehi"),
            ([5], "Januari", ["Selasa"], "Isra Mikraj Nabi Muhammad S.A.W. 1448 Hijriah"),
            ([6], "Februari", ["Sabtu"], "Tahun Baru Imlek 2578 Kongzili"),
            ([8], "Maret", ["Senin"], "Hari Suci Nyepi (Tahun Baru Saka 1949)"),
            ([10, 11], "Maret", ["Rabu", "Kamis"], "Idul Fitri 1448 Hijriah"),
            ([26], "Maret", ["Jumat"], "Wafat Yesus Kristus"),
            ([28], "Maret", ["Minggu"], "Kebangkitan Yesus Kristus (Paskah)"),
            ([1], "Mei", ["Sabtu"], "Hari Buruh Internasional"),
            ([6], "Mei", ["Kamis"], "Kenaikan Yesus Kristus"),
            ([17], "Mei", ["Senin"], "Idul Adha 1448 Hijriah"),
            ([20], "Mei", ["Kamis"], "Hari Raya Waisak 2571 BE"),
            ([1], "Juni", ["Selasa"], "Hari Lahir Pancasila"),
            ([6], "Juni", ["Minggu"], "1 Muharam Tahun Baru Islam 1449 Hijriah"),
            ([15], "Agustus", ["Minggu"], "Maulid Nabi Muhammad S.A.W."),
            ([17], "Agustus", ["Selasa"], "Proklamasi Kemerdekaan"),
            ([25], "Desember", ["Sabtu"], "Kelahiran Yesus Kristus"),
            ([26], "Desember", ["Minggu"], "Isra Mikraj Nabi Muhammad S.A.W. 1449 Hijriah"),
        ],
        "cuti": [
            ([5], "Februari", ["Jumat"], "Tahun Baru Imlek 2578 Kongzili"),
            ([9, 12, 15], "Maret", ["Selasa", "Jumat", "Senin"], "Idul Fitri 1448 Hijriah"),
            ([25], "Maret", ["Kamis"], "Wafat Yesus Kristus"),
            ([18], "Mei", ["Selasa"], "Idul Adha 1448 Hijriah"),
            ([19], "Mei", ["Rabu"], "Hari Raya Waisak 2571 BE"),
            ([24], "Desember", ["Jumat"], "Kelahiran Yesus Kristus"),
        ],
    },
]



def rows(dec, key, kind, table):
    out = []
    for no, (days, month, wds, label) in enumerate(dec[key], 1):
        if len(days) != len(wds):
            sys.exit(f"{dec['year']} {table} no. {no}: {len(days)} days but {len(wds)} weekdays")
        for d, wd in zip(days, wds):
            date = datetime.date(dec["year"], MONTHS[month], d)
            if WEEKDAYS[date.weekday()] != wd:
                sys.exit(f"{dec['year']} {table} no. {no}: {date} is {WEEKDAYS[date.weekday()]}, source says {wd}")
            row = {"date": date.isoformat(), "weekday": wd, "kind": kind, "label": label,
                   "ref": f"Lampiran {table} no. {no}"}
            if any(x in label for x in ("Idul Fitri", "Idul Adha")):
                row["set_by_minister_of_religion"] = True
            out.append(row)
    return out


def main(dst):
    years = []
    for dec in DECREES:
        days = rows(dec, "libur", "public_holiday", "A") + rows(dec, "cuti", "cuti_bersama", "B")
        days.sort(key=lambda r: (r["date"], r["kind"]))
        dates = [r["date"] for r in days]
        if len(dates) != len(set(dates)):
            sys.exit(f"{dec['year']}: a date is listed twice")
        years.append({
            "year": dec["year"], "decree": dec["decree"], "signed": dec["signed"], "source_file": dec["source_file"],
            "public_holidays": sum(r["kind"] == "public_holiday" for r in days),
            "cuti_bersama": sum(r["kind"] == "cuti_bersama" for r in days),
            "days": days,
        })
    out = {
        "name": "Hari libur nasional dan cuti bersama",
        "kinds": {"public_holiday": "Hari libur nasional (Lampiran A)", "cuti_bersama": "Cuti bersama (Lampiran B)"},
        "years": years,
        "notes": [
            "One row per day; a range in the source (e.g. '21-22 Maret') becomes one row per day.",
            "KEDUA of each decree: 1 Ramadan, Idul Fitri and Idul Adha are fixed by a decree of the Minister of "
            "Religious Affairs (sidang isbat); rows marked set_by_minister_of_religion may move by a day. "
            "Idul Fitri 1447 H was fixed on 21 Maret 2026, as in the SKB.",
            "Cuti bersama reduces annual leave (KEEMPAT); for ASN it follows a Keputusan Presiden, for private "
            "employers it is set by each employer (KELIMA, KEENAM). Schools follow their own calendar authority "
            "(kaldik-jateng, kalender-nasional), which usually adopts these days.",
            "Weekend days are listed when the source lists them (e.g. Paskah on a Sunday).",
        ],
    }
    with open(dst, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
        f.write("\n")
    for y in years:
        print(f"{y['year']}: {y['public_holidays']} public holiday days, {y['cuti_bersama']} cuti bersama days")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
