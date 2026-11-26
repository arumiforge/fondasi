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
Checks: every phase has outcomes, outcome element names match the element table (differences are kept per subject
in `source_notes`), the appendix signature block is cut off and no NIP-like number reaches the output. Text is kept as printed (line breaks joined; list items keep their own line).

  python3 -I tools/converters/capaian-pembelajaran.py sources/capaian-pembelajaran data
  python3 -I tools/converters/capaian-pembelajaran.py --index data   # index.json only (after the religion files)
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


LIGATURES = {"\uf001": "fi", "\uf002": "fl", "\ufb01": "fi", "\ufb02": "fl"}


def unligature(s):
    for k, v in LIGATURES.items():
        s = s.replace(k, v)
    return s


def norm_space(s):
    return re.sub(r"[ \t]+", " ", unligature(BIDI.sub("", s)).replace(ZW, " ")).strip()


def is_label(line):
    """A short label line such as "Tajwid" or "• Mengamati" that the text under it follows."""
    bare = re.sub(r"^[•●]\s*", "", line)
    return len(line) <= 40 and len(bare.split()) <= 5 and bare[:1].isupper() and not re.search(r"[.,;:)]$", line)


def join_lines(lines):
    """Join wrapped lines. A new line starts before a list item (1., a., ●, -), after a line ending with ':', and
    around a short label line ("Tajwid") that precedes its text."""
    lines = [x for x in (norm_space(r) for r in lines) if x]
    out, prev = "", ""
    for i, line in enumerate(lines):
        nxt = lines[i + 1] if i + 1 < len(lines) else ""
        if not out:
            out = line
        elif out.endswith(("•", "●")):
            out += " " + line  # bullet printed alone on its line, its label on the next
        elif re.match(r"^((\d+(\.\d+)*\.|[a-z]\.|[a-z]\)|\d+\)|●|•|-|–)\s|[•●]$)", line) or out.endswith(":"):
            out += "\n" + line
        elif out.endswith("-") and not out.endswith(" -"):
            out += line
        elif line[:1].isupper() and is_label(prev):
            out += "\n" + line
        elif is_label(line) and re.search(r"[.;]$", prev) and nxt[:1].isupper():
            out += "\n" + line  # a label after a finished sentence ("... benar. Al-Qur'an")
        else:
            out += " " + line
        prev = line
    return out


def norm_key(s):
    return re.sub(r"[^a-z0-9]+", "", s.lower().replace("’", "'"))


SMALL = {"dan", "atau", "serta", "untuk", "dengan", "di", "ke", "dari", "pada", "yang", "bagi", "dalam", "of", "and",
         "for"}
ACRONYMS = {"MTS": "MTs", "KKA": "KKA", "IPAS": "IPAS", "IPA": "IPA", "IPS": "IPS", "PJOK": "PJOK", "RA": "RA",
            "MI": "MI", "MA": "MA", "MAK": "MAK", "MAPK": "MAPK", "SMK": "SMK", "PAUD": "PAUD", "TKLB": "TKLB",
            "PKPBI": "PKPBI", "POMSK": "POMSK", "TIK": "TIK", "K3": "K3", "K3LH": "K3LH", "TV": "TV", "DKV": "DKV"}


def nice_title(printed):
    """Title case for a heading printed in capitals: Indonesian small words in lower case, acronyms kept
    ("ILMU PENGETAHUAN ALAM DAN SOSIAL (IPAS)" → "Ilmu Pengetahuan Alam dan Sosial (IPAS)")."""
    def word(w, first):
        core = w.strip("(),.:;/")
        if core.upper() in ACRONYMS:
            return w.replace(core, ACRONYMS[core.upper()])
        if not first and core.lower() in SMALL:
            return w.lower()
        parts = re.split(r"([-/])", w.lower())
        parts = [re.sub(r"^(\(?)(\w)", lambda m: m.group(1) + m.group(2).upper(), x) for x in parts]
        return re.sub(r"(['’])([A-Z])", lambda m: m.group(1) + m.group(2).lower(), "".join(parts))

    words = printed.split()
    out = []
    for i, w in enumerate(words):
        if "/" in w and not w.startswith("("):
            out.append("/".join(word(x, i == 0) for x in w.split("/")))
        else:
            out.append(word(w, i == 0))
    return " ".join(out)


def printed_twice(title):
    m = re.match(r"^(.+?) CAPAIAN PEMBELAJARAN (.+)$", title)
    return m.group(1) if m and norm_key(m.group(1)) == norm_key(m.group(2)) else None


def clean_heading(title):
    """Drop a heading printed twice ("X CAPAIAN PEMBELAJARAN X") and a leading "MATA PELAJARAN"."""
    title = printed_twice(title) or title
    return re.sub(r"^MATA PELAJARAN\s+", "", title)


def key_of(title):
    s = title.lower()
    s = re.sub(r"\(.*?\)", "", s)
    s = re.sub(r"[^a-z0-9]+", "_", s).strip("_")
    return s


# ------------------------------------------------------------------ section splitting

HEAD = re.compile(r"^(?:(" + ROMAN + r"(?:\.\d+)?|\d+(?:\.\s?\d+)+)\.?\s*)?CAPAIAN PEMBELAJARAN\s+(.*)$")


SIGNATURE = re.compile(r"^\s*(KEPALA BADAN|DIREKTUR JENDERAL PENDIDIKAN ISLAM|DIREKTUR JENDERAL|TTD\.?|"
                       r"Salinan sesuai dengan aslinya)\b.*$")


def sections(pages, first, last):
    """Yield (title, number, start_page, lines[(page, text)]) for each subject section between PDF pages."""
    lines = []
    for pno in range(first, last + 1):
        for ln in pages[pno - 1].split("\n"):
            if ln.strip() and not re.match(r"^\s*-\s*\d+\s*-\s*$", ln) and "jdih.kemendikdasmen" not in ln:
                lines.append((pno, ln))
    # the signature block that closes an appendix (official's name, NIP) is not part of any subject
    for k, (_, ln) in enumerate(lines):
        if SIGNATURE.match(ln):
            lines = lines[:k]
            break
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
    """A table cell: wrapped lines joined with spaces; only list items keep their own line."""
    out, prev = "", ""
    for line in (norm_space(x) for x in (c or "").split("\n")):
        if not line or PAGENO.match(line):
            continue
        if not out:
            out = line
        elif out.endswith(("•", "●")):
            out += " " + line  # bullet printed alone on its line, its label on the next
        elif re.match(r"^((\d+(\.\d+)*\.|[a-z]\.|[a-z]\)|\d+\)|●|•|–)\s|[•●]$)", line):
            out += "\n" + line
        elif re.match(r"^[•●] ", out.split("\n")[-1]) and is_label(out.split("\n")[-1]) and line[:1].isupper():
            out += "\n" + line  # "• Tajwid" is a label; its description starts on the next line
        elif out.endswith("-") and not out.endswith(" -"):
            out += line
        else:
            out += " " + line
    return out


PAGENO = re.compile(r"^\s*-\s*\d+\s*-\s*$")


def mend_words(text, vocab):
    """Rejoin a word that a narrow table cell broke without a hyphen ("Mempresent asikan") when the joined word
    occurs in the section's own text and the first part does not."""
    words = text.split(" ")
    out, i = [], 0
    while i < len(words):
        a = words[i]
        if i + 1 < len(words):
            b = words[i + 1]
            ka, kb = a.lower().strip("(-"), re.sub(r"[^a-z]", "", b.lower())
            if len(ka) >= 4 and ka.isalpha() and b[:1].islower() and ka not in vocab and (ka + kb) in vocab:
                out.append(a + b)
                i += 2
                continue
        out.append(a)
        i += 1
    return " ".join(out)


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

        prose_parts.append("\n".join(x for x in (page.filter(outside).extract_text() or "").split("\n")
                                     if not PAGENO.match(x)))
        for t in tables:
            # merged cells come back as None (SK 9941 tables); drop them
            rows = [[c for c in r if c is not None] for r in t.extract()]
            if not rows or not rows[0]:
                continue
            first = next((c for c in rows[0] if c and c.strip()), "")
            if first.strip().lower().startswith("elemen"):
                hdr = [_clean_cell(c).lower() for c in rows[0] if c and c.strip()]
                header = hdr
                rows = rows[1:]
            elif header and len(rows[0]) == len(header) and pno > c_pages[0] and t.bbox[1] < 120:
                hdr = header  # continuation of the table on the next page without a repeated header row
            else:
                continue
            for ri, r in enumerate(rows):
                cells = [_clean_cell(c) for c in r]
                if len(cells) != len(hdr):
                    cells = [c for c in cells if c]
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
                if name and name[:1].islower() and not desc and elements:
                    # a name cell that the table splits over two rows ("Analisis Data" / "dan Peluang")
                    elements[-1]["name"] += " " + name
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
    vocab = set(re.findall(r"[a-z]+", " ".join(norm_space(t) for _, t in sec["lines"]).lower()))
    for e in elements:
        e.pop("_page", None)
        e["name"] = mend_words(norm_space(e["name"].replace("\n", " ")), vocab)
        if e.get("sub_element") is not None:
            e["sub_element"] = mend_words(norm_space(e["sub_element"].replace("\n", " ")), vocab)
        e["description"] = "\n".join(mend_words(norm_space(x), vocab) for x in e["description"].split("\n"))
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
        # "Pada akhir fase fondasi" is printed in lower case in 046 Lampiran V XXXII.4
        mi = re.match(r"^(?:Pada akhir [Ff]ase|Rumusan Capaian Pembelajaran Fase) ([A-F]|[Ff]ondasi)\b", s)
        if mi and cur is None:
            cur = {"phase": mi.group(1).capitalize(), "applies_to": None, "page": pno, "numbered": False, "num": None, "intro": "",
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


def lingkup_tables(a_pages):
    """PAUD (046 Lampiran I) prints, inside A. Rasional, one table per element: Lingkup Capaian Pembelajaran |
    Deskripsi. Returns the rasional prose outside those tables and the rows grouped per table, or (None, [])."""
    groups, prose = [], []
    for pno in a_pages:
        page = PDF.pages[pno - 1]
        tables = [t for t in page.find_tables() if (t.extract()[0][0] or "").strip().lower().startswith("lingkup")]
        boxes = [t.bbox for t in tables]

        def outside(obj, boxes=boxes):
            x, y = (obj.get("x0", 0) + obj.get("x1", 0)) / 2, (obj.get("top", 0) + obj.get("bottom", 0)) / 2
            return not any(b[0] <= x <= b[2] and b[1] <= y <= b[3] for b in boxes)

        prose += [x for x in (page.filter(outside).extract_text() or "").split("\n")
                  if not PAGENO.match(x) and "jdih.kemendikdasmen" not in x]
        for t in tables:
            rows = [[_clean_cell(c) for c in r] for r in t.extract()[1:]]
            if rows and not rows[0][0] and groups:
                groups[-1][-1][1] += " " + rows[0][1]  # a description continued from the previous page
                rows = rows[1:]
            else:
                groups.append([])
            groups[-1] += [[r[0], r[1]] for r in rows if len(r) == 2]
    if not groups:
        return None, []
    text = "\n".join(prose)
    m1, m2 = re.search(r"A\.\s*Rasional\s*\n", text), re.search(r"\nB\.\s*Tujuan\s*\n", text)
    return join_lines(text[m1.end() if m1 else 0: m2.start() if m2 else len(text)].split("\n")), groups


def parse_section(sec, issues):
    parts = split_parts(sec)
    for k in "ABCD":
        if k not in parts:
            issues.append(f"{sec['title']}: part {k} missing")
            parts.setdefault(k, [])
    c_pages = sorted({p for p, _ in parts["C"]} | ({parts["D"][0][0]} if parts["D"] else set()))
    karakteristik, elements = element_table(sec, c_pages)
    rasional, lingkup = None, []
    if any("Lingkup Capaian" in t for _, t in parts["A"]):
        rasional, lingkup = lingkup_tables(sorted({p for p, _ in parts["A"]} | ({parts["B"][0][0]} if parts["B"] else set())))
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
    if lingkup:
        # one table per element, in the order of the CP; the element names come from the CP headings
        cp_names = [o["element"] for o in phases[0]["outcomes"]] if phases else []
        if len(cp_names) != len(lingkup):
            issues.append(f"{sec['title']}: part {len(lingkup)} lingkup tables for {len(cp_names)} elements")
        else:
            elements = [{"name": n, "sub_element": sub, "description": desc}
                        for n, rows in zip(cp_names, lingkup) for sub, desc in rows]
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
        "key": key_of(clean_heading(sec["title"])), "title": nice_title(clean_heading(sec["title"])),
        "title_printed": sec["title"],
        "number": re.sub(r"\.\s+", ".", sec["number"]) if sec["number"] else None, "pages": [sec["page"], pages[-1] if pages else sec["page"]],
        "rasional": rasional if rasional is not None else join_lines([l for _, l in parts["A"]]),
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
RELIGION_FILES = {"umum": "agama.json.gz", "pendidikan-khusus": "pendidikan-khusus-agama.json.gz"}
# every file of the set in index order: 046/9941 appendices, then the religion files from 020
SET_FILES = ["paud", "umum", "agama", "smk", "kesetaraan", "pendidikan-khusus", "pendidikan-khusus-agama", "madrasah"]
HARD = ("part ", " empty", "no phases")


# Grades of each phase as 046 prints them for most subjects ("Umumnya untuk Kelas ..."); SLB adds mental age.
PHASE_GRADES = {"A": [1, 2], "B": [3, 4], "C": [5, 6], "D": [7, 8, 9], "E": [10], "F": [11, 12]}
ROMAN_N = {"I": 1, "II": 2, "III": 3, "IV": 4, "V": 5, "VI": 6, "VII": 7, "VIII": 8, "IX": 9, "X": 10, "XI": 11,
           "XII": 12}
# Printed errors that the document itself resolves (F-031): (file, printed number) -> (number, reason)
NUMBER_FIXES = {("pendidikan-khusus", "XXII.3"): ("XXXII.3", "the neighbouring sections are XXXII.2 and XXXII.4")}
# (file, number, printed text, text used, reason); applied to element names and outcome headings of that subject
TEXT_FIXES = [("smk", "V.43", "dan fiSiologi", "dan Fisiologi",
               "the element table prints the ligature glyph and a capital S ('ﬁSiologi'); its CP heading has "
               "'Anatomi dan Fisiologi Kecantikan'")]


def printed_grades(applies_to):
    m = re.search(r"[Kk]elas\s+(.*)$", applies_to or "")
    if not m:
        return None
    nums = re.findall(r"\b(XII|XI|IX|X|VIII|VII|VI|IV|V|III|II|I|1[0-2]|[1-9])\b", m.group(1))
    return sorted({ROMAN_N.get(n) or int(n) for n in nums}) or None


def finish_subject(sub, source, levels, issues, fname, errata):
    if (fname, sub["number"]) in NUMBER_FIXES:
        num, why = NUMBER_FIXES[(fname, sub["number"])]
        errata.append({"subject": sub["key"], "field": "number", "printed": sub["number"], "used": num,
                       "page": sub["pages"][0], "reason": why})
        sub["number_printed"], sub["number"] = sub["number"], num
    for f, num, old, new, why in TEXT_FIXES:
        if f == fname and sub["number"] == num:
            hit = False
            for e in sub["elements"]:
                if old in e["name"]:
                    e["name"], hit = e["name"].replace(old, new), True
            for ph in sub["phases"]:
                for o in ph["outcomes"]:
                    if old in o["element"]:
                        o["element"], hit = o["element"].replace(old, new), True
            if not hit:
                sys.exit(f"text fix not applied: {f} {num} {old!r}")
            errata.append({"subject": sub["key"], "field": "element name", "printed": old, "used": new,
                           "page": sub["pages"][0], "reason": why})
    unmatched = {}
    for x in issues:
        m = re.search(r"Fase (\S+) element '(.*)' not in table", x)
        if m:
            unmatched.setdefault(m.group(2), []).append(m.group(1))
    notes = [f"CP heading '{el}' (Fase {', '.join(ph)}) is not printed with this name in the element table"
             for el, ph in unmatched.items()]
    for ph in sub["phases"]:
        if ph.get("applies_to"):
            ph["applies_to"] = re.sub(r"[).]+$", "", ph["applies_to"]).strip()
            printed = printed_grades(ph["applies_to"])
            if ph["phase"] in PHASE_GRADES and printed and printed != PHASE_GRADES[ph["phase"]]:
                errata.append({"subject": sub["key"], "field": f"Fase {ph['phase']} applies_to",
                               "printed": ph["applies_to"], "page": ph["page"],
                               "reason": f"names grades {printed}; Fase {ph['phase']} is grades "
                                         f"{PHASE_GRADES[ph['phase']]} everywhere else in the decree. Kept as "
                                         "printed; use the phase, not this text, for grades"})
            if re.search(r"\b(\w+) \1\b", ph["applies_to"]):
                errata.append({"subject": sub["key"], "field": f"Fase {ph['phase']} applies_to",
                               "printed": ph["applies_to"], "page": ph["page"],
                               "reason": "a word is printed twice; kept as printed"})
        for o in ph["outcomes"]:
            t = (o["text"] or "").strip()
            if t in ("", "-", "–"):
                o["text"] = None
                o["no_cp"] = True
    sub["source"] = f"{source} ({'number ' + sub['number'] + ', ' if sub['number'] else ''}PDF p. "\
                    f"{sub['pages'][0]}–{sub['pages'][1]})"
    sub["levels"] = levels
    if printed_twice(sub["title_printed"]):
        notes.append("the heading is printed twice in the source")
    if notes:
        sub["source_notes"] = notes
    return sub


def build(src, out):
    global PDF, ZWMODE
    import gzip
    import logging
    import pdfplumber
    logging.getLogger("pdfminer").setLevel(logging.ERROR)
    opened = {}
    hard = []
    os.makedirs(os.path.join(out, "capaian-pembelajaran"), exist_ok=True)
    for fname, pdfname, first, last, source, levels, title in PARTS:
        path = os.path.join(src, pdfname)
        if path not in opened:
            opened[path] = (pdfplumber.open(path), pdf_pages(path))
        PDF, pages = opened[path]
        ZWMODE = sum(p.count(ZW) for p in pages) > 100
        subjects, keys, errata = [], set(), []
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
            subjects.append(finish_subject(sub, source, levels, issues, fname, errata))
        data = {"file": fname, "source": source, "subjects": subjects}
        if errata:
            data["errata"] = errata
        if fname in RELIGION_FILES:
            data["religion"] = (f"Pendidikan Agama dan Budi Pekerti (six religions) of this appendix was replaced by "
                                f"Kepka BKPDM 020/2026; it is in {RELIGION_FILES[fname]} (scan, checked transcription, "
                                f"tools/converters/capaian-pembelajaran-agama.py).")
        raw = json.dumps(data, ensure_ascii=False, indent=1).encode("utf-8") + b"\n"
        if re.search(rb"\bNIP\b|\b\d{18}\b", raw):
            sys.exit(f"{fname}: looks like a NIP (personal data) in the output")
        with open(os.path.join(out, "capaian-pembelajaran", fname + ".json.gz"), "wb") as f:
            with gzip.GzipFile(filename="", mode="wb", fileobj=f, mtime=0) as g:
                g.write(raw)
        print(f"{fname}: {len(subjects)} subjects")
    if hard:
        sys.exit("structure problems:\n  " + "\n  ".join(hard))
    return write_index(out)


def write_index(out):
    """index.json from the files present (046/9941 appendices and the 020 religion files), in SET_FILES order."""
    import gzip
    d = os.path.join(out, "capaian-pembelajaran")
    index, files, totals = [], [], {"subjects": 0, "phases": 0, "outcomes": 0}
    for fname in SET_FILES:
        path = os.path.join(d, fname + ".json.gz")
        if not os.path.exists(path):
            continue
        files.append(fname + ".json.gz")
        for sub in json.load(gzip.open(path))["subjects"]:
            index.append({"file": fname + ".json.gz", "key": sub["key"], "title": sub["title"],
                          "number": sub["number"], "phases": [p["phase"] for p in sub["phases"]],
                          "levels": sub["levels"], "source": sub["source"]})
            totals["subjects"] += 1
            totals["phases"] += len(sub["phases"])
            totals["outcomes"] += sum(len(p["outcomes"]) for p in sub["phases"])
    missing = [f + ".json.gz" for f in SET_FILES if f + ".json.gz" not in files]
    with open(os.path.join(d, "index.json"), "w", encoding="utf-8") as f:
        doc = {"name": "Capaian Pembelajaran", "files": files, "totals": totals,
               "phases": {**{"Fondasi": {"grades": [], "note": "PAUD, RA and TKLB"}},
                          **{k: {"grades": v} for k, v in PHASE_GRADES.items()}},
               "phase_note": ("Grades per phase as the decrees print them for most subjects. SLB phases also "
                              "name a mental age (see each phase's applies_to). Use these grades rather than "
                              "the printed applies_to text, which varies and has misprints (see errata)."),
               "subjects": index}
        if missing:
            doc["pending"] = missing
        json.dump(doc, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print(f"index: {totals}" + (f", pending {missing}" if missing else ""))
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
    elif len(sys.argv) == 3 and sys.argv[1] == "--index":
        write_index(sys.argv[2])
    elif len(sys.argv) == 3 and os.path.isdir(sys.argv[1]):
        build(sys.argv[1], sys.argv[2])
    else:
        sys.exit(__doc__)
