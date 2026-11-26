#!/usr/bin/env python3
"""Build the data set `kerangka-tka` (R-16, F-030): the Tes Kemampuan Akademik framework.

Sources (sources/kerangka-tka/, SOURCE.txt):
  - Perka BSKAP 047/H/AN/2025 (2025-07-24), Lampiran "Kerangka Asesmen TKA jenjang SD/MI/sederajat dan
    SMP/MTs/sederajat": test subjects, item types and forms, content and competencies per level and subject.
  - Kepmendikdasmen 56/2026 (2026-03-06), Pedoman Penyelenggaraan TKA dan AN: test subjects for every level
    (incl. the SMA/SMK electives), schedule and minutes per test, score range, result categories.

Both PDFs have a clean text layer. The content is transcribed below as printed, with the PDF page of every part.
Every text unit (sentence, list item, table cell) is checked against the PDF: its letters and digits must occur in
the page text or in a table cell that pdfplumber reads on that page; every table cell of the framework tables must
be covered by the transcription. The sample questions (part IV of 047) are left out: they are examples with
figures, not framework data. The script stops on any mismatch, then writes data/kerangka-tka/kerangka-tka.json:

  python3 -I tools/converters/kerangka-tka.py sources/kerangka-tka data
"""
import json
import os
import re
import subprocess
import sys

P047 = "Perka_BSKAP_No_047_H_AN_2025_Kerangka_Asesmen_TKA_SD_MI_dan_SMP_MTs.pdf"
P56 = "Kepmendikdasmen_No_56_Tahun_2026_Pedoman_Penyelenggaraan_TKA_dan_AN.pdf"
REF047 = "Perka BSKAP 047/H/AN/2025, Lampiran"
REF56 = "Kepmendikdasmen 56/2026, Lampiran"

# Printing errors (F-031): kept as printed; each must occur in the data. (document, page, printed, reason)
ERRATA = [
    ("047", 24, "peginterpretasian", "'peginterpretasian' for 'penginterpretasian' (SMP, Data dan Peluang)"),
    ("047", 21, "Persamaan dan Pertidaksamaan Linier", "'Linier' in the sub-element name; its items print "
     "'linear' (SMP, Aljabar)"),
]

# ------------------------------------------------------------------ 047 part II: subjects, item types and forms

ITEM_TYPES = [
    {"key": "tunggal", "label": "Soal tunggal",
     "description": "Soal tunggal merupakan soal yang berdiri sendiri, tidak terkait dengan soal-soal lain."},
    {"key": "grup", "label": "Soal grup",
     "description": "Soal grup adalah sekumpulan soal yang mengacu pada sebuah stimulus yang sama."},
]
ITEM_FORMS = [
    {"key": "pg", "label": "pilihan ganda sederhana",
     "description": "Pada soal pilihan ganda sederhana, hanya terdapat satu pilihan jawaban yang benar. Peserta "
                    "diminta memilih satu jawaban dari pilihan yang tersedia."},
    {"key": "pgk_mcma", "label": "pilihan ganda kompleks (PGK) model multiple choice multiple answers (MCMA)",
     "description": "Pada soal pilihan ganda kompleks MCMA, terdapat kemungkinan lebih dari satu pilihan jawaban "
                    "benar. Peserta diminta memilih lebih dari satu pilihan yang dianggap benar."},
    {"key": "pgk_kategori", "label": "pilihan ganda kompleks (PGK) model kategori",
     "description": "Pada soal pilihan ganda kompleks kategori, terdapat beberapa pernyataan yang semuanya perlu "
                    "direspon, misalnya dengan pilihan “benar” atau “salah” dan “sesuai” atau “tidak sesuai”. "
                    "Peserta diminta untuk memberi respon untuk masing-masing pernyataan tersebut."},
]
FORMS_INTRO = ("Semua bentuk soal menyajikan beberapa pilihan jawaban atau respons untuk sebuah pokok soal.")

# ------------------------------------------------------------------ 047 part III: content and competencies

READING_ASPECTS = [
    "mengidentifikasi informasi tersurat dalam teks;",
    "menyusun ulang, mengelompokkan, membuat ikhtisar, dan menyajikan kembali informasi tersurat dalam teks;",
    "mengidentifikasi dan menyimpulkan informasi tersirat dalam teks;",
    "menilai gagasan, fakta, atau opini dalam teks; dan",
    "menanggapi isi teks, merefleksi diri dengan tokoh atau kejadian, dan menanggapi bahasa penulis dalam teks.",
]
READING_COMPETENCIES = {  # name as in the table: description as in the list before it
    "Pemahaman Tekstual": "pemahaman tekstual, yaitu kemampuan untuk memahami informasi yang dikemukakan secara "
                          "eksplisit, mengelompokkan, menyusun ulang, dan menyajikan kembali informasi secara "
                          "eksplisit dari teks;",
    "Pemahaman Inferensial": "pemahaman inferensial, yaitu kemampuan untuk menarik kesimpulan berdasarkan "
                             "informasi yang tersirat dalam teks; dan",
    "Evaluasi dan Apresiasi": "evaluasi dan apresiasi, yaitu kemampuan untuk membuat penilaian terhadap ide, "
                              "menanggapi teks secara emosional dan estetis dengan mempertimbangkan dampaknya "
                              "terhadap perasaan, imajinasi, serta penggunaan bahasa oleh penulis.",
}


def bahasa_indonesia(level, pages, intro, texts, characteristics, subs):
    return {
        "level": level, "subject": "Bahasa Indonesia", "pages": pages, "intro": intro,
        "muatan": {
            "intro": "Keterampilan membaca diujikan pada dua jenis teks, yaitu teks informasi dan teks fiksi.",
            "text_types": [{"label": "Teks informasi", "description": texts[0]},
                           {"label": "Teks fiksi", "description": texts[1]}],
            "text_characteristics": [{"label": k, "description": v} for k, v in characteristics],
        },
        "kompetensi": {
            "aspects": READING_ASPECTS,
            "competencies": [{"no": i + 1, "name": name, "description": READING_COMPETENCIES[name],
                              "subcompetencies": subs[name]} for i, name in enumerate(READING_COMPETENCIES)],
        },
    }


BI_SD = bahasa_indonesia(
    "SD/MI/sederajat", [8, 10],
    "TKA Bahasa Indonesia SD/MI/sederajat difokuskan pada salah satu keterampilan berbahasa, yakni membaca. "
    "Membaca dipilih sebagai fokus karena merupakan keterampilan yang menjadi fondasi untuk terus belajar dan "
    "bekerja pada era teknologi yang berubah dan berkembang sangat cepat.",
    ["Teks informasi merupakan teks yang berisi fakta sederhana dari berbagai bidang atau topik serta berskala "
     "lokal dan nasional.",
     "Teks fiksi merupakan cerita rekaan yang dapat berupa fantasi atau faktual (sejarah/biografi) dengan latar "
     "cerita konkret, tokoh berkarakter datar, konflik tunggal dengan penyelesaian tertutup, alur maju, dan sudut "
     "pandang orang pertama."],
    [("Karakteristik kosakata", "kata dasar, kata berimbuhan, kata konkret, dominan makna denotatif, makna "
      "konotatif konteks terbatas."),
     ("Karakteristik kalimat", "jumlah kata 3–7 per kalimat, pola kalimat dasar SPOK, struktur bahasa tulis "
      "bercampur bahasa lisan terbatas."),
     ("Karakteristik wacana", "kohesi pengacuan/referensi, konjungsi antarparagraf penambahan/penjelasan; panjang "
      "teks 150–200 kata (kecuali teks puisi).")],
    {"Pemahaman Tekstual": [
        "Mengidentifikasi penggunaan kosakata umum dan khusus dalam berbagai bidang.",
        "Mengidentifikasi objek berdasarkan kosakata yang digunakan dalam teks fiksi atau nonfiksi.",
        "Menyusun kembali informasi dari teks dalam bentuk ikhtisar/bagan.",
        "Mengidentifikasi informasi tersurat dalam teks."],
     "Pemahaman Inferensial": [
        "Menyimpulkan ide pokok, gagasan pendukung, amanat, tokoh, peristiwa, dan/atau nilai-nilai dalam teks.",
        "Menyimpulkan perubahan sederhana pada objek, karakter, dan/atau latar dalam teks fiksi atau nonfiksi.",
        "Menjelaskan makna ungkapan yang digunakan dalam teks."],
     "Evaluasi dan Apresiasi": [
        "Menilai relevansi peristiwa dalam teks dengan kehidupan sehari-hari berdasarkan pengalaman atau "
        "pengetahuan pribadi.",
        "Menilai kesesuaian antarunsur dan/atau antarinformasi dalam teks.",
        "Menyimpulkan respons emosional terhadap unsur teks fiksi."]})

BI_SMP = bahasa_indonesia(
    "SMP/MTs/sederajat", [15, 17],
    "Sebagaimana TKA Bahasa Indonesia SD/MI/sederajat, TKA Bahasa Indonesia SMP/MTs/sederajat juga difokuskan pada "
    "keterampilan membaca.",
    ["Teks informasi merupakan teks yang berisi fakta, konsep, atau prosedur dari berbagai bidang atau topik yang "
     "berskala lokal, nasional, atau global. Teks informasi dapat berupa teks tunggal maupun teks jamak.",
     "Teks fiksi merupakan cerita rekaan yang dapat bersifat faktual (sejarah/biografi) atau realisme dengan latar "
     "cerita konkret atau abstrak, tokoh berkarakter bulat, konflik tunggal atau jamak dengan penyelesaian "
     "tertutup, alur campuran, dan sudut pandang orang ketiga."],
    [("Karakteristik kosakata", "kata umum, kata berimbuhan/konfiks, kata abstrak, makna denotatif, istilah "
      "teknis, makna konotatif konteks tertentu."),
     ("Karakteristik kalimat", "jumlah kata per kalimat 5–9 kata, kalimat tunggal berbagai pola, kalimat majemuk "
      "setara."),
     ("Karakteristik wacana", "kohesi penyulihan/substitusi, konjungsi antarparagraf perbandingan dan "
      "penekanan/intensifikasi, penggunaan tanda baca untuk mendukung deskripsi; panjang teks 200–250 kata "
      "(kecuali teks puisi).")],
    {"Pemahaman Tekstual": [
        "Mengidentifikasi penggunaan istilah dalam berbagai bidang.",
        "Mengidentifikasi objek dan/atau latar berdasarkan kosakata yang digunakan dalam teks fiksi atau nonfiksi.",
        "Mengidentifikasi informasi penting yang tersurat dalam teks.",
        "Menyusun kerangka atau bagan berdasarkan bagian-bagian penting dalam teks."],
     "Pemahaman Inferensial": [
        "Menyimpulkan ide pokok, gagasan pendukung, tokoh, peristiwa, latar, dan/atau nilai-nilai dalam dan/atau "
        "antarteks.",
        "Menjelaskan kelogisan hubungan antarperistiwa, antargagasan, dan/atau antarinformasi dalam dan/atau "
        "antarteks.",
        "Memprediksi peristiwa dalam teks.",
        "Menjelaskan bahasa kias dan citraan yang digunakan dalam teks fiksi."],
     "Evaluasi dan Apresiasi": [
        "Menilai relevansi peristiwa dalam teks dengan kehidupan sehari-hari.",
        "Menilai kesesuaian dan/atau keakuratan unsur, kebahasaan, atau isi berdasarkan perbandingan informasi "
        "dalam dan/atau antarteks.",
        "Menyimpulkan respons emosional terhadap unsur teks fiksi."]})

COGNITIVE_INTRO = (
    "Kemampuan matematis diukur pada tiga level kognitif, yaitu Pengetahuan dan Pemahaman (Knowing and "
    "Understanding), Aplikasi (Applying), dan Penalaran (Reasoning). Kemampuan matematis dalam setiap cakupan "
    "sub-elemen memungkinkan diukur dalam satu atau beberapa level kognitif. Setiap level kognitif mencakup beberapa "
    "proses berpikir. Berikut deskripsi proses berpikir untuk setiap level kognitif.")
SCOPE_INTRO = ("Memahami, mengaplikasikan, dan bernalar yang lebih tinggi untuk menyelesaikan permasalahan terkait "
               "cakupan sub-elemen berikut:")


def levels(*lv):
    names = [("Pengetahuan dan Pemahaman", "Knowing and Understanding"), ("Aplikasi", "Applying"),
             ("Penalaran", "Reasoning")]
    return [{"level": i + 1, "name": names[i][0], "name_en": names[i][1],
             "processes": [{"name": n, "description": d} for n, d in procs]} for i, procs in enumerate(lv)]


def content(no, element, sub, scope, note=None):
    c = {"no": no, "element": element, "sub_element": sub, "competency": SCOPE_INTRO, "scope": scope}
    if note:
        c["note"] = note
    return c


MAT_SD = {
    "level": "SD/MI/sederajat", "subject": "Matematika", "pages": [10, 15],
    "intro": "TKA Matematika SD/MI/sederajat mengukur kemampuan murid dalam memahami fakta, konsep, prinsip, dan "
             "prosedur matematika, serta kemampuan mereka dalam menerapkan pengetahuan matematika untuk "
             "menyelesaikan masalah (problem solving).",
    "muatan": {
        "intro": "Muatan TKA Matematika SD/MI/sederajat merujuk pada elemen kurikulum atau materi matematika yang "
                 "dipelajari murid yang ada pada Kurikulum 2013 dan Kurikulum Merdeka. Elemen ini meliputi:",
        "elements": ["bilangan,", "geometri dan pengukuran, dan", "data."],
        "notes": ["Pengetahuan matematika diukur melalui permasalahan dalam konteks matematika dan permasalahan "
                  "dalam konteks keseharian yang dapat meliputi kejadian atau situasi di lingkup personal, "
                  "keluarga, atau lingkungan sekitar."],
    },
    "kompetensi": {
        "intro": "Tes Kemampuan Akademik (TKA) Matematika SD/MI/sederajat mengukur kemampuan matematis sebagai "
                 "berikut:",
        "abilities": ["pengetahuan matematika,", "representasi matematis,", "penalaran,",
                      "pemecahan masalah matematis, dan", "koneksi matematis."],
        "cognitive_intro": COGNITIVE_INTRO,
        "cognitive_levels": levels(
            [("Menghitung", "Melakukan perhitungan berdasarkan prosedur yang mencakup operasi hitung aritmatika "
              "(+, -, ×, ÷, atau kombinasinya)."),
             ("Memahami informasi", "Memahami informasi dari grafik fungsi, tabel, diagram, infografis, atau "
              "bentuk visual lainnya."),
             ("Mengelompokkan", "Mengelompokkan objek berdasarkan fakta, konsep, dan prinsip matematika dalam "
              "cakupan sub-elemen."),
             ("Mengidentifikasi", "Melakukan identifikasi terhadap objek menggunakan konsep, fakta, dan prinsip "
              "matematika dalam cakupan sub-elemen.")],
            [("Memodelkan", "Memodelkan permasalahan kontekstual terkait cakupan sub-elemen ke dalam kalimat "
              "matematika."),
             ("Mengaplikasikan", "Mengaplikasikan rumus matematika untuk menyelesaikan permasalahan yang "
              "melibatkan konsep dan prosedur matematis yang familiar dan rutin."),
             ("Menginterpretasikan", "Menjelaskan makna dari berbagai situasi, kejadian, pernyataan, representasi, "
              "atau masalah matematika.")],
            [("Menganalisis", "Menentukan, menjelaskan, dan menggunakan hubungan beberapa konsep, fakta, prinsip, "
              "atau prosedur matematika dalam cakupan sub-elemen."),
             ("Memecahkan masalah", "Mengaitkan beberapa konsep, fakta, prinsip, prosedur, dan representasi "
              "matematika dalam cakupan sub-elemen, untuk menyelesaikan permasalahan dalam situasi baru atau "
              "konteks yang tidak rutin."),
             ("Mengevaluasi", "Mengevaluasi alternatif strategi dan solusi dari suatu pemecahan masalah."),
             ("Menyimpulkan", "Menarik kesimpulan yang valid dari informasi, data, atau bukti yang diberikan "
              "menggunakan konsep, fakta, prinsip, dan prosedur matematika dalam cakupan sub-elemen.")]),
        "content_intro": "Muatan dan kompetensi yang diukur dalam TKA Matematika SD/MI/sederajat dirangkum dalam "
                         "tabel berikut:",
        "content": [
            content(1, "Bilangan", "Bilangan Rasional", [
                "Pecahan senilai menggunakan gambar dan simbol matematika;",
                "Perbandingan dan pengurutan bilangan pecahan;",
                "Relasi berbagai bentuk pecahan (pecahan sederhana, desimal, persen);",
                "Operasi penjumlahan, pengurangan, perkalian, dan pembagian bilangan cacah;",
                "Operasi penjumlahan dan pengurangan bilangan pecahan, serta operasi perkalian dan pembagian "
                "bilangan pecahan dengan bilangan asli;",
                "Kelipatan, faktor, KPK, dan FPB bilangan asli."]),
            content(2, "Geometri dan Pengukuran", "Objek Geometri", [
                "Bentuk bangun datar;",
                "Konstruksi bangun ruang dan visualisasi spasial (bagian depan, atas, dan samping)."],
                "Bangun datar mencakup segitiga, segiempat, dan segi banyak\nBangun ruang mencakup kubus, balok, "
                "dan gabungannya"),
            content(2, "Geometri dan Pengukuran", "Pengukuran", [
                "Panjang benda menggunakan satuan baku;",
                "Hubungan antar-satuan baku panjang (mm, dm, cm, m, dam, hm, km);",
                "Volume benda menggunakan satuan baku;",
                "Hubungan antar-satuan baku volume (ml, dl, cl, l, dal, hl, kl);",
                "Berat benda menggunakan satuan baku;",
                "Hubungan antar-satuan baku berat (mg, dg, cg, g, dag, hg, kg);",
                "Waktu;",
                "Hubungan antar-satuan waktu (detik, menit, jam, hari, pekan, bulan, tahun);",
                "Laju perubahan (kecepatan);",
                "Keliling dan luas bangun datar (segitiga, segiempat, dan segi banyak);",
                "Volume bangun ruang (kubus, balok, dan gabungannya);",
                "Besar sudut;",
                "Penaksiran ukuran."]),
            content(3, "Data", "Penyajian dan Penggunaan Data", [
                "Penyajian data (gambar, piktogram, diagram batang, dan tabel frekuensi);",
                "Pengambilan informasi dan penggunaan data."]),
        ],
    },
}

MAT_SMP = {
    "level": "SMP/MTs/sederajat", "subject": "Matematika", "pages": [18, 25],
    "intro": "Sebagaimana TKA Matematika SD/MI/sederajat, TKA Matematika SMP/MTs/sederajat juga mengukur kemampuan "
             "murid dalam memahami fakta, konsep, prinsip, dan prosedur matematika, serta kemampuan mereka dalam "
             "menerapkan pengetahuan matematika untuk menyelesaikan masalah (problem solving).",
    "muatan": {
        "intro": "Muatan TKA Matematika SMP/MTs/sederajat merujuk pada elemen kurikulum atau materi matematika yang "
                 "dipelajari murid yang ada pada Kurikulum 2013 dan Kurikulum Merdeka. Elemen ini meliputi:",
        "elements": ["bilangan,", "aljabar,", "geometri dan pengukuran, serta", "data dan peluang."],
        "notes": ["Penggunaan logika matematika diintegrasikan langsung dengan elemen matematika yang tertera dalam "
                  "kurikulum.",
                  "Pengetahuan matematika diukur melalui permasalahan dalam konteks matematika dan permasalahan "
                  "dalam konteks keseharian yang dapat meliputi kejadian atau situasi di lingkup personal, "
                  "keluarga, atau lingkungan sekitar yang bersifat lokal."],
    },
    "kompetensi": {
        "intro": "Tes Kemampuan Akademik (TKA) Matematika SMP/MTs/sederajat mengukur kemampuan matematis sebagai "
                 "berikut:",
        "abilities": ["pengetahuan matematika,", "representasi matematis,",
                      "penalaran dan penggunaan logika matematis,", "pemecahan masalah matematis, dan",
                      "koneksi matematis."],
        "cognitive_intro": COGNITIVE_INTRO,
        "cognitive_levels": levels(
            [("Menghitung", "Melakukan perhitungan berdasarkan prosedur yang mencakup operasi hitung aritmatika "
              "(+, -, ×, ÷, atau kombinasinya), operasi aljabar, atau operasi matematika lainnya."),
             ("Memahami informasi", "Memahami informasi dari grafik fungsi, tabel, diagram, infografis, atau "
              "bentuk visual lainnya."),
             ("Mengelompokkan", "Mengelompokkan objek berdasarkan fakta, konsep, dan prinsip matematika dalam "
              "cakupan sub-elemen."),
             ("Mengidentifikasi", "Melakukan identifikasi terhadap objek menggunakan konsep, fakta, dan prinsip "
              "matematika dalam cakupan sub-elemen.")],
            [("Memodelkan", "Memodelkan permasalahan kontekstual terkait cakupan sub-elemen ke dalam kalimat "
              "matematika."),
             ("Mengaplikasikan", "Mengaplikasikan strategi dan operasi matematika (berupa operasi hitung, operasi "
              "aljabar, atau bentuk operasi lainnya) untuk menyelesaikan permasalahan yang melibatkan konsep dan "
              "prosedur matematis yang familiar dan rutin."),
             ("Menginterpretasikan", "Memahami dan menjelaskan makna dari berbagai situasi, kejadian, pernyataan, "
              "representasi, atau masalah matematika.")],
            [("Menganalisis", "Menentukan, menjelaskan, dan menggunakan hubungan beberapa konsep, fakta, prinsip, "
              "atau prosedur matematika dalam cakupan sub-elemen."),
             ("Memecahkan masalah", "Mengaitkan beberapa konsep, fakta, prinsip, prosedur, dan representasi "
              "matematika dalam cakupan sub-elemen, untuk menyelesaikan permasalahan dalam situasi baru atau "
              "konteks yang tidak rutin."),
             ("Mengevaluasi", "Mengevaluasi alternatif strategi dan solusi dari suatu pemecahan masalah."),
             ("Menyimpulkan", "Menarik kesimpulan yang valid dari informasi, data, atau bukti yang diberikan "
              "menggunakan konsep, fakta, prinsip, dan prosedur matematika dalam cakupan sub-elemen."),
             ("Melakukan generalisasi", "Menyusun pernyataan matematis yang menggambarkan hubungan yang lebih umum "
              "terkait konsep, fakta, prinsip, dan prosedur dalam cakupan sub-elemen")]),
        "content_intro": "Muatan dan kompetensi yang diukur dalam TKA Matematika SMP/MTs/sederajat dirangkum dalam "
                         "tabel berikut:",
        "content": [
            content(1, "Bilangan", "Bilangan Real", [
                "Perbandingan dan sifat-sifat bilangan;",
                "Operasi aritmetika pada bilangan;",
                "Estimasi/perkiraan hasil perhitungan;",
                "Faktorisasi prima bilangan asli;",
                "Rasio (skala, proporsi, dan laju perubahan);",
                "Perbandingan senilai dan berbalik nilai."],
                "Bilangan mencakup bilangan bulat, bilangan rasional dan irasional, bilangan berpangkat bulat, "
                "bilangan akar, dan bilangan dalam notasi ilmiah"),
            content(2, "Aljabar", "Persamaan dan Pertidaksamaan Linier", [
                "Persamaan linear satu variabel;",
                "Pertidaksamaan linear satu variabel;",
                "Sistem persamaan linear dua variabel."]),
            content(2, "Aljabar", "Bentuk Aljabar", [
                "Bentuk aljabar dan sifat-sifat operasinya (komutatif, asosiatif, dan distributif)."]),
            content(2, "Aljabar", "Fungsi", [
                "Relasi dan fungsi (domain, kodomain, range), serta penyajiannya."]),
            content(2, "Aljabar", "Barisan dan Deret", [
                "Barisan berhingga bilangan;",
                "Deret berhingga bilangan."]),
            content(3, "Geometri dan Pengukuran", "Objek Geometri", [
                "Hubungan antar-sudut yang terbentuk oleh dua garis yang berpotongan, dan oleh dua garis sejajar "
                "yang dipotong suatu garis transversal (termasuk penentuan besar sudut dalam segitiga);",
                "Teorema Pythagoras.",
                "Kekongruenan dan kesebangunan bangun datar;",
                "Jaring-jaring bangun ruang (prisma, tabung, limas dan kerucut)."]),
            content(3, "Geometri dan Pengukuran", "Transformasi Geometri", [
                "Transformasi tunggal (refleksi, translasi, rotasi, dan dilatasi) terhadap titik, garis, dan bangun "
                "datar pada bidang."]),
            content(3, "Geometri dan Pengukuran", "Pengukuran", [
                "Keliling dan luas bangun datar (daerah segi banyak dan daerah lingkaran, serta daerah "
                "gabungannya);",
                "Volume bangun ruang (prisma, limas, dan bola)."]),
            content(4, "Data dan Peluang", "Data", [
                "Perumusan pertanyaan untuk mendapatkan data, serta penyajian, dan peginterpretasian data;",
                "Penentuan dan penaksiran rerata (mean), median, modus, dan jangkauan (range) dari data;",
                "Perbandingan ukuran pemusatan dan ukuran penyebaran beberapa kelompok data."],
                "Penyajian data meliputi: diagram batang, diagram garis, diagram lingkaran, dan tabel"),
            content(4, "Data dan Peluang", "Peluang", [
                "Peluang dan frekuensi relatif dari kejadian tunggal."]),
        ],
    },
}

FRAMEWORKS = [BI_SD, MAT_SD, BI_SMP, MAT_SMP]

# ------------------------------------------------------------------ 56: subjects per level, schedule, scores

ELECTIVES = ["Matematika lanjutan", "Bahasa Indonesia lanjutan", "Bahasa Inggris lanjutan", "Fisika", "Kimia",
             "Biologi", "Ekonomi", "Sosiologi", "Geografi", "Sejarah", "Antropologi", "PPKn/Pendidikan Pancasila",
             "Bahasa Arab", "Bahasa Jerman", "Bahasa Prancis", "Bahasa Jepang", "Bahasa Korea", "Bahasa Mandarin",
             "Produk/Projek Kreatif dan Kewirausahaan", "Teori Kompetensi Kejuruan (Program Keahlian)"]
LEVELS = [
    {"level": "SD/MI/sederajat", "grades": [6], "subjects": ["bahasa Indonesia", "matematika"], "framework": True},
    {"level": "SMP/MTs/sederajat", "grades": [9], "subjects": ["bahasa Indonesia", "matematika"], "framework": True},
    {"level": "SMA/MA/sederajat", "grades": [12], "subjects": ["bahasa Indonesia", "matematika", "bahasa Inggris"],
     "electives": {"choose": 2, "options": list(range(1, 20))}, "framework": False},
    {"level": "SMK/MAK", "grades": [12, 13], "subjects": ["bahasa Indonesia", "matematika", "bahasa Inggris"],
     "electives": {"choose": 2, "options": list(range(1, 21)),
                   "note": "Mata pelajaran pilihan Teori Kompetensi Kejuruan pada angka (20) untuk jenjang SMK/MAK "
                           "sesuai program keahlian pada masing-masing peserta."},
     "framework": False},
]
LEVELS_NOTE = ("Kelas 13 is SMK program 4 (empat) tahun. Kerangka asesmen in this set covers SD/MI/sederajat and "
               "SMP/MTs/sederajat only (Perka BSKAP 047/H/AN/2025).")

# Session times as printed (WIB, WITA, WIT); "–" and "-" as printed are normalised to "-".
SD_SMP_SESSIONS = [("07.00-08.45", "08.00-09.45", "09.00-10.45"), ("09.15-11.00", "10.15-12.00", "11.15-13.00"),
                   ("11.30-13.15", "12.30-14.15", "13.30-15.15"), ("13.45-15.30", "14.45-16.30", "15.45-17.30")]
SMA_I = [("07.00-08.30", "08.00-09.30", "09.00-10.30"), ("09.00-10.30", "10.00-11.30", "11.00-12.30"),
         ("11.00-12.30", "12.00-13.30", "13.00-14.30"), ("13.00-14.30", "14.00-15.30", "15.00-16.30")]
SMA_II_III = [("07.00-08.20", "08.00-09.20", "09.00-10.20"), ("09.00-10.20", "10.00-11.20", "11.00-12.20"),
              ("11.00-12.20", "12.00-13.20", "13.00-14.20"), ("13.00-14.20", "14.00-15.20", "15.00-16.20")]
SMA_IV = [("07.00-08.50", "08.00-09.50", "09.00-10.50"), ("09.30-11.20", "10.30-12.20", "11.30-13.20"),
          ("12.00-13.50", "13.00-14.50", "13.00-15.50"), ("14.30-16.20", "15.30-17.20", "16.30-18.20")]
ERRATA.append(("56", 48, "13.00-15.50", "SMA/SMK day IV session 3 WIT printed '13.00 - 15.50'; WIB 12.00–13.50 and "
               "WITA 13.00–14.50 give WIT 14.00–15.50"))


def day(n, label, tests, sessions):
    return {"day": n, "label": label, "tests": [{"name": t, "minutes": m} for t, m in tests],
            "sessions": [{"session": i + 1, "wib": a, "wita": b, "wit": c} for i, (a, b, c) in enumerate(sessions)]}


SCHEDULE = [
    {"levels": ["SD/MI/sederajat"], "days": [
        day(1, "I", [("Latihan", 10), ("Matematika dan Numerasi", 75), ("Survei Karakter", 20)], SD_SMP_SESSIONS),
        day(2, "II", [("Latihan", 10), ("Bahasa Indonesia dan Literasi Membaca", 75),
                      ("Survei Lingkungan Belajar", 20)], SD_SMP_SESSIONS)]},
    {"levels": ["SMP/MTs/sederajat"], "days": [
        day(1, "I", [("Latihan", 10), ("Matematika dan Numerasi", 75), ("Survei Karakter", 20)], SD_SMP_SESSIONS),
        day(2, "II", [("Latihan", 10), ("Bahasa Indonesia dan Literasi", 75), ("Survei Lingkungan Belajar", 20)],
            SD_SMP_SESSIONS)]},
    {"levels": ["SMA/MA/sederajat", "SMK/MAK"], "days": [
        day(1, "I", [("Latihan", 10), ("Bahasa Indonesia dan Literasi Membaca", 60), ("Survei Karakter", 20)],
            SMA_I),
        day(2, "II", [("Latihan", 10), ("Bahasa Inggris", 50), ("Survei Lingkungan Belajar", 20)], SMA_II_III),
        day(3, "III", [("Latihan", 10), ("Matematika dan Numerasi", 70)], SMA_II_III),
        day(4, "IV", [("Latihan", 10), ("Mata Pelajaran Pilihan Pertama", 50), ("Mata Pelajaran Pilihan Kedua", 50)],
            SMA_IV)]},
]
SCHEDULE_NOTES = [
    "TKA dan AN dilaksanakan selama 4 (empat) hari untuk SMA/MA/sederajat dan SMK/MAK; dan 2 (dua) hari untuk "
    "jenjang SD/MI/sederajat dan SMP/MTs/sederajat;",
    "Survei Lingkungan Belajar untuk pendidik dan kepala satuan pendidikan dilaksanakan selama 4 (empat) minggu;",
    "Penggabungan soal numerasi AN juga dilakukan pada mata uji Matematika pada jenjang SD/MI/sederajat dan "
    "SMP/MTs/sederajat dan Matematika Wajib pada jenjang SMA/MA/sederajat dan SMK/MAK.",
]

SCORING = {
    "ranges": [
        {"levels": ["SD/MI/sederajat", "SMP/MTs/sederajat"], "min": 0, "max": 100, "decimals": 2,
         "istimewa_from": 95.00},
        {"levels": ["SMA/MA/sederajat", "SMK/MAK"], "min": 200, "max": 800, "decimals": 2, "istimewa_from": 725.00},
    ],
    "categories": ["Baik", "Memadai", "Kurang"],
    "texts": [
        "Hasil TKA untuk jenjang SD/MI/sederajat dan SMP/MTs/sederajat dilaporkan dalam rentang nilai 0 (nol) sampai "
        "dengan 100 (seratus) dengan pembulatan 2 (dua) angka di belakang koma.",
        "Hasil TKA untuk jenjang SMA/MA/sederajat dan SMK/MAK dilaporkan dalam rentang nilai 200 (dua ratus) sampai "
        "dengan 800 (delapan ratus) dengan pembulatan 2 (dua) angka di belakang koma.",
        "Kategori capaian hasil TKA merupakan pengelompokan nilai yang dicapai dalam setiap mata pelajaran.",
        "Predikat istimewa diperuntukkan peserta jenjang SD/MI/sederajat dan SMP/MTs/sederajat yang mendapatkan "
        "nilai 95,00 atau lebih di masing-masing mata uji.",
        "Predikat istimewa diperuntukkan peserta jenjang SMA/MA/sederajat dan SMK/MAK yang mendapatkan nilai 725,00 "
        "atau lebih di masing-masing mata uji.",
    ],
    "note": "Kepmendikdasmen 56/2026 names the categories without cut scores.",
}

# ------------------------------------------------------------------ checks against the PDFs


def norm(t):
    return re.sub(r"[^a-z0-9]", "", t.lower())


def pdf_pages(path):
    out = subprocess.run(["pdftotext", path, "-"], capture_output=True, text=True, check=True).stdout
    return out.split("\f")


def table_cells(path, pages):
    import pdfplumber
    cells = {}
    with pdfplumber.open(path) as pdf:
        for p in pages:
            cells[p] = [c for t in pdf.pages[p - 1].extract_tables() for r in t for c in r if c and c.strip()]
    return cells


def units(obj):
    """Every string in obj, split into sentences / items as they appear in the PDF."""
    if isinstance(obj, str):
        for part in obj.split("\n"):
            if part.strip():
                yield part
    elif isinstance(obj, dict):
        for k, v in obj.items():
            if k not in ("key", "level", "levels", "subject", "name_en") or isinstance(v, (list, dict)):
                yield from units(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from units(v)


def check(src, out):
    pdf047 = os.path.join(src, P047)
    pages = pdf_pages(pdf047)
    corpus047 = norm(" ".join(pages[6:25]))  # PDF p. 7–25 (parts II and III)
    cells = table_cells(pdf047, range(9, 26))
    corpus047 += "|" + "|".join(norm(c) for p in cells for c in cells[p])
    bad = []
    for u in units([ITEM_TYPES, ITEM_FORMS, FORMS_INTRO, FRAMEWORKS]):
        if norm(u) and norm(u) not in corpus047:
            bad.append(u)
    # every table cell must be covered by the transcription
    ours = norm(" ".join(units(FRAMEWORKS)) + " Kompetensi Subkompetensi No Level Proses Berpikir Deskripsi "
                "Elemen Materi Sub-elemen Submateri Batasan Catatan Knowing and Understanding Applying Reasoning")
    missing = [c for p in cells for c in cells[p] if norm(c) not in ours and not re.fullmatch(r"[\d.]+", c.strip())]
    pages56 = pdf_pages(os.path.join(src, P56))
    corpus56 = norm(" ".join(pages56))
    for u in units([ELECTIVES, [lv["subjects"] for lv in LEVELS], LEVELS[3]["electives"]["note"], SCHEDULE_NOTES,
                    SCORING["texts"], SCORING["categories"],
                    [t["name"] for s in SCHEDULE for d in s["days"] for t in d["tests"]]]):
        if norm(u) not in corpus56:
            bad.append(u)
    sched = norm(" ".join(pages56[46:48]))  # PDF p. 47–48 (printed - 44 -, - 45 -)
    for s in SCHEDULE:
        for d in s["days"]:
            for t in d["tests"]:
                if norm(f"{t['minutes']} menit") not in sched:
                    bad.append(f"{t['name']} {t['minutes']} menit")
            for x in d["sessions"]:
                for v in (x["wib"], x["wita"], x["wit"]):
                    a, b = v.split("-")
                    if a not in pages56[46] + pages56[47] or b not in pages56[46] + pages56[47]:
                        bad.append(v)
    for doc, page, printed, why in ERRATA:
        if norm(printed) not in norm(json.dumps(out, ensure_ascii=False)):
            bad.append(f"erratum not in the data: {printed}")
    if bad or missing:
        for b in bad:
            print("not in the PDF:", b[:140])
        for m in missing:
            print("table cell not transcribed:", m.replace("\n", " ")[:140])
        sys.exit(1)


def main(src, out_dir):
    data = {
        "source": {"framework": f"{REF047} (PDF p. 7–25)", "administration": f"{REF56} (BAB IV, PDF p. 31–32; BAB VIII, p. 47–48; BAB X, p. 52–53)"},
        "item_types": ITEM_TYPES, "item_forms_intro": FORMS_INTRO, "item_forms": ITEM_FORMS,
        "levels": LEVELS, "levels_note": LEVELS_NOTE,
        "electives": [{"no": i + 1, "label": e} for i, e in enumerate(ELECTIVES)],
        "frameworks": FRAMEWORKS,
        "schedule": SCHEDULE, "schedule_notes": SCHEDULE_NOTES,
        "scoring": SCORING,
        "errata": [{"source": REF047 if d == "047" else REF56, "page": p, "printed": t, "reason": w}
                   for d, p, t, w in ERRATA],
    }
    check(src, data)
    os.makedirs(os.path.join(out_dir, "kerangka-tka"), exist_ok=True)
    with open(os.path.join(out_dir, "kerangka-tka", "kerangka-tka.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
        f.write("\n")
    n_sub = sum(len(c["subcompetencies"]) for fw in FRAMEWORKS if fw["subject"] == "Bahasa Indonesia"
                for c in fw["kompetensi"]["competencies"])
    n_scope = sum(len(c["scope"]) for fw in FRAMEWORKS if fw["subject"] == "Matematika"
                  for c in fw["kompetensi"]["content"])
    n_proc = sum(len(lv["processes"]) for fw in FRAMEWORKS if fw["subject"] == "Matematika"
                 for lv in fw["kompetensi"]["cognitive_levels"])
    print(f"kerangka-tka: {len(FRAMEWORKS)} frameworks, {n_sub} subcompetencies, {n_scope} content items, "
          f"{n_proc} thinking processes, {len(ELECTIVES)} electives, {len(ERRATA)} errata")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
