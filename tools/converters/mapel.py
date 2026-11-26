#!/usr/bin/env python3
"""Build the data set `mapel` (R-08, F-030): subjects and time allocation per level and grade.

Sources (sources/mapel/, SOURCE.txt):
  - Permendikdasmen 13/2025, Lampiran II "Struktur Kurikulum" (replaces Lampiran II of Permendikbudristek 12/2024):
    Tabel 1–29 for SD/MI, SMP/MTs, SMA/MA, SMK/MAK, SDLB/MILB, SMPLB/MTsLB, SMALB/MALB and Paket A/B/C, plus PAUD.
  - Permendikbudristek 12/2024, articles still in force (Pasal 33: Bahasa Inggris SD/MI transition).
  - KMA 1503/2025, Lampiran II BAB III (madrasah: MI, MTs, MA, MAK, MILB, MTsLB, MALB; RA), a scanned decree:
    every cell read from the page images, see KMA_TABLES.

The tables are transcribed by hand below with the PDF page of every table (the text layer is clean; merged cells
were checked on page images). The script checks every row (intrakurikuler + kokurikuler = total) and every printed
total row against the sum of its rows, then writes data/mapel/mapel.json:

  python3 -I tools/converters/mapel.py data

Conventions: JP per school year as printed; a printed "-" is stored as 0; a range such as "720-900" is stored as
[min, max]. `key` values are Fondasi keys for joining tables (not official codes; Dapodik subject codes come with
referensi-dapodik, R-07). Labels are as printed.
"""
import json
import os
import sys

P13 = "Permendikdasmen 13/2025, Lampiran II"
P12 = "Permendikbudristek 12/2024"

# ------------------------------------------------------------------ subjects (labels as printed)

RELIGIONS = ["Pendidikan Agama Islam dan Budi Pekerti", "Pendidikan Agama Kristen dan Budi Pekerti",
             "Pendidikan Agama Katolik dan Budi Pekerti", "Pendidikan Agama Buddha dan Budi Pekerti",
             "Pendidikan Agama Hindu dan Budi Pekerti", "Pendidikan Agama Khonghucu dan Budi Pekerti"]
ARTS = ["Seni Musik", "Seni Rupa", "Seni Teater", "Seni Tari"]
ARTS_CRAFTS = ARTS + ["Prakarya Budi Daya", "Prakarya Kerajinan", "Prakarya Rekayasa", "Prakarya Pengolahan"]
PKK = ["Pengembangan orientasi, mobilitas, sosial, dan komunikasi (penyandang disabilitas netra)",
       "Pengembangan komunikasi, persepsi bunyi, dan irama (penyandang disabilitas rungu)",
       "Pengembangan diri (penyandang disabilitas intelektual)",
       "Pengembangan diri dan pengembangan gerak (penyandang disabilitas fisik)",
       "Pengembangan komunikasi, interaksi sosial, dan perilaku (penyandang disabilitas mental)"]
SKILLS = ["Tata Busana", "Tata Boga", "Tata Kecantikan", "Tata Gerha", "Teknologi Informasi Komunikasi",
          "Perbengkelan Sepeda Motor", "Cetak Saring/Sablon", "Seni Membatik", "Suvenir",
          "Budidaya Tanaman Hortikultura", "Pijat/Akupresur", "Teknik Penyiaran Radio", "Seni Musik", "Fotografi",
          "Desain Grafis", "Seni Tari", "Seni Lukis", "Elektronika Alat Rumah Tangga", "Budidaya Perikanan",
          "Budidaya Peternakan", "Koding dan Kecerdasan Artifisial"]

SUBJECTS = {
    "pendidikan_agama": {"label": "Pendidikan Agama dan Budi Pekerti", "variants": RELIGIONS,
                         "note": "One row with a merged cell in every table; each student takes the variant of "
                                 "their religion (footnote a)."},
    "pendidikan_pancasila": {"label": "Pendidikan Pancasila"},
    "bahasa_indonesia": {"label": "Bahasa Indonesia"},
    "matematika": {"label": "Matematika"},
    "ipas": {"label": "Ilmu Pengetahuan Alam dan Sosial"},
    "ipa": {"label": "Ilmu Pengetahuan Alam"},
    "ips": {"label": "Ilmu Pengetahuan Sosial"},
    "bahasa_inggris": {"label": "Bahasa Inggris"},
    "pjok": {"label": "Pendidikan Jasmani Olahraga dan Kesehatan",
             "aliases": ["Pendidikan Jasmani, Olahraga, dan Kesehatan", "PJOK"]},
    "seni_budaya": {"label": "Seni dan Budaya", "options": ARTS,
                    "note": "The school offers at least one; each student chooses one."},
    "seni_budaya_prakarya": {"label": "Seni, Budaya, dan Prakarya", "options": ARTS_CRAFTS,
                             "note": "The school offers at least one; each student chooses one."},
    "informatika": {"label": "Informatika"},
    "sejarah": {"label": "Sejarah"},
    "koding_ka": {"label": "Koding dan Kecerdasan Artifisial"},
    "muatan_lokal": {"label": "Muatan Lokal"},
    # SMA/MA electives (Fase F)
    "matematika_lanjut": {"label": "Matematika Tingkat Lanjut"},
    "fisika": {"label": "Fisika"},
    "kimia": {"label": "Kimia"},
    "biologi": {"label": "Biologi"},
    "geografi": {"label": "Geografi"},
    "sejarah_lanjut": {"label": "Sejarah Tingkat Lanjut"},
    "sosiologi": {"label": "Sosiologi"},
    "ekonomi": {"label": "Ekonomi"},
    "bahasa_indonesia_lanjut": {"label": "Bahasa Indonesia Tingkat Lanjut"},
    "bahasa_inggris_lanjut": {"label": "Bahasa Inggris Tingkat Lanjut"},
    "bahasa_arab": {"label": "Bahasa Arab"},
    "bahasa_jepang": {"label": "Bahasa Jepang"},
    "bahasa_jerman": {"label": "Bahasa Jerman"},
    "bahasa_korea": {"label": "Bahasa Korea"},
    "bahasa_mandarin": {"label": "Bahasa Mandarin"},
    "bahasa_prancis": {"label": "Bahasa Prancis"},
    "antropologi": {"label": "Antropologi"},
    "prakarya_kewirausahaan": {"label": "Prakarya dan Kewirausahaan",
                               "options": ["budi daya", "kerajinan", "rekayasa", "pengolahan"]},
    "mapel_lainnya": {"label": "Mata pelajaran lainnya yang dikembangkan sesuai dengan sumber daya yang tersedia"},
    # SMK/MAK
    "projek_ipas": {"label": "Projek Ilmu Pengetahuan Alam dan Sosial",
                    "note": "The share of science and social science follows the needs of the Program Keahlian."},
    "dasar_program_keahlian": {"label": "Dasar-Dasar Program Keahlian",
                               "note": "The subject name follows the name of the Program Keahlian."},
    "konsentrasi_keahlian": {"label": "Konsentrasi Keahlian",
                             "note": "The subject name follows the name of the Konsentrasi Keahlian."},
    "kik": {"label": "Kreativitas, Inovasi, dan Kewirausahaan"},
    "pkl": {"label": "Praktik Kerja Lapangan"},
    "mapel_pilihan_smk": {"label": "Mata Pelajaran Pilihan",
                          "note": "The subject the student chooses (to start a business, work in the field or "
                                  "continue studying)."},
    # special education
    "program_kebutuhan_khusus": {"label": "Program Kebutuhan Khusus", "options": PKK,
                                 "note": "Chosen according to the student's disability."},
    "kelompok_keterampilan": {"label": "Kelompok Keterampilan", "options": SKILLS,
                              "note": "Schools may develop other skills (explanation 4, PDF p. 65)."},
    # madrasah (KMA 1503/2025)
    "quran_hadis": {"label": "Al-Qur'an Hadis",
                    "note": "MA Program Keagamaan: taught as Tafsir and Hadis (KMA 1503/2025, MA rule 13, p. 42)."},
    "akidah_akhlak": {"label": "Akidah Akhlak",
                      "note": "MA Program Keagamaan: taught as Ilmu Kalam and Akhlak Tasawuf (MA rule 13, p. 42)."},
    "fikih": {"label": "Fikih"},
    "ski": {"label": "Sejarah Kebudayaan Islam"},
    "penguatan_program": {"label": "Penguatan Program",
                          "note": "For MA with an SK of the Direktorat Jenderal Pendidikan Islam (MA Program "
                                  "Keagamaan, MA Akademik, MA Plus Keterampilan)."},
    "ilmu_tafsir": {"label": "Ilmu Tafsir"},
    "ilmu_hadis": {"label": "Ilmu Hadis"},
    "ushul_fikih": {"label": "Ushul Fikih"},
    "bahasa_arab_lanjut": {"label": "Bahasa Arab Tingkat Lanjut"},
    "mapel_lainnya_ma": {"label": "Mata pelajaran lainnya yang dikembangkan sesuai dengan penguatan program"},
    # kesetaraan
    "pemberdayaan_keterampilan": {"label": "Muatan Pemberdayaan dan Keterampilan",
                                  "options": ["Pemberdayaan", "Keterampilan"],
                                  "note": "Carried out as kokurikuler."},
}

SMA_ELECTIVES = ["matematika_lanjut", "fisika", "kimia", "biologi", "geografi", "sejarah_lanjut", "sosiologi",
                 "ekonomi", "bahasa_indonesia_lanjut", "bahasa_inggris_lanjut", "bahasa_arab", "bahasa_jepang",
                 "bahasa_jerman", "bahasa_korea", "bahasa_mandarin", "bahasa_prancis", "antropologi", "informatika",
                 "koding_ka", "prakarya_kewirausahaan", "mapel_lainnya"]

# ------------------------------------------------------------------ tables

ENGLISH_SD = ("Until 2026/2027 an elective that schools offer when ready; compulsory from 2027/2028 "
              f"({P12} Pasal 33 huruf a, not amended by Permendikdasmen 13/2025).")


def row(key, group, intra, ko, total, **extra):
    r = {"subject": key, "group": group, "intrakurikuler": intra, "kokurikuler": ko, "total": total}
    r.update(extra)
    return r


def wajib(*rows):
    return [row(k, "wajib", i, ko, t, **(x[0] if x else {})) for k, i, ko, t, *x in rows]


def sd_table(n, grades, weeks, pages, rows, total_wajib, extra_rows, totals, footnotes):
    return {"table": n, "levels": ["SD", "MI"], "grades": grades, "weeks_per_year": weeks, "jp_minutes": 35,
            "pages": pages, "rows": rows + extra_rows, "totals": totals, "footnotes": footnotes}


FN_REL = "Diikuti oleh Peserta Didik sesuai dengan agama masing-masing."
FN_ARTS = ("Satuan Pendidikan menyediakan minimal 1 (satu) jenis seni (seni musik, seni rupa, seni teater, dan/atau "
           "seni tari). Peserta Didik memilih 1 (satu) jenis seni (seni musik, seni rupa, seni teater, atau seni tari).")
FN_ARTS_CRAFTS = ("Satuan Pendidikan menyediakan minimal 1 (satu) jenis seni atau prakarya (seni musik, seni rupa, "
                  "seni teater, seni tari, prakarya budi daya, prakarya kerajinan, prakarya rekayasa, dan/atau "
                  "prakarya pengolahan). Peserta Didik memilih 1 (satu) jenis seni atau prakarya.")


def fn_mulok(jp):
    return f"Paling banyak 2 (dua) JP per minggu atau {jp} JP per tahun."


def fn_kka(jp):
    return f"Dialokasikan 2 (dua) JP per minggu atau {jp} JP per tahun sebagai mata pelajaran pilihan."


EN = {"transition": ENGLISH_SD, "compulsory_from": "2027/2028"}

TABLES = [
    # ---------------- SD/MI (Lampiran II B)
    {"table": 1, "levels": ["SD", "MI"], "grades": [1], "weeks_per_year": 36, "jp_minutes": 35, "pages": [15, 16],
     "rows": wajib(("pendidikan_agama", 108, 36, 144), ("pendidikan_pancasila", 144, 36, 180),
                   ("bahasa_indonesia", 252, 36, 288), ("matematika", 144, 36, 180), ("pjok", 108, 36, 144),
                   ("seni_budaya", 108, 36, 144))
     + [row("muatan_lokal", "muatan_lokal", 72, 0, 72)],
     "totals": [{"label": "Total JP Mata Pelajaran Wajib", "sum": ["wajib"], "jp": [864, 216, 1080]},
                {"label": "Total JP Mata Pelajaran Umum + Muatan Lokal", "sum": ["wajib", "muatan_lokal"],
                 "jp": [936, 216, 1152], "note": "Tabel 2–3 call this row 'Wajib + Muatan Lokal'."}],
     "footnotes": {"a": FN_REL, "b": FN_ARTS, "c": fn_mulok(72)}},
    {"table": 2, "levels": ["SD", "MI"], "grades": [2], "weeks_per_year": 36, "jp_minutes": 35, "pages": [16, 17],
     "rows": wajib(("pendidikan_agama", 108, 36, 144), ("pendidikan_pancasila", 144, 36, 180),
                   ("bahasa_indonesia", 288, 36, 324), ("matematika", 180, 36, 216), ("pjok", 108, 36, 144),
                   ("seni_budaya", 108, 36, 144))
     + [row("muatan_lokal", "muatan_lokal", 72, 0, 72)],
     "totals": [{"label": "Total JP Mata Pelajaran Wajib", "sum": ["wajib"], "jp": [936, 216, 1152]},
                {"label": "Total JP Mata Pelajaran Wajib + Muatan Lokal", "sum": ["wajib", "muatan_lokal"],
                 "jp": [1008, 216, 1224]}],
     "footnotes": {"a": FN_REL, "b": FN_ARTS, "c": fn_mulok(72)}},
    {"table": 3, "levels": ["SD", "MI"], "grades": [3, 4], "weeks_per_year": 36, "jp_minutes": 35, "pages": [17, 18],
     "rows": wajib(("pendidikan_agama", 108, 36, 144), ("pendidikan_pancasila", 144, 36, 180),
                   ("bahasa_indonesia", 216, 36, 252), ("matematika", 180, 36, 216), ("ipas", 180, 36, 216),
                   ("pjok", 108, 36, 144), ("seni_budaya", 108, 36, 144), ("bahasa_inggris", 72, 0, 72, EN))
     + [row("muatan_lokal", "muatan_lokal", 72, 0, 72)],
     "totals": [{"label": "Total JP Mata Pelajaran Wajib", "sum": ["wajib"], "jp": [1116, 252, 1368]},
                {"label": "Total JP Mata Pelajaran Wajib + Muatan Lokal", "sum": ["wajib", "muatan_lokal"],
                 "jp": [1188, 252, 1440]}],
     "footnotes": {"a": FN_REL, "b": FN_ARTS, "c": fn_mulok(72)}},
    {"table": 4, "levels": ["SD", "MI"], "grades": [5], "weeks_per_year": 36, "jp_minutes": 35, "pages": [18, 20],
     "rows": wajib(("pendidikan_agama", 108, 36, 144), ("pendidikan_pancasila", 144, 36, 180),
                   ("bahasa_indonesia", 216, 36, 252), ("matematika", 180, 36, 216), ("ipas", 180, 36, 216),
                   ("pjok", 108, 36, 144), ("seni_budaya", 108, 36, 144), ("bahasa_inggris", 72, 0, 72, EN))
     + [row("koding_ka", "pilihan", 72, 0, 72), row("muatan_lokal", "muatan_lokal", 72, 0, 72)],
     "totals": [{"label": "Total JP Mata Pelajaran Wajib", "sum": ["wajib"], "jp": [1116, 252, 1368]},
                {"label": "Total JP Mata Pelajaran Wajib + Mata Pelajaran Pilihan/Muatan Lokal",
                 "sum": ["wajib", "muatan_lokal"], "jp": [1188, 252, 1440]},
                {"label": "Total JP Mata Pelajaran Wajib + Mata Pelajaran Pilihan + Muatan Lokal",
                 "sum": ["wajib", "pilihan", "muatan_lokal"], "jp": [1260, 252, 1512]}],
     "footnotes": {"a": FN_REL, "b": FN_ARTS, "c": fn_kka(72), "d": fn_mulok(72)}},
    {"table": 5, "levels": ["SD", "MI"], "grades": [6], "weeks_per_year": 32, "jp_minutes": 35, "pages": [20, 21],
     "rows": wajib(("pendidikan_agama", 96, 32, 128), ("pendidikan_pancasila", 128, 32, 160),
                   ("bahasa_indonesia", 192, 32, 224), ("matematika", 160, 32, 192), ("ipas", 160, 32, 192),
                   ("pjok", 96, 32, 128), ("seni_budaya", 96, 32, 128), ("bahasa_inggris", 64, 0, 64, EN))
     + [row("koding_ka", "pilihan", 64, 0, 64), row("muatan_lokal", "muatan_lokal", 64, 0, 64)],
     "totals": [{"label": "Total JP Mata Pelajaran Wajib", "sum": ["wajib"], "jp": [992, 224, 1216]},
                {"label": "Total JP Mata Pelajaran Wajib + Mata Pelajaran Pilihan/Muatan Lokal",
                 "sum": ["wajib", "muatan_lokal"], "jp": [1056, 224, 1280]},
                {"label": "Total JP Mata Pelajaran Wajib + Mata Pelajaran Pilihan + Muatan Lokal",
                 "sum": ["wajib", "pilihan", "muatan_lokal"], "jp": [1120, 224, 1344]}],
     "footnotes": {"a": FN_REL, "b": FN_ARTS, "c": fn_kka(64), "d": fn_mulok(64)}},
    # ---------------- SMP/MTs (Lampiran II C)
    {"table": 6, "levels": ["SMP", "MTs"], "grades": [7, 8], "weeks_per_year": 36, "jp_minutes": 40,
     "pages": [22, 23],
     "rows": wajib(("pendidikan_agama", 72, 36, 108), ("pendidikan_pancasila", 72, 36, 108),
                   ("bahasa_indonesia", 180, 36, 216), ("matematika", 144, 36, 180), ("ipa", 144, 36, 180),
                   ("ips", 108, 36, 144), ("bahasa_inggris", 108, 36, 144), ("pjok", 72, 36, 108),
                   ("informatika", 72, 36, 108), ("seni_budaya_prakarya", 72, 36, 108))
     + [row("koding_ka", "pilihan", 72, 0, 72), row("muatan_lokal", "muatan_lokal", 72, 0, 72)],
     "totals": [{"label": "Total JP Mata Pelajaran Wajib", "sum": ["wajib"], "jp": [1044, 360, 1404]},
                {"label": "Total JP Mata Pelajaran Wajib + Mata Pelajaran Pilihan/Muatan Lokal",
                 "sum": ["wajib", "muatan_lokal"], "jp": [1116, 360, 1476]},
                {"label": "Total JP Mata Pelajaran Wajib + Mata Pelajaran Pilihan + Muatan Lokal",
                 "sum": ["wajib", "pilihan", "muatan_lokal"], "jp": [1188, 360, 1548]}],
     "footnotes": {"a": FN_REL, "b": FN_ARTS_CRAFTS, "c": fn_kka(72), "d": fn_mulok(72)}},
    {"table": 7, "levels": ["SMP", "MTs"], "grades": [9], "weeks_per_year": 32, "jp_minutes": 40,
     "pages": [23, 25],
     "rows": wajib(("pendidikan_agama", 64, 32, 96), ("pendidikan_pancasila", 64, 32, 96),
                   ("bahasa_indonesia", 160, 32, 192), ("matematika", 128, 32, 160), ("ipa", 128, 32, 160),
                   ("ips", 96, 32, 128), ("bahasa_inggris", 96, 32, 128), ("pjok", 64, 32, 96),
                   ("informatika", 64, 32, 96), ("seni_budaya_prakarya", 64, 32, 96))
     + [row("koding_ka", "pilihan", 64, 0, 64), row("muatan_lokal", "muatan_lokal", 64, 0, 64)],
     "totals": [{"label": "Total JP Mata Pelajaran Wajib", "sum": ["wajib"], "jp": [928, 320, 1248]},
                {"label": "Total JP Mata Pelajaran Wajib + Mata Pelajaran Pilihan/Muatan Lokal",
                 "sum": ["wajib", "muatan_lokal"], "jp": [992, 320, 1312]},
                {"label": "Total JP Mata Pelajaran Wajib + Mata Pelajaran Pilihan + Muatan Lokal",
                 "sum": ["wajib", "pilihan", "muatan_lokal"], "jp": [1056, 320, 1376]}],
     "footnotes": {"a": FN_REL, "b": FN_ARTS_CRAFTS, "c": fn_kka(64), "d": fn_mulok(64)}},
    # ---------------- SMA/MA (Lampiran II D)
    {"table": 8, "levels": ["SMA", "MA"], "grades": [10], "weeks_per_year": 36, "jp_minutes": 45,
     "pages": [26, 27],
     "rows": wajib(("pendidikan_agama", 72, 36, 108), ("pendidikan_pancasila", 72, 0, 72),
                   ("bahasa_indonesia", 108, 36, 144), ("matematika", 108, 36, 144),
                   ("ipa", 216, 108, 324, {"components": ["Fisika", "Kimia", "Biologi"]}),
                   ("ips", 288, 144, 432, {"components": ["Sosiologi", "Ekonomi", "Sejarah", "Geografi"]}),
                   ("bahasa_inggris", 108, 0, 108), ("pjok", 72, 36, 108), ("informatika", 72, 0, 72),
                   ("seni_budaya_prakarya", 72, 0, 72))
     + [row("koding_ka", "pilihan", 72, 0, 72), row("muatan_lokal", "muatan_lokal", 72, 0, 72)],
     "totals": [{"label": "Total JP Mata Pelajaran Wajib", "sum": ["wajib"], "jp": [1188, 396, 1584]},
                {"label": "Total JP Mata Pelajaran Wajib + Mata Pelajaran Pilihan/Muatan Lokal",
                 "sum": ["wajib", "muatan_lokal"], "jp": [1260, 396, 1656]},
                {"label": "Total JP Mata Pelajaran Wajib + Mata Pelajaran Pilihan + Muatan Lokal",
                 "sum": ["wajib", "pilihan", "muatan_lokal"], "jp": [1332, 396, 1728]}],
     "footnotes": {"a": FN_REL, "b": FN_ARTS_CRAFTS, "c": fn_kka(72), "d": fn_mulok(72)},
     "note": "IPA and IPS in grade X are not split into separate subjects; the school organises their content "
             "(integrated, in alternating blocks, or in parallel with separate JP) (PDF p. 27–28)."},
    {"table": 9, "levels": ["SMA", "MA"], "grades": [11], "weeks_per_year": 36, "jp_minutes": 45,
     "pages": [28, 30],
     "rows": wajib(("pendidikan_agama", 72, 36, 108), ("pendidikan_pancasila", 72, 0, 72),
                   ("bahasa_indonesia", 108, 36, 144), ("matematika", 108, 36, 144), ("bahasa_inggris", 108, 0, 108),
                   ("pjok", 72, 36, 108), ("sejarah", 72, 0, 72), ("seni_budaya", 72, 0, 72))
     + [row("pilihan_sma", "pilihan", [720, 900], 0, [720, 900], options=SMA_ELECTIVES,
            choose=[4, 5], jp_each=180, jp_each_exceptions={"prakarya_kewirausahaan": 72}),
        row("muatan_lokal", "muatan_lokal", 72, 0, 72)],
     "totals": [{"label": "Total JP Mata Pelajaran Wajib", "sum": ["wajib"], "jp": [684, 144, 828]},
                {"label": "Total JP Mata Pelajaran Wajib + Mata Pelajaran Pilihan", "sum": ["wajib", "pilihan"],
                 "jp": [[1404, 1584], 144, [1548, 1728]]},
                {"label": "Total JP Mata Pelajaran Wajib + Mata Pelajaran Pilihan + Muatan Lokal",
                 "sum": ["wajib", "pilihan", "muatan_lokal"], "jp": [[1476, 1656], 144, [1620, 1800]]}],
     "footnotes": {"a": FN_REL, "b": FN_ARTS,
                   "c": "Alokasi masing-masing mata pelajaran pilihan yaitu 5 (lima) JP per minggu atau 180 JP per "
                        "tahun.",
                   "d": "Alokasi mata pelajaran Prakarya dan Kewirausahaan yaitu 2 (dua) JP per minggu atau 72 JP "
                        "per tahun.",
                   "e": "Peserta didik memilih 4 (empat) sampai 5 (lima) mata pelajaran atau setara dengan 20 sampai "
                        "25 JP per minggu sesuai dengan kebutuhan Peserta Didik dan sumber daya yang tersedia di "
                        "Satuan Pendidikan.",
                   "f": fn_mulok(72)},
     "note": "Every school opens all compulsory subjects and at least 7 electives; each student takes 4–5 electives "
             "and may change them until grade XI semester 2. Schools designated for sport or arts may open "
             "Olahraga or Seni (PDF p. 28, 32–33)."},
    {"table": 10, "levels": ["SMA", "MA"], "grades": [12], "weeks_per_year": 32, "jp_minutes": 45,
     "pages": [30, 32],
     "rows": wajib(("pendidikan_agama", 64, 32, 96), ("pendidikan_pancasila", 64, 0, 64),
                   ("bahasa_indonesia", 96, 32, 128), ("matematika", 96, 32, 128), ("bahasa_inggris", 96, 0, 96),
                   ("seni_budaya", 64, 0, 64), ("pjok", 64, 32, 96), ("sejarah", 64, 0, 64))
     + [row("pilihan_sma", "pilihan", [640, 800], 0, [640, 800], options=SMA_ELECTIVES,
            choose=[4, 5], jp_each=160, jp_each_exceptions={"prakarya_kewirausahaan": 64}),
        row("muatan_lokal", "muatan_lokal", 64, 0, 64)],
     "totals": [{"label": "Jumlah JP Mata Pelajaran Wajib", "sum": ["wajib"], "jp": [608, 128, 736]},
                {"label": "Total JP Mata Pelajaran Wajib + Mata Pelajaran Pilihan", "sum": ["wajib", "pilihan"],
                 "jp": [[1248, 1408], 128, [1376, 1536]]},
                {"label": "Total JP Mata Pelajaran Wajib + Mata Pelajaran Pilihan + Muatan Lokal",
                 "sum": ["wajib", "pilihan", "muatan_lokal"], "jp": [[1312, 1472], 128, [1440, 1600]]}],
     "footnotes": {"a": FN_REL, "b": FN_ARTS,
                   "c": "Alokasi masing-masing mata pelajaran pilihan yaitu 5 (lima) JP per minggu atau 160 JP per "
                        "tahun.",
                   "d": "Alokasi mata pelajaran Prakarya dan Kewirausahaan yaitu 2 (dua) JP per minggu atau 64 JP "
                        "per tahun.",
                   "e": "Peserta didik memilih 4 (empat) sampai 5 (lima) mata pelajaran atau setara dengan 20 sampai "
                        "25 JP per minggu.",
                   "f": fn_mulok(64)}},
    # ---------------- SMK/MAK (Lampiran II E)
    {"table": 11, "levels": ["SMK", "MAK"], "grades": [10], "weeks_per_year": 36, "jp_minutes": 45,
     "pages": [33, 35],
     "rows": [row("pendidikan_agama", "umum", 108, 0, 108), row("pendidikan_pancasila", "umum", 72, 0, 72),
              row("bahasa_indonesia", "umum", 108, 36, 144), row("pjok", "umum", 108, 0, 108),
              row("sejarah", "umum", 72, 0, 72), row("seni_budaya", "umum", 72, 0, 72),
              row("matematika", "kejuruan", 108, 36, 144), row("bahasa_inggris", "kejuruan", 108, 36, 144),
              row("informatika", "kejuruan", 108, 36, 144), row("projek_ipas", "kejuruan", 180, 36, 216),
              row("dasar_program_keahlian", "kejuruan", 432, 0, 432),
              row("koding_ka", "pilihan", 72, 0, 72), row("muatan_lokal", "muatan_lokal", 72, 0, 72)],
     "totals": [{"label": "Total JP Mata Pelajaran Umum", "sum": ["umum"], "jp": [540, 36, 576]},
                {"label": "Total JP Mata Pelajaran Kejuruan", "sum": ["kejuruan"], "jp": [936, 144, 1080]},
                {"label": "Total JP Mata Pelajaran Umum + Mata Pelajaran Kejuruan", "sum": ["umum", "kejuruan"],
                 "jp": [1476, 180, 1656]},
                {"label": "Total JP Mata Pelajaran Pilihan", "sum": ["pilihan"], "jp": [72, 0, 72]},
                {"label": "Total JP Mata Pelajaran Umum + Mata Pelajaran Kejuruan + Mata Pelajaran Pilihan/ "
                          "Muatan Lokal", "sum": ["umum", "kejuruan", "muatan_lokal"], "jp": [1548, 180, 1728]},
                {"label": "Total JP Mata Pelajaran Umum + Mata Pelajaran Kejuruan + Mata Pelajaran Pilihan + "
                          "Muatan Lokal", "sum": ["umum", "kejuruan", "pilihan", "muatan_lokal"],
                 "jp": [1620, 180, 1800]}],
     "footnotes": {"a": FN_REL, "b": FN_ARTS,
                   "c": "Proporsi JP antara aspek Ilmu Pengetahuan Alam dan aspek Ilmu Pengetahuan Sosial "
                        "disesuaikan dengan kebutuhan Program Keahlian.",
                   "d": "Nama mata pelajaran menyesuaikan nama Program Keahlian.", "e": fn_kka(72),
                   "f": fn_mulok(72)}},
    {"table": 12, "levels": ["SMK", "MAK"], "grades": [11], "weeks_per_year": 36, "jp_minutes": 45,
     "pages": [35, 36],
     "rows": [row("pendidikan_agama", "umum", 90, 18, 108), row("pendidikan_pancasila", "umum", 54, 18, 72),
              row("bahasa_indonesia", "umum", 90, 18, 108), row("pjok", "umum", 54, 18, 72),
              row("sejarah", "umum", 54, 18, 72),
              row("matematika", "kejuruan", 90, 18, 108), row("bahasa_inggris", "kejuruan", 108, 36, 144),
              row("konsentrasi_keahlian", "kejuruan", 648, 0, 648), row("kik", "kejuruan", 180, 0, 180),
              row("mapel_pilihan_smk", "kejuruan", 144, 0, 144),
              row("muatan_lokal", "muatan_lokal", 72, 0, 72)],
     "totals": [{"label": "Total JP Mata Pelajaran Umum", "sum": ["umum"], "jp": [342, 90, 432]},
                {"label": "Total JP Mata Pelajaran Kejuruan", "sum": ["kejuruan"], "jp": [1170, 54, 1224]},
                {"label": "Total JP Mata Pelajaran Umum + Mata Pelajaran Kejuruan", "sum": ["umum", "kejuruan"],
                 "jp": [1512, 144, 1656]},
                {"label": "Total JP Mata Pelajaran Umum + Mata Pelajaran Kejuruan + Muatan Lokal",
                 "sum": ["umum", "kejuruan", "muatan_lokal"], "jp": [1584, 144, 1728]}],
     "footnotes": {"a": FN_REL, "b": "Nama mata pelajaran sesuai dengan nama Konsentrasi Keahlian.",
                   "c": "Nama mata pelajaran merupakan mata pelajaran yang dipilih oleh Peserta Didik.",
                   "d": fn_mulok(72)},
     "note": "The 'Mata Pelajaran Pilihan' row sits inside the Kejuruan group and its total."},
    {"table": 13, "levels": ["SMK", "MAK"], "grades": [12], "programme_years": 3, "weeks_per_year": 32,
     "jp_minutes": 45, "pages": [36, 37],
     "rows": [row("pendidikan_agama", "umum", 32, 16, 48), row("pendidikan_pancasila", "umum", 32, 0, 32),
              row("bahasa_indonesia", "umum", 32, 16, 48),
              row("matematika", "kejuruan", 48, 0, 48), row("bahasa_inggris", "kejuruan", 64, 0, 64),
              row("konsentrasi_keahlian", "kejuruan", 352, 0, 352), row("kik", "kejuruan", 80, 0, 80),
              row("pkl", "kejuruan", 736, 0, 736), row("mapel_pilihan_smk", "kejuruan", 64, 0, 64),
              row("muatan_lokal", "muatan_lokal", 32, 0, 32)],
     "totals": [{"label": "Jumlah JP Mata Pelajaran Umum", "sum": ["umum"], "jp": [96, 32, 128]},
                {"label": "Total JP Mata Pelajaran Kejuruan", "sum": ["kejuruan"], "jp": [1344, 0, 1344]},
                {"label": "Total JP Mata Pelajaran Umum + Mata Pelajaran Kejuruan", "sum": ["umum", "kejuruan"],
                 "jp": [1440, 32, 1472]},
                {"label": "Total JP Mata Pelajaran Umum + Mata Pelajaran Kejuruan + Muatan Lokal",
                 "sum": ["umum", "kejuruan", "muatan_lokal"], "jp": [1472, 32, 1504]}],
     "footnotes": {"a": FN_REL, "b": "Nama mata pelajaran sesuai dengan konsentrasi keahlian.",
                   "c": "Mata pelajaran Praktik Kerja Lapangan (PKL) dilaksanakan paling sedikit selama 1 semester "
                        "atau 16 (enam belas) minggu efektif.",
                   "d": "Nama mata pelajaran merupakan mata pelajaran yang dipilih oleh Peserta Didik.",
                   "e": "Paling banyak 2 (dua) JP per minggu atau 32 (tiga puluh dua) JP per tahun."},
     "note": "Grade XII of the 3-year programme has no PJOK, Sejarah or Seni dan Budaya rows (as printed). The "
             "Mata Pelajaran Pilihan row prints only two cells (64, 64); the Kejuruan total confirms 64 "
             "intrakurikuler."},
    {"table": 14, "levels": ["SMK", "MAK"], "grades": [12], "programme_years": 4, "weeks_per_year": 36,
     "jp_minutes": 45, "pages": [37, 39],
     "rows": [row("pendidikan_agama", "umum", 90, 18, 108), row("pendidikan_pancasila", "umum", 54, 18, 72),
              row("bahasa_indonesia", "umum", 90, 18, 108), row("pjok", "umum", 54, 18, 72),
              row("sejarah", "umum", 54, 18, 72),
              row("matematika", "kejuruan", 90, 18, 108), row("bahasa_inggris", "kejuruan", 108, 36, 144),
              row("konsentrasi_keahlian", "kejuruan", 648, 0, 648), row("kik", "kejuruan", 180, 0, 180),
              row("mapel_pilihan_smk", "kejuruan", 144, 0, 144),
              row("muatan_lokal", "muatan_lokal", 72, 0, 72)],
     "totals": [{"label": "Total JP Mata Pelajaran Umum", "sum": ["umum"], "jp": [342, 90, 432]},
                {"label": "Total JP Mata Pelajaran Kejuruan", "sum": ["kejuruan"], "jp": [1170, 54, 1224]},
                {"label": "Total JP Mata Pelajaran Umum + Mata Pelajaran Kejuruan", "sum": ["umum", "kejuruan"],
                 "jp": [1512, 144, 1656]},
                {"label": "Total JP Mata Pelajaran Umum + Mata Pelajaran Kejuruan + Muatan Lokal",
                 "sum": ["umum", "kejuruan", "muatan_lokal"], "jp": [1584, 144, 1728]}],
     "footnotes": {"a": FN_REL, "b": "Nama mata pelajaran sesuai dengan nama konsentrasi keahlian.",
                   "c": "Nama mata pelajaran merupakan mata pelajaran yang dipilih oleh Peserta Didik.",
                   "d": fn_mulok(72)}},
    {"table": 15, "levels": ["SMK", "MAK"], "grades": [13], "programme_years": 4, "weeks_per_year": 32,
     "jp_minutes": 45, "pages": [39],
     "rows": [row("matematika", "kejuruan", 64, 0, 64), row("bahasa_inggris", "kejuruan", 192, 0, 192),
              row("pkl", "kejuruan", 1216, 0, 1216)],
     "totals": [{"label": "Total JP Mata Pelajaran Umum", "sum": ["umum"], "jp": [0, 0, 0]},
                {"label": "Total JP Mata Pelajaran Kejuruan", "sum": ["kejuruan"], "jp": [1472, 0, 1472]},
                {"label": "Total JP Mata Pelajaran Umum + Mata Pelajaran Kejuruan", "sum": ["umum", "kejuruan"],
                 "jp": [1472, 0, 1472]}],
     "footnotes": {"a": "Mata pelajaran Praktik Kerja Lapangan dilaksanakan paling sedikit selama 10 (sepuluh) bulan "
                        "atau 26 (dua puluh enam) minggu efektif."},
     "note": "No general subjects in grade XIII (printed '-')."},
]

# ---------------- SDLB/MILB (Lampiran II F), 1 JP = 30 minutes
FN_PKK = "Dipilih sesuai jenis hambatan Peserta Didik."
SDLB = [
    (16, [1], 36, [40, 42], [("pendidikan_agama", 108, 36, 144), ("pendidikan_pancasila", 72, 0, 72),
                             ("bahasa_indonesia", 108, 36, 144), ("matematika", 72, 0, 72), ("pjok", 72, 0, 72),
                             ("seni_budaya", 252, 108, 360), ("program_kebutuhan_khusus", 216, 0, 216)],
     72, [900, 180, 1080], [972, 180, 1152]),
    (17, [2], 36, [42, 43], [("pendidikan_agama", 108, 36, 144), ("pendidikan_pancasila", 72, 0, 72),
                             ("bahasa_indonesia", 108, 36, 144), ("matematika", 108, 36, 144), ("pjok", 72, 0, 72),
                             ("seni_budaya", 252, 108, 360), ("program_kebutuhan_khusus", 216, 0, 216)],
     72, [936, 216, 1152], [1008, 216, 1224]),
    (18, [3, 4], 36, [44, 45], [("pendidikan_agama", 108, 36, 144), ("pendidikan_pancasila", 72, 0, 72),
                                ("bahasa_indonesia", 72, 36, 108), ("matematika", 72, 36, 108),
                                ("ipas", 72, 0, 72), ("pjok", 72, 0, 72), ("seni_budaya", 360, 144, 504),
                                ("program_kebutuhan_khusus", 216, 0, 216), ("bahasa_inggris", 72, 0, 72)],
     72, [1116, 252, 1368], [1188, 252, 1440]),
    (19, [5], 36, [45, 47], [("pendidikan_agama", 108, 36, 144), ("pendidikan_pancasila", 72, 0, 72),
                             ("bahasa_indonesia", 108, 36, 144), ("matematika", 108, 36, 144),
                             ("ipas", 72, 0, 72), ("pjok", 72, 0, 72), ("seni_budaya", 360, 144, 504),
                             ("program_kebutuhan_khusus", 144, 0, 144), ("bahasa_inggris", 72, 0, 72)],
     72, [1116, 252, 1368], [1188, 252, 1440]),
    (20, [6], 32, [47, 49], [("pendidikan_agama", 96, 32, 128), ("pendidikan_pancasila", 64, 0, 64, {"printed_intrakurikuler": 54}),
                             ("bahasa_indonesia", 96, 32, 128), ("matematika", 96, 32, 128),
                             ("ipas", 64, 0, 64, {"printed_intrakurikuler": 54}), ("pjok", 64, 0, 64, {"printed_intrakurikuler": 54}), ("seni_budaya", 320, 128, 448),
                             ("program_kebutuhan_khusus", 128, 0, 128), ("bahasa_inggris", 64, 0, 64)],
     64, [992, 224, 1216], [1056, 224, 1280]),
]
for n, grades, weeks, pages, rows, mulok, t_w, t_wm in SDLB:
    TABLES.append({
        "table": n, "levels": ["SDLB", "MILB"], "grades": grades, "weeks_per_year": weeks, "jp_minutes": 30,
        "pages": pages, "rows": wajib(*rows) + [row("muatan_lokal", "muatan_lokal", mulok, 0, mulok)],
        "totals": [{"label": "Total JP Mata Pelajaran Wajib", "sum": ["wajib"], "jp": t_w},
                   {"label": "Total JP Mata Pelajaran Wajib + Muatan Lokal", "sum": ["wajib", "muatan_lokal"],
                    "jp": t_wm}],
        "footnotes": {"a": FN_REL, "b": FN_ARTS, "c": FN_PKK, "d": fn_mulok(mulok)}})

# ---------------- SMPLB/MTsLB (II G, 1 JP = 35 min) and SMALB/MALB (II H, 1 JP = 40 min)
GENERAL_LB = ["pendidikan_agama", "pendidikan_pancasila", "bahasa_indonesia", "matematika", "ipa", "ips",
              "bahasa_inggris", "pjok", "seni_budaya"]
LB_SEC = [
    # table, levels, grades, weeks, jp_min, pages, per-subject (intra, ko), skills, pkk, mulok, wajib, wajib+mulok,
    # weeks for the subjects marked b), skills note
    (21, ["SMPLB", "MTsLB"], [7], 36, 35, [49, 51], (54, 18), (468, 144), 108, 72, [1062, 306, 1368],
     [1134, 306, 1440], 27, "Peserta Didik memilih minimal 2 (dua) keterampilan."),
    (22, ["SMPLB", "MTsLB"], [8], 36, 35, [51, 54], (54, 18), (468, 144), 108, 72, [1062, 306, 1368],
     [1134, 306, 1440], 27, "Peserta Didik memilih 1 (satu) keterampilan."),
    (23, ["SMPLB", "MTsLB"], [9], 32, 35, [54, 56], (48, 16), (416, 128), 96, 64, [944, 272, 1216],
     [1008, 272, 1280], 24, "Peserta Didik memilih 1 (satu) keterampilan."),
    (24, ["SMALB", "MALB"], [10], 36, 40, [57, 59], (54, 18), (648, 216), 72, 72, [1206, 378, 1584],
     [1278, 378, 1656], 27, "Peserta Didik memilih 1 (satu) keterampilan."),
    (25, ["SMALB", "MALB"], [11], 36, 40, [59, 61], (54, 18), (720, 216), 72, 72, [1278, 378, 1656],
     [1350, 378, 1728], 27, "Peserta Didik memilih 1 (satu) keterampilan."),
    (26, ["SMALB", "MALB"], [12], 32, 40, [62, 64], (48, 16), (640, 192), 64, 64, [1136, 336, 1472],
     [1200, 336, 1536], 24, "Peserta Didik memilih 1 (satu) keterampilan."),
]
for n, levels, grades, weeks, jpm, pages, (gi, gk), (si, sk), pkk, mulok, t_w, t_wm, wk_b, fn_skill in LB_SEC:
    rows = [row(k, "wajib", gi, gk, gi + gk) for k in GENERAL_LB]
    rows += [row("kelompok_keterampilan", "wajib", si, sk, si + sk),
             row("program_kebutuhan_khusus", "wajib", pkk, 0, pkk),
             row("muatan_lokal", "muatan_lokal", mulok, 0, mulok)]
    TABLES.append({
        "table": n, "levels": levels, "grades": grades, "weeks_per_year": weeks, "jp_minutes": jpm, "pages": pages,
        "rows": rows,
        "totals": [{"label": "Total JP Mata Pelajaran Wajib", "sum": ["wajib"], "jp": t_w},
                   {"label": "Total JP Mata Pelajaran Wajib + Muatan Lokal", "sum": ["wajib", "muatan_lokal"],
                    "jp": t_wm}],
        "footnotes": {"a": FN_REL,
                      "b": f"Pembelajaran tidak penuh {weeks} minggu untuk memenuhi alokasi Kokurikuler, "
                           f"Intrakurikuler dialokasikan {wk_b} minggu untuk the general subjects (each listed in the "
                           "footnote as printed).",
                      "c": FN_ARTS, "d": fn_skill, "e": FN_PKK, "f": fn_mulok(mulok)}})

# ---------------- kesetaraan (Lampiran II I): SKK per phase, compulsory subjects in one merged cell
PAKET = [
    {"programme": "Paket A", "levels": ["Paket A"], "table": 27, "pages": [66, 67], "jp_minutes": 35,
     "phases": {"A": [1, 2], "B": [3, 4], "C": [5, 6]},
     "wajib": ["pendidikan_agama", "pendidikan_pancasila", "bahasa_indonesia", "matematika", "pjok", "seni_budaya",
               "ipas", "bahasa_inggris"],
     "not_in_phase": {"A": ["ipas", "bahasa_inggris"]},
     "skk": {"wajib": {"A": 48, "B": 62, "C": 62, "total": 172},
             "pemberdayaan_keterampilan": {"A": 14, "B": 14, "C": 14, "total": 42},
             "muatan_lokal": {"A": 2, "B": 2, "C": 2, "total": 6}},
     "totals": [{"label": "Total SKK Mata Pelajaran Wajib + Muatan Pemberdayaan dan Keterampilan",
                 "sum": ["wajib", "pemberdayaan_keterampilan"], "skk": {"A": 62, "B": 76, "C": 76, "total": 214}},
                {"label": "Total SKK Kelompok Mata Pelajaran Wajib + Muatan Pemberdayaan dan Keterampilan + "
                          "Muatan Lokal", "sum": ["wajib", "pemberdayaan_keterampilan", "muatan_lokal"],
                 "skk": {"A": 64, "B": 78, "C": 78, "total": 220}}]},
    {"programme": "Paket B", "levels": ["Paket B"], "table": 28, "pages": [68], "jp_minutes": 40,
     "phases": {"D": [7, 8, 9]},
     "wajib": ["pendidikan_agama", "pendidikan_pancasila", "bahasa_indonesia", "matematika", "ipa", "ips",
               "bahasa_inggris", "pjok", "seni_budaya"],
     "skk": {"wajib": {"D": 84, "total": 84}, "pemberdayaan_keterampilan": {"D": 29, "total": 29},
             "muatan_lokal": {"D": 2, "total": 2}},
     "totals": [{"label": "Total SKK Mata Pelajaran dan/atau Muatan Wajib + Muatan Pemberdayaan dan Keterampilan",
                 "sum": ["wajib", "pemberdayaan_keterampilan"], "skk": {"D": 113, "total": 113}},
                {"label": "Total SKK Mata Pelajaran dan/atau Muatan Wajib + Muatan Pemberdayaan dan Keterampilan "
                          "+ Muatan Lokal", "sum": ["wajib", "pemberdayaan_keterampilan", "muatan_lokal"],
                 "skk": {"D": 115, "total": 115}}]},
    {"programme": "Paket C", "levels": ["Paket C"], "table": 29, "pages": [69, 70], "jp_minutes": 45,
     "phases": {"E": [10], "F": [11, 12]},
     "wajib": ["pendidikan_agama", "pendidikan_pancasila", "bahasa_indonesia", "matematika", "bahasa_inggris",
               "ipa", "ips", "sejarah", "pjok", "seni_budaya"],
     "only_in_phase": {"ipa": "E", "ips": "E", "sejarah": "F"},
     "components": {"ipa": ["Fisika", "Biologi", "Kimia"], "ips": ["Sejarah", "Ekonomi", "Geografi", "Sosiologi"]},
     "pilihan": ["antropologi", "bahasa_arab", "bahasa_indonesia_lanjut", "bahasa_inggris_lanjut", "bahasa_jepang",
                 "bahasa_jerman", "bahasa_korea", "bahasa_mandarin", "bahasa_prancis", "biologi", "ekonomi",
                 "fisika", "geografi", "informatika", "kimia", "matematika_lanjut", "sejarah_lanjut", "sosiologi"],
     "skk": {"wajib": {"E": 32, "F": 32, "total": 64}, "pilihan": {"E": 0, "F": 40, "total": 40},
             "pemberdayaan_keterampilan": {"E": 12, "F": 12, "total": 24},
             "muatan_lokal": {"E": 2, "F": 2, "total": 4}},
     "totals": [{"label": "Total SKK Mata Pelajaran Wajib + Mata Pelajaran Pilihan", "sum": ["wajib", "pilihan"],
                 "skk": {"E": 32, "F": 72, "total": 104}},
                {"label": "Total SKK Kelompok Mata Pelajaran Wajib + Mata Pelajaran Pilihan + Muatan "
                          "Pemberdayaan dan Keterampilan", "sum": ["wajib", "pilihan", "pemberdayaan_keterampilan"],
                 "skk": {"E": 44, "F": 84, "total": 128}},
                {"label": "Total SKK Kelompok Mata Pelajaran Wajib + Mata Pelajaran Pilihan + Muatan "
                          "Pemberdayaan dan Keterampilan + Muatan Lokal",
                 "sum": ["wajib", "pilihan", "pemberdayaan_keterampilan", "muatan_lokal"],
                 "skk": {"E": 46, "F": 86, "total": 132}}],
     "note": "Elective rules follow SMA/MA (explanation 4, PDF p. 71)."},
]
SKK_RULE = ("1 SKK = 1 jam tatap muka, or 2 jam tutorial, or 3 jam mandiri, or a proportional mix; 1 jam = 35 minutes "
            "(Paket A), 40 (Paket B), 45 (Paket C); muatan lokal at most 2 SKK per phase (PDF p. 66–67).")

PAUD = {
    "levels": ["TK", "RA", "TKLB", "BA", "KB", "TPA", "SPS"],
    "levels_note": "taman kanak-kanak, raudhatul athfal, taman kanak-kanak luar biasa, bustanul athfal, kelompok "
                   "bermain, taman penitipan anak, atau bentuk lain yang sederajat (as printed)",
    "phase": "Fondasi",
    "elements": ["nilai agama dan budi pekerti", "jati diri",
                 "dasar-dasar literasi, matematika, sains, teknologi, rekayasa, dan seni"],
    "minutes_per_week_min": {"4-6": 900, "3-4": 360},
    "tklb": "Time allocation is flexible; Program Kebutuhan Khusus from Fase Fondasi based on assessment.",
    "ref": f"{P13} A (PDF p. 14–15)",
}

PHASES = {"Fondasi": "PAUD", "A": [1, 2], "B": [3, 4], "C": [5, 6], "D": [7, 8, 9], "E": [10], "F": [11, 12]}
PHASES_REF = f"{P13}, Tabel 27–29 column headings (PDF p. 66–69); SMK grade XIII belongs to Fase F"


def phase_of(grade):
    for p, gs in PHASES.items():
        if isinstance(gs, list) and grade in gs:
            return p
    return "F" if grade == 13 else None


RULES = [
    {"levels": ["SD", "MI", "SMP", "MTs", "SMA", "MA", "SMK", "MAK"],
     "text": "Muatan Lokal covers local potential (seni budaya, prakarya, PJOK, bahasa, teknologi) and may be "
             "integrated into other subjects, into kokurikuler, or taught as a separate subject.",
     "ref": f"{P13} B–E explanations (PDF p. 21, 25, 33, 40)"},
    {"levels": ["SD", "MI", "SMP", "MTs", "SMA", "MA", "SMK", "MAK"],
     "text": "Inclusive schools add the subject Program Kebutuhan Khusus according to the students' needs.",
     "ref": f"{P13} B–E explanations"},
    {"levels": ["SD", "MI", "SMP", "MTs", "SMA", "MA", "SMK", "MAK"],
     "text": "Koding dan Kecerdasan Artifisial is an elective the school may offer according to its resources; "
             f"schools start offering it gradually from 2025/2026 ({P13.split(',')[0]} Pasal 32A).",
     "ref": f"{P13} explanations; Permendikdasmen 13/2025 Pasal 32A (PDF p. 5)"},
    {"levels": ["SD", "MI"], "text": ENGLISH_SD, "ref": f"{P12} Pasal 33 (PDF p. 11)"},
    {"levels": ["SMP", "MTs", "SMA", "MA"],
     "text": "Special sport or arts classes or schools may use the kokurikuler time to strengthen sport or arts.",
     "ref": f"{P13} C–D explanations (PDF p. 25, 33)"},
    {"levels": ["SMK", "MAK"],
     "text": "PKL is taught in blocks of 46 JP per week; Matematika, Bahasa Inggris, Informatika and Koding dan "
             "Kecerdasan Artifisial follow the context of the programme.",
     "ref": f"{P13} E explanations (PDF p. 39)"},
    {"levels": ["SDLB", "MILB", "SMPLB", "MTsLB", "SMALB", "MALB"],
     "text": "Bahasa Inggris in SMPLB and SMALB is compulsory for students without intellectual disability and "
             "optional for students with intellectual disability; time allocation is flexible; the phase follows "
             "a diagnostic assessment; SMALB grade XI does PKL for the skill subject for at least one month.",
     "ref": f"{P13} H explanations (PDF p. 64–65)"},
]


# ------------------------------------------------------------------ madrasah: KMA 1503/2025 Lampiran II BAB III
# Scanned decree: every cell read from the page images (printed page = PDF page) and checked against the printed
# totals below. Madrasah tables replace Pendidikan Agama with Al-Qur'an Hadis, Akidah Akhlak, Fikih, SKI and add
# Bahasa Arab; muatan lokal is a range.

KMA = "KMA 1503/2025, Lampiran II BAB III"
KMA_ARTS = ("Madrasah menyediakan minimal 1 (satu) jenis seni (seni musik, seni rupa, seni teater, dan/atau seni "
            "tari). Peserta Didik memilih 1 (satu) jenis seni.")
KMA_ARTS_CRAFTS = ("Madrasah menyediakan minimal 1 (satu) jenis seni atau prakarya (seni musik, seni rupa, seni "
                   "teater, seni tari, dan/atau prakarya). Peserta Didik memilih 1 (satu) jenis seni atau prakarya.")


def kma_mulok(lo, hi):
    return f"Paling sedikit {lo} JP per tahun dan paling banyak {hi}."


def W(*rows):
    return wajib(*rows)


MI_REL = [("quran_hadis",), ("akidah_akhlak",), ("fikih",)]
KMA_TABLES = [
    {"table": 1, "levels": ["MI"], "grades": [1], "weeks_per_year": 36, "jp_minutes": 35, "pages": [28],
     "rows": W(("quran_hadis", 72, 36, 108), ("akidah_akhlak", 72, 0, 72), ("fikih", 72, 0, 72),
               ("bahasa_arab", 72, 0, 72), ("pendidikan_pancasila", 144, 36, 180),
               ("bahasa_indonesia", 252, 36, 288), ("matematika", 144, 0, 144), ("pjok", 108, 0, 108),
               ("seni_budaya", 108, 0, 108))
     + [row("muatan_lokal", "muatan_lokal", [72, 216], 0, [72, 216])],
     "totals": [{"label": "Total JP Mata Pelajaran Wajib", "sum": ["wajib"], "jp": [1044, 108, 1152]},
                {"label": "Total JP Mata Pelajaran Wajib + Muatan Lokal", "sum": ["wajib", "muatan_lokal"],
                 "jp": [[1116, 1260], 108, [1224, 1368]]}],
     "footnotes": {"a": KMA_ARTS, "b": "Paling sedikit 72 JP per tahun dan paling banyak 216 sebagai mata "
                                       "pelajaran pilihan."}},
    {"table": 2, "levels": ["MI"], "grades": [2], "weeks_per_year": 36, "jp_minutes": 35, "pages": [28, 29],
     "rows": W(("quran_hadis", 72, 36, 108), ("akidah_akhlak", 72, 0, 72), ("fikih", 72, 0, 72),
               ("bahasa_arab", 72, 0, 72), ("pendidikan_pancasila", 144, 36, 180),
               ("bahasa_indonesia", 288, 36, 324), ("matematika", 180, 0, 180), ("pjok", 108, 0, 108),
               ("seni_budaya", 108, 0, 108))
     + [row("muatan_lokal", "muatan_lokal", [72, 216], 0, [72, 216])],
     "totals": [{"label": "Total JP Mata Pelajaran Wajib", "sum": ["wajib"], "jp": [1116, 108, 1224]},
                {"label": "Total JP Mata Pelajaran Wajib + Muatan Lokal", "sum": ["wajib", "muatan_lokal"],
                 "jp": [[1188, 1332], 108, [1296, 1440]]}],
     "footnotes": {"a": KMA_ARTS, "b": kma_mulok(72, 216)}},
    {"table": 3, "levels": ["MI"], "grades": [3, 4], "weeks_per_year": 36, "jp_minutes": 35, "pages": [29],
     "rows": W(("quran_hadis", 72, 0, 72), ("akidah_akhlak", 72, 0, 72), ("fikih", 72, 36, 108),
               ("ski", 72, 0, 72), ("bahasa_arab", 72, 0, 72), ("pendidikan_pancasila", 144, 0, 144),
               ("bahasa_indonesia", 216, 36, 252), ("matematika", 180, 0, 180), ("ipas", 180, 36, 216),
               ("pjok", 108, 0, 108), ("seni_budaya", 108, 0, 108), ("bahasa_inggris", 72, 0, 72, EN))
     + [row("muatan_lokal", "muatan_lokal", [72, 216], 0, [72, 216])],
     "totals": [{"label": "Total JP Mata Pelajaran Wajib", "sum": ["wajib"], "jp": [1368, 108, 1476]},
                {"label": "Total JP Mata Pelajaran Wajib + Muatan Lokal", "sum": ["wajib", "muatan_lokal"],
                 "jp": [[1440, 1584], 108, [1548, 1692]]}],
     "footnotes": {"a": KMA_ARTS, "b": kma_mulok(72, 216)}},
    {"table": 4, "levels": ["MI"], "grades": [5], "weeks_per_year": 36, "jp_minutes": 35, "pages": [30],
     "rows": W(("quran_hadis", 72, 0, 72), ("akidah_akhlak", 72, 36, 108), ("fikih", 72, 0, 72),
               ("ski", 72, 0, 72), ("bahasa_arab", 72, 0, 72), ("pendidikan_pancasila", 144, 0, 144),
               ("bahasa_indonesia", 216, 36, 252), ("matematika", 180, 0, 180), ("ipas", 180, 0, 180),
               ("pjok", 108, 0, 108), ("seni_budaya", 108, 36, 144), ("bahasa_inggris", 72, 0, 72, EN))
     + [row("koding_ka", "pilihan", 72, 0, 72), row("muatan_lokal", "muatan_lokal", [72, 216], 0, [72, 216])],
     "totals": [{"label": "Total JP Mata Pelajaran Wajib", "sum": ["wajib"], "jp": [1368, 108, 1476]},
                {"label": "Total JP Mata Pelajaran Wajib + Muatan Lokal", "sum": ["wajib", "muatan_lokal"],
                 "jp": [[1440, 1584], 108, [1548, 1692]]},
                {"label": "Total JP Mata Pelajaran Wajib + Mata Pelajaran Pilihan + Muatan Lokal",
                 "sum": ["wajib", "pilihan", "muatan_lokal"], "jp": [[1512, 1656], 108, [1620, 1764]]}],
     "footnotes": {"a": KMA_ARTS, "b": "Paling banyak 2 (dua) JP per minggu atau 72 JP per tahun sebagai mata "
                                       "pelajaran pilihan.", "c": kma_mulok(72, 216)}},
    {"table": 5, "levels": ["MI"], "grades": [6], "weeks_per_year": 32, "jp_minutes": 35, "pages": [30, 31],
     "rows": W(("quran_hadis", 64, 0, 64), ("akidah_akhlak", 64, 32, 96), ("fikih", 64, 0, 64),
               ("ski", 64, 0, 64), ("bahasa_arab", 64, 0, 64), ("pendidikan_pancasila", 128, 0, 128),
               ("bahasa_indonesia", 192, 32, 224), ("matematika", 160, 0, 160), ("ipas", 160, 0, 160),
               ("pjok", 96, 32, 128), ("seni_budaya", 96, 0, 96), ("bahasa_inggris", 64, 0, 64, EN))
     + [row("koding_ka", "pilihan", 64, 0, 64), row("muatan_lokal", "muatan_lokal", [64, 192], 0, [64, 192])],
     "totals": [{"label": "Total JP Mata Pelajaran Wajib", "sum": ["wajib"], "jp": [1216, 96, 1312]},
                {"label": "Total JP Mata Pelajaran Wajib + Pilihan + Muatan Lokal", "sum": ["wajib", "muatan_lokal"],
                 "jp": [[1280, 1408], 96, [1376, 1504]],
                 "note": "Labelled with 'Pilihan', but the figures are Wajib + Muatan Lokal; the next row includes "
                         "the elective."},
                {"label": "Total JP Mata Pelajaran Wajib + Mata Pelajaran Pilihan + Muatan Lokal",
                 "sum": ["wajib", "pilihan", "muatan_lokal"], "jp": [[1344, 1472], 96, [1440, 1568]]}],
     "footnotes": {"a": KMA_ARTS, "b": "Paling banyak 2 (dua) JP per minggu atau 64 JP per tahun sebagai mata "
                                       "pelajaran pilihan.", "c": kma_mulok(64, 192)}},
]

MTS_ROWS = ["quran_hadis", "akidah_akhlak", "fikih", "ski", "bahasa_arab", "pendidikan_pancasila",
            "bahasa_indonesia", "matematika", "ipa", "ips", "bahasa_inggris", "pjok", "informatika",
            "seni_budaya_prakarya"]


def mts(n, grade, weeks, pages, cells, kka, mulok, totals, fn_kka_text, **extra):
    rows = [row(k, "wajib", *c[:3], **(c[3] if len(c) > 3 else {})) for k, c in zip(MTS_ROWS, cells)]
    rows += [row("koding_ka", "pilihan", kka, 0, kka), row("muatan_lokal", "muatan_lokal", mulok, 0, mulok)]
    t = {"table": n, "levels": ["MTs"], "grades": [grade], "weeks_per_year": weeks, "jp_minutes": 40,
         "pages": pages, "rows": rows, "totals": totals,
         "footnotes": {"a": KMA_ARTS_CRAFTS, "b": fn_kka_text, "c": kma_mulok(*mulok)}}
    t.update(extra)
    return t


KMA_TABLES += [
    mts(6, 7, 36, [32, 33],
        [(72, 36, 108), (72, 0, 72), (72, 0, 72), (72, 0, 72), (108, 0, 108), (72, 36, 108), (180, 36, 216),
         (144, 0, 144), (144, 0, 144), (108, 0, 108), (108, 0, 108), (72, 36, 108), (72, 0, 72), (72, 0, 72)],
        72, [72, 216],
        [{"label": "Total JP Mata Pelajaran Wajib", "sum": ["wajib"], "jp": [1368, 144, 1512]},
         {"label": "Total JP Mata Pelajaran Wajib + Muatan Lokal", "sum": ["wajib", "muatan_lokal"],
          "jp": [[1440, 1584], 144, [1584, 1728]]},
         {"label": "Total JP Mata Pelajaran Wajib + Mata Pelajaran Pilihan + Muatan Lokal",
          "sum": ["wajib", "pilihan", "muatan_lokal"], "jp": [[1512, 1656], 144, [1656, 1800]]}],
        "Paling banyak 2 (dua) JP per minggu atau 72 JP per tahun mata pelajaran pilihan."),
    mts(7, 8, 36, [33, 34],
        [(72, 0, 72), (72, 0, 72), (72, 36, 108), (72, 0, 72), (108, 0, 108), (72, 0, 72), (180, 0, 180),
         (144, 36, 180), (144, 36, 180), (108, 0, 108), (108, 0, 108), (72, 0, 72), (72, 0, 72), (72, 36, 108)],
        72, [72, 216],
        [{"label": "Total JP Mata Pelajaran Wajib", "sum": ["wajib"], "jp": [1368, 144, 1512]},
         {"label": "Total JP Mata Pelajaran Wajib + Muatan Lokal", "sum": ["wajib", "muatan_lokal"],
          "jp": [[1440, 1584], 144, [1584, 1728]]},
         {"label": "Total JP Mata Pelajaran Wajib + Mata Pelajaran Pilihan/Muatan Lokal",
          "sum": ["wajib", "pilihan", "muatan_lokal"], "jp": [[1512, 1656], 144, [1656, 1800]],
          "note": "Labelled 'Pilihan/Muatan Lokal', but the figures include both."}],
        "Paling banyak 2 (dua) JP per minggu atau 72 JP per tahun mata pelajaran pilihan."),
    mts(8, 9, 32, [34, 35],
        [(64, 0, 64), (64, 32, 96, {"printed_total": 64}), (64, 0, 64), (64, 0, 64), (96, 0, 96), (64, 0, 64),
         (160, 0, 160), (128, 0, 128), (128, 0, 128), (96, 32, 128), (96, 32, 128), (64, 0, 64), (64, 32, 96),
         (64, 0, 64)],
        64, [64, 192],
        [{"label": "Total JP Mata Pelajaran Wajib", "sum": ["wajib"], "jp": [1216, 128, 1344]},
         {"label": "Total JP Mata Pelajaran Wajib + Muatan Lokal", "sum": ["wajib", "muatan_lokal"],
          "jp": [[1280, 1408], 128, [1408, 1536]], "printed_jp": [[1280, 1408], 128, [1408, 1538]]},
         {"label": "Total JP Mata Pelajaran Wajib + Mata Pelajaran Pilihan + Muatan Lokal",
          "sum": ["wajib", "pilihan", "muatan_lokal"], "jp": [[1344, 1472], 128, [1472, 1600]]}],
        "Dialokasikan 2 (dua) JP per minggu atau 64 JP per tahun mata pelajaran pilihan."),
]

MA_ELECTIVES = ["ilmu_tafsir", "ilmu_hadis", "ushul_fikih", "matematika_lanjut", "fisika", "kimia", "biologi",
                "geografi", "sejarah_lanjut", "sosiologi", "ekonomi", "bahasa_indonesia_lanjut",
                "bahasa_inggris_lanjut", "bahasa_arab_lanjut", "bahasa_jepang", "bahasa_jerman", "bahasa_korea",
                "bahasa_mandarin", "bahasa_prancis", "antropologi", "informatika", "koding_ka",
                "prakarya_kewirausahaan", "mapel_lainnya_ma"]
KMA_TABLES += [
    {"table": 9, "levels": ["MA"], "grades": [10], "weeks_per_year": 36, "jp_minutes": 45, "pages": [36, 37],
     "rows": W(("quran_hadis", 72, 36, 108), ("akidah_akhlak", 72, 0, 72), ("fikih", 72, 0, 72),
               ("ski", 72, 0, 72), ("bahasa_arab", 144, 0, 144), ("pendidikan_pancasila", 72, 36, 108),
               ("bahasa_indonesia", 108, 36, 144), ("matematika", 108, 0, 108),
               ("ipa", 216, 0, 216, {"components": ["Fisika", "Kimia", "Biologi"]}),
               ("ips", 288, 0, 288, {"components": ["Sosiologi", "Ekonomi", "Sejarah", "Geografi"]}),
               ("bahasa_inggris", 108, 0, 108), ("pjok", 72, 0, 72), ("informatika", 72, 0, 72),
               ("seni_budaya_prakarya", 72, 0, 72))
     + [row("koding_ka", "pilihan", 72, 0, 72), row("penguatan_program", "pilihan", 216, 0, 216),
        row("muatan_lokal", "muatan_lokal", [72, 216], 0, [72, 216])],
     "totals": [{"label": "Total JP Mata Pelajaran Wajib", "sum": ["wajib"], "jp": [1548, 108, 1656]},
                {"label": "Total JP Mata Pelajaran Wajib + Muatan Lokal", "sum": ["wajib", "muatan_lokal"],
                 "jp": [[1620, 1764], 108, [1728, 1872]]},
                {"label": "Total JP Mata Pelajaran Wajib + Koding dan Kecerdasan Artifisial + Muatan Lokal",
                 "sum": ["wajib", "koding_ka", "muatan_lokal"], "jp": [[1692, 1836], 108, [1800, 1944]]},
                {"label": "Total JP Mata Pelajaran Wajib + Penguatan Program + Muatan Lokal",
                 "sum": ["wajib", "penguatan_program", "muatan_lokal"], "jp": [[1836, 1980], 108, [1944, 2088]]},
                {"label": "Total JP Mata Pelajaran Wajib + Mata Pelajaran Pilihan + Muatan Lokal",
                 "sum": ["wajib", "pilihan", "muatan_lokal"], "jp": [[1908, 2052], 108, [2016, 2160]]}],
     "footnotes": {"a": KMA_ARTS_CRAFTS, "b": "Dialokasikan 72 JP per tahun sebagai mata pelajaran pilihan.",
                   "c": "Madrasah yang memilih penguatan program adalah Madrasah yang memiliki SK Direktorat "
                        "Jenderal Pendidikan Islam, yaitu MA Program Keagamaan, MA Akademik, dan MA Plus "
                        "Keterampilan.", "d": kma_mulok(72, 216)},
     "note": "IPA and IPS in grade X are not split into separate subjects (p. 37–38)."},
    {"table": 10, "levels": ["MA"], "grades": [11], "weeks_per_year": 36, "jp_minutes": 45, "pages": [38, 39],
     "rows": W(("quran_hadis", 72, 0, 72), ("akidah_akhlak", 72, 0, 72), ("fikih", 72, 36, 108),
               ("ski", 72, 0, 72), ("bahasa_arab", 72, 0, 72), ("pendidikan_pancasila", 72, 0, 72),
               ("bahasa_indonesia", 108, 0, 108), ("matematika", 108, 36, 144), ("bahasa_inggris", 108, 0, 108),
               ("pjok", 72, 36, 108), ("sejarah", 72, 0, 72), ("seni_budaya", 72, 0, 72))
     + [row("pilihan_ma", "pilihan", [720, 900], 0, [720, 900], options=MA_ELECTIVES, choose=[4, 5],
            jp_each=180, jp_each_exceptions={"ilmu_tafsir": 144, "ilmu_hadis": 144, "ushul_fikih": 144,
                                             "prakarya_kewirausahaan": 72, "mapel_lainnya_ma": 180}),
        row("muatan_lokal", "muatan_lokal", [72, 216], 0, [72, 216])],
     "totals": [{"label": "Total JP Mata Pelajaran Umum", "sum": ["wajib"], "jp": [972, 108, 1080]},
                {"label": "Total JP Mata Pelajaran Umum + pilihan", "sum": ["wajib", "pilihan"],
                 "jp": [[1692, 1872], 108, [1800, 1980]], "printed_jp": [[1692, 1871], 108, [1800, 1980]]},
                {"label": "Total JP Mata Pelajaran Umum + Pilihan + Muatan Lokal",
                 "sum": ["wajib", "pilihan", "muatan_lokal"], "jp": [[1764, 2088], 108, [1872, 2196]]}],
     "footnotes": {"a": KMA_ARTS,
                   "b": "Alokasi masing-masing mata pelajaran pilihan yaitu 4 (empat) JP per minggu atau 144 JP per "
                        "tahun.",
                   "c": "Alokasi masing-masing mata pelajaran pilihan yaitu 5 (lima) JP per minggu atau 180 JP per "
                        "tahun.",
                   "d": "Alokasi mata pelajaran pilihan yaitu 2 (dua) JP per minggu atau 72 JP per tahun.",
                   "e": "Alokasi mata pelajaran pilihan yaitu 6 (enam) JP per minggu atau 180 JP per tahun, bagi "
                        "Madrasah yang memiliki SK Direktorat Jenderal Pendidikan Islam (MA Program Keagamaan, MA "
                        "Akademik, MA Plus Keterampilan).",
                   "f": "Paling sedikit 72 JP per tahun dan paling banyak 216 sebagai mata pelajaran pilihan."},
     "note": "Footnote e prints 6 JP per week with 180 JP per year (6 × 36 = 216), as printed. Every MA opens all "
             "general subjects and at least 7 electives; each student chooses 4–5 and may change them until grade "
             "XI semester 2 (p. 38, 41)."},
    {"table": 11, "levels": ["MA"], "grades": [12], "weeks_per_year": 32, "jp_minutes": 45, "pages": [39, 41],
     "rows": W(("quran_hadis", 64, 0, 64), ("akidah_akhlak", 64, 32, 96), ("fikih", 64, 0, 64),
               ("ski", 64, 0, 64), ("bahasa_arab", 64, 0, 64), ("pendidikan_pancasila", 64, 0, 64),
               ("bahasa_indonesia", 96, 0, 96), ("matematika", 96, 32, 128), ("bahasa_inggris", 96, 0, 96),
               ("seni_budaya", 64, 0, 64), ("pjok", 64, 32, 96), ("sejarah", 64, 0, 64))
     + [row("pilihan_ma", "pilihan", [640, 800], 0, [640, 800], options=MA_ELECTIVES, choose=[4, 5],
            jp_each=160, jp_each_exceptions={"ilmu_tafsir": 128, "ilmu_hadis": 128, "ushul_fikih": 128,
                                             "prakarya_kewirausahaan": 64, "mapel_lainnya_ma": 192}),
        row("muatan_lokal", "muatan_lokal", [64, 192], 0, [64, 192])],
     "totals": [{"label": "Total JP Mata Pelajaran Umum", "sum": ["wajib"], "jp": [864, 96, 960]},
                {"label": "Total JP Mata Pelajaran Umum + pilihan", "sum": ["wajib", "pilihan"],
                 "jp": [[1504, 1664], 96, [1600, 1760]]},
                {"label": "Total JP Mata Pelajaran Umum + Pilihan + Muatan Lokal",
                 "sum": ["wajib", "pilihan", "muatan_lokal"], "jp": [[1568, 1856], 96, [1664, 1952]]}],
     "footnotes": {"a": KMA_ARTS,
                   "b": "4 (empat) JP per minggu atau 128 JP per tahun.",
                   "c": "5 (lima) JP per minggu atau 160 JP per tahun.",
                   "d": "2 (dua) JP per minggu atau 64 JP per tahun.",
                   "e": "6 (enam) JP per minggu atau 192 JP per tahun untuk Madrasah yang memiliki SK Direktorat "
                        "Jenderal Pendidikan Islam.",
                   "f": kma_mulok(64, 192)}},
    # MAK
    {"table": 12, "levels": ["MAK"], "grades": [10], "weeks_per_year": 36, "jp_minutes": 45, "pages": [42, 43],
     "rows": [row(k, "umum", i, ko, t) for k, i, ko, t in [
         ("quran_hadis", 72, 0, 72), ("akidah_akhlak", 72, 0, 72), ("fikih", 72, 0, 72), ("ski", 72, 0, 72),
         ("bahasa_arab", 144, 0, 144), ("pendidikan_pancasila", 72, 0, 72), ("bahasa_indonesia", 108, 36, 144),
         ("pjok", 108, 0, 108), ("sejarah", 72, 0, 72), ("seni_budaya", 72, 0, 72)]]
     + [row(k, "kejuruan", i, ko, t) for k, i, ko, t in [
         ("matematika", 108, 36, 144), ("bahasa_inggris", 108, 36, 144), ("informatika", 108, 36, 144),
         ("projek_ipas", 180, 36, 216), ("dasar_program_keahlian", 432, 0, 432)]]
     + [row("koding_ka", "pilihan", 72, 0, 72), row("muatan_lokal", "muatan_lokal", [72, 216], 0, [72, 216])],
     "totals": [{"label": "Total JP Mata Pelajaran Umum (A)", "sum": ["umum"], "jp": [864, 36, 900]},
                {"label": "Jumlah JP Kelompok Mata Pelajaran Kejuruan (B)", "sum": ["kejuruan"],
                 "jp": [936, 144, 1080]},
                {"label": "Total JP Mata Pelajaran Umum + Mata Pelajaran Kejuruan", "sum": ["umum", "kejuruan"],
                 "jp": [1800, 180, 1980]},
                {"label": "Total JP Mata Pelajaran Umum + Kejuruan + Muatan Lokal",
                 "sum": ["umum", "kejuruan", "muatan_lokal"], "jp": [[1872, 2016], 180, [2052, 2196]]},
                {"label": "Total JP Mata Pelajaran Umum + Mata Pelajaran Kejuruan + Mata Pelajaran Pilihan + "
                          "Muatan Lokal", "sum": ["umum", "kejuruan", "pilihan", "muatan_lokal"],
                 "jp": [[1944, 2088], 180, [2124, 2268]]}],
     "footnotes": {"a": KMA_ARTS, "b": "Proporsi JP antara aspek IPA dan aspek IPS disesuaikan dengan kebutuhan "
                                       "Program Keahlian.", "c": "Nama mata pelajaran menyesuaikan nama program "
                                                                 "keahlian.",
                   "d": "Dialokasikan 2 (dua) JP per minggu atau 72 JP per tahun sebagai mata pelajaran pilihan.",
                   "e": "Paling sedikit 72 JP per tahun dan paling banyak 216 sebagai mata pelajaran pilihan."}},
    {"table": 13, "levels": ["MAK"], "grades": [11], "weeks_per_year": 36, "jp_minutes": 45, "pages": [44],
     "rows": [row(k, "umum", i, ko, t) for k, i, ko, t in [
         ("quran_hadis", 72, 0, 72), ("akidah_akhlak", 72, 0, 72), ("fikih", 72, 36, 108), ("ski", 72, 0, 72),
         ("bahasa_arab", 72, 0, 72), ("pendidikan_pancasila", 72, 0, 72), ("bahasa_indonesia", 72, 36, 108),
         ("pjok", 72, 0, 72), ("sejarah", 72, 0, 72)]]
     + [row(k, "kejuruan", i, ko, t) for k, i, ko, t in [
         ("matematika", 108, 0, 108), ("bahasa_inggris", 108, 36, 144), ("konsentrasi_keahlian", 648, 0, 648),
         ("kik", 180, 0, 180), ("mapel_pilihan_smk", 144, 0, 144)]]
     + [row("muatan_lokal", "muatan_lokal", [72, 216], 0, [72, 216])],
     "totals": [{"label": "Jumlah JP Mata Pelajaran Umum", "sum": ["umum"], "jp": [648, 72, 720]},
                {"label": "Jumlah JP Mata Pelajaran Kejuruan", "sum": ["kejuruan"], "jp": [1188, 36, 1224]},
                {"label": "Total JP Mata Pelajaran Umum + Mata Pelajaran Kejuruan", "sum": ["umum", "kejuruan"],
                 "jp": [1836, 108, 1944]},
                {"label": "Total JP Mata Pelajaran Umum + Mata Pelajaran Kejuruan + Muatan Lokal",
                 "sum": ["umum", "kejuruan", "muatan_lokal"], "jp": [[1908, 2052], 108, [2016, 2160]]}],
     "footnotes": {"a": "Nama mata pelajaran sesuai dengan nama Konsentrasi Keahlian.",
                   "b": "Nama mata pelajaran merupakan mata pelajaran yang dipilih oleh Peserta Didik.",
                   "c": "Paling sedikit 72 JP per tahun dan paling banyak 216."}},
    {"table": 14, "levels": ["MAK"], "grades": [12], "weeks_per_year": 36, "jp_minutes": 45, "pages": [44, 45],
     "rows": [row(k, "umum", i, ko, t) for k, i, ko, t in [
         ("quran_hadis", 64, 0, 64), ("akidah_akhlak", 64, 0, 64), ("fikih", 64, 0, 64), ("ski", 64, 0, 64),
         ("bahasa_arab", 64, 0, 64), ("pendidikan_pancasila", 32, 0, 32), ("bahasa_indonesia", 32, 32, 64)]]
     + [row(k, "kejuruan", i, ko, t) for k, i, ko, t in [
         ("matematika", 48, 0, 48), ("bahasa_inggris", 64, 0, 64), ("konsentrasi_keahlian", 352, 0, 352),
         ("kik", 80, 0, 80), ("pkl", 736, 0, 736), ("mapel_pilihan_smk", 64, 0, 64)]]
     + [row("muatan_lokal", "muatan_lokal", [64, 192], 0, [64, 192])],
     "totals": [{"label": "Jumlah JP Mata Pelajaran Umum", "sum": ["umum"], "jp": [384, 32, 416]},
                {"label": "Jumlah JP Mata Pelajaran Kejuruan", "sum": ["kejuruan"], "jp": [1344, 0, 1344]},
                {"label": "Total JP Mata Pelajaran Umum + Mata Pelajaran Kejuruan", "sum": ["umum", "kejuruan"],
                 "jp": [1728, 32, 1760]},
                {"label": "Total JP Mata Pelajaran Umum + Mata Pelajaran Kejuruan + Muatan Lokal",
                 "sum": ["umum", "kejuruan", "muatan_lokal"], "jp": [[1792, 1920], 32, [1824, 1952]]}],
     "footnotes": {"a": "Nama mata pelajaran sesuai dengan nama Konsentrasi Keahlian.",
                   "b": "Mata Pelajaran Praktik Kerja Lapangan (PKL) dilaksanakan sekurang-kurangnya 1 semester atau "
                        "16 (enam belas) minggu efektif.",
                   "c": "Nama mata pelajaran merupakan mata pelajaran yang dipilih oleh Peserta Didik.",
                   "d": "Paling sedikit 64 JP per tahun dan paling banyak 192."},
     "note": "The heading prints '1 tahun = 36 minggu', but the allocations follow 32 weeks like the other grade "
             "XII tables (as printed)."},
]

KMA_PKK_NOTE = ("MILB tables print all five Program Kebutuhan Khusus options as 'Pengembangan orientasi, mobilitas, "
                "sosial dan komunikasi (Penyandang disabilitas netra/rungu/intelektual/fisik/mental)' (as printed); "
                "MTsLB and MALB print the same five options as Permendikdasmen 13/2025.")
MILB = [
    (15, [1], 36, 30, [47], [("quran_hadis", 72, 36, 108), ("akidah_akhlak", 72, 0, 72), ("fikih", 72, 0, 72),
                             ("bahasa_arab", 72, 0, 72), ("pendidikan_pancasila", 72, 0, 72),
                             ("bahasa_indonesia", 108, 36, 144), ("matematika", 72, 0, 72), ("pjok", 72, 0, 72),
                             ("seni_budaya", 252, 36, 288), ("program_kebutuhan_khusus", 216, 0, 216)],
     72, [1080, 108, 1188], [1152, 108, 1260], {}),
    (16, [2], 36, 30, [48], [("quran_hadis", 72, 36, 108), ("akidah_akhlak", 72, 0, 72), ("fikih", 72, 0, 72),
                             ("bahasa_arab", 72, 0, 72), ("pendidikan_pancasila", 72, 0, 72),
                             ("bahasa_indonesia", 108, 36, 144), ("matematika", 108, 0, 108), ("pjok", 72, 0, 72),
                             ("seni_budaya", 252, 36, 288), ("program_kebutuhan_khusus", 216, 0, 216)],
     72, [1116, 108, 1224], [1188, 108, 1296], {}),
    (17, [3, 4], 36, 30, [49], [("quran_hadis", 72, 0, 72), ("akidah_akhlak", 72, 0, 72), ("fikih", 72, 36, 108),
                                ("ski", 72, 0, 72), ("bahasa_arab", 72, 0, 72), ("pendidikan_pancasila", 72, 0, 72),
                                ("bahasa_indonesia", 72, 36, 108), ("matematika", 72, 0, 72), ("ipas", 72, 0, 72),
                                ("pjok", 72, 0, 72), ("seni_budaya", 360, 36, 396),
                                ("program_kebutuhan_khusus", 216, 0, 216), ("bahasa_inggris", 72, 0, 72)],
     72, [1368, 108, 1476], [1440, 108, 1548], {}),
    (18, [5], 36, 30, [50, 51], [("quran_hadis", 72, 0, 72), ("akidah_akhlak", 72, 36, 108), ("fikih", 72, 0, 72),
                                 ("ski", 72, 0, 72), ("bahasa_arab", 72, 0, 72), ("pendidikan_pancasila", 72, 0, 72),
                                 ("bahasa_indonesia", 108, 0, 108), ("matematika", 108, 0, 108), ("ipas", 72, 0, 72),
                                 ("pjok", 72, 0, 72), ("seni_budaya", 360, 36, 396),
                                 ("program_kebutuhan_khusus", 144, 0, 144), ("bahasa_inggris", 72, 0, 72)],
     72, [1368, 108, 1476], [1440, 108, 1548], {"unresolved": True}),
    (19, [6], 32, 33, [51, 52], [("quran_hadis", 64, 0, 64), ("akidah_akhlak", 64, 32, 96), ("fikih", 64, 0, 64),
                                 ("ski", 64, 0, 64), ("bahasa_arab", 64, 0, 64), ("pendidikan_pancasila", 64, 0, 64),
                                 ("bahasa_indonesia", 96, 32, 128), ("matematika", 96, 0, 96), ("ipas", 64, 0, 64),
                                 ("pjok", 64, 0, 64), ("seni_budaya", 320, 32, 352),
                                 ("program_kebutuhan_khusus", 128, 0, 128), ("bahasa_inggris", 64, 0, 64)],
     64, [1216, 96, 1312], [1280, 96, 1376],
     {"label": "Total JP Mata Pelajaran Wajib + Pilihan + Muatan Lokal",
      "note": "Labelled with 'Pilihan'; the table has no elective."}),
]
for n, grades, weeks, jpm, pages, rows, mulok, t_w, t_wm, extra in MILB:
    second = {"label": "Total JP Mata Pelajaran Wajib + Muatan Lokal", "sum": ["wajib", "muatan_lokal"],
              "jp": t_wm}
    first = {"label": "Total JP Mata Pelajaran Wajib", "sum": ["wajib"], "jp": t_w}
    if extra.get("unresolved"):
        first["unresolved"] = second["unresolved"] = True
    else:
        second.update(extra)
    t = {"table": n, "levels": ["MILB"], "grades": grades, "weeks_per_year": weeks, "jp_minutes": jpm,
         "pages": pages, "rows": wajib(*rows) + [row("muatan_lokal", "muatan_lokal", mulok, 0, mulok)],
         "totals": [first, second],
         "footnotes": {"a": KMA_ARTS, "b": "Dipilih sesuai jenis hambatan Peserta Didik."}, "note": KMA_PKK_NOTE}
    if jpm == 33:
        t["note"] += (" The heading prints '1 JP = 33 menit' (every other MILB table: 30 minutes); stored as "
                      "printed.")
    KMA_TABLES.append(t)

LB13 = ["quran_hadis", "akidah_akhlak", "fikih", "ski", "bahasa_arab", "pendidikan_pancasila", "bahasa_indonesia",
        "matematika", "ipa", "ips", "bahasa_inggris", "pjok", "seni_budaya"]
KMA_LB = [
    # table, levels, grade, weeks, jp_min, pages, general (i, ko), skills (i, ko, total), pkk (i, total), mulok,
    # wajib totals, wajib+mulok totals, footnote a weeks (as printed), skills footnote
    (20, "MTsLB", 7, 36, 35, [52, 54], (54, 18), (468, 36, 504), (108, 108), 72, [1278, 270, 1548],
     [1350, 270, 1620], (36, 27), "Peserta Didik memilih minimal 2 (dua) keterampilan."),
    (21, "MTsLB", 8, 36, 35, [54, 56], (54, 18), (468, 36, 504), (108, 108), 72, [1278, 270, 1548],
     [1350, 270, 1620], (36, 27), "Peserta Didik memilih 1 (satu) keterampilan."),
    (22, "MTsLB", 9, 32, 35, [56, 58], (48, 16), (416, 32, 448, 504), (96, 96, 108), 64, [1136, 240, 1376],
     [1200, 240, 1440], (32, 24), "Peserta Didik memilih 1 (satu) keterampilan."),
    (23, "MALB", 10, 36, 40, [58, 60], (54, 18), (648, 36, 684), (72, 72), 72, [1422, 270, 1692],
     [1494, 270, 1764], (32, 24), "Peserta Didik memilih 1 (satu) keterampilan."),
    ("24a", "MALB", 11, 36, 40, [60, 61], (54, 18), (720, 36, 756), (72, 72), 72, [1494, 270, 1764],
     [1566, 270, 1836], (32, 24), "Peserta Didik memilih 1 (satu) keterampilan."),
    ("24b", "MALB", 12, 32, 40, [62, 63], (48, 16), (640, 32, 672), (64, 64, 72), 64, [1328, 240, 1568],
     [1392, 240, 1632], (32, 24), "Peserta Didik memilih 1(satu) keterampilan."),
]
for n, level, grade, weeks, jpm, pages, (gi, gk), sk, pk, mulok, t_w, t_wm, (wa, wb), fn_skill in KMA_LB:
    rows = [row(k, "wajib", gi, gk, gi + gk) for k in LB13]
    rows.append(row("kelompok_keterampilan", "wajib", sk[0], sk[1], sk[2],
                    **({"printed_total": sk[3]} if len(sk) > 3 else {})))
    rows.append(row("program_kebutuhan_khusus", "wajib", pk[0], 0, pk[1],
                    **({"printed_total": pk[2]} if len(pk) > 2 else {})))
    rows.append(row("muatan_lokal", "muatan_lokal", mulok, 0, mulok))
    t = {"table": n, "levels": [level], "grades": [grade], "weeks_per_year": weeks, "jp_minutes": jpm,
         "pages": pages, "rows": rows,
         "totals": [{"label": "Total JP Mata Pelajaran Wajib", "sum": ["wajib"], "jp": t_w},
                    {"label": "Total JP Mata Pelajaran Wajib + Muatan Lokal", "sum": ["wajib", "muatan_lokal"],
                     "jp": t_wm}],
         "footnotes": {"a": f"Pembelajaran tidak penuh {wa} minggu untuk memenuhi alokasi Kokurikuler, "
                            f"Intrakurikuler dialokasikan {wb} minggu.",
                       "b": KMA_ARTS, "c": fn_skill, "d": "Dipilih sesuai jenis hambatan Peserta Didik."}}
    if wa != weeks:
        t["note"] = f"Footnote a prints {wa}/{wb} weeks although the table assumes {weeks} weeks (as printed)."
    if isinstance(n, str):
        t["table"] = 24
        t["table_id"] = f"KMA-T{n}"
        t["note"] = (t.get("note", "") + " The decree numbers both the grade XI and the grade XII MALB table "
                     "'Tabel 24'.").strip()
    KMA_TABLES.append(t)

KMA_RA = {
    "levels": ["RA"], "ref": f"{KMA} A (p. 27)",
    "minutes_per_week_min": {"4-6": 900},
    "note": "Structure set by the head of the RA; intrakurikuler by meaningful play towards CP Fase Fondasi and "
            "Panca Cinta; kokurikuler towards the graduate profile and Panca Cinta (STPPA); RA luar biasa: early "
            "intervention, Program Kebutuhan Khusus from Fase Fondasi.",
}

KMA_RULES = [
    {"levels": ["MI", "MTs", "MA", "MAK"],
     "text": "The structure is set by the head of the madrasah with at least these allocations; the madrasah may "
             "add at most 6 JP per week based on its analysis of learning outcomes and available time.",
     "ref": f"{KMA} (p. 28, 32, 36, 42, 46)"},
    {"levels": ["MI", "MTs", "MA", "MAK", "MILB", "MTsLB", "MALB"],
     "text": "Muatan lokal follows the madrasah's character and local potential: keagamaan, seni budaya, prakarya, "
             "PJOK, bahasa, teknologi and/or riset (LB: without keagamaan and riset).",
     "ref": f"{KMA} (p. 31, 35, 41, 46, 64)"},
    {"levels": ["MTs", "MA"],
     "text": "A madrasah with a special programme may use the muatan lokal (MTs) or penguatan program (MA) time "
             "for religious, sport or arts strengthening; MA: grades X–XI 72–216 JP, grade XII 64–192 JP.",
     "ref": f"{KMA} (p. 36, 42)"},
    {"levels": ["MI", "MTs", "MA", "MAK"],
     "text": "Kokurikuler team: subject teachers whose kokurikuler time is moved may be facilitators (1 JP per "
             "class); the coordinator's load equals 2 teaching hours per class per year, at most 3 classes.",
     "ref": f"{KMA} (p. 32, 36, 42, 46)"},
    {"levels": ["MI"], "text": ENGLISH_SD, "ref": f"{P12} Pasal 33 (PDF p. 11)"},
]

# ------------------------------------------------------------------ checks

def add(a, b):
    if isinstance(a, list) or isinstance(b, list):
        a = a if isinstance(a, list) else [a, a]
        b = b if isinstance(b, list) else [b, b]
        return [a[0] + b[0], a[1] + b[1]]
    return a + b


def norm(v):
    return v if not (isinstance(v, list) and v[0] == v[1]) else v[0]


ERRATA = [  # printed values that contradict the table's own totals (user decision 2026-11-26: store the value the
    # totals require and keep the printed one in `printed_*`); `unresolved` = the totals cannot tell which cell is wrong
    {"source": "P13", "table": 20, "where": ["pendidikan_pancasila", "ipas", "pjok"], "pages": [47, 48],
     "printed": {"intrakurikuler": 54}, "stored": {"intrakurikuler": 64},
     "reason": "Each row prints intrakurikuler 54, kokurikuler '-' and total 64; only 64 makes 'Total JP Mata "
               "Pelajaran Wajib' (992 intrakurikuler, 1.216) add up."},
    {"source": "KMA", "table": 8, "where": ["akidah_akhlak"], "pages": [34],
     "printed": {"total": 64}, "stored": {"total": 96},
     "reason": "Prints 64 + 32 = 64; the table total 1.344 needs 96."},
    {"source": "KMA", "table": 8, "where": ["Total JP Mata Pelajaran Wajib + Muatan Lokal"], "pages": [35],
     "printed": {"total": [1408, 1538]}, "stored": {"total": [1408, 1536]},
     "reason": "1.344 + 192 = 1.536."},
    {"source": "KMA", "table": 10, "where": ["Total JP Mata Pelajaran Umum + pilihan"], "pages": [39],
     "printed": {"intrakurikuler": [1692, 1871]}, "stored": {"intrakurikuler": [1692, 1872]},
     "reason": "972 + 900 = 1.872; the total column (1.980) agrees."},
    {"source": "KMA", "table": 18, "where": ["Total JP Mata Pelajaran Wajib", "Total JP Mata Pelajaran Wajib + "
                                             "Muatan Lokal"], "pages": [50], "unresolved": True,
     "printed": {"kokurikuler": 108, "total": [1476, 1548]}, "rows_give": {"kokurikuler": 72, "total": [1440, 1512]},
     "reason": "The rows print kokurikuler only for Akidah Akhlak (36) and Seni dan Budaya (36); the totals count "
               "108. The table does not show which row lacks 36 JP; rows and totals are stored as printed."},
    {"source": "KMA", "table": 22, "where": ["kelompok_keterampilan", "program_kebutuhan_khusus"],
     "pages": [56, 57], "printed": {"total": [504, 108]}, "stored": {"total": [448, 96]},
     "reason": "416 + 32 = 448 and 96 + 0 = 96; the table total 1.376 (1.136 + 240) agrees with the stored values."},
    {"source": "KMA", "table": "24b", "where": ["program_kebutuhan_khusus"], "pages": [63],
     "printed": {"total": 72}, "stored": {"total": 64},
     "reason": "64 + 0 = 64; the table total 1.568 (1.328 + 240) agrees."},
]


def tid(src, t):
    return t.get("table_id") or f"{src}-T{t['table']}"


def has_erratum(src, t, where):
    key = t.get("table_id", "").split("-T")[-1] if t.get("table_id") else t["table"]
    return any(e["source"] == src and str(e["table"]) == str(key) and where in e["where"] for e in ERRATA)


def check_tables(src, tables):
    for t in tables:
        for r in t["rows"]:
            if r["subject"] not in SUBJECTS and r["subject"] not in ("pilihan_sma", "pilihan_ma"):
                sys.exit(f"{tid(src, t)}: unknown subject {r['subject']}")
            for k in r.get("options", []):
                if k not in SUBJECTS:
                    sys.exit(f"{tid(src, t)}: unknown option {k}")
            if norm(add(r["intrakurikuler"], r["kokurikuler"])) != norm(r["total"]):
                sys.exit(f"{tid(src, t)}: {r['subject']} intra + ko != total")
            if any(k.startswith("printed_") for k in r) and not has_erratum(src, t, r["subject"]):
                sys.exit(f"{tid(src, t)}: {r['subject']} has a printed value but no erratum")
        for tot in t["totals"]:
            s = [0, 0, 0]
            for r in t["rows"]:
                if r["group"] in tot["sum"] or r["subject"] in tot["sum"]:
                    s = [add(s[0], r["intrakurikuler"]), add(s[1], r["kokurikuler"]), add(s[2], r["total"])]
            ok = [norm(x) for x in s] == [norm(x) for x in tot["jp"]]
            if tot.get("unresolved"):
                if ok or not has_erratum(src, t, tot["label"]):
                    sys.exit(f"{tid(src, t)}: unresolved total '{tot['label']}' without erratum or now adding up")
            elif not ok:
                sys.exit(f"{tid(src, t)}: '{tot['label']}' {tot['jp']}, rows give {s}")
            if "printed_jp" in tot and not has_erratum(src, t, tot["label"]):
                sys.exit(f"{tid(src, t)}: '{tot['label']}' has a printed value but no erratum")


def check():
    nums = [t["table"] for t in TABLES] + [p["table"] for p in PAKET]
    if sorted(nums) != list(range(1, 30)):
        sys.exit(f"Permendikdasmen tables missing or doubled: {sorted(nums)}")
    knums = sorted(str(t.get("table_id", t["table"])) for t in KMA_TABLES)
    want = sorted([str(i) for i in range(1, 24)] + ["KMA-T24a", "KMA-T24b"])
    if knums != want:
        sys.exit(f"KMA tables missing or doubled: {knums}")
    check_tables("P13", TABLES)
    check_tables("KMA", KMA_TABLES)
    for p in PAKET:
        for tot in p["totals"]:
            for ph, v in tot["skk"].items():
                if sum(p["skk"][g][ph] for g in tot["sum"]) != v:
                    sys.exit(f"Tabel {p['table']}: '{tot['label']}' {ph} does not add up")
        for g, by in p["skk"].items():
            if sum(v for k, v in by.items() if k != "total") != by["total"]:
                sys.exit(f"Tabel {p['table']}: {g} phases do not add up to the total")
        for k in p["wajib"] + p.get("pilihan", []):
            if k not in SUBJECTS:
                sys.exit(f"Tabel {p['table']}: unknown subject {k}")
    for k in SMA_ELECTIVES + MA_ELECTIVES:
        if k not in SUBJECTS:
            sys.exit(f"unknown elective {k}")
    used = {r["subject"] for t in TABLES + KMA_TABLES for r in t["rows"]} | set(SMA_ELECTIVES + MA_ELECTIVES)
    used |= {k for p in PAKET for k in p["wajib"] + p.get("pilihan", [])} | {"pemberdayaan_keterampilan"}
    if set(SUBJECTS) - used:
        sys.exit(f"subjects never used: {sorted(set(SUBJECTS) - used)}")


def finish(src, t, ref):
    t = dict(t)
    t["id"] = t.pop("table_id", None) or f"{src}-T{t['table']}"
    t["source"] = src
    t["phase"] = sorted({phase_of(g) for g in t["grades"]})
    t["ref"] = f"{ref}, Tabel {t['table']} ({'PDF ' if src == 'P13' else ''}p. {'–'.join(map(str, t['pages']))})"
    t["unit"] = "JP per tahun"
    return t


def main(out):
    check()
    tables = [finish("P13", t, P13) for t in TABLES] + [finish("KMA", t, KMA) for t in KMA_TABLES]
    data = {
        "name": "Mata pelajaran dan alokasi waktu",
        "sources": {
            "P13": "Permendikdasmen 13/2025 (in force 2025-07-15), Lampiran II Struktur Kurikulum; PDF pages",
            "P12": "Permendikbudristek 12/2024, articles not amended by 13/2025 (Pasal 33)",
            "KMA": "Keputusan Menteri Agama 1503/2025 (2025-09-22), Lampiran II BAB III; printed page = PDF page",
        },
        "phases": PHASES, "phases_ref": PHASES_REF,
        "subjects": [dict(key=k, **v) for k, v in SUBJECTS.items()],
        "tables": tables,
        "kesetaraan": {"unit": "SKK", "rule": SKK_RULE, "programmes": PAKET},
        "paud": PAUD, "ra": KMA_RA,
        "rules": [dict(r, source="P13") for r in RULES] + [dict(r, source="KMA") for r in KMA_RULES],
        "errata": ERRATA,
        "notes": [
            "Pick the table by `levels` (SD, MI, SMP, MTs, SMA, MA, SMK, MAK, SDLB, MILB, SMPLB, MTsLB, SMALB, MALB) "
            "and grade. Madrasah use the KMA tables (source KMA); MI/MTs/MA/MAK also appear in the Permendikdasmen "
            "tables, which the KMA adapts for madrasah.",
            "A row's `group`: wajib, pilihan, muatan_lokal; SMK/MAK: umum, kejuruan, pilihan, muatan_lokal. Printed "
            "'-' is 0; ranges are [min, max]. Elective blocks (pilihan_sma, pilihan_ma) list `options`, `choose` "
            "and the JP per elective.",
            "Weekly JP = JP per tahun / weeks_per_year; the decrees print yearly figures only. Kokurikuler is an "
            "annual allocation, so a weekly kokurikuler figure is only an equivalent.",
            "`errata` lists printed cells that contradict the table's own totals; rows keep the printed value in "
            "`printed_*` and totals in `printed_jp`.",
        ],
    }
    d = os.path.join(out, "mapel")
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "mapel.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
        f.write("\n")
    n_tot = sum(len(t["totals"]) for t in TABLES + KMA_TABLES) + sum(len(p["totals"]) for p in PAKET)
    print(f"ok: {len(TABLES)} + {len(PAKET)} Permendikdasmen tables, {len(KMA_TABLES)} KMA tables, "
          f"{len(SUBJECTS)} subjects, {n_tot} printed totals checked, {len(ERRATA)} errata "
          f"({sum(1 for e in ERRATA if e.get('unresolved'))} unresolved)")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
