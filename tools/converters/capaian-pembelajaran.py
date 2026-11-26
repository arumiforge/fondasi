#!/usr/bin/env python3
"""Build the data set `capaian-pembelajaran` (R-15, F-030): learning outcomes (CP) per subject and phase.

Sources (sources/capaian-pembelajaran/, SOURCE.txt):
  - Kepka BSKAP 046/H/KR/2025 (Lampiran I PAUD, II SD/SMP/SMA, III SMK, IV Paket, V SLB), born-digital: parsed
    from `pdftotext -layout` output. Headings end with U+200B in this PDF, which marks where a wrapped heading ends.
  - Kepka BKPDM 020/2026 replaces the religion CP of 046 (scanned): see the religion part.
  - SK Dirjen Pendis 9941/2025: CP of the madrasah subjects.

Every section of 046 follows the same pattern, which the parser requires (and reports when a section does not):
  "CAPAIAN PEMBELAJARAN <SUBJECT>", A. Rasional, B. Tujuan, C. Karakteristik (prose + table Elemen | Deskripsi),
  D. Capaian Pembelajaran: "n. Fase X (Umumnya untuk ...)", "Pada akhir Fase X, ...", "n.m. <Element>" + text.
Checks: every phase has outcomes, outcome element names match the element table, phases appear in order, no text
is left over. Text is kept as printed (line breaks joined; list items keep their own line).

  python3 -I tools/converters/capaian-pembelajaran.py sources/capaian-pembelajaran data
  python3 -I tools/converters/capaian-pembelajaran.py <pdf> <out> <first> <last> <tag>   # one part, for checking
"""
import json
import os
import re
import subprocess
import sys

ZW = "\u200b"
ZWMODE = True  # the PDF marks heading ends with U+200B (046 does, SK 9941 does not); set in main()


def mostly_upper(t):
    letters = [c for c in t if c.isalpha()]
    return bool(letters) and sum(c.isupper() for c in letters) / len(letters) >= 0.8
ROMAN = r"[IVXL]+"


def pdf_pages(path):
    out = subprocess.run(["pdftotext", "-layout", path, "-"], check=True, capture_output=True, text=True).stdout
    return out.split("\f")


BIDI = re.compile("[\u200e\u200f\u202a-\u202e\u2066-\u2069]")


def norm_space(s):
    return re.sub(r"[ \t]+", " ", BIDI.sub("", s).replace(ZW, " ")).strip()


def join_lines(lines):
    """Join wrapped lines. A new line starts before a list item (1., a., ●, -), after a line ending with ':', and
    after a short label line ("Tajwid") that precedes its text."""
    out, prev = "", ""
    for raw in lines:
        line = norm_space(raw)
        if not line:
            continue
        if not out:
            out = line
        elif re.match(r"^(\d+(\.\d+)*\.|[a-z]\.|[a-z]\)|\d+\)|●|•|-|–)\s", line) or out.endswith(":"):
            out += "\n" + line
        elif out.endswith("-") and not out.endswith(" -"):
            out += line
        elif line[:1].isupper() and len(prev) <= 40 and not re.search(r"[.,;:)]$", prev) \
                and len(prev.split()) <= 5 and prev[:1].isupper():
            out += "\n" + line
        else:
            out += " " + line
        prev = line
    return out


def norm_key(s):
    return re.sub(r"[^a-z0-9]+", "", s.lower().replace("’", "'"))


def key_of(title):
    s = title.lower()
    s = re.sub(r"\(.*?\)", "", s)
    s = re.sub(r"[^a-z0-9]+", "_", s).strip("_")
    return s


# ------------------------------------------------------------------ section splitting

HEAD = re.compile(r"^(?:(" + ROMAN + r"(?:\.\d+)?|\d+(?:\.\s?\d+)+)\.?\s*)?CAPAIAN PEMBELAJARAN\s+(.*)$")


def sections(pages, first, last):
    """Yield (title, number, start_page, lines[(page, text)]) for each subject section between PDF pages."""
    lines = []
    for pno in range(first, last + 1):
        for ln in pages[pno - 1].split("\n"):
            if ln.strip() and not re.match(r"^\s*-\s*\d+\s*-\s*$", ln) and "jdih.kemendikdasmen" not in ln:
                lines.append((pno, ln))
    heads = []
    i = 0
    while i < len(lines):
        txt = norm_space(lines[i][1])
        m = HEAD.match(txt)
        if m and mostly_upper(txt):
            title = m.group(2)
            j = i + 1
            while j < len(lines):
                nxt = norm_space(lines[j][1])
                if nxt and mostly_upper(nxt) and not re.match(r"^[A-H]\.", nxt) and len(nxt) < 80 \
                        and not HEAD.match(nxt):
                    title += " " + nxt
                    j += 1
                else:
                    break
            heads.append((i, j, title.strip(), m.group(1)))
            i = j
        else:
            i += 1
    out = []
    for n, (i, j, title, num) in enumerate(heads):
        end = heads[n + 1][0] if n + 1 < len(heads) else len(lines)
        body = lines[j:end]
        # a group heading ("I. CAPAIAN PEMBELAJARAN PENDIDIKAN AGAMA") has no body of its own
        if not any(norm_space(t).startswith("A.") and "Rasional" in t for _, t in body):
            continue
        out.append({"title": title, "number": num, "page": lines[i][0], "lines": body})
    return out


# ------------------------------------------------------------------ one section

PART = re.compile(r"^([A-D])\.\s*(Rasional|Tujuan|Karakteristik|Capaian Pembelajaran)(\s+(Mata Pelajaran|[A-Z]).*)?$")
PHASE = re.compile(r"^(\d+)\.\s*Fase\s+([A-F]|Fondasi)\b\s*(.*)$")
ITEM = re.compile(r"^(\d+)\.(\d+)\.\s*(.*)$")


def split_parts(sec):
    parts, cur = {}, None
    for pno, ln in sec["lines"]:
        m = PART.match(norm_space(ln))
        if m:
            cur = m.group(1)
            parts[cur] = []
            continue
        if cur:
            parts[cur].append((pno, ln))
    return parts


PDF = None  # pdfplumber document, opened in main()


def _clean_cell(c):
    return join_lines((c or "").split("\n"))


def element_table(sec, c_pages):
    """Read C. Karakteristik with pdfplumber: prose outside tables, and the Elemen table(s) (ruled tables)."""
    elements, prose_parts, header = [], [], None
    for pno in c_pages:
        page = PDF.pages[pno - 1]
        tables = page.find_tables()
        boxes = [t.bbox for t in tables]

        def outside(obj, boxes=boxes):
            x, y = (obj.get("x0", 0) + obj.get("x1", 0)) / 2, (obj.get("top", 0) + obj.get("bottom", 0)) / 2
            return not any(b[0] <= x <= b[2] and b[1] <= y <= b[3] for b in boxes)

        prose_parts.append(page.filter(outside).extract_text() or "")
        for t in tables:
            rows = t.extract()
            if not rows or not rows[0]:
                continue
            if (rows[0][0] or "").strip().lower().startswith("elemen"):
                hdr = [_clean_cell(c).lower() for c in rows[0]]
                header = hdr
                rows = rows[1:]
            elif header and len(rows[0]) == len(header) and pno > c_pages[0] and t.bbox[1] < 120:
                hdr = header  # continuation of the table on the next page without a repeated header row
            else:
                continue
            for ri, r in enumerate(rows):
                cells = [_clean_cell(c) for c in r]
                if len(cells) != len(hdr):
                    continue
                rec = dict(zip(hdr, cells))
                name = rec.get("elemen", "")
                desc = rec.get("deskripsi", "")
                sub = rec.get("subelemen") or rec.get("sub-elemen") or rec.get("sub elemen")
                # first row of a table that continues on a new page: a cell split by the page break
                split_cell = (ri == 0 and elements and pno != elements[-1].get("_page")
                              and (desc[:1].islower() or desc[:1] in ",;)" or not desc))
                if split_cell:
                    if name:
                        elements[-1]["name"] += " " + name
                    if sub:
                        elements[-1]["sub_element"] = (elements[-1].get("sub_element", "") + " " + sub).strip()
                    if desc:
                        d = elements[-1]["description"]
                        elements[-1]["description"] = (d[:-1] + desc) if d.endswith("-") and not d.endswith(" -") \
                            else (d + " " + desc).strip()
                    elements[-1]["_page"] = pno
                    continue
                if name or (sub and not desc.startswith(tuple("abcdefghijklmnopqrstuvwxyz"))) or not elements:
                    e = {"name": name or (elements[-1]["name"] if elements else ""), "description": desc, "_page": pno}
                    if sub is not None:
                        e["sub_element"] = sub
                    elements.append(e)
                else:
                    d = elements[-1]["description"]
                    elements[-1]["description"] = (d[:-1] + desc) if d.endswith("-") and not d.endswith(" -") \
                        else (d + " " + desc).strip()
                    if sub:
                        elements[-1]["sub_element"] = (elements[-1].get("sub_element", "") + " " + sub).strip()
    text = "\n".join(prose_parts).replace(ZW, " ")
    m1 = re.search(r"C\.\s*Karakteristik\s*\n", text)
    m2 = re.search(r"\nD\.\s*Capaian Pembelajaran\s*\n", text)
    body = text[m1.end() if m1 else 0: m2.start() if m2 else len(text)]
    for e in elements:
        e.pop("_page", None)
        e["name"] = norm_space(e["name"])
        e["description"] = norm_space(e["description"])
    return join_lines(body.split("\n")), elements


ITEMN = re.compile(r"^(\d+(?:\.\d+)+)\.?\s+(.*)$")


def strip_prefix(name, word):
    return re.sub(r"^" + word + r"\s+", "", name)


PHASE2 = re.compile(r"^(?:(\d+)\.\s*)?Fase\s+([A-F]|Fondasi)\s*(\(.*)?$")
TOP = re.compile(r"^(\d+)\.\s*(.+)$")


CONNECT = ("dan", "atau", "serta", "yang", "untuk", "dengan", "di", "ke", "dari", "pada", "&", "-", ",")


def needs_more(name, nxt):
    """A heading continues on the next line when it is clearly unfinished."""
    if not nxt or ITEMN.match(nxt) or PHASE2.match(nxt) or TOP.match(nxt):
        return False
    return (name.count("(") > name.count(")") or name.rstrip().endswith((",", "-", "&", "/"))
            or name.rstrip().split()[-1].lower() in CONNECT or nxt[:1].islower() or nxt[:1] == ")")


def heading_end(first, lines, i, names, extend=True):
    name, i, rest = _heading_end(first, lines, i, names, extend)
    while not rest and i + 1 < len(lines) and not (ZWMODE and lines[i][1].rstrip().endswith(ZW)) \
            and needs_more(name, norm_space(lines[i + 1][1])):
        i += 1
        name += " " + norm_space(lines[i][1])
    return name, i, rest


def _heading_end(first, lines, i, names, extend=True):
    """Read a wrapped heading starting at lines[i]; return (name, last index). Known element names decide where a
    heading ends; otherwise the U+200B at its end does."""
    name = first
    if names:
        bare = lambda x: norm_key(re.sub(r"^(Sub)?[Ee]lemen\s+", "", x))  # noqa: E731
        cand = [n for n in names if n.startswith(bare(name))]
        while cand and bare(name) not in names and i + 1 < len(lines):
            nxt = norm_space(lines[i + 1][1])
            if not any(n.startswith(bare(name + " " + nxt)) for n in cand):
                break
            i += 1
            name += " " + nxt
        if bare(name) in names or not cand:
            # a heading printed without U+200B and followed on the same line by text is cut at the name
            for n in sorted(names, key=len, reverse=True):
                if norm_key(name).startswith(n) and norm_key(name) != n:
                    words, acc = name.split(), ""
                    for k in range(1, len(words) + 1):
                        if norm_key(" ".join(words[:k])) == n and words[k:] and words[k][:1].isupper() \
                                and len(words) - k > 3:
                            return " ".join(words[:k]), i, " ".join(words[k:])
            return name, i, ""
    while extend and ZWMODE and not lines[i][1].rstrip().endswith(ZW) and i + 1 < len(lines) \
            and not ITEMN.match(norm_space(lines[i + 1][1])) and not PHASE2.match(norm_space(lines[i + 1][1])):
        i += 1
        name += " " + norm_space(lines[i][1])
    return name, i, ""


def outcomes(lines, names):
    """Parse D. Capaian Pembelajaran into phases with intro and outcomes (element, optional sub-element)."""
    phases, cur, item, group, buf = [], None, None, None, []

    def flush():
        nonlocal buf
        if item is not None:
            item["text"] = join_lines(buf)
        elif cur is not None and not cur["outcomes"]:
            cur["intro"] = join_lines(buf)
        elif buf and cur is not None:
            cur.setdefault("trailing", []).append(join_lines(buf))
        buf = []

    i = 0
    while i < len(lines):
        pno, ln = lines[i]
        s = norm_space(ln)
        m = PHASE2.match(re.sub(r"^[^\w]+(?=\d+\.\s*Fase)", "", s))
        if m and (m.group(3) or (i + 1 < len(lines) and "Umumnya" in lines[i + 1][1])):
            flush()
            head = m.group(3) or ""
            while ")" not in head and not lines[i][1].rstrip().endswith(ZW) and i + 1 < len(lines) \
                    and not norm_space(lines[i + 1][1]).startswith("Pada akhir"):
                i += 1
                head += " " + norm_space(lines[i][1])
            cur = {"phase": m.group(2), "applies_to": head.strip().strip("()").strip(), "page": pno,
                   "numbered": bool(m.group(1)), "num": m.group(1), "intro": "", "outcomes": []}
            phases.append(cur)
            item = group = None
            i += 1
            continue
        mi = re.match(r"^(?:Pada akhir [Ff]ase|Rumusan Capaian Pembelajaran Fase) ([A-F]|Fondasi)\b", s)
        if mi and cur is None:
            cur = {"phase": mi.group(1), "applies_to": None, "page": pno, "numbered": False, "num": None, "intro": "",
                   "outcomes": []}
            phases.append(cur)
        if cur is not None:
            m = ITEMN.match(s) if cur["numbered"] else TOP.match(s)
            if m and cur["numbered"]:
                ok = m.group(1).split(".")[0] == cur["num"]
            elif m:
                # unnumbered phase: "n. Name" is an element heading when the name is a known element, or when it
                # is a short label (no sentence) numbered in sequence
                short = len(m.group(2).split()) <= 8 and not re.search(r"[.;:,]$", m.group(2))
                zw_numbered = re.match(r"^\s*\d+\." + ZW, ln) is not None
                ok = (norm_key(m.group(2)) in names or short or zw_numbered) \
                    and int(m.group(1)) == len(cur["outcomes"]) + 1
            else:
                ok = False
            if ok:
                flush()
                num = m.group(1)
                name, i, rest = heading_end(m.group(2), lines, i, names, extend=cur["numbered"])
                name = norm_space(name)
                nxt = norm_space(lines[i + 1][1]) if i + 1 < len(lines) else ""
                mm = ITEMN.match(nxt)
                if not rest and mm and mm.group(1).startswith(num + "."):
                    group = strip_prefix(name, "Elemen")
                    item = None
                    i += 1
                    continue
                if num.count(".") >= 2 and group:
                    item = {"element": group, "sub_element": strip_prefix(name, "Subelemen"), "text": "",
                            "page": pno}
                else:
                    group = None
                    item = {"element": strip_prefix(name, "Elemen"), "text": "", "page": pno}
                cur["outcomes"].append(item)
                if rest:
                    buf.append(rest)
                i += 1
                continue
        buf.append(ln)
        i += 1
    flush()
    for ph in phases:
        ph.pop("numbered", None)
        ph.pop("num", None)
    return phases


def cp_table(pages):
    """CP printed as a table with columns No | Elemen | Capaian Pembelajaran (CP)."""
    out = []
    for pno in pages:
        for t in PDF.pages[pno - 1].find_tables():
            rows = t.extract()
            if not rows:
                continue
            hdr = [_clean_cell(c).lower() for c in rows[0]]
            if any("elemen" in h for h in hdr) and any("capaian" in h for h in hdr):
                body = rows[1:]
            elif out and len(rows[0]) == 3:
                body = rows
            else:
                continue
            for r in body:
                cells = [_clean_cell(c) for c in r]
                if len(cells) != 3:
                    continue
                no, el, cp = cells
                if el or not out:
                    out.append({"element": norm_space(el.replace("\n", " ")), "text": cp, "page": pno})
                else:
                    out[-1]["text"] = (out[-1]["text"] + "\n" + cp).strip()
    return out


def parse_section(sec, issues):
    parts = split_parts(sec)
    for k in "ABCD":
        if k not in parts:
            issues.append(f"{sec['title']}: part {k} missing")
            parts.setdefault(k, [])
    c_pages = sorted({p for p, _ in parts["C"]} | ({parts["D"][0][0]} if parts["D"] else set()))
    karakteristik, elements = element_table(sec, c_pages)
    names = {norm_key(e["name"]) for e in elements} | {norm_key(e.get("sub_element", "")) for e in elements}
    names.discard("")
    phases = outcomes(parts["D"], names)
    if not phases or not any(p["outcomes"] for p in phases):
        tab = cp_table(sorted({p for p, _ in parts["D"]}))
        if tab:
            intro = phases[0]["intro"] if phases else join_lines([l for _, l in parts["D"]][:8])
            ph = phases[0]["phase"] if phases else ("Fondasi" if "fondasi" in intro.lower() else None)
            phases = [{"phase": ph, "applies_to": None, "page": parts["D"][0][0], "intro": intro.split(" No ")[0],
                       "outcomes": tab}]
    for ph in phases:
        if not ph["outcomes"] and not ph["intro"]:
            issues.append(f"{sec['title']}: Fase {ph['phase']} empty")
        for o in ph["outcomes"]:
            if not o["text"]:
                issues.append(f"{sec['title']}: Fase {ph['phase']} {o['element']}: no text")
            elif o["text"][:1] == ")" or o["text"].split()[0].lower() in CONNECT \
                    or (o.get("sub_element") or o["element"]).count("(") > (o.get("sub_element") or o["element"]).count(")") \
                    or len((o.get("sub_element") or o["element"]).split()) > 14:
                issues.append(f"{sec['title']}: Fase {ph['phase']} {o['element']}: text starts '{o['text'][:30]}'")
            if names and norm_key(o.get("sub_element") or o["element"]) not in names \
                    and norm_key(o["element"]) not in names:
                issues.append(f"{sec['title']}: Fase {ph['phase']} element '{o['element']}' not in table "
                              f"{sorted(names)}")
    pages = sorted({p for p, _ in sec["lines"]})
    return {
        "key": key_of(sec["title"]), "title": sec["title"].title(), "title_printed": sec["title"],
        "number": sec["number"], "pages": [sec["page"], pages[-1] if pages else sec["page"]],
        "rasional": join_lines([l for _, l in parts["A"]]),
        "tujuan": join_lines([l for _, l in parts["B"]]),
        "karakteristik": karakteristik, "elements": elements, "phases": phases,
    }


K046 = "Kepka_BSKAP_No_046_H_KR_2025_Capaian_Pembelajaran.pdf"
K9941 = "SK_Dirjen_Pendis_No_9941_Tahun_2025_CP_PAI_dan_Bahasa_Arab_pada_Madrasah.pdf"
REF046 = "Kepka BSKAP 046/H/KR/2025"
REF9941 = "SK Dirjen Pendis 9941/2025"

# (file, pdf, first page, last page, source reference, levels, title override)
PARTS = [
    ("paud", K046, 7, 22, f"{REF046}, Lampiran I", ["PAUD"], "Fase Fondasi"),
    ("umum", K046, 23, 347, f"{REF046}, Lampiran II", ["SD", "MI", "SMP", "MTs", "SMA", "MA", "SMK", "MAK",
                                                       "Paket A", "Paket B", "Paket C"], None),
    ("smk", K046, 348, 1190, f"{REF046}, Lampiran III", ["SMK", "MAK"], None),
    ("kesetaraan", K046, 1191, 1287, f"{REF046}, Lampiran IV", ["Paket A", "Paket B", "Paket C"], None),
    ("pendidikan-khusus", K046, 1288, 1691, f"{REF046}, Lampiran V", ["TKLB", "SDLB", "SMPLB", "SMALB"], None),
    ("madrasah", K9941, 6, 108, f"{REF9941}, Lampiran", ["RA", "MI", "MTs", "MA", "MAK"], None),
]
# Religion CP of 046 (Lampiran II I.1–I.6 and Lampiran V I.1–I.6) was replaced by Kepka BKPDM 020/2026 (scanned);
# it is left out until 020 is transcribed and checked (user decision 2026-11-26).
RELIGION_PENDING = ("PENDIDIKAN AGAMA ", "PENDIDIKAN KHUSUS PENDIDIKAN AGAMA ")
HARD = ("part ", " empty", "no phases")


def finish_subject(sub, source, levels, issues):
    notes = []
    for x in issues:
        notes.append(x.split(": ", 1)[1] if ": " in x else x)
    for ph in sub["phases"]:
        for o in ph["outcomes"]:
            t = (o["text"] or "").strip()
            if t in ("", "-", "–"):
                o["text"] = None
                o["no_cp"] = True
    sub["source"] = f"{source} ({'number ' + sub['number'] + ', ' if sub['number'] else ''}PDF p. "\
                    f"{sub['pages'][0]}–{sub['pages'][1]})"
    sub["levels"] = levels
    if notes:
        sub["source_notes"] = sorted(set(n for n in notes if not any(h in n for h in HARD)))
    return sub


def build(src, out):
    global PDF, ZWMODE
    import gzip
    import logging
    import pdfplumber
    logging.getLogger("pdfminer").setLevel(logging.ERROR)
    opened = {}
    index, totals, hard = [], {"subjects": 0, "phases": 0, "outcomes": 0}, []
    os.makedirs(os.path.join(out, "capaian-pembelajaran"), exist_ok=True)
    for fname, pdfname, first, last, source, levels, title in PARTS:
        path = os.path.join(src, pdfname)
        if path not in opened:
            opened[path] = (pdfplumber.open(path), pdf_pages(path))
        PDF, pages = opened[path]
        ZWMODE = sum(p.count(ZW) for p in pages) > 100
        subjects, keys = [], set()
        for sec in sections(pages, first, last):
            if fname in ("umum", "pendidikan-khusus") and sec["title"].startswith(RELIGION_PENDING):
                continue
            issues = []
            sub = parse_section(sec, issues)
            if title:
                sub["title"] = title
                sub["key"] = key_of(title)
            if not sub["phases"]:
                issues.append(f"{sub['title']}: no phases")
            hard += [f"{fname}: {x}" for x in issues if any(h in x for h in HARD)]
            k, n = sub["key"], 2
            while sub["key"] in keys:
                sub["key"] = f"{k}_{n}"
                n += 1
            keys.add(sub["key"])
            subjects.append(finish_subject(sub, source, levels, issues))
        data = {"file": fname, "source": source, "subjects": subjects}
        if fname in ("umum", "pendidikan-khusus"):
            data["pending"] = ("Pendidikan Agama dan Budi Pekerti (six religions): replaced by Kepka BKPDM 020/2026; "
                               "added when its scanned text has been transcribed and checked.")
        raw = json.dumps(data, ensure_ascii=False, indent=1).encode("utf-8") + b"\n"
        with open(os.path.join(out, "capaian-pembelajaran", fname + ".json.gz"), "wb") as f:
            with gzip.GzipFile(filename="", mode="wb", fileobj=f, mtime=0) as g:
                g.write(raw)
        for sub in subjects:
            index.append({"file": fname + ".json.gz", "key": sub["key"], "title": sub["title"],
                          "number": sub["number"], "phases": [p["phase"] for p in sub["phases"]],
                          "levels": sub["levels"], "source": sub["source"]})
            totals["subjects"] += 1
            totals["phases"] += len(sub["phases"])
            totals["outcomes"] += sum(len(p["outcomes"]) for p in sub["phases"])
        print(f"{fname}: {len(subjects)} subjects")
    if hard:
        sys.exit("structure problems:\n  " + "\n  ".join(hard))
    with open(os.path.join(out, "capaian-pembelajaran", "index.json"), "w", encoding="utf-8") as f:
        json.dump({"name": "Capaian Pembelajaran", "files": [p[0] + ".json.gz" for p in PARTS],
                   "pending": "Pendidikan Agama dan Budi Pekerti (Kepka BKPDM 020/2026)", "totals": totals,
                   "subjects": index}, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print(f"ok: {totals}")
    return totals


def main(pdf, out, first=23, last=347, tag="II"):
    global PDF
    import logging
    import pdfplumber
    logging.getLogger("pdfminer").setLevel(logging.ERROR)
    global ZWMODE
    PDF = pdfplumber.open(pdf)
    pages = pdf_pages(pdf)
    ZWMODE = sum(p.count(ZW) for p in pages) > 100
    issues = []
    subjects = [parse_section(s, issues) for s in sections(pages, first, last)]
    print(f"{len(subjects)} subjects, {sum(len(s['phases']) for s in subjects)} phases, "
          f"{sum(len(p['outcomes']) for s in subjects for p in s['phases'])} outcomes, {len(issues)} issues")
    for x in issues:
        print("  !", x)
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, f"draft-lampiran-{tag}.json"), "w", encoding="utf-8") as f:
        json.dump(subjects, f, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    if len(sys.argv) == 6:
        main(sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), sys.argv[5])
    elif len(sys.argv) == 3 and os.path.isdir(sys.argv[1]):
        build(sys.argv[1], sys.argv[2])
    else:
        sys.exit(__doc__)
