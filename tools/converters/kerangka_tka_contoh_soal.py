"""Sample questions of Perka BSKAP 047/H/AN/2025, Lampiran part IV (PDF p. 25–46), for kerangka-tka.py.

Transcribed as printed. Text in the PDF's text layer is checked by kerangka-tka.py; formulas (fractions,
powers, the equation system) and the texts inside images were read on the page images. Math is written in TeX
between $…$. Figures are cut from the page renders (FIGURES) and stored next to kerangka-tka.json.
"""

# name: (page, x0, top, x1, bottom) in PDF points; photos are stored as JPEG, drawings as PNG
FIGURES = {
    "sd-bi-1-teks": (25, 135, 473, 561, 775),
    "sd-bi-5-a": (29, 166, 77, 278, 294), "sd-bi-5-b": (29, 166, 306, 278, 549),
    "sd-bi-5-c": (29, 166, 559, 275, 762), "sd-bi-5-d": (30, 166, 77, 277, 318),
    "sd-mtk-4-dadu": (33, 297, 596, 378, 680),
    "sd-mtk-6-diagram": (35, 150, 72, 524, 298),
    "smp-bi-1-ulasan-1": (36, 136, 221, 562, 521), "smp-bi-1-ulasan-2": (36, 136, 563, 562, 795),
    "smp-bi-4-puisi": (39, 148, 104, 525, 584),
    "smp-mtk-4-jembatan": (43, 201, 711, 473, 853), "smp-mtk-4-sketsa": (44, 257, 126, 418, 285),
    "smp-mtk-5-rumah": (45, 232, 72, 442, 240),
}
PHOTOS = {"sd-bi-1-teks", "smp-bi-1-ulasan-1", "smp-bi-4-puisi", "smp-mtk-4-jembatan"}


def fig(name):
    return "contoh-soal/" + name + (".jpg" if name in PHOTOS else ".png")


SCOPE = "Memahami, mengaplikasikan, dan bernalar yang lebih tinggi untuk menyelesaikan permasalahan terkait "
MCMA = "Pilihlah jawaban yang benar! Jawaban benar lebih dari satu."

# Texts (stimuli) shared by a group of questions. `text_from_image`: the text is printed inside the image and was
# transcribed from it.
STIMULI = [
    {"id": "sd-bi-a", "level": "SD/MI/sederajat", "subject": "Bahasa Indonesia", "questions": [1, 2, 3],
     "lead": "Teks untuk soal nomor 1 s.d. 3!", "page": 25, "figures": [fig("sd-bi-1-teks")],
     "title": "Danau untuk Semua", "text_from_image": True,
     "attribution": {"credit": "Perka BSKAP 047/H/AN/2025, Lampiran, Contoh Soal (p. 25)",
                     "note": "No author is printed; credit the regulation."},
     "text": [
         "Di hutan ada sebuah danau tempat semua binatang minum. Suatu pagi, air danau menjadi kotor karena Rino si "
         "badak berendam di dalamnya. Binatang-binatang lain jadi tidak bisa minum. Namun, mereka takut menegur Rino "
         "karena badannya besar dan bercula. Mereka diam seribu bahasa. Rino malah merasa bangga karena jadi pusat "
         "perhatian.",
         "Esoknya, Rino masih berendam. Binatang-binatang makin kehausan.",
         "“Aduh, bagaimana ini?” ujar Bani si kelinci. Hewan lain juga mulai gelisah.",
         "Binatang-binatang hutan pun berkumpul dan bermusyawarah. Hari si harimau mengusulkan agar meminta bantuan "
         "Ucil si kancil.",
         "“Setuju!!” semua binatang berteriak antusias.",
         "Ucil menemui Rino.",
         "“Selamat siang. Maaf mengganggu Tuan. Ada kabar penting,” kata Ucil dengan lembut.",
         "Rino segera bangun. Ia merasa tersanjung dengan ucapan Ucil.",
         "“Kabar penting? Cepat bicara!” kata Rino.",
         "“Hamba kasihan kepada Tuan. Badan besar berendam di danau kecil. Tidak pantas, Tuan. Oh ya, ada makhluk "
         "yang menutup jalan air supaya tidak mengalir. Sayang, makhluk itu tidak kelihatan oleh mata kita, dia "
         "makhluk gaib,” lanjut Ucil.",
         "Rino mengerutkan dahinya.",
         "“Percayalah, Tuan,” bujuk Ucil.",
         "Rino segera berjalan menuju pohon nangka. Ia pun mengawasi pohon itu selama setengah hari. Sementara itu, "
         "binatang yang lain bergantian datang untuk minum air danau.",
         "Rino selesai mengawasi pohon nangka. Ia kembali menuju danau. Sementara, binatang lainnya sudah "
         "meninggalkan danau. Mereka sudah tidak haus lagi."]},
    {"id": "sd-bi-b", "level": "SD/MI/sederajat", "subject": "Bahasa Indonesia", "questions": [4, 5, 6],
     "lead": "Teks untuk soal nomor 4 s.d. 6!", "page": 27, "figures": [],
     "title": "Hewan Pemakan Daun, Apa Itu?", "text_from_image": False,
     "attribution": {"credit": "Majalah Bobo (bobo.grid.id), adapted (\"dengan penyesuaian\") in Perka BSKAP "
                               "047/H/AN/2025, Lampiran, Contoh Soal (p. 27–28)",
                     "owner": "Bobo (bobo.grid.id)",
                     "url": "http://bobo.grid.id/read/084266052/bukan-herbivora-inilah-sebutan-untuk-hewan-pemakan-"
                            "daun-tanaman?page=all"},
     "text": [
         "Hewan bisa dibagi menjadi tiga kelompok berdasarkan makanan mereka. Karnivora, hewan pemakan daging. "
         "Contoh hewan karnivora adalah singa. Selanjutnya herbivora, yaitu hewan pemakan tumbuhan. Sapi adalah "
         "contoh hewan herbivora. Terakhir, hewan omnivora, yaitu hewan pemakan daging dan tumbuhan, seperti beruang.",
         "Dari kelompok herbivora, ada hewan yang hanya makan daun saja. Mereka disebut folivora. Hewan folivora hanya "
         "makan daun untuk hidup. Namun, daun itu susah untuk dicerna, apalagi kalau sudah tua. Kadang-kadang daun "
         "juga mengandung zat yang bisa berbahaya.",
         "Agar bisa mencerna daun, tubuh hewan folivora punya cara khusus. Mereka punya usus yang panjang agar "
         "makanan bisa diproses lebih lama. Tubuh hewan folivora bekerja lebih lambat, jadi tidak terlalu banyak "
         "bergerak. Di dalam perut hewan folivora juga ada bakteri baik yang membantu mencerna daun. Beberapa hewan "
         "folivora lebih suka daun muda karena lebih lembut dan mudah dimakan.",
         "Ada beberapa contoh hewan folivora yang hidup di alam. Misalnya, panda yang makan daun bambu. Ada juga koala "
         "yang makan daun eukaliptus. Mereka tinggal di hutan dan sangat bergantung pada daun untuk makan. Karena "
         "itu, hutan tempat mereka tinggal harus dijaga supaya mereka bisa terus hidup."],
     "source": "Sumber: http://bobo.grid.id/read/084266052/bukan-herbivora-inilah-sebutan-untuk-hewan-pemakan-daun-"
               "tanaman?page=all (dengan penyesuaian)"},
    {"id": "smp-bi-a", "level": "SMP/MTs/sederajat", "subject": "Bahasa Indonesia", "questions": [1, 2, 3],
     "lead": "Teks untuk soal nomor 1 s.d. 3!", "page": 36,
     "figures": [fig("smp-bi-1-ulasan-1"), fig("smp-bi-1-ulasan-2")], "text_from_image": True,
     "parts": [
         {"label": "Teks Ulasan 1", "title": "Pantai Glagah",
          "attribution": {"credit": "Website screenshot printed in Perka BSKAP 047/H/AN/2025, Lampiran, Contoh Soal "
                                    "(p. 36); byline 'Admin'", "note": "The site name is not shown; credit the "
                                    "regulation."}, "text": [
             "Pantai Glagah di Kulon Progo adalah salah satu pantai unik di selatan Yogyakarta. Pasir hitamnya memberi "
             "kesan eksotis yang berbeda dari pantai lainnya. Ombak besar yang menerjang pemecah gelombang "
             "menciptakan suasana alam yang menakjubkan. Di sisi timur, terdapat laguna tenang yang cocok untuk "
             "wisata keluarga, terutama anak-anak.",
             "Akses menuju pantai ini cukup mudah dari pusat Kota Yogyakarta. Fasilitasnya lengkap, seperti area "
             "parkir luas, warung makan, dan tempat duduk untuk bersantai. Ketika senja tiba, suasana menjadi lebih "
             "indah dengan langit yang memerah dan matahari terbenam perlahan di cakrawala.",
             "Namun, pengunjung tidak disarankan berenang karena ombaknya cukup ganas. Beberapa sudut pantai juga "
             "terlihat kurang bersih. Meski begitu, Pantai Glagah tetap menjadi tempat menenangkan diri."]},
         {"label": "Teks Ulasan 2", "title": "Pantai Drini, Gunung Kidul",
          "byline": "Noordin Ahya - WartaKU, Senin, 23 April 2025 11:04 WIB",
          "attribution": {"credit": "Noordin Ahya, WartaKU (23 April 2025), website screenshot printed in Perka BSKAP "
                                    "047/H/AN/2025, Lampiran, Contoh Soal (p. 36)", "owner": "Noordin Ahya / WartaKU"},
          "text": [
             "Pantai Drini di Gunung Kidul tuh beneran hidden gem yang wajib masuk bucket list liburan kamu! Nggak "
             "cuma karena pasir putih dan air lautnya yang bening banget, tapi juga karena pulau karang kecil yang "
             "unik. Pulau itu seperti pemisah dua dunia—satu sisi ombaknya tenang, sisi lainnya agak liar. Serasa "
             "lagi liat dua kepribadian alam yang beda tapi tetap satu kesatuan.",
             "Yang bikin makin seru, kamu bisa jalan kaki ke pulau karangnya pas air laut surut. View dari atas cakep "
             "banget buat foto, apalagi pas golden hour. Banyak banget sudut estetis yang bisa kamu eksplor.",
             "Fasilitas di sini juga udah lumayan oke. Ada warung makan, parkiran luas, dan tempat duduk buat santai-"
             "santai. Pantai Drini tuh ibarat tempat nongkrongnya laut dan langit—sederhana, tapi punya vibes yang "
             "nggak bisa dibeli. Sekali datang, rasanya pengen balik lagi buat nyari tenang dalam riuhnya dunia."]}]},
    {"id": "smp-bi-b", "level": "SMP/MTs/sederajat", "subject": "Bahasa Indonesia", "questions": [4, 5, 6],
     "lead": "Teks untuk soal nomor 4 s.d. 6!", "page": 39, "figures": [fig("smp-bi-4-puisi")],
     "title": "Perempuan-Perempuan Perkasa", "text_from_image": True, "poem": True,
     "attribution": {"credit": "Hartojo Andangdjaja, \"Perempuan-Perempuan Perkasa\", as printed in Perka BSKAP "
                               "047/H/AN/2025, Lampiran, Contoh Soal (p. 39)", "owner": "Hartojo Andangdjaja"},
     "text": [
         "Perempuan-perempuan yang membawa bakul di pagi buta,\ndari manakah mereka\nKe stasiun kereta mereka datang "
         "dari bukit-bukit desa\nsebelum peluit kereta pagi terjaga\nsebelum hari bermula dalam pesta kerja",
         "Perempuan-perempuan yang membawa bakul dalam kereta,\nke manakah mereka\nDi atas roda-roda baja mereka "
         "berkendara\nMereka berlomba dengan surya menuju ke gerbang kota\nmerebut hidup di pasar-pasar kota",
         "Perempuan-perempuan yang membawa bakul di pagi buta,\nsiapakah mereka\nMereka ialah ibu-ibu yang perkasa\n"
         "akar-akar yang melata dari tanah perbukitan turun ke kota\nMereka: cinta kasih yang bergerak menghidupi "
         "desa demi desa"],
     "source": "(Puisi karya Hartojo Andangdjaja)"},
]


def bi(level, no, page, komp, sub, form, question, key, stimulus, options=None, statements=None,
       responses=None, form_note=None):
    q = {"level": level, "subject": "Bahasa Indonesia", "no": no, "page": page, "stimulus": stimulus,
         "kompetensi": komp, "subkompetensi": sub, "bentuk_soal": form, "jenis_soal": "Grup", "question": question}
    return fill(q, form, key, options, statements, responses, form_note)


def mtk(level, no, page, element, sub, scope, cog, form, question, key, options=None, statements=None,
        responses=None, figures=None):
    q = {"level": level, "subject": "Matematika", "no": no, "page": page, "elemen": element, "sub_elemen": sub,
         "kompetensi": SCOPE + scope, "level_kognitif": cog, "bentuk_soal": form, "question": question}
    if figures:
        q["figures"] = [fig(f) for f in figures]
    return fill(q, form, key, options, statements, responses)


def fill(q, form, key, options, statements, responses, form_note=None):
    kind = {"Pilihan Ganda": "pg", "PGK MCMA": "pgk_mcma", "PGK Kategori": "pgk_kategori"}[form]
    if form_note:  # printed label contradicts the item's build; see ERRATA
        kind = form_note
    q["item_form"] = kind
    if kind == "pg":
        q["options"] = [dict({"label": "ABCD"[i]}, **(t if isinstance(t, dict) else {"text": t}))
                        for i, t in enumerate(options)]
        q["key"] = key
    elif kind == "pgk_mcma":
        q["options"] = [{"no": i + 1, "text": t} for i, t in enumerate(options)]
        q["key"] = key
    else:
        q["responses"] = responses
        q["statements"] = statements
        q["key"] = key
    q["key_printed"] = {"pg": lambda k: k, "pgk_mcma": lambda k: " dan ".join(f"Pernyataan {n}" for n in k),
                        "pgk_kategori": lambda k: ", ".join(k)}[kind](key)
    return q


SD, SMP = "SD/MI/sederajat", "SMP/MTs/sederajat"
BS, SS, ST = ["Benar", "Salah"], ["Sesuai", "Tidak Sesuai"], ["Setuju", "Tidak Setuju"]

QUESTIONS = [
    # ---------------------------------------------------------------- SD Bahasa Indonesia
    bi(SD, 1, 26, "Pemahaman Tekstual", "Mengidentifikasi informasi tersurat dalam teks", "Pilihan Ganda",
       ["Siapa yang memiliki usul untuk meminta bantuan hewan yang cerdik?"], "D", "sd-bi-a",
       options=["Bani.", "Ucil.", "Rino.", "Hari."]),
    bi(SD, 2, 26, "Pemahaman Inferensial", "Menjelaskan makna ungkapan yang digunakan dalam teks", "PGK Kategori",
       ["“Mereka diam seribu bahasa.”", "Apa arti “diam seribu bahasa” pada teks fabel tersebut?"], "B", "sd-bi-a",
       options=["Para binatang di hutan tidak mampu melakukan sesuatu.",
                "Semua binatang di hutan menahan untuk tidak berkomentar.",
                "Penghuni hutan tidak mau mendengarkan pendapat orang lain.",
                "Binatang-binatang di hutan tidak mengetahui masalah yang terjadi."], form_note="pg"),
    bi(SD, 3, 27, "Evaluasi dan Apresiasi", "Menilai relevansi peristiwa dalam teks dengan kehidupan sehari-hari "
       "berdasarkan pengalaman atau pengetahuan pribadi", "PGK Kategori",
       ["Apa contoh peristiwa yang dapat ditemukan dalam kehidupan sehari-hari berdasarkan kejadian yang dialami "
        "Ucil pada cerita tersebut?", "Tentukan Sesuai atau Tidak Sesuai untuk setiap pernyataan berikut!"],
       ["Tidak Sesuai", "Sesuai", "Sesuai"], "sd-bi-a", responses=SS,
       statements=["Tita memberi ide cemerlang yang dapat dilakukan oleh teman-teman di kelas.",
                   "Jani menghargai kepercayaan yang diberikan teman-teman sekelas kepada dirinya.",
                   "Nina bertanggung jawab dalam menjalankan tugas yang dipercayakan kepadanya."]),
    bi(SD, 4, 28, "Pemahaman Tekstual", "Mengidentifikasi informasi tersurat dalam teks", "PGK MCMA",
       ["Apa saja contoh hewan folivora berdasarkan informasi tersebut?", MCMA], [2, 3], "sd-bi-b",
       options=["Sapi.", "Koala.", "Panda."]),
    bi(SD, 5, 28, "Pemahaman Tekstual", "Menyusun kembali informasi dari teks dalam bentuk ikhtisar/bagan",
       "Pilihan Ganda", ["Bagan mana yang sesuai untuk menggambarkan informasi pada teks tersebut?"], "D", "sd-bi-b",
       options=[{"figure": fig("sd-bi-5-a"), "text_from_image": "Tiga Kelompok Utama Hewan Folivora → Pengertian "
                 "Hewan Folivora → Contoh Hewan Folivora → Cara Hewan Folivora Mencerna Daun"},
                {"figure": fig("sd-bi-5-b"), "text_from_image": "Tiga Kelompok Utama Hewan Folivora → Contoh Hewan "
                 "Folivora → Pengertian Hewan Folivora → Cara Hewan Folivora Mencerna Daun"},
                {"figure": fig("sd-bi-5-c"), "text_from_image": "Tiga Kelompok Utama Hewan → Contoh Hewan Folivora "
                 "→ Pengertian Hewan Folivora → Cara Hewan Folivora Mencerna Daun"},
                {"figure": fig("sd-bi-5-d"), "text_from_image": "Tiga Kelompok Utama Hewan → Pengertian Hewan "
                 "Folivora → Cara Hewan Folivora Mencerna Daun → Contoh Hewan Folivora"}]),
    bi(SD, 6, 30, "Pemahaman Inferensial", "Menyimpulkan ide pokok, gagasan pendukung, amanat, tokoh, peristiwa, "
       "dan/atau nilai-nilai dalam teks", "Pilihan Ganda",
       ["Apa gagasan utama yang disampaikan pada paragraf ketiga teks tersebut?"], "C", "sd-bi-b",
       options=["Jenis daun yang cocok untuk hewan folivora.", "Pembagian hewan berdasarkan makanan mereka.",
                "Cara khusus tubuh hewan folivora mencerna daun.",
                "Peranan penting hutan bagi kehidupan hewan folivora."]),
    # ---------------------------------------------------------------- SD Matematika
    mtk(SD, 1, 31, "Bilangan", "Bilangan Rasional", "operasi penjumlahan dan pengurangan bilangan pecahan, serta "
        "operasi perkalian dan pembagian bilangan pecahan dengan bilangan asli", "Pengetahuan dan Pemahaman",
        "Pilihan Ganda", ["$120\\% - 3 + 2 \\times 0{,}75 + \\frac{2}{3} = \\ldots$"], "A",
        options=["$\\frac{11}{30}$", "$\\frac{49}{60}$", "$\\frac{31}{30}$", "$\\frac{98}{60}$"]),
    mtk(SD, 2, 31, "Bilangan", "Bilangan Rasional", "operasi penjumlahan dan pengurangan bilangan pecahan, serta "
        "operasi perkalian dan pembagian bilangan pecahan dengan bilangan asli", "Aplikasi", "Pilihan Ganda",
        ["Menjelang tahun ajaran baru, Toko Buku ABC memberikan diskon 10% untuk semua jenis buku. Diketahui harga "
         "buku X adalah $\\frac{1}{2}$ dari harga buku Y dan harga buku Z adalah 0,75 kali harga buku Y. Apabila "
         "harga buku Y adalah Rp24.000,00, harga buku X + Z setelah dikenakan diskon adalah …."], "C",
        options=["Rp18.000,00", "Rp24.000,00", "Rp27.000,00", "Rp30.000,00"]),
    mtk(SD, 3, 32, "Bilangan", "Bilangan Rasional", "operasi penjumlahan dan pengurangan bilangan pecahan, serta "
        "operasi perkalian dan pembagian bilangan pecahan dengan bilangan asli", "Penalaran", "PGK Kategori",
        ["Pak Bondan seorang penjual susu kedelai. Suatu hari, Pak Bondan memproduksi susu kedelai sebanyak 9 wadah "
         "yang masing-masing berisi $4\\frac{3}{4}$ liter susu kedelai. Seluruh hasil produksi tersebut akan "
         "dituangkan ke dalam 47 botol besar dengan isi yang sama banyak dan ke dalam 17 botol kecil dengan isi "
         "setiap botolnya adalah setengah botol besar.",
         "Tentukan Benar atau Salah untuk setiap pernyataan berikut tentang hasil produksi susu kedelai Pak Bondan!"],
        ["Benar", "Benar", "Salah"], responses=BS,
        statements=["Pada hari itu Pak Bondan memproduksi $42\\frac{3}{4}$ liter susu kedelai.",
                    "Setiap botol besar diisi susu kedelai sebanyak $\\frac{57}{74}$ liter.",
                    "Total susu kedelai yang dikemas dalam botol kecil adalah $\\frac{969}{74}$ liter."]),
    mtk(SD, 4, 33, "Geometri dan Pengukuran", "Objek Geometri", "konstruksi bangun ruang dan visualisasi spasial "
        "(bagian depan, atas, dan samping)", "Aplikasi", "Pilihan Ganda",
        ["Mae sedang bermain ular tangga dengan Doni. Bermain ular tangga membutuhkan dadu dan bidak. Diketahui "
         "bahwa jumlah titik pada setiap dua sisi berlawanan pada dadu adalah sama. Pada saat giliran Mae bermain, "
         "Mae melempar dadunya. Berikut adalah dadu hasil lemparan Mae.",
         "Pada dadu tersebut, banyak titik yang ada di sisi bawah adalah …."], "B",
        options=["2", "3", "4", "5"], figures=["sd-mtk-4-dadu"]),
    mtk(SD, 5, 34, "Geometri dan Pengukuran", "Pengukuran", "hubungan antar-satuan baku berat (mg, dg, cg, g, dag, "
        "hg, kg)", "Aplikasi", "PGK MCMA",
        ["Setiap bulan Ramadan, SD Harapan mengadakan bakti sosial. Mereka membagi sembako yang berisi 3 kg beras, "
         "dua bungkus gula pasir dengan berat masing-masing kemasan 5 hg, dan lima bungkus mi instan dengan berat "
         "per bungkus 85 g.", "Seberapa berat paket sembako tersebut?", MCMA], [1, 3],
        options=["Total berat semua isi paket adalah 4.425 gram.",
                 "Berat mi instan dalam paket tersebut lebih dari 0,5 kilogram.",
                 "Satu kemasan gula pasir lebih berat dibandingkan seluruh mi instan."]),
    mtk(SD, 6, 34, "Data", "Penyajian dan Penggunaan Data", "pengambilan informasi dan penggunaan data",
        "Aplikasi", "PGK Kategori",
        ["SD Harapan baru saja meresmikan ruang perpustakaan untuk siswa. Bu Anita sedang mendata banyak siswa yang "
         "berkunjung ke perpustakaan tersebut pada lima hari pertama sejak diresmikan. Diagram berikut "
         "menggambarkan data yang diperoleh Bu Anita.",
         "Deskripsi apakah yang tepat tentang data pada diagram tersebut?",
         "Tentukan Benar atau Salah untuk setiap pernyataan berikut!"],
        ["Benar", "Salah", "Benar"], responses=BS, figures=["sd-mtk-6-diagram"],
        statements=["Banyak siswa yang mengunjungi perpustakaan pada hari Senin hanya $\\frac{3}{4}$ dari pengunjung "
                    "pada hari Rabu.",
                    "Total siswa pengunjung perpustakaan mulai dari hari Senin hingga hari Jumat adalah 100.",
                    "Perbedaan banyak pengunjung harian dengan hari sebelumnya tidak lebih dari 5 orang."]),
    # ---------------------------------------------------------------- SMP Bahasa Indonesia
    bi(SMP, 1, 37, "Pemahaman Tekstual", "Mengidentifikasi objek dan/atau latar berdasarkan kosakata yang digunakan "
       "dalam teks fiksi atau nonfiksi", "Pilihan Ganda",
       ["Kosakata yang menggambarkan keserasian suara deburan alam pada teks ulasan ke-1 ditunjukkan pada "
        "frasa ...."], "D", "smp-bi-a",
       options=["alternatif wisata", "kanvas alam", "panggung cahaya", "harmoni alam"]),
    bi(SMP, 2, 37, "Pemahaman Inferensial", "Menjelaskan kelogisan hubungan antarperistiwa, antargagasan, dan/atau "
       "antarinformasi dalam dan/atau antarteks", "PGK MCMA",
       ["Apa saja perbedaan informasi yang ada pada kedua teks tersebut?", MCMA], [1, 3], "smp-bi-a",
       options=["Kemudahan akses.", "Fasilitas yang tersedia.", "Tempat untuk berfoto.", "Keindahan saat senja."]),
    bi(SMP, 3, 38, "Evaluasi dan Apresiasi", "Menilai kesesuaian dan/atau keakuratan unsur, kebahasaan, atau isi "
       "berdasarkan perbandingan informasi dalam dan/atau antarteks", "PGK MCMA",
       ["Banu: Aku lebih suka membaca ulasan pada teks 2 rasanya lebih dekat denganku. Aku jadi ingin ke sana! "
        "Teks ulasan 2 sangat menarik!",
        "Komar: Justru aku lebih suka ulasan pada teks 1 karena sangat jelas dan menarik minatku untuk mengunjungi "
        "pantai itu.",
        "Mengapa penyataan Banu lebih tepat untuk menggambarkan keunggulan teks ulasan kedua yang tidak ada pada "
        "teks ulasan pertama?",
        "Tentukan Benar atau Salah untuk setiap pernyataan berikut!"],
       ["Benar", "Salah", "Salah"], "smp-bi-a", responses=BS, form_note="pgk_kategori",
       statements=["Gaya penyajian teks menggunakan bahasa nonformal sehingga lebih santai.",
                   "Penyajian gambar pada teks yang membuat pembaca lebih tertarik membaca.",
                   "Akhir ulasan dilengkapi kalimat ajakan kepada pembaca untuk mengunjungi pantai."]),
    bi(SMP, 4, 39, "Pemahaman Tekstual", "Mengidentifikasi objek dan/atau latar berdasarkan kosakata yang digunakan "
       "dalam teks fiksi atau nonfiksi", "PGK MCMA",
       ["Pilihan kata mana saja yang menunjukkan latar waktu pada puisi tersebut?", MCMA], [2, 4], "smp-bi-b",
       options=["Bukit-bukit desa.", "Sebelum hari bermula.", "Akar-akar yang melata.", "Berlomba dengan surya."]),
    bi(SMP, 5, 40, "Pemahaman Inferensial", "Menjelaskan bahasa kias dan citraan yang digunakan dalam teks fiksi",
       "Pilihan Ganda", ["Apa makna merebut hidup di pasar-pasar kota pada teks puisi tersebut?"], "A", "smp-bi-b",
       options=["Kegigihan dan perjuangan perempuan dalam bekerja.", "Keuletan dan pencapaian seseorang dalam bekerja.",
                "Aktivitas dan keseharian perempuan yang bekerja di pasar.",
                "Tanggung jawab dan kewajiban perempuan pada keluarga."]),
    bi(SMP, 6, 40, "Evaluasi dan Apresiasi", "Menyimpulkan respons emosional terhadap unsur teks fiksi",
       "PGK Kategori",
       ["Setelah membaca puisi tersebut, tiga murid berpendapat sebagai berikut.",
        "Dina: Wah, ternyata banyak perempuan hebat ya. Mereka bekerja penuh semangat!",
        "Mira: Iya, mereka rela bangun pagi-pagi untuk bekerja.",
        "Tika: Tapi, kasihan ya mereka pasti lelah setelah seharian bekerja.",
        "Pendapat siapa yang tepat untuk menggambarkan suasana haru yang muncul setelah membaca puisi tersebut?",
        "Tentukan Setuju atau Tidak Setuju untuk setiap pernyataan berikut berdasarkan teks!"],
       ["Setuju", "Setuju", "Tidak Setuju"], "smp-bi-b", responses=ST,
       statements=["Dina karena menunjukkan kekagumannya kepada para perempuan yang bekerja.",
                   "Mira karena pendapatnya juga senada dengan pendapat yang disampaikan Dina.",
                   "Tika karena pendapatnya menunjukkan rasa empati terhadap perempuan pekerja."]),
    # ---------------------------------------------------------------- SMP Matematika
    mtk(SMP, 1, 41, "Bilangan", "Bilangan Real", "faktorisasi prima bilangan asli", "Penalaran", "PGK MCMA",
        ["Terdapat tiga bilangan yang dinyatakan dengan $(33^2 - 3^2)$, $(8^2 + 296)$, dan $(36 \\times 35)$.",
         "Bilangan apa saja yang merupakan faktor persekutuan ketiga bilangan tersebut?", MCMA], [3, 4],
        options=["$2^3 \\times 3^3 \\times 7$", "$2^2 \\times 3^2 \\times 7$", "$2^2 \\times 3^2 \\times 5$",
                 "$2 \\times 3^2 \\times 5$"]),
    mtk(SMP, 2, 42, "Bilangan", "Bilangan Real", "perbandingan senilai dan berbalik nilai", "Aplikasi",
        "Pilihan Ganda",
        ["Harga setengah kilogram cabe rawit pada hari ini adalah Rp35.000,00. Jika hari ini Ibu membeli cabe rawit "
         "seberat $2\\frac{1}{4}$ kilogram, total harga yang harus dibayar Ibu adalah …."], "B",
        options=["Rp175.000,00", "Rp157.500,00", "Rp140.000,00", "Rp87.500,00"]),
    mtk(SMP, 3, 42, "Aljabar", "Persamaan dan Pertidaksamaan Linier", "sistem persamaan linear dua variabel",
        "Aplikasi", "PGK Kategori",
        ["Misalkan a dan b merupakan dua bilangan real sehingga sistem persamaan linear (SPL)",
         "$\\begin{cases} 2x + ay = 4, \\\\ bx - 2y = -1, \\end{cases}$",
         "mempunyai solusi $(x, y) = (5,-2)$.",
         "Tentukan Benar atau Salah untuk setiap pernyataan berikut terkait dengan nilai a dan b!"],
        ["Benar", "Benar", "Salah"], responses=BS,
        statements=["a merupakan bilangan prima.", "b merupakan bilangan ganjil.", "10a + b = 31."]),
    mtk(SMP, 4, 43, "Geometri dan Pengukuran", "Objek Geometri", "hubungan antar-sudut yang terbentuk oleh dua garis "
        "yang berpotongan, dan oleh dua garis sejajar yang dipotong suatu garis transversal (termasuk penentuan "
        "besar sudut dalam segitiga)", "Aplikasi", "PGK Kategori",
        ["Desain jembatan yang tepat sangat penting untuk memperkuat struktur karena menentukan kestabilan, "
         "ketahanan, dan keselamatan jembatan dalam menghadapi beban dan kondisi lingkungan. Salah satu contoh "
         "desain jembatan tampak pada gambar.",
         "Bagian rangka jembatan tersebut dapat digambarkan dengan sketsa garis sebagai berikut:",
         "Diketahui garis L1 sejajar dengan garis L2 dan garis L3 sejajar dengan garis L4. Jika besar sudut A "
         "adalah $50^\\circ$, tentukan Benar atau Salah untuk setiap pernyataan berikut!"],
        ["Benar", "Salah", "Benar"], responses=BS, figures=["smp-mtk-4-jembatan", "smp-mtk-4-sketsa"],
        statements=["Besar sudut D adalah $50^\\circ$.",
                    "Besar sudut C dapat ditentukan dengan menggunakan aturan sudut berpelurus yaitu sebesar "
                    "$50^\\circ$.",
                    "Sudut B dan E sama besar yaitu $130^\\circ$."]),
    mtk(SMP, 5, 44, "Geometri dan Pengukuran", "Pengukuran", "keliling dan luas bangun datar (daerah segi banyak "
        "dan daerah lingkaran, serta daerah gabungannya)", "Penalaran", "Pilihan Ganda",
        ["Pak Doni mempunyai rumah dengan tampak samping kanan sebagai berikut.",
         "Pak Doni ingin mengecat dinding samping kanan rumah tersebut. Terdapat empat merek cat di pasaran yang "
         "dapat digunakan Pak Doni seperti ditunjukkan pada tabel berikut.",
         {"table": [["Merek Cat", "1 kg Dapat Mengecat", "Kemasan yang Tersedia di Toko"],
                    ["Momilex", "7 m²", "5 kg-an dan 10 kg-an"], ["Josun", "8 m²", "2 kg-an dan 10 kg-an"],
                    ["Bulux", "10 m²", "2 kg-an dan 5 kg-an"], ["Noppin", "9 m²", "1 kg-an dan 5 kg-an"]]},
         "Pak Doni ingin membeli cat dengan merek yang sama. Supaya sisa cat yang dibeli paling sedikit, cat merek "
         "apakah yang sebaiknya dipilih?"], "C",
        options=["Momilex.", "Josun.", "Bulux.", "Noppin."], figures=["smp-mtk-5-rumah"]),
    mtk(SMP, 6, 45, "Data dan Peluang", "Data", "penentuan dan penaksiran rerata (mean), median, modus, dan "
        "jangkauan (range) dari data", "Aplikasi", "Pilihan Ganda",
        ["Berdasarkan data diketahui bahwa rata-rata berat satu butir telur kecil 45 gram, satu telur sedang 55 gram, "
         "dan satu telur besar 65 gram. Seorang karyawan toko bahan pangan, sedang mengemas setiap 10 butir telur ke "
         "dalam satu kemasan dengan ketentuan bahwa rata-rata berat per telur dalam setiap kemasan tersebut adalah "
         "55 gram. Jika dalam satu kemasan sudah berisi 1 telur besar, 5 telur sedang, dan 2 telur kecil, maka dua "
         "telur tambahan yang harus dipilih supaya tetap memenuhi aturan pengemasan adalah …."], "D",
        options=["2 telur sedang", "2 telur besar", "1 telur besar dan 1 telur kecil",
                 "1 telur besar dan 1 telur sedang"]),
]

# printing errors and inconsistencies in part IV (F-031): (page, printed, reason)
ERRATA = [
    (26, "PGK Kategori", "SD Bahasa Indonesia no. 2 is labelled 'PGK Kategori' but is built as Pilihan Ganda (A–D, "
     "one key); stored with item_form 'pg', bentuk_soal as printed"),
    (38, "PGK MCMA", "SMP Bahasa Indonesia no. 3 is labelled 'PGK MCMA' but is built as PGK Kategori (Benar/Salah per "
     "statement); stored with item_form 'pgk_kategori', bentuk_soal as printed"),
    (38, "Mengapa penyataan Banu", "'penyataan' for 'pernyataan' (SMP Bahasa Indonesia no. 3)"),
    (37, "harmoni alam", "SMP Bahasa Indonesia no. 1: none of the four phrases (key D 'harmoni alam') occurs in Teks "
     "Ulasan 1 as printed on p. 36"),
]
# User decision 2026-11-27 (F-034): third-party works may be used for education when their owners are credited.
ATTRIBUTION_RULE = (
    "Every stimulus and figure is reproduced from Perka BSKAP 047/H/AN/2025 for education. Show the stimulus's "
    "`attribution.credit` (and the regulation) wherever the text or figure is shown; third-party works stay with "
    "their owners.")
NOTES = [
    "The degree sign is printed as a superscript letter O/o (50O, 50o) on p. 44; written $^\\circ$ here.",
    "Options and statements are printed with empty check boxes; MCMA keys are statement numbers as printed "
    "('Pernyataan 2 dan Pernyataan 3').",
]
