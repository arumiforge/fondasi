#!/usr/bin/env python3
"""Build data/kodepos from cahyadsn/wilayah_kodepos (MIT): the postal code of every village (desa/kelurahan),
keyed by the Kemendagri region code used in data/wilayah.

  git clone --depth 1 https://github.com/cahyadsn/wilayah_kodepos.git /tmp/src   # outside the repository
  python3 -I tools/converters/kodepos.py /tmp/src/db/wilayah_kodepos.sql data/wilayah/wilayah.json.gz data/kodepos

The SQL dump is untrusted input: rows are read with a strict pattern, never executed. The script refuses to write
when a row is malformed, a code is listed twice, or a code is not a village of the `wilayah` set; it reports
villages without a postal code.
"""
import gzip
import json
import os
import re
import sys

ROW = re.compile(r"\('(\d{2}\.\d{2}\.\d{2}\.\d{4})',\s*(?:'(\d{5})'|NULL)\)")


def main(sql_path, wilayah_path, out_dir):
    sql = open(sql_path, encoding="utf-8-sig").read()
    inserts = re.findall(r"INSERT INTO\s+`?wilayah_kodepos`?\s*(?:\([^)]*\))?\s*VALUES\s*(.*?);", sql, re.S | re.I)
    if not inserts:
        sys.exit("no INSERT statements found")
    pairs = {}
    for block in inserts:
        rest = ROW.sub("", block)
        if re.sub(r"[\s,]", "", rest):
            sys.exit(f"unexpected text in an INSERT block: {rest.strip()[:80]!r}")
        for code, postal in ROW.findall(block):
            if code in pairs:
                sys.exit(f"{code} listed twice")
            pairs[code] = postal or None
    villages = {c: n for c, n in json.load(gzip.open(wilayah_path, "rt", encoding="utf-8")) if len(c) == 13}
    unknown = sorted(set(pairs) - set(villages))
    if unknown:
        sys.exit(f"{len(unknown)} codes are not villages of the wilayah set, e.g. {unknown[:5]}")
    missing_village = sorted(set(villages) - set(pairs))
    rows = [[c, pairs[c]] for c in sorted(pairs)]
    os.makedirs(out_dir, exist_ok=True)
    data = json.dumps(rows, ensure_ascii=False, separators=(",", ":")).encode()
    with open(os.path.join(out_dir, "kodepos.json.gz"), "wb") as fh:
        with gzip.GzipFile(fileobj=fh, mode="wb", mtime=0, filename="") as gz:
            gz.write(data)
    no_code = [c for c, p in rows if p is None]
    print(json.dumps({
        "villages": len(rows),
        "postal_codes": len({p for _, p in rows if p}),
        "without_postal_code": len(no_code),
        "without_postal_code_sample": no_code[:10],
        "wilayah_villages_not_listed": len(missing_village),
        "provinces_first_digit": sorted({p[0] for _, p in rows if p}),
    }, indent=1))


if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    main(*sys.argv[1:])
