#!/usr/bin/env python3
"""Build data/referensi-dapodik (R-07, F-039): option labels of the Dapodik application and its data structure.

Sources (sources/referensi-dapodik/, received from the user on 2026-11-28; untrusted input, parsed only):
  referensi-dropdown.json   option lists the user's read-only tool observed in the Dapodik 2027.b user interface
                            (2026-10-12/13): labels in the order shown, no IDs or codes
  katalog-rincian-gtk.json  the 21 detail categories of a GTK record (resource name, label, primary key)
  webservice-fields.json    endpoint and field names of the Dapodik local web service (getSekolah, getGtk,
                            getRombonganBelajar, getPesertaDidik), taken from the user's pull report
Plus one list read in the Panduan Aplikasi Dapodik versi 2027 (status hidup ayah/ibu, page 50, a screenshot).

Labels stay exactly as Dapodik prints them (spelling, duplicates, two income bands); doubtful labels are listed in
`errata` as unresolved (F-031) and never corrected. Codes are not in any source: every list has `codes: null`.

  python3 -I tools/converters/referensi-dapodik.py sources/referensi-dapodik data/referensi-dapodik
"""
import json
import os
import re
import sys

VERSION = "2026-10-13"  # date the lists were observed in Dapodik

# key in the source -> Indonesian title, the Dapodik list/export column it fills, related skema-siswa option list
LISTS = {
    "agama": ("Agama", {"export": "Agama", "webservice": "agama_id"}, "agama"),
    "kebutuhan_khusus": ("Kebutuhan khusus", {"export": "Kebutuhan Khusus", "webservice": "kebutuhan_khusus"}, "abk"),
    "tempat_tinggal": ("Jenis tinggal", {"export": "Jenis Tinggal"}, "tempat_tinggal"),
    "moda_transportasi": ("Alat transportasi", {"export": "Alat Transportasi"}, "transportasi"),
    "pendidikan": ("Jenjang pendidikan orang tua/wali", {"export": "Data Ayah/Ibu/Wali: Jenjang Pendidikan"},
                   "pendidikan"),
    "pekerjaan": ("Pekerjaan orang tua/wali", {"export": "Data Ayah/Ibu/Wali: Pekerjaan",
                                                "webservice": "pekerjaan_ayah_id, pekerjaan_ibu_id, pekerjaan_wali_id"},
                  "pekerjaan"),
    "penghasilan": ("Penghasilan orang tua/wali", {"export": "Data Ayah/Ibu/Wali: Penghasilan"}, "penghasilan"),
    "hobi": ("Hobi", {}, None),
    "cita_cita": ("Cita-cita", {}, None),
    "jenis_pendaftaran": ("Jenis pendaftaran", {"webservice": "jenis_pendaftaran_id"}, None),
}

STATUS_HIDUP = {
    "type": "single", "fields": ["ayah.status_hidup", "ibu.status_hidup"], "labels": ["Hidup", "Wafat"],
    "source": "Panduan Aplikasi Dapodik versi 2027 v1.0 (Juli 2026), 5.2.6, PDF p. 51 (printed p. 50), screenshot "
              "of the Data Ayah Kandung form",
    "observed_date": "2026-07-01", "verified_in_ui": False,
}

# Labels printed in a way that cannot be right as a number or a spelling; kept as printed (F-031).
DOUBTFUL = {
    ("penghasilan", "Rp5.500.001 Rp10.00.000"): "\"Rp10.00.000\" has a missing digit (Rp10.000.000 is likely meant)",
    ("penghasilan", "> 10.0000.000"): "\"10.0000.000\" has four digits in a group (10.000.000 is likely meant)",
    ("penghasilan", "Rp1.000.001 Rp3.000.000"): "no dash between the two amounts",
    ("hobi", "mendaki"): "the only label in lower case",
    ("cita_cita", "Atlit Olahraga"): "\"Atlit\" beside \"Atlet\"; both are offered",
}


def confidence(c):
    if c.get("source") == "user_provided":
        return "operator"  # given by a school operator, not read in the interface
    return "observed_ui" if c.get("verified_in_ui") else "secondary"


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    src, out = sys.argv[1:]
    raw = json.load(open(os.path.join(src, "referensi-dropdown.json"), encoding="utf-8"))
    cats = raw["catalogs"]
    if sorted(cats) != sorted(LISTS):
        raise SystemExit(f"unexpected lists: {sorted(set(cats) ^ set(LISTS))}")
    lists, errata = {}, []
    for key, (title, where, skema) in LISTS.items():
        c = cats[key]
        labels = c["labels"]
        if len(labels) != c["count"]:
            raise SystemExit(f"{key}: {len(labels)} labels, count says {c['count']}")
        for lab in labels:
            if not isinstance(lab, str) or not lab.strip() or len(lab) > 80 or re.search(r"[{}\x00-\x1f]|</?[A-Za-z]", lab):
                raise SystemExit(f"{key}: label not accepted: {lab!r}")
        dups = sorted({x for x in labels if labels.count(x) > 1})
        entry = {"title": title, "type": c["type"], "dapodik_fields": c["fields"], **where,
                 "options": [{"order": i + 1, "label": lab} for i, lab in enumerate(labels)],
                 "codes": None, "confidence": confidence(c), "observed": c.get("observed_date"),
                 "recheck": bool(c.get("requires_live_recheck"))}
        if skema:
            entry["skema_siswa_list"] = skema
        notes = [n for n in [c.get("notes")] if n]
        if key == "pendidikan":
            notes.append("Dapodik shows this list sorted alphabetically.")
        if key == "penghasilan":
            notes.append("Two sets of bands are offered together: six older bands (\"Kurang dari Rp. 500,000\" … "
                         "\"Lebih dari Rp. 20,000,000\") and five newer ones (\"< Rp1.000.000\" … \"> 10.0000.000\"), "
                         "plus \"Tidak Berpenghasilan\".")
        if dups:
            notes.append(f"Duplicate labels kept: {', '.join(dups)}; never pick one by position.")
        if notes:
            entry["notes"] = notes
        lists[key] = entry
        for lab in labels:
            if (key, lab) in DOUBTFUL:
                errata.append({"list": key, "printed": lab, "status": "unresolved", "reason": DOUBTFUL[(key, lab)]})
    lists["status_hidup"] = {"title": "Status hidup ayah/ibu", "type": "single",
                             "dapodik_fields": STATUS_HIDUP["fields"],
                             "options": [{"order": i + 1, "label": x} for i, x in enumerate(STATUS_HIDUP["labels"])],
                             "codes": None, "confidence": "guide_screenshot", "observed": STATUS_HIDUP["observed_date"],
                             "recheck": True, "skema_siswa_list": "status_hidup", "source": STATUS_HIDUP["source"],
                             "notes": ["New in Dapodik 2027 (radio buttons in the Orang Tua/Wali tab)."]}
    if len(errata) != len(DOUBTFUL):
        raise SystemExit("an expected doubtful label is missing from the source")

    gtk = json.load(open(os.path.join(src, "katalog-rincian-gtk.json"), encoding="utf-8"))
    details = [{"resource": k, "label": v["label"], "label_printed": v.get("label_asli", v["label"]),
                "primary_key": v["primary_key"]} for k, v in gtk.items()]
    if len(details) != 21:
        raise SystemExit(f"{len(details)} GTK detail categories, expected 21")
    ws = json.load(open(os.path.join(src, "webservice-fields.json"), encoding="utf-8"))
    endpoints = []
    for e in ws["endpoints"]:
        if not re.fullmatch(r"get[A-Za-z]+", e["endpoint"]) or not all(re.fullmatch(r"[a-z_]+", f) for f in e["fields"]):
            raise SystemExit(f"unexpected endpoint or field name in {e['endpoint']!r}")
        endpoints.append({"endpoint": e["endpoint"], "semester_scoped": e["semester_scoped"], "fields": e["fields"]})

    obj = {
        "name": "Referensi Dapodik",
        "app": f"Aplikasi Dapodik {raw['context']['observed_version']}, {raw['context']['observed_period']}",
        "lists": lists,
        "errata": errata,
        "gtk_details": details,
        "webservice": {"note": "Fields the Dapodik local web service returns (read-only pull of 2026-10-13). An *_id "
                               "field comes with *_id_str, the label of the same option.",
                       "semester_id": ws["semester_id"], "endpoints": endpoints},
        "notes": [
            "Labels are as Dapodik shows them, in the order shown. Codes (IDs) were not extracted: `codes` is null in "
            "every list, and an app must not derive a code from the position.",
            "The web service returns codes with their labels (agama_id with agama_id_str, pekerjaan_ayah_id with "
            "pekerjaan_ayah_id_str): reading them there is the way to fill `codes` later.",
            "Lists of skema-siswa differ from these labels (e.g. agama \"Katolik\"/\"Buddha\" vs Dapodik \"Katholik\"/"
            "\"Budha\"; its income bands are not Dapodik's). `skema_siswa_list` names the related list; a mapping is "
            "the app's decision.",
            "Region fields are a live search in Dapodik; use the set wilayah.",
        ],
    }
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "referensi-dapodik.json"), "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
        f.write("\n")
    counts = {"lists": len(lists), "options": sum(len(l["options"]) for l in lists.values()),
              "errata": len(errata), "gtk_details": len(details), "webservice_endpoints": len(endpoints),
              "webservice_fields": sum(len(e["fields"]) for e in endpoints)}
    manifest = {
        "version": VERSION,
        "description": "Option labels of Aplikasi Dapodik 2027 for student and parent data (agama, kebutuhan khusus, "
                       "jenis tinggal, alat transportasi, jenjang pendidikan, pekerjaan, penghasilan, status hidup, "
                       "hobi, cita-cita, jenis pendaftaran) as the interface shows them, the 21 detail categories of a "
                       "GTK record, and the field names of the Dapodik local web service. Labels only: codes are not "
                       "included yet.",
        "status": "partial: labels without codes (R-07); refill `codes` from the web service's *_id fields",
        "source": "Read-only observation of the Dapodik 2027.b interface and local web service by the user's tool "
                  "(2026-10-12/13), received 2026-11-28 (sources/referensi-dapodik/); Panduan Aplikasi Dapodik versi "
                  "2027 v1.0 p. 50 for status hidup",
        "licence": "Labels and field names of a public government application (Kemendikdasmen); facts",
        "procedure": "python3 -I tools/converters/referensi-dapodik.py sources/referensi-dapodik data/referensi-dapodik, "
                     "then tools/data-check --write",
        "counts": counts,
        "files": ["referensi-dapodik.json"],
    }
    with open(os.path.join(out, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(json.dumps(counts))


if __name__ == "__main__":
    main()
