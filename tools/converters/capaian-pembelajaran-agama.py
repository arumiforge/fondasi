#!/usr/bin/env python3
"""Religion CP (Pendidikan Agama dan Budi Pekerti) from Kepka BKPDM 020/2026 for the set `capaian-pembelajaran`
(R-15, F-032).

020 is a scan. Its checked transcription lives in sources/capaian-pembelajaran/transkripsi-020/ (format in the
README there); this script parses it into the same structure as the other files of the set and writes
data/capaian-pembelajaran/agama.json.gz (Lampiran I) and pendidikan-khusus-agama.json.gz (Lampiran II).

  python3 -I tools/converters/capaian-pembelajaran-agama.py sources/capaian-pembelajaran data
  python3 -I tools/converters/capaian-pembelajaran-agama.py sources/capaian-pembelajaran data \\
      --ocr <dir with p-NN.txt> --sinaubareng <cp-pendidikan-agama-sd-bkpdm-020-2026.json>

The two optional checks run while the transcription is made and are not needed for a rebuild:
  --ocr          compares each transcribed page with the tesseract draft of the same page and lists every run of
                 three or more words that only one of them has (dropped or doubled lines show up here).
  --sinaubareng  compares phases A–C of Lampiran I with sinaubareng's independent word-by-word transcription.
"""
import gzip
import json
import os
import re
import sys
import difflib

REF = "Kepka BKPDM 020/2026"
PARTS = {
    "1": ("agama", f"{REF}, Lampiran I", ["SD", "MI", "SMP", "MTs", "SMA", "MA", "SMK", "MAK", "Paket A", "Paket B",
                                         "Paket C"]),
    "2": ("pendidikan-khusus-agama", f"{REF}, Lampiran II", ["SDLB", "SMPLB", "SMALB"]),
}
RELIGIONS = ["islam", "kristen", "katolik", "hindu", "buddha", "khonghucu"]
SMALL = {"dan", "atau", "serta", "untuk", "dengan", "di", "ke", "dari", "pada", "yang", "bagi", "dalam"}


def nice_title(printed):
    words = []
    for i, w in enumerate(printed.split()):
        lw = w.lower()
        words.append(lw if i and lw in SMALL else lw[:1].upper() + lw[1:])
    return " ".join(words)


def cells(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def read_section(path):
    """Lines of a transcription file -> list of (page, kind, text). Continuation lines are joined here."""
    out, page = [], None
    with open(path, encoding="utf-8") as f:
        for n, raw in enumerate(f, 1):
            line = raw.rstrip("\n").strip()
            if not line:
                continue
            m = re.match(r"^\[p\. (\d+)\]$", line)
            if m:
                page = int(m.group(1))
                continue
            if page is None:
                sys.exit(f"{path}:{n}: text before the first [p. N]")
            if line.startswith("+ "):
                if not out or out[-1][1] != "text":
                    sys.exit(f"{path}:{n}: '+' continues no paragraph")
                p, k, t = out[-1]
                out[-1] = (p, k, t + " " + line[2:])
            elif line.startswith("|+ "):
                if not out or out[-1][1] != "row":
                    sys.exit(f"{path}:{n}: '|+' continues no table row")
                p, k, t = out[-1]
                prev, more = cells(t), cells("| " + line[3:])
                if len(prev) != len(more):
                    sys.exit(f"{path}:{n}: continued row has {len(more)} cells, row has {len(prev)}")
                out[-1] = (p, k, "| " + " | ".join(" ".join(x for x in (a, b) if x) for a, b in zip(prev, more)) + " |")
            elif line.startswith("|"):
                out.append((page, "row", line))
            elif line.startswith("#"):
                level = len(line) - len(line.lstrip("#"))
                out.append((page, f"h{level}", line[level:].strip()))
            else:
                out.append((page, "text", line))
    return out


def tables(rows, path):
    """Rows -> tables; a row whose first cell is "Elemen" starts a new table. An empty first cell repeats the cell
    above (merged cells in the source)."""
    out = []
    for r in rows:
        c = cells(r)
        if c[0].lower() == "elemen":
            out.append(([h.lower() for h in c], []))
            continue
        if not out:
            sys.exit(f"{path}: table row before a header row: {r[:80]}")
        hdr, recs = out[-1]
        if len(c) != len(hdr):
            sys.exit(f"{path}: table row has {len(c)} cells, header {len(hdr)}: {r[:80]}")
        if not c[0]:
            if not recs:
                sys.exit(f"{path}: first row of a table has an empty first cell")
            c[0] = recs[-1][hdr[0]]
        recs.append(dict(zip(hdr, c)))
    return out


def parse(path):
    items = read_section(path)
    if not items or items[0][1] != "h1":
        sys.exit(f"{path}: must start with '# <number> <heading>'")
    m = re.match(r"^(\d\.\d)\s+(.*)$", items[0][2])
    number, printed = m.group(1), m.group(2)
    part, buf, rows = None, {"A": [], "B": [], "C": [], "D": []}, {"C": []}
    elements, phases, ph, out = [], [], None, None
    for page, kind, text in items[1:]:
        if kind == "h2":
            part = text[0]
            if not re.match(r"^[A-D]\. (Rasional|Tujuan|Karakteristik|Capaian Pembelajaran)$", text):
                sys.exit(f"{path}: unexpected part heading '{text}'")
            continue
        if kind == "h3":
            m = re.match(r"^(\d+)\. Fase ([A-F])\s*\((.*)\)$", text)
            if not m:
                sys.exit(f"{path}: bad phase heading '{text}'")
            ph = {"phase": m.group(2), "applies_to": m.group(3), "page": page, "intro": "", "outcomes": []}
            phases.append(ph)
            out = None
            continue
        if kind == "h4":
            m = re.match(r"^(\d+)\.(\d+)\.?\s+(.*)$", text)
            if not m or ph is None:
                sys.exit(f"{path}: bad element heading '{text}'")
            out = {"element": m.group(3), "text": "", "page": page}
            ph["outcomes"].append(out)
            continue
        if part == "D":
            if kind == "row":
                ph.setdefault("_rows", []).append(text)
            elif out is not None:
                out["text"] = (out["text"] + "\n" + text).strip()
            elif ph is not None:
                ph["intro"] = (ph["intro"] + "\n" + text).strip()
            else:
                buf["D"].append(text)
            continue
        if kind == "row":
            rows[part if part in rows else "C"].append(text)
        else:
            buf[part].append(text)
    for hdr, recs in tables(rows["C"], path):
        for r in recs:
            e = next((x for x in elements if x["name"] == r["elemen"]), None)
            if e is None:
                e = {"name": r["elemen"], "description": None}
                elements.append(e)
            if "deskripsi" in r:
                e["description"] = r["deskripsi"]
            if r.get("subelemen"):
                e.setdefault("sub_elements", []).append(r["subelemen"])
    for ph in phases:
        if "_rows" in ph:  # CP printed as a table: Elemen | (Subelemen |) Capaian Pembelajaran
            recs = [r for _, rs in tables(ph.pop("_rows"), path) for r in rs]
            for r in recs:
                o = {"element": r.get("elemen", ""), "text": r.get("capaian pembelajaran", ""), "page": ph["page"]}
                if r.get("subelemen"):
                    o["sub_element"] = r["subelemen"]
                ph["outcomes"].append(o)
        for o in ph["outcomes"]:
            if o["text"] in ("-", "–", ""):
                o["text"], o["no_cp"] = None, True
        if not ph["outcomes"]:
            sys.exit(f"{path}: Fase {ph['phase']} has no outcomes")
    pages = sorted({p for p, _, _ in items})
    # CP tables print some names differently from the element table ("Nilai- nilai", "Terhadap"); when the letters
    # are the same, the element table's spelling is used and the printed one is listed in source_notes
    canon = {norm_key(e["name"]): e["name"] for e in elements}
    canon.update({norm_key(x): x for e in elements for x in e.get("sub_elements", [])})
    notes = set()
    for ph in phases:
        for o in ph["outcomes"]:
            for k in ("element", "sub_element"):
                v = o.get(k)
                if v and canon and v not in canon.values():
                    if norm_key(v) in canon:
                        notes.add(f"CP heading '{v}' is printed '{canon[norm_key(v)]}' in the element table")
                        o[k] = canon[norm_key(v)]
                    else:
                        notes.add(f"CP heading '{v}' is not printed with this name in the element table")
    sub = {
        "key": key_of(printed), "title": nice_title(printed), "title_printed": printed, "number": number,
        "pages": [pages[0], pages[-1]],
        "rasional": "\n".join(buf["A"]), "tujuan": "\n".join(buf["B"]), "karakteristik": "\n".join(buf["C"]),
        "elements": elements, "phases": phases,
    }
    if notes:
        sub["source_notes"] = sorted(notes)
    for k in ("rasional", "tujuan", "karakteristik"):
        if not sub[k]:
            sys.exit(f"{path}: {k} is empty")
    return sub


def norm_key(s):
    return re.sub(r"[^a-z0-9]+", "", s.lower())


def key_of(title):
    s = re.sub(r"^CAPAIAN PEMBELAJARAN\s+", "", title).lower()
    return re.sub(r"[^a-z0-9]+", "_", s).strip("_")


# ------------------------------------------------------------------ checks used while transcribing

def words(t):
    import unicodedata
    t = "".join(c for c in unicodedata.normalize("NFKD", t) if not unicodedata.combining(c))
    return re.findall(r"[a-z0-9]+", t.lower())


def check_ocr(path, ocr_dir):
    """Word runs of 3+ that only the transcription or only the OCR has, per page (diacritics ignored)."""
    by_page, page = {}, None
    for line in open(path, encoding="utf-8"):
        m = re.match(r"^\[p\. (\d+)\]$", line.strip())
        if m:
            page = int(m.group(1))
        elif line.strip():
            by_page.setdefault(page, []).append(re.sub(r"^(#+|\+|\|\+)\s", "", line.strip()))
    found = 0
    for page, texts in sorted(by_page.items()):
        f = os.path.join(ocr_dir, f"p-{page:02d}.txt")
        if not os.path.exists(f):
            continue
        a = words(" ".join(texts))
        b = words(open(f, encoding="utf-8").read())
        sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
        for op, i1, i2, j1, j2 in sm.get_opcodes():
            if op == "equal":
                continue
            if (i2 - i1) >= 3 or (j2 - j1) >= 3:
                found += 1
                print(f"  p.{page} {op}: transcription [{' '.join(a[i1:i2])[:120]}] / ocr [{' '.join(b[j1:j2])[:120]}]")
    return found


def check_sinaubareng(subjects, path):
    d = json.load(open(path, encoding="utf-8"))
    norm = lambda t: (t or "").replace("’", "'").replace("‘", "'").replace("ŏ", "ǒ").replace("ĭ", "ǐ") \
        .replace("ŭ", "ǔ").replace("ă", "ǎ").replace("ĕ", "ě")  # noqa: E731  (sinaubareng stores carons)
    diffs, compared = 0, 0
    for rel in d["religions"]:
        sub = next((s for s in subjects if s["number"] == rel["decree_section"]), None)
        if not sub:
            continue
        for sph in rel["phases"]:
            ph = next(p for p in sub["phases"] if p["phase"] == sph["phase"])
            if sph.get("summary") and norm(sph["summary"]) != norm(ph["intro"].split("\n")[0]):
                diffs += 1
                print(f"  {rel['key']} {sph['phase']} intro:\n    ours: {ph['intro']}\n    sb:   {sph['summary']}")
            ours = [(o["element"], o.get("sub_element"), o["text"]) for o in ph["outcomes"]]
            theirs = [(o["element"], o.get("sub_element"), o["text"]) for o in sph["outcomes"]]
            if len(ours) != len(theirs):
                diffs += 1
                print(f"  {rel['key']} {sph['phase']}: {len(ours)} outcomes, sinaubareng {len(theirs)}")
            for a, b in zip(ours, theirs):
                compared += 1
                if norm(a[2]) != norm(b[2]) or norm(a[0]) != norm(b[0]) and norm(a[0]) != norm(b[1] or ""):
                    diffs += 1
                    print(f"  {rel['key']} {sph['phase']} {a[0]} / {b[0]} {b[1] or ''}:\n    ours: {a[2]}\n    sb:   {b[2]}")
    print(f"sinaubareng: {compared} outcomes compared, {diffs} differences")
    return diffs


def build(src, out, ocr=None, sb=None):
    tdir = os.path.join(src, "transkripsi-020")
    files = sorted(f for f in os.listdir(tdir) if re.match(r"^\d\.\d-[a-z]+\.txt$", f))
    by_part = {}
    for f in files:
        sub = parse(os.path.join(tdir, f))
        fname, source, levels = PARTS[sub["number"][0]]
        sub["source"] = f"{source} (number {sub['number']}, PDF p. {sub['pages'][0]}–{sub['pages'][1]})"
        sub["levels"] = levels
        by_part.setdefault(fname, []).append(sub)
        if ocr:
            print(f"{f}: OCR comparison")
            check_ocr(os.path.join(tdir, f), ocr)
    if sb:
        check_sinaubareng(by_part.get("agama", []), sb)
    os.makedirs(os.path.join(out, "capaian-pembelajaran"), exist_ok=True)
    for fname, subjects in by_part.items():
        data = {"file": fname, "source": PARTS[subjects[0]["number"][0]][1] + " (scan; checked transcription in "
                "sources/capaian-pembelajaran/transkripsi-020/)", "subjects": subjects}
        raw = json.dumps(data, ensure_ascii=False, indent=1).encode("utf-8") + b"\n"
        with open(os.path.join(out, "capaian-pembelajaran", fname + ".json.gz"), "wb") as f:
            with gzip.GzipFile(filename="", mode="wb", fileobj=f, mtime=0) as g:
                g.write(raw)
        n = sum(len(p["outcomes"]) for s in subjects for p in s["phases"])
        print(f"{fname}: {len(subjects)} subjects, {n} outcomes")
    return by_part


if __name__ == "__main__":
    args = sys.argv[1:]
    opts = {}
    while len(args) > 2 and args[-2].startswith("--"):
        opts[args[-2][2:]] = args[-1]
        args = args[:-2]
    if len(args) != 2:
        sys.exit(__doc__)
    build(args[0], args[1], opts.get("ocr"), opts.get("sinaubareng"))
