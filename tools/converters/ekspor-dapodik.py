#!/usr/bin/env python3
"""Build data/ekspor-dapodik: the column layout of the Excel exports of the Dapodik application (F-038).

Input: Excel files exported from Aplikasi Dapodik versi 2027 by a school (received from the user). They are kept
OUTSIDE the repository, because exports carry the school's operator and, once filled, personal data of students
and staff. This converter reads only structure:

  - list exports (Daftar Guru, Daftar Tenaga Kependidikan, Daftar Peserta Didik, Rekap Pembelajaran): the sheet
    name, the row and the text of the column headers (two header rows where columns are grouped);
  - the PTK form (Formulir Pendidik dan Tenaga Kependidikan, F-PTK): section titles, numbered field labels and the
    column headers of its tables, taken only from the label columns (A to H) and the "No" header rows.

No cell value is copied. Before writing, the converter collects every other non-empty cell of every file (school
name, dates, values a filled form carries) and refuses to write if any of them (4 characters or more) appears in
the output, and it refuses any output string with six or more digits in a row.

  python3 -I tools/converters/ekspor-dapodik.py <dir with the xlsx files> data/ekspor-dapodik
"""
import datetime
import hashlib
import json
import os
import re
import sys

import openpyxl

VERSION = "2026-10-20"  # newest "Tanggal Unduh" printed in the exports
APP = "Aplikasi Dapodik versi 2027, semester 2026/2027 Ganjil (20261)"

LISTS = {  # file kind -> (export title printed in A1, label)
    "Daftar guru": ("guru", "Daftar Guru"),
    "Daftar tendik": ("tendik", "Daftar Tenaga Kependidikan"),
    "Daftar Peserta Didik": ("peserta_didik", "Daftar Peserta Didik"),
    "Rekap Mengajar": ("pembelajaran", "Rekap Pembelajaran"),
}

GENERIC = {"Daftar Guru", "Daftar Tenaga Kependidikan", "Daftar Peserta Didik", "Rekap Pembelajaran", "Nama Sekolah",
           "NPSN", "Braille", "Bahasa Isyarat", "RT", "RW", "Kode Pos", "Bujur", "L", "P", "Masih", "Masih Menerima"}
used = set()       # (file, coordinate) of cells copied into the output
forbidden = set()  # every other cell text


def text(v):
    return re.sub(r"\s+", " ", str(v)).strip()


def header_row(rows, first):
    for i, r in enumerate(rows):
        if r and text(r[0] or "") == first:
            return i
    raise SystemExit(f"no header row starting with {first!r}")


def list_export(path, ws):
    rows = list(ws.iter_rows())
    kind, label = LISTS[ws.title]
    hi = header_row([[c.value for c in r] for r in rows], "No")
    cols = []
    for c in rows[hi]:
        if c.value not in (None, ""):
            cols.append({"col": c.column_letter, "label": text(c.value)})
            used.add((path, c.coordinate))
    sub = []
    if hi + 1 < len(rows) and any(c.value not in (None, "") for c in rows[hi + 1]) \
            and text(rows[hi + 1][0].value or "") == "":  # second header row (Data Ayah / Ibu / Wali)
        for c in rows[hi + 1]:
            if c.value not in (None, ""):
                sub.append({"col": c.column_letter, "label": text(c.value)})
                used.add((path, c.coordinate))
    # attach sub-columns to the grouped header to their left
    if sub:
        letters = [x["col"] for x in cols]
        for s in sub:
            parent = max((x for x in cols if openpyxl.utils.column_index_from_string(x["col"])
                          <= openpyxl.utils.column_index_from_string(s["col"])),
                         key=lambda x: openpyxl.utils.column_index_from_string(x["col"]))
            parent.setdefault("sub", []).append(s)
        del letters
    data_rows = sum(1 for r in rows[hi + 1 + bool(sub):] if any(c.value not in (None, "") for c in r))
    if data_rows:
        raise SystemExit(f"{os.path.basename(path)}: {data_rows} data rows; use an export without data rows")
    first_data_row = hi + 2 + bool(sub)
    return kind, {"label": label, "sheet": ws.title, "title_rows": hi, "header_row": hi + 1,
                  "header_rows": 1 + bool(sub), "first_data_row": first_data_row,
                  "title_lines": ["judul ekspor", "nama satuan pendidikan", "kecamatan, kabupaten/kota, provinsi",
                                  "tanggal unduh dan pengunduh"][:hi] if kind != "pembelajaran" else
                  ["judul ekspor", "nama sekolah", "NPSN", "semester", "tanggal", "pengunduh"],
                  "columns": cols}


def ptk_form(path, ws):
    """Section titles, numbered fields and table headers of the F-PTK sheet (labels only)."""
    sections, cur, in_table = [], None, False
    for r in ws.iter_rows():
        cells = {c.column_letter: c for c in r if c.value not in (None, "")}
        if not cells:
            continue
        a = cells.get("A")
        av = text(a.value) if a is not None else ""
        if a is not None and av == "No":  # table header row
            cols = [{"col": k, "label": text(c.value)} for k, c in cells.items()]
            for c in cells.values():
                used.add((path, c.coordinate))
            cur["table"] = cols
            in_table = True
            continue
        if a is not None and not re.fullmatch(r"\d+", av) and len(cells) == 1 and av:
            if av.upper().startswith("FORMULIR"):
                continue
            cur = {"title": av, "fields": []}
            sections.append(cur)
            used.add((path, a.coordinate))
            in_table = False
            continue
        if in_table:
            continue  # table rows hold values
        # labels sit in columns B-H ("Jika PNS," in C and "N I P" in H); values start in column I or later
        labs = [c for k, c in sorted(cells.items(), key=lambda kv: openpyxl.utils.column_index_from_string(kv[0]))
                if k in ("B", "C", "D", "E", "F", "G", "H")]
        if cur is None or not labs:
            continue
        field = {"label": " ".join(text(c.value) for c in labs)}
        for c in labs:
            used.add((path, c.coordinate))
        lab = labs[0]
        if a is not None and re.fullmatch(r"\d+", av):
            field["no"] = int(av)
            used.add((path, a.coordinate))
        elif lab.column_letter == "B" and cur["fields"] and field["label"].startswith("("):
            cur["fields"][-1]["hint"] = field["label"]
            continue
        cur["fields"].append(field)
    return sections


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    src, out = sys.argv[1:]
    exports, form, files = {}, None, []
    for name in sorted(os.listdir(src)):
        if not name.endswith(".xlsx"):
            continue
        path = os.path.join(src, name)
        files.append({"bytes": os.path.getsize(path),
                      "sha256": hashlib.sha256(open(path, "rb").read()).hexdigest()})
        wb = openpyxl.load_workbook(path, data_only=True)
        for ws in wb.worksheets:
            if ws.title in LISTS:
                kind, spec = list_export(path, ws)
                exports[kind] = spec
            elif ws.title == "Formulir PTK":
                form = {"label": "Formulir Pendidik dan Tenaga Kependidikan (F-PTK)", "sheet": ws.title,
                        "sections": ptk_form(path, ws)}
            else:
                raise SystemExit(f"{name}: unknown sheet {ws.title!r}")
            for r in ws.iter_rows():
                for c in r:
                    if c.value not in (None, "") and (path, c.coordinate) not in used:
                        forbidden.add(text(c.value))
    if sorted(exports) != ["guru", "pembelajaran", "peserta_didik", "tendik"] or form is None:
        raise SystemExit(f"expected four list exports and the F-PTK form, got {sorted(exports)}")
    obj = {
        "name": "Susunan kolom ekspor Dapodik",
        "app": APP,
        "exports": exports,
        "ptk_form": form,
        "notes": [
            "Only column headers and form labels. The exports were empty of data rows; the F-PTK form came filled "
            "for one person and none of its values is kept.",
            "Daftar Guru and Daftar Tenaga Kependidikan share the same 51 columns.",
            "Daftar Peserta Didik has a second header row under Data Ayah, Data Ibu and Data Wali (`sub`).",
            "Option values and their Dapodik codes are not in these exports; they wait for referensi-dapodik (R-07).",
        ],
    }
    blob = json.dumps(obj, ensure_ascii=False, indent=1)
    strings = set()

    def walk(x):
        if isinstance(x, dict):
            for v in x.values():
                walk(v)
        elif isinstance(x, list):
            for v in x:
                walk(v)
        elif isinstance(x, str):
            strings.add(x)
    walk(obj)
    # A source value may equal an output string only when it is one of these generic words (export titles and
    # labels that the exports also print as titles or as option values of the filled form).
    leaks = sorted(v for v in forbidden if v in strings and v not in GENERIC)
    # Values with digits (numbers of identity cards, decrees, dates) must not appear even inside a longer string.
    leaks += sorted(v for v in forbidden if re.search(r"\d", v) and len(v) >= 6 and v in blob)
    if leaks:
        detail = f": {leaks}" if os.environ.get("SHOW_LEAKS") else " (SHOW_LEAKS=1 lists them)"
        raise SystemExit(f"refusing to write: {len(leaks)} source values would appear in the output{detail}")
    if re.search(r"\d{6,}", blob):
        raise SystemExit("refusing to write: a run of six or more digits in the output")
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "ekspor-dapodik.json"), "w", encoding="utf-8") as f:
        f.write(blob + "\n")
    counts = {k: len(v["columns"]) + sum(len(c.get("sub", [])) for c in v["columns"]) for k, v in exports.items()}
    counts["ptk_form_fields"] = sum(len(s["fields"]) for s in form["sections"])
    counts["ptk_form_tables"] = sum(1 for s in form["sections"] if "table" in s)
    manifest = {
        "version": VERSION,
        "description": "Column layout of the Excel exports of Aplikasi Dapodik versi 2027: Daftar Guru, Daftar Tenaga "
                       "Kependidikan, Daftar Peserta Didik (with the parent sub-columns), Rekap Pembelajaran, and the "
                       "sections, numbered fields and tables of the PTK form (F-PTK). Headers and labels only: no "
                       "personal data, no school data.",
        "status": "ready for these five exports; option codes wait for referensi-dapodik (R-07)",
        "source": f"Exports of {APP}, downloaded by an SMP in Kabupaten Kudus on 2026-10-13 and 2026-10-20 and "
                  "received from the user (2026-11-28); not kept (F-038): sizes and SHA-256 in "
                  "sources/ekspor-dapodik/SOURCE.txt",
        "licence": "Structure of a government application's export (public government system); no content copied",
        "procedure": "python3 -I tools/converters/ekspor-dapodik.py <dir with the xlsx files> data/ekspor-dapodik, "
                     "then tools/data-check --write. The converter refuses to write when any source value would "
                     "appear in the output",
        "counts": counts,
        "files": ["ekspor-dapodik.json"],
    }
    with open(os.path.join(out, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(json.dumps(counts), json.dumps(files))


if __name__ == "__main__":
    main()
