#!/usr/bin/env python3
"""Build data/sekolah (schools of every level) from referensi.data.kemendikdasmen.go.id.

Two steps, so the slow crawl and the conversion are separate and repeatable:

  python3 -I tools/converters/sekolah.py fetch [--groups=dikdas,dikmen] RAW_DIR [PROVINCE_CODE ...]
      Saves the public list pages unchanged: per province and group, the list of every district
      (kecamatan). Groups: dikdas (SD, MI, SMP, MTs…), dikmen (SMA, MA, SMK, SLB…), paud (TK, KB, RA, TPA,
      SPS…), dikmas (PKBM, SKB, courses…). Polite: one request per second, resumable (pages already saved
      are skipped; a page without the school table is never saved). PROVINCE_CODE is the 6-digit Dapodik
      code, e.g. 030000 for Jawa Tengah, or a regency code (030100) to fetch one regency; without codes, every
      province is fetched.

  python3 -I tools/converters/sekolah.py build [--groups=dikdas,dikmen] RAW_DIR OUT_DIR WILAYAH_JSON_GZ VERSION
      Parses the saved pages (untrusted input: parsed as text, never executed), links each school to the
      Kemendagri region codes of the `wilayah` set by matching names (regency → district → village), and
      writes one gzipped JSON file per province plus manifest.json and a match report.

  python3 -I tools/converters/sekolah.py plan DATA_DIR WORKERS
      Prints WORKERS lists of Dapodik regency codes (xxxx00) with about the same number of units each.

  python3 -I tools/converters/sekolah.py coords DATA_DIR RAW_DIR COORDS_DIR [REGENCY ...] [--threads=N]
      R-17: fetches the detail page /satpen/detail/<npsn> of every unit of the built set (DATA_DIR) in the given
      regencies, one request per second, resumable; raw pages go gzipped to RAW_DIR (outside the repository), and
      each finished regency gets COORDS_DIR/<regency>.tsv with Lintang and Bujur as printed. Without REGENCY every
      regency is fetched; N threads share one queue of units, largest regencies first (F-029).

Region codes are never invented: when a name does not match uniquely, the code stays null and the school
is listed in the report.
"""
import gzip
import html
import json
import os
import re
import sys
import threading
import time
import unicodedata
import urllib.request

BASE = "https://referensi.data.kemendikdasmen.go.id"
UA = "fondasi-data-converter (public reference data; 1 request/s)"
# group → (jalur filter, suffix after the region code in URLs; PAUD pads the code with two spaces)
GROUP_URL = {"dikdas": ("jf", ""), "dikmen": ("jf", ""), "paud": ("all", "%20%20"), "dikmas": ("jn", "")}
GROUPS = ("dikdas", "dikmen")
# F-028: every form listed in the formal groups is kept (SPK, Pendidikan Diniyah Formal included); from Dikmas only
# the equivalency providers; schools abroad ("Luar Negeri", 350000) are left out.
KEEP_FORMS = {"dikmas": {"PKBM", "SKB"}}
EXCLUDED_PROVINCES = {"350000"}


def url(group, code, level):
    jalur, pad = GROUP_URL[group]
    return f"{BASE}/satpen/{group}/{code}{pad}/{level}?jalur={jalur}&status=all"


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read().decode("utf-8", "replace")
        except Exception as e:  # network hiccups: back off and retry; a busy or rate-limiting site gets a long pause
            if attempt == 4:
                raise
            busy = getattr(e, "code", None) in (429, 502, 503, 504)
            time.sleep((60 if busy else 5) * (attempt + 1))
            print(f"  retry {url}: {e}", file=sys.stderr, flush=True)


def child_links(page, group, level, parent_prefix):
    codes = re.findall(rf'href="/satpen/{group}/(\d{{6}})(?:%20)*/{level}\?', page)
    seen = []
    for c in codes:
        if c.startswith(parent_prefix) and c not in seen:
            seen.append(c)
    return seen


def child_counts(page, group, level, prefix):
    """Child code → {form: count} from the summary table of a regency page (headers such as 'PKBM ↕')."""
    heads = [re.sub(r"[^\w ]", "", text(h)).strip() for h in re.findall(r"<th[^>]*>(.*?)</th>", page, re.S)]
    out = {}
    for r in re.findall(r"<tr[^>]*>(.*?)</tr>", page, re.S):
        m = re.search(rf'href="/satpen/{group}/(\d{{6}})(?:%20)*/{level}\?', r)
        cells = [text(c) for c in re.findall(r"<td[^>]*>(.*?)</td>", r, re.S)]
        if m and m.group(1).startswith(prefix) and len(cells) == len(heads):
            out[m.group(1)] = {h: int(c) for h, c in zip(heads, cells) if c.isdigit()}
    return out


def fetch(raw, provinces, groups=GROUPS):
    os.makedirs(raw, exist_ok=True)

    def cached(path, url, marker):
        """Fetch once; a page must be complete and carry `marker` (list header) to be saved."""
        if os.path.exists(path):
            return open(path, encoding="utf-8").read()
        for attempt in range(3):
            time.sleep(1 if attempt == 0 else 15)
            page = get(url)
            if "</html>" in page and marker in page:
                break
        else:
            if "</html>" not in page:
                raise RuntimeError(f"incomplete page: {url}")
            print(f"  warning: no list header ({marker}) in {url}; saved as is", file=sys.stderr)
        tmp = f"{path}.{os.getpid()}.tmp"  # one name per worker: workers may save the same province page
        with open(tmp, "w", encoding="utf-8") as f:
            f.write(page)
        os.replace(tmp, path)
        return page

    # the national page is always kept: build reads the province names from it
    top = cached(os.path.join(raw, "dikdas-000000.html"), f"{BASE}/satpen/dikdas/000000/0", "Nama Wilayah")
    provinces = provinces or child_links(top, "dikdas", 1, "")
    for code in provinces:
        prov = code[:2] + "0000"
        for group in groups:
            d = os.path.join(raw, prov, group)
            os.makedirs(d, exist_ok=True)
            p1 = cached(os.path.join(d, f"{prov}.html"), url(group, prov, 1), "Nama Wilayah")
            # a regency code (e.g. 030100) fetches only that regency, so several workers can share a province
            kabs = [k for k in child_links(p1, group, 2, prov[:2]) if code == prov or k == code]
            for kab in kabs:
                p2 = cached(os.path.join(d, f"{kab}.html"), url(group, kab, 2), "Nama Wilayah")
                counts = child_counts(p2, group, 3, kab[:4]) if group in KEEP_FORMS else {}
                for kec in child_links(p2, group, 3, kab[:4]):
                    # the regency page counts each form per district: skip districts with none of the kept forms
                    if kec in counts and not any(counts[kec].get(f, 0) for f in KEEP_FORMS[group]):
                        continue
                    cached(os.path.join(d, f"{kec}.html"), url(group, kec, 3), ">NPSN<")
            print(f"fetched {code} {group}", file=sys.stderr, flush=True)


# ---------------------------------------------------------------- coordinates (R-17)

DETAIL = BASE + "/satpen/detail/{}"


def units_by_regency(data_dir):
    """Dapodik regency code (xxxx00) → sorted NPSNs of the units in the built set."""
    out = {}
    for path in sorted(os.listdir(data_dir)):
        if path.endswith(".json.gz"):
            for s in json.load(gzip.open(os.path.join(data_dir, path), "rt", encoding="utf-8")):
                out.setdefault(s["kode_kecamatan_dapodik"][:4] + "00", []).append(s["npsn"])
    return {k: sorted(v) for k, v in out.items()}


def plan(data_dir, workers):
    """Split the regencies into `workers` lists of about the same number of pages (largest first)."""
    units = units_by_regency(data_dir)
    bins = [[0, []] for _ in range(int(workers))]
    for kab in sorted(units, key=lambda k: -len(units[k])):
        b = min(bins, key=lambda b: b[0])
        b[0] += len(units[kab])
        b[1].append(kab)
    for size, kabs in bins:
        print(size, " ".join(sorted(kabs)))


def detail_value(page, label):
    """Text of the detail-value cell after the detail-label `label` (None when the label is missing)."""
    m = re.search(rf'<div class="detail-label">\s*{re.escape(label)}\s*</div>\s*<div class="detail-value">(.*?)</div>',
                  page, re.S)
    return text(m.group(1)) if m else None


TSV_HEADER = "npsn\tlintang\tbujur\tnpsn_halaman\tjenjang\n"


def coords_row(npsn, page):
    """npsn, Lintang and Bujur exactly as printed, the NPSN the page itself shows, and its Jenjang Pendidikan."""
    shown = detail_value(page, "NPSN") or ""
    return [npsn, detail_value(page, "Lintang") or "", detail_value(page, "Bujur") or "", shown.split(" ")[0],
            (detail_value(page, "Jenjang Pendidikan") or "").lower()]


def extract_coords(data_dir, raw, out):
    """Rewrite OUT/<regency>.tsv from the raw pages of every regency already finished (after a format change)."""
    units = units_by_regency(data_dir)
    for f in sorted(os.listdir(out)):
        kab = f[:-4]
        if f.endswith(".tsv") and kab in units:
            rows_ = [coords_row(n, gzip.open(os.path.join(raw, kab, f"{n}.html.gz"), "rt", encoding="utf-8").read())
                     for n in units[kab]]
            write_tsv(os.path.join(out, f), rows_)


def write_tsv(path, rows_):
    with open(path + ".tmp", "w", encoding="utf-8") as f:
        f.write(TSV_HEADER)
        f.writelines("\t".join(r) + "\n" for r in rows_)
    os.replace(path + ".tmp", path)


def fetch_detail(npsn, path):
    """Fetch one detail page (complete, with its detail table) and save it gzipped."""
    page = get(DETAIL.format(npsn))
    for _ in range(2):
        if "</html>" in page and 'class="detail-label"' in page:
            break
        time.sleep(15)
        page = get(DETAIL.format(npsn))
    if "</html>" not in page:
        raise RuntimeError(f"incomplete page: {DETAIL.format(npsn)}")
    tmp = f"{path}.{os.getpid()}.{threading.get_ident()}.tmp"
    with gzip.open(tmp, "wt", encoding="utf-8") as f:
        f.write(page)
    os.replace(tmp, path)


def fetch_coords(data_dir, raw, out, regencies, threads=1):
    """Fetch the detail page of every unit of the given Dapodik regencies (all regencies when none is given).

    THREADS workers share one queue of units (largest regencies first), each waiting a second between its
    requests (F-029). Raw pages are kept gzipped under RAW/<regency>/<npsn>.html.gz and never fetched twice;
    when a regency is complete its extract OUT/<regency>.tsv is written. Run one process at a time."""
    import queue
    units = units_by_regency(data_dir)
    os.makedirs(out, exist_ok=True)
    regencies = regencies or sorted(units, key=lambda k: -len(units[k]))
    todo, left, lock, failed = queue.Queue(), {}, threading.Lock(), []

    def finish(kab):
        rows_ = [coords_row(n, gzip.open(os.path.join(raw, kab, f"{n}.html.gz"), "rt", encoding="utf-8").read())
                 for n in units[kab]]
        write_tsv(os.path.join(out, f"{kab}.tsv"), rows_)
        print(f"done {kab} {len(rows_)} units", file=sys.stderr, flush=True)

    for kab in regencies:
        if os.path.exists(os.path.join(out, f"{kab}.tsv")) or kab not in units:
            continue
        os.makedirs(os.path.join(raw, kab), exist_ok=True)
        missing = [n for n in units[kab] if not os.path.exists(os.path.join(raw, kab, f"{n}.html.gz"))]
        if not missing:
            finish(kab)
            continue
        left[kab] = len(missing)
        for n in missing:
            todo.put((kab, n))
    print(f"queue: {todo.qsize()} pages in {len(left)} regencies, {threads} threads", file=sys.stderr, flush=True)
    fetched = [0]

    def work():
        while True:
            try:
                kab, npsn = todo.get_nowait()
            except queue.Empty:
                return
            time.sleep(1)
            try:
                fetch_detail(npsn, os.path.join(raw, kab, f"{npsn}.html.gz"))
            except Exception as e:  # get() already retried with pauses: note it and go on
                print(f"failed {kab} {npsn}: {e}", file=sys.stderr, flush=True)
                failed.append(npsn)
                continue
            with lock:
                fetched[0] += 1
                left[kab] -= 1
                last = left[kab] == 0
                if fetched[0] % 1000 == 0:
                    print(f"fetched {fetched[0]}", file=sys.stderr, flush=True)
            if last:
                finish(kab)

    pool = [threading.Thread(target=work, daemon=True) for _ in range(int(threads))]
    for t in pool:
        t.start()
    for t in pool:
        t.join()
    if failed:
        sys.exit(f"{len(failed)} pages failed; run again to retry them")


# ---------------------------------------------------------------- coordinate checks

# Indonesia's extent with a margin (Weh to Rote, Sabang to Merauke); outside it a pair is never a location here
LAT_RANGE, LON_RANGE = (-11.5, 6.5), (94.0, 141.5)
NEAR_KM = 5.0  # simplified boundaries and coastlines: a point this close outside its regency still counts as inside
ISLAND_KM = 50.0  # a point in no regency (sea, small islands) belongs to the nearest regency within this distance


def load_boundaries(path):
    """Kemendagri code → list of polygons (each a list of rings of (lat, lon)) from cahyadsn/wilayah_boundaries SQL.

    The SQL is parsed as text (never executed): each row is ('code','name',lat,lng,'[[...]]')."""
    out = {}
    for f in sorted(os.listdir(path)):
        if not f.endswith(".sql"):
            continue
        for code, coords in re.findall(r"\('([\d.]+)','[^']*',[-\d.eE]+,[-\d.eE]+,'(\[.*?\])'\)", open(
                os.path.join(path, f), encoding="utf-8").read()):
            geo = json.loads(coords)
            # Polygon = [ring, ...], MultiPolygon = [[ring, ...], ...]; a ring is [[lat, lon], ...]
            polys = [geo] if isinstance(geo[0][0][0], (int, float)) else geo
            out[code] = [[[(p[0], p[1]) for p in ring] for ring in poly] for poly in polys]
    return out


def _bbox(polys):
    pts = [p for poly in polys for ring in poly for p in ring]
    return (min(p[0] for p in pts), max(p[0] for p in pts), min(p[1] for p in pts), max(p[1] for p in pts))


def inside(polys, lat, lon):
    """Even-odd rule over every ring (holes included)."""
    hit = False
    for poly in polys:
        for ring in poly:
            j = len(ring) - 1
            for i in range(len(ring)):
                (yi, xi), (yj, xj) = ring[i], ring[j]
                if (yi > lat) != (yj > lat) and lon < (xj - xi) * (lat - yi) / (yj - yi) + xi:
                    hit = not hit
                j = i
    return hit


def distance_km(polys, lat, lon):
    """Shortest distance from the point to the boundary (equirectangular, good enough for a few kilometres)."""
    import math
    k = math.cos(math.radians(lat)) * 111.32
    best = float("inf")
    for poly in polys:
        for ring in poly:
            for (y1, x1), (y2, x2) in zip(ring, ring[1:] + ring[:1]):
                ax, ay, bx, by = (x1 - lon) * k, (y1 - lat) * 110.57, (x2 - lon) * k, (y2 - lat) * 110.57
                dx, dy = bx - ax, by - ay
                t = 0.0 if dx == dy == 0 else max(0.0, min(1.0, -(ax * dx + ay * dy) / (dx * dx + dy * dy)))
                best = min(best, math.hypot(ax + t * dx, ay + t * dy))
    return best


class Regions:
    def __init__(self, path):
        self.polys = load_boundaries(path)
        self.boxes = {c: _bbox(p) for c, p in self.polys.items()}

    def contains(self, code, lat, lon):
        b = self.boxes.get(code)
        return bool(b) and b[0] <= lat <= b[1] and b[2] <= lon <= b[3] and inside(self.polys[code], lat, lon)

    def near(self, code, lat, lon, km=NEAR_KM):
        return code in self.polys and (self.contains(code, lat, lon) or distance_km(self.polys[code], lat, lon) <= km)

    def nearest(self, lat, lon, km):
        deg = km / 100.0
        best = (km, None)
        for c, b in self.boxes.items():
            if b[0] - deg <= lat <= b[1] + deg and b[2] - deg <= lon <= b[3] + deg:
                best = min(best, (distance_km(self.polys[c], lat, lon), c))
        return best[1]

    def regency_of(self, lat, lon):
        return next((c for c in self.polys if self.contains(c, lat, lon)), None)


def in_indonesia(lat, lon):
    return LAT_RANGE[0] <= lat <= LAT_RANGE[1] and LON_RANGE[0] <= lon <= LON_RANGE[1]


# F-035: a pair whose latitude sign was lost or whose Lintang/Bujur were swapped is corrected only when the
# corrected pair lies in the unit's own regency; the rule used is kept in koordinat_perbaikan and in the errata
FIXES = (("tanda_lintang", lambda a, o: (-a, o)), ("tertukar", lambda a, o: (o, a)),
         ("tertukar_tanda", lambda a, o: (-o, a)), ("tanda_bujur", lambda a, o: (a, -o)))


def check_point(unit, lat_s, lon_s, regions):
    """(lintang, bujur, koordinat_cek, koordinat_perbaikan) for one unit from the printed Lintang/Bujur.

    koordinat_cek: kabupaten (inside its regency or within NEAR_KM of it; at sea or on a small island, when its
    regency is the nearest one within ISLAND_KM) | provinsi (another regency of its province) | luar_provinsi
    (elsewhere in Indonesia) | tidak_diperiksa (no region code) | luar_indonesia | nol | kosong."""
    try:
        lat, lon = float(lat_s), float(lon_s)
    except (TypeError, ValueError):
        return None, None, "kosong", None
    if lat == 0 or lon == 0 or (abs(lat) < 0.01 and abs(lon) < 0.01):
        return None, None, "nol", None
    kab, prov = unit.get("kode_kabupaten"), unit.get("kode_provinsi")
    if in_indonesia(lat, lon) and kab and in_own_regency(regions, kab, lat, lon):
        return round(lat, 7), round(lon, 7), "kabupaten", None
    if kab:
        for name, fix in FIXES:
            flat, flon = fix(lat, lon)
            if in_indonesia(flat, flon) and in_own_regency(regions, kab, flat, flon):
                return round(flat, 7), round(flon, 7), "kabupaten", name
    if not in_indonesia(lat, lon):
        return None, None, "luar_indonesia", None
    lat, lon = round(lat, 7), round(lon, 7)
    if not kab and not prov:
        return lat, lon, "tidak_diperiksa", None
    host = regions.regency_of(lat, lon) or regions.nearest(lat, lon, ISLAND_KM)
    if host and prov and host.startswith(prov + "."):
        return lat, lon, "provinsi", None
    return lat, lon, "luar_provinsi", None


def in_own_regency(regions, kab, lat, lon):
    if regions.near(kab, lat, lon):
        return True
    # at sea or on a small island the simplified boundaries leave out: the nearest regency counts
    return regions.regency_of(lat, lon) is None and regions.nearest(lat, lon, ISLAND_KM) == kab


def load_coords(path):
    out = {}
    for f in sorted(os.listdir(path)):
        if f.endswith(".tsv"):
            for line in open(os.path.join(path, f), encoding="utf-8").read().splitlines()[1:]:
                npsn, lat, lon, shown, group = (line.split("\t") + ["", "", "", ""])[:5]
                out[npsn] = (lat, lon, shown, group)
    return out


ERRATA = []


def add_coordinates(items, coords, regions, stats):
    """Set lintang, bujur and koordinat_cek on every unit (in place) and count the results in `stats`."""
    for s in items:
        lat_s, lon_s, shown, group = coords.get(s["npsn"], (None, None, None, None))
        fix = None
        if lat_s is None:
            lat, lon, cek = None, None, "belum_diambil"
        elif shown and shown != s["npsn"]:
            lat, lon, cek = None, None, "halaman_lain"  # the detail page belongs to another NPSN: never used
        else:
            lat, lon, cek, fix = check_point(s, lat_s, lon_s, regions)
        s["lintang"], s["bujur"], s["koordinat_cek"], s["koordinat_perbaikan"] = lat, lon, cek, fix
        if fix:
            ERRATA.append({"npsn": s["npsn"], "printed": [lat_s, lon_s], "used": [lat, lon], "rule": fix})
        for key in ("all", s["bentuk_pendidikan"], s.get("kode_provinsi") or "?", "jenjang:" + (group or "?")):
            stats.setdefault(key, {}).setdefault(cek, 0)
            stats[key][cek] += 1


def mark_duplicates(files):
    """koordinat_sama = how many units in the whole set share exactly this pair (1 = no other unit)."""
    seen = {}
    for items in files.values():
        for s in items:
            if s["lintang"] is not None:
                seen[(s["lintang"], s["bujur"])] = seen.get((s["lintang"], s["bujur"]), 0) + 1
    for items in files.values():
        for s in items:
            s["koordinat_sama"] = seen.get((s["lintang"], s["bujur"])) if s["lintang"] is not None else None
    return seen


def write_gz(path, items):
    data = json.dumps(items, ensure_ascii=False, indent=0).encode()
    with open(path, "wb") as fh:
        with gzip.GzipFile(fileobj=fh, mode="wb", mtime=0, filename="") as gz:
            gz.write(data)


COORD_FIELDS = {
    "lintang": "latitude in decimal degrees from the unit's detail page (Lintang), rounded to 7 decimals; null when "
               "koordinat_cek is nol, kosong, luar_indonesia, halaman_lain or belum_diambil",
    "bujur": "longitude in decimal degrees (Bujur), same rules as lintang",
    "koordinat_cek": "check of the pair (F-035): kabupaten (inside the unit's regency or within 5 km of it; at sea or on "
                     "an island the simplified boundaries leave out, when its regency is the nearest within 50 km) | "
                     "provinsi (in another regency of its province; kept as printed) | luar_provinsi (elsewhere in "
                     "Indonesia; kept as printed) | tidak_diperiksa (no region code to check against) | nol (0 printed) "
                     "| kosong (nothing printed) | luar_indonesia (outside Indonesia and no correction fits) | "
                     "halaman_lain (the page shows another NPSN) | belum_diambil (page not fetched)",
    "koordinat_perbaikan": "null when the pair is used as printed; otherwise the correction that puts it in the unit's "
                           "own regency (F-035): tanda_lintang (latitude sign), tanda_bujur, tertukar (Lintang and Bujur "
                           "swapped), tertukar_tanda (swapped, latitude sign); printed values in the manifest errata",
    "koordinat_sama": "number of units in the whole set with exactly the same pair (1 = unique); null without a pair",
}


def merge_coords(data_dir, coords_dir, bounds_dir, version):
    """Add coordinates to the built set in DATA_DIR (in place) and update its manifest; report on stdout."""
    regions = Regions(bounds_dir)
    coords = load_coords(coords_dir)
    manifest_path = os.path.join(data_dir, "manifest.json")
    manifest = json.load(open(manifest_path, encoding="utf-8"))
    files, stats, report = {}, {}, {"outside_region": [], "outside_indonesia": []}
    for entry in manifest["files"]:
        items = json.load(gzip.open(os.path.join(data_dir, entry["file"]), "rt", encoding="utf-8"))
        add_coordinates(items, coords, regions, stats)
        files[entry["file"]] = items
        for s in items:
            c = s["koordinat_cek"]
            if c in ("provinsi", "luar_provinsi"):
                report["outside_region"].append(
                    f"{s['npsn']} {c} {s['lintang']},{s['bujur']} {s['kabupaten']} -> {regions.regency_of(s['lintang'], s['bujur'])}")
            elif c == "luar_indonesia":
                raw = coords.get(s["npsn"])
                report["outside_indonesia"].append(f"{s['npsn']} {raw[0]},{raw[1]}")
    pairs = mark_duplicates(files)
    for name, items in files.items():
        write_gz(os.path.join(data_dir, name), items)
    groups = {}
    for (lat, lon), n in pairs.items():
        if n > 1:
            groups[n] = groups.get(n, 0) + 1
    with_pair = sum(n for n in pairs.values())
    manifest["version"] = version
    manifest["fields"].update(COORD_FIELDS)
    manifest["with_coordinates"] = with_pair
    manifest["coordinates"] = {
        "checks": dict(sorted(stats["all"].items())),
        "shared_pairs": {"units_in_shared_pairs": sum(n for n in pairs.values() if n > 1),
                         "pairs_by_size": dict(sorted(groups.items()))},
        "corrected": len(ERRATA),
        "by_group": {k[8:]: dict(sorted(v.items())) for k, v in sorted(stats.items()) if k.startswith("jenjang:")},
        "by_province": {e["kode_provinsi"]: dict(sorted(stats.get(e["kode_provinsi"], {}).items()))
                        for e in manifest["files"]},
        "by_form": {k: dict(sorted(v.items())) for k, v in sorted(stats.items())
                    if k not in ("all", "?") and not k.startswith("jenjang:") and not re.fullmatch(r"\d\d", k)},
    }
    manifest["coordinate_errata"] = sorted(ERRATA, key=lambda e: e["npsn"])
    for e in manifest["files"]:
        e["with_coordinates"] = sum(1 for s in files[e["file"]] if s["lintang"] is not None)
    json.dump(manifest, open(manifest_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    open(manifest_path, "a").write("\n")
    json.dump(report, sys.stdout, ensure_ascii=False, indent=1)


# ---------------------------------------------------------------- build

def text(cell):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", cell))).strip()


def rows(page):
    out = []
    for r in re.findall(r"<tr[^>]*>(.*?)</tr>", page, re.S):
        cells = [text(c) for c in re.findall(r"<td[^>]*>(.*?)</td>", r, re.S)]
        if cells:
            out.append(cells)
    return out


def region_names(page, group, level, prefix):
    """Map child code → name from a list page (the name is the link text)."""
    names = {}
    for code, label in re.findall(rf'href="/satpen/{group}/(\d{{6}})(?:%20)*/{level}\?[^"]*"[^>]*>(.*?)</a>', page, re.S):
        if code.startswith(prefix):
            names[code] = text(label)
    return names


# Dapodik writes some names differently from Kemendagri; these are spellings of the same name, not guesses
NAME_ALIAS = {"dkijakarta": "daerahkhususibukotajakarta", "diyogyakarta": "daerahistimewayogyakarta"}


def norm(name):
    """Lower-case ASCII letters and digits; level words (Prov., Kab., Kec., Desa…) dropped, 'Kota' kept."""
    s = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode().lower().strip()
    s = re.sub(r"^(kota adm\.|kota administrasi)\s*", "kota ", s)
    s = re.sub(r"^(prov\.|kab\.\s*adm\.|kab\.|kec\.|kel\.)\s*", "", s)
    s = re.sub(r"^(provinsi|kabupaten administrasi|kabupaten|kecamatan|desa|kelurahan)\s+", "", s)
    s = re.sub(r"\bkep\.\s*", "kepulauan ", s)
    s = re.sub(r"[^a-z0-9]", "", s)
    return NAME_ALIAS.get(s, s)


def load_wilayah(path):
    rows_ = json.load(gzip.open(path, "rt", encoding="utf-8"))
    by_parent = {}
    names = {}
    for code, name in rows_:
        names[code] = name
        NAMES[code] = name
        parent = code.rsplit(".", 1)[0] if "." in code else ""
        by_parent.setdefault(parent, []).append((code, name))
    return names, by_parent


NUMBER = {"i": "1", "ii": "2", "iii": "3", "iv": "4", "v": "5", "vi": "6", "vii": "7", "viii": "8", "ix": "9",
          "x": "10", "satu": "1", "dua": "2", "tiga": "3", "empat": "4", "lima": "5"}
ABBREV = {"sei": "sungai", "sui": "sungai", "s": "sungai", "mns": "meunasah", "kp": "kampung", "tnjng": "tanjung",
          "kep": "kepulauan"}
PLACE_WORD = re.compile(r"^(kampung|kampong|nagari|gampong|jorong|dusun|desa|kelurahan|kel|negeri)\.?\s+")


def tokens(name):
    """Words of a name in one spelling: level words dropped, numbers as digits, common abbreviations written out."""
    s = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode().lower().strip()
    s = re.sub(r"^(kota adm\.|kota administrasi)\s*", "kota ", s)
    s = re.sub(r"^(prov\.|kab\.\s*adm\.|kab\.|kec\.|kel\.)\s*", "", s)
    s = re.sub(r"^(provinsi|kabupaten administrasi|kabupaten|kecamatan|desa|kelurahan)\s+", "", s)
    return [NUMBER.get(t, ABBREV.get(t, t)) for t in re.findall(r"[a-z0-9]+", s)]


def canon(name):
    """norm() plus one spelling for numbers (II = Dua = 2) and common abbreviations (Sei = Sungai, MNS = Meunasah)."""
    s = "".join(tokens(name))
    return NAME_ALIAS.get(s, s)


# words that tell two neighbouring places apart; a spelling rule never matches names that differ in them
MARKER_WORDS = {"utara", "selatan", "barat", "timur", "tengah", "darat", "laut", "hulu", "hilir", "ilir", "ulu",
                "mudik", "mudiak", "atas", "bawah", "lama", "baru", "kidul", "lor", "wetan", "kulon", "induk",
                "dalam", "luar", "besar", "kecil", "raya", "pantai", "pasar", "pekan", "kota", "kampung"}


def markers(name):
    return sorted(t for t in tokens(name) if t in MARKER_WORDS or t.isdigit() or len(t) == 1)


def match(by_parent, parent, name, kota=None):
    """Unique match of `name` among the children of `parent`, trying stricter rules first.

    Rules after the exact one are used only when they leave exactly one candidate; every such match is listed in
    the report (`matched_by_spelling_variant`). A rule that leaves several candidates stops the search: the code
    stays null rather than being guessed."""
    cands = by_parent.get(parent, [])
    if kota is not None and parent and len(parent) == 2:
        cands = [c for c in cands if c[1].lower().startswith("kota") == kota]
    key = norm(name)
    hits = [c for c in cands if norm(c[1]) == key]
    if len(hits) == 1:
        return hits[0][0]
    if hits:
        return None
    ckey = canon(name)

    def found(hits):
        LOOSE_MATCHES.append(f"{name} = {hits[0][1]} ({hits[0][0]})")
        return hits[0][0]

    # numbers and abbreviations (Lumpatan II/Lumpatan 2, Sei Rambah/Sungai Rambah); old Dutch spellings (dj, oe, tj);
    # Javanese/Sundanese a/e/o and doubled letters (Purwodadi/Purwadadi, Baturaden/Baturraden); u/o, i/y and a silent
    # h or w (Sokogelap/Sukogelap, Madiocondro/Madyocondro, Sidoarjo/Sidoharjo)
    mk = markers(name)
    for tier in (lambda k: k, loose, skeleton, skeleton_wide):
        hits = [c for c in cands if tier(canon(c[1])) == tier(ckey) and markers(c[1]) == mk]
        if len(hits) == 1:
            return found(hits)
        if hits:
            return None
    # one letter added, dropped or changed (Pucakwangi/Puncakwangi, Babad/Babat), names of 6+ letters only
    if len(ckey) >= 6:
        hits = [c for c in cands if one_edit(loose(canon(c[1])), loose(ckey)) and markers(c[1]) == mk]
        if len(hits) == 1:
            return found(hits)
        if hits:
            return None
    # the same name with or without a word around it: "Kec. Kota Blora" is "Blora", "Kisaran Barat" is
    # "Kota Kisaran Barat", "Batu Nadua" in Kota Padangsidimpuan is "Padangsidimpuan Batunadua",
    # "Kampung Tengah" / "Nagari Ganggo Hilia" are "Tengah" / "Ganggo Hilia"
    keys = ["kota" + ckey]
    if ckey.startswith("kota") and len(ckey) > 4:
        keys.append(ckey[4:])
    if parent in NAMES:
        keys.append(re.sub(r"^kota", "", canon(NAMES[parent])) + ckey)
    bare = PLACE_WORD.sub("", unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode().lower().strip())
    if canon(bare) != ckey:
        keys.append(canon(bare))
    for k in keys:
        hits = [c for c in cands if canon(c[1]) == k]
        if len(hits) == 1:
            return found(hits)
    return None


def one_edit(a, b):
    """True when a and b differ by exactly one inserted, deleted or replaced letter."""
    if a == b or abs(len(a) - len(b)) > 1:
        return False
    if len(a) > len(b):
        a, b = b, a
    i = 0
    while i < len(a) and a[i] == b[i]:
        i += 1
    return a[i + (len(a) == len(b)):] == b[i + 1:]


LOOSE_MATCHES = []
NAMES = {}


def loose(key):
    return key.replace("dj", "j").replace("oe", "u").replace("tj", "c")


def skeleton(key):
    return re.sub(r"(.)\1+", r"\1", re.sub(r"[eo]", "a", loose(key)))


def skeleton_wide(key):
    k = re.sub(r"[hw]", "", loose(key)).replace("y", "i")
    return re.sub(r"(.)\1+", r"\1", re.sub(r"[aeou]", "a", k))


def slug(name):
    s = norm_keep(name)
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", s)).strip("-")


def norm_keep(name):
    s = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode().lower()
    return re.sub(r"^prov\.\s+", "", s)


PROVINCE_FIX = {"d.k.i. jakarta": "dki-jakarta", "d.i. yogyakarta": "di-yogyakarta"}


def build(raw, out, wilayah_path, version, groups=GROUPS):
    names, by_parent = load_wilayah(wilayah_path)
    top_path = os.path.join(raw, "dikdas-000000.html")
    prov_names = {}
    if os.path.exists(top_path):
        prov_names = region_names(open(top_path, encoding="utf-8").read(), "dikdas", 1, "")
    os.makedirs(out, exist_ok=True)
    manifest_files, report = [], {"unmatched_regency": [], "unmatched_district": [], "unmatched_village": 0, "villages_unmatched_sample": []}
    total = 0
    levels_seen = {}
    for prov in sorted(p for p in os.listdir(raw) if re.fullmatch(r"\d{6}", p) and p not in EXCLUDED_PROVINCES):
        schools = {}
        prov_label = None
        kab_label, kec_label = {}, {}
        for group in groups:
            d = os.path.join(raw, prov, group)
            if not os.path.isdir(d):
                continue
            p1 = open(os.path.join(d, f"{prov}.html"), encoding="utf-8").read()
            kab_label.update(region_names(p1, group, 2, prov[:2]))
            for f in sorted(os.listdir(d)):
                code = f[:-5]
                if re.fullmatch(r"\d{4}00", code) and code != prov:
                    kec_label.update(region_names(open(os.path.join(d, f), encoding="utf-8").read(), group, 3, code[:4]))
            for f in sorted(os.listdir(d)):
                code = f[:-5]
                if not (re.fullmatch(r"\d{6}", code) and code[4:] != "00"):
                    continue
                for cells in rows(open(os.path.join(d, f), encoding="utf-8").read()):
                    if len(cells) < 7 or not re.fullmatch(r"[0-9A-Z]{8}", cells[1]):
                        continue
                    npsn, nama, bentuk, status, alamat, desa = cells[1:7]
                    if group in KEEP_FORMS and bentuk not in KEEP_FORMS[group]:
                        continue
                    schools[npsn] = {"npsn": npsn, "nama": nama, "bentuk_pendidikan": bentuk,
                                     "status_sekolah": status.upper(), "alamat": alamat, "desa": desa,
                                     "_kec": code}
        if not schools:
            continue
        prov_label = prov_names.get(prov) or prov
        wprov = match(by_parent, "", prov_label)
        kab_code, kec_code = {}, {}
        for k, label in kab_label.items():
            c = match(by_parent, wprov, label, kota=label.lower().startswith("kota")) if wprov else None
            kab_code[k] = c
            if not c:
                report["unmatched_regency"].append(f"{k} {label}")
        for k, label in kec_label.items():
            parent = kab_code.get(k[:4] + "00")
            c = match(by_parent, parent, label) if parent else None
            kec_code[k] = c
            if not c:
                report["unmatched_district"].append(f"{k} {label} ({kab_label.get(k[:4] + '00')})")
        items = []
        for s in schools.values():
            kec = s.pop("_kec")
            kab = kec[:4] + "00"
            kc = kec_code.get(kec)
            vc = match(by_parent, kc, s["desa"]) if kc else None
            if kc and not vc:
                report["unmatched_village"] += 1
                if len(report["villages_unmatched_sample"]) < 200:
                    report["villages_unmatched_sample"].append(f"{s['npsn']} {s['desa']} / {kec_label.get(kec)} / {kab_label.get(kab)}")
            s["kecamatan"] = kec_label.get(kec, "")
            s["kabupaten"] = kab_label.get(kab, "")
            s["provinsi"] = prov_label
            s["kode_desa"] = vc
            s["kode_kecamatan"] = kc
            s["kode_kabupaten"] = kab_code.get(kab)
            s["kode_provinsi"] = wprov
            s["kode_kecamatan_dapodik"] = kec
            items.append(s)
            levels_seen[s["bentuk_pendidikan"]] = levels_seen.get(s["bentuk_pendidikan"], 0) + 1
        items.sort(key=lambda x: (x["kode_kecamatan_dapodik"], x["desa"], x["nama"], x["npsn"]))
        key = norm_keep(prov_label)
        fname = PROVINCE_FIX.get(key, slug(prov_label)) + ".json.gz"
        data = json.dumps(items, ensure_ascii=False, indent=0).encode()
        with open(os.path.join(out, fname), "wb") as fh:
            with gzip.GzipFile(fileobj=fh, mode="wb", mtime=0, filename="") as gz:
                gz.write(data)
        counts = {}
        for s in items:
            counts[s["bentuk_pendidikan"]] = counts.get(s["bentuk_pendidikan"], 0) + 1
        manifest_files.append({"file": fname, "province": re.sub(r"^Prov\.\s+", "", prov_label),
                               "kode_provinsi": wprov, "kode_dapodik": prov, "schools": len(items),
                               "levels": dict(sorted(counts.items())),
                               "with_village_code": sum(1 for s in items if s["kode_desa"])})
        total += len(items)
    wilayah_manifest = os.path.join(os.path.dirname(wilayah_path), "manifest.json")
    wilayah_version = json.load(open(wilayah_manifest))["version"] if os.path.exists(wilayah_manifest) else "?"
    manifest = {
        "version": version,
        "description": "Schools and other education units in Indonesia, one gzipped JSON file per province "
                       "(public data, no personal data), linked to the Kemendagri region codes of the wilayah set.",
        "status": "ready",
        "groups": list(groups),
        "levels": sorted(levels_seen),
        "source": f"{BASE}/satpen/<group>/<district>/3 (Kemendikdasmen Dapodik reference pages; Dikdas, Dikmen, PAUD "
                  "and Dikmas lists per district, status 'all'), crawled on the version date; the pages show no "
                  "source date",
        "licence": "Public government data, no personal data",
        "procedure": "tools/converters/sekolah.py fetch (raw pages) then build; regions matched by name to "
                     f"wilayah {wilayah_version}, never invented (F-028 for what is kept)",
        "fields": {
            "npsn": "NPSN as published: 8 characters (non-formal units may start with a letter); 'NP…' numbers are "
                    "temporary numbers, not NPSNs",
            "nama": "name as published",
            "bentuk_pendidikan": "form as published: SD, MI, SMP, MTs, SMA, MA, SMK, SLB, SPK …, PDF …, TK, KB, RA, …",
            "status_sekolah": "NEGERI | SWASTA",
            "alamat": "street address as published (empty for a few units)",
            "desa": "village name as published",
            "kecamatan": "'Kec. …' as published",
            "kabupaten": "'Kab. …' / 'Kota …' as published",
            "provinsi": "'Prov. …' as published",
            "kode_desa": "Kemendagri village code xx.xx.xx.xxxx (wilayah), null when the name does not match uniquely",
            "kode_kecamatan": "Kemendagri district code xx.xx.xx, null when unmatched",
            "kode_kabupaten": "Kemendagri regency code xx.xx, null when unmatched",
            "kode_provinsi": "Kemendagri province code xx",
            "kode_kecamatan_dapodik": "6-digit Dapodik district code of the source page",
        },
        "schools": total,
        "with_village_code": sum(f["with_village_code"] for f in manifest_files),
        "levels_count": dict(sorted(levels_seen.items())),
        "matched_by_spelling_variant": len(LOOSE_MATCHES),
        "unmatched": {"regencies": len(report["unmatched_regency"]), "districts": len(report["unmatched_district"]),
                      "villages": report["unmatched_village"]},
        "files": manifest_files,
        "notes": [
            "Only active units: the district lists leave out units the source marks as merged or closed "
            "(their detail pages say e.g. 'STATUS SATUAN PENDIDIKAN: MERGER').",
            "Madrasah (MI, MTs, MA) come from the same Kemendikdasmen lists; their NSM follows from Kemenag (R-02).",
            "Kept forms and regions: decision F-028. Region codes are matched by name to wilayah; spelling variants "
            "are accepted only when one candidate remains and numbers and words such as Utara/Barat/Lama agree "
            "(count in matched_by_spelling_variant, full list printed by the build); otherwise the code is null.",
            "Village codes point to the village of the school's Dapodik district; where Dapodik and Kemendagri place "
            "a village in different districts the code stays null.",
        ],
    }
    with open(os.path.join(out, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
        f.write("\n")
    report["matched_by_spelling_variant"] = LOOSE_MATCHES
    json.dump(report, sys.stdout, ensure_ascii=False, indent=1)

if __name__ == "__main__":
    args = sys.argv[1:]
    groups = GROUPS
    if len(args) > 1 and args[1].startswith("--groups="):
        groups = tuple(g for g in args.pop(1).split("=", 1)[1].split(",") if g)
        if not groups or any(g not in GROUP_URL for g in groups):
            sys.exit(f"unknown group; choose from {', '.join(GROUP_URL)}")
    if len(args) >= 2 and args[0] == "fetch":
        fetch(args[1], args[2:], groups)
    elif len(args) >= 4 and args[0] == "coords":
        threads = 1
        if args[-1].startswith("--threads="):
            threads = int(args.pop().split("=", 1)[1])
        fetch_coords(args[1], args[2], args[3], args[4:], threads)
    elif len(args) == 5 and args[0] == "coords-merge":
        merge_coords(*args[1:])
    elif len(args) == 4 and args[0] == "coords-extract":
        extract_coords(*args[1:])
    elif len(args) == 3 and args[0] == "plan":
        plan(args[1], args[2])
    elif len(args) == 5 and args[0] == "build":
        build(*args[1:], groups=groups)
    else:
        sys.exit(__doc__)
