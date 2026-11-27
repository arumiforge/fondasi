#!/usr/bin/env python3
"""Check a built batas-wilayah folder (F-035): Fondasi's data/batas-wilayah, a folder built elsewhere with
tools/converters/batas-wilayah.py build, or a server copy made with its presisi command.

  python3 -I tools/checks/batas-wilayah.py <data_dir> [--wilayah=<wilayah.json.gz>] [--big] [--render <out_dir>]
                                          [--jobs=N]

Regencies are checked in parallel, one worker process per CPU (--jobs to change); BIG requests run in parallel too.

Checks, for every regency listed in <data_dir>/manifest.json:

  coverage    every village and district of data/wilayah in that regency has a polygon (lists those without one;
              the manifest's villages_without_polygon must list the same), and no feature has a code outside it
  districts   each district is exactly the union of its villages: its boundary edges are the village edges that
              are not shared inside the district, and its area equals the sum of its villages' areas (both computed
              from the coordinates in the files; a gap or overlap would change one of them). The area_km2 fields
              must agree too (sum of the villages' area_km2 = the district's, within rounding)
  holes       a hole in the regency (a place surrounded by villages but covered by none) is a gap, unless BIG has
              an undefined area there (lakes, TIPADM 999): there may be no more holes than undefined_areas
  borders     where two regencies of the folder meet, both files carry the same border, point for point: an
              edge of one regency's outline that runs along another regency's outline (both ends and the middle
              within 2 x tolerance_m, at least 1 m) without being one of its edges is a mismatch (a sliver gap or
              overlap). In a full-precision copy (tolerance 0) such edges come from BIG itself and are only
              reported. Check neighbours together: put all of them in one folder
  --big       compares area_km2 of every district with LUASWH of BIG's own district layer BATAS_KECAMATAN_AR
              (the field says HA but holds square kilometres). Must agree to 4 decimals; a difference of one unit
              in the 4th decimal is reported as rounding and passes, anything more fails. GET requests only, to
              geoservices.big.go.id
  --render    writes <out_dir>/<regency>.svg and <out_dir>/provinsi.svg: thin village lines, thick district lines,
              thickest regency lines, dashed where a village on either side has the status "Batas Indikatif";
              villages are tinted by status

Exit code 1 when any check fails. Python standard library only; the files are read as untrusted input (strict code
patterns, nothing executed).
"""
import gzip
import json
import math
import multiprocessing
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
BIG_DISTRICTS = ("https://geoservices.big.go.id/rbi/rest/services/BATASWILAYAH/BATAS_KECAMATAN_AR/MapServer/0/"
                 "query")
REGENCY = re.compile(r"^\d{2}\.\d{2}$")
DISTRICT = re.compile(r"^\d{2}\.\d{2}\.\d{2}$")
VILLAGE = re.compile(r"^\d{2}\.\d{2}\.\d{2}\.\d{4}$")
STATUSES = ("Batas Definitif", "Hasil Kesepakatan", "Batas Indikatif")

failures = []
_lines = None  # in a worker process: lines collected for the parent, which prints them in regency order


def emit(line, failed=False):
    if failed:
        failures.append(line)
    if _lines is None:
        print(line, flush=True)
    else:
        _lines.append((line, failed))


def fail(msg):
    emit("FAIL " + msg, True)


def ok(msg):
    emit("ok   " + msg)


def note(msg):
    emit("       " + msg)


# ---------------------------------------------------------------- geometry

WGS84_A, WGS84_F = 6378137.0, 1 / 298.257223563
WGS84_E = math.sqrt(WGS84_F * (2 - WGS84_F))


def _q(phi):  # authalic latitude helper (Snyder 1987, eq. 3-12)
    e, s = WGS84_E, math.sin(phi)
    return (1 - e * e) * (s / (1 - e * e * s * s) - math.log((1 - e * s) / (1 + e * s)) / (2 * e))


QP = _q(math.pi / 2)


def ring_area(ring):
    """Signed area in square metres on the WGS 84 ellipsoid (> 0 counter-clockwise), as the converter computes it."""
    beta = [math.asin(_q(math.radians(y)) / QP) for _, y in ring]
    s = 0.0
    for i in range(len(ring) - 1):
        s += math.radians(ring[i + 1][0] - ring[i][0]) * (2 + math.sin(beta[i]) + math.sin(beta[i + 1]))
    return -s * (WGS84_A ** 2 * QP / 2) / 2


def polygons(geom):
    if geom.get("type") == "Polygon":
        polys = [geom["coordinates"]]
    elif geom.get("type") == "MultiPolygon":
        polys = geom["coordinates"]
    else:
        raise ValueError(f"unexpected geometry type {geom.get('type')!r}")
    out = []
    for poly in polys:
        rings = []
        for r in poly:
            ring = [(float(p[0]), float(p[1])) for p in r]
            if len(ring) < 4 or ring[0] != ring[-1]:
                raise ValueError("ring not closed")
            if not all(94 <= x <= 142 and -12 <= y <= 7 for x, y in ring):
                raise ValueError("coordinate outside Indonesia")
            rings.append(ring)
        out.append(rings)
    return out


def area(polys):  # outer counter-clockwise, holes clockwise (RFC 7946): the signed sum is the area
    return sum(ring_area(r) for poly in polys for r in poly)


def edges(ring):
    for p, q in zip(ring, ring[1:]):
        if p != q:
            yield (p, q) if p < q else (q, p)


def net_edges(polys_list):
    """Directed edges summed over polygons (RFC 7946 orientation): an edge shared by two polygons cancels, so what
    remains is the boundary of their union. Keyed by the edge with its points in sorted order; the value is the net
    count in that direction (usually +1 or -1)."""
    net = Counter()
    for polys in polys_list:
        for poly in polys:
            for r in poly:
                for p, q in zip(r, r[1:]):
                    if p < q:
                        net[(p, q)] += 1
                    elif q < p:
                        net[(q, p)] -= 1
    return Counter({e: n for e, n in net.items() if n})


def metres(lat):
    ky = math.pi * 6371007.2 / 180
    return math.cos(math.radians(lat)) * ky, ky


def point_segment_m(p, a, b):
    kx, ky = metres(p[1])
    px, py = (p[0] - a[0]) * kx, (p[1] - a[1]) * ky
    bx, by = (b[0] - a[0]) * kx, (b[1] - a[1]) * ky
    d2 = bx * bx + by * by
    t = 0.0 if not d2 else max(0.0, min(1.0, (px * bx + py * by) / d2))
    return math.hypot(px - t * bx, py - t * by)


# ---------------------------------------------------------------- reading

def read_collection(path):
    with gzip.open(path, "rt", encoding="utf-8") as f:
        data = json.load(f)
    if data.get("type") != "FeatureCollection" or not isinstance(data.get("features"), list):
        raise ValueError("not a GeoJSON FeatureCollection")
    return data["features"]


def load_regency(data_dir, kab):
    villages, districts = {}, {}
    for f in read_collection(os.path.join(data_dir, "desa", f"{kab}.geojson.gz")):
        p = f.get("properties") or {}
        code = p.get("code")
        if not isinstance(code, str) or not VILLAGE.match(code) or not code.startswith(kab + "."):
            raise ValueError(f"desa/{kab}: bad village code {code!r}")
        if code in villages:
            raise ValueError(f"desa/{kab}: {code} appears twice")
        status = p.get("status")
        status = [status] if isinstance(status, str) else status
        if not status or any(s not in STATUSES for s in status):
            raise ValueError(f"desa/{kab}: {code}: unexpected status {p.get('status')!r}")
        villages[code] = {"props": p, "status": status, "polys": polygons(f.get("geometry") or {})}
    for f in read_collection(os.path.join(data_dir, "kecamatan", f"{kab}.geojson.gz")):
        p = f.get("properties") or {}
        code = p.get("code")
        if not isinstance(code, str) or not DISTRICT.match(code) or not code.startswith(kab + "."):
            raise ValueError(f"kecamatan/{kab}: bad district code {code!r}")
        if code in districts:
            raise ValueError(f"kecamatan/{kab}: {code} appears twice")
        districts[code] = {"props": p, "polys": polygons(f.get("geometry") or {})}
    return villages, districts


# ---------------------------------------------------------------- checks per regency

def check_regency(kab, entry, villages, districts, names):
    label = f"{kab} {names.get(kab, '?')}"
    # coverage
    want_v = sorted(c for c in names if len(c) == 13 and c.startswith(kab + "."))
    want_d = sorted(c for c in names if len(c) == 8 and c.startswith(kab + "."))
    no_v = [c for c in want_v if c not in villages]
    no_d = [c for c in want_d if c not in districts]
    extra = sorted(c for c in list(villages) + list(districts) if c not in names)
    if extra:
        fail(f"{label}: codes not in data/wilayah: {', '.join(extra[:10])}")
    if no_v or no_d:
        fail(f"{label}: without polygon: {len(no_v)} villages, {len(no_d)} districts")
        for c in no_v + no_d:
            note(f"{c} {names[c]}")
    else:
        ok(f"{label}: all {len(want_v)} villages and {len(want_d)} districts have a polygon")
    if sorted(entry.get("villages_without_polygon", [])) != no_v:
        fail(f"{label}: manifest villages_without_polygon does not match the files")
    if entry.get("villages") != len(villages) or entry.get("districts") != len(districts):
        fail(f"{label}: manifest counts {entry.get('villages')}/{entry.get('districts')} differ from the files "
             f"{len(villages)}/{len(districts)}")

    # districts = union of villages
    members = defaultdict(list)
    for code, v in villages.items():
        if v["props"].get("district") != code[:8]:
            fail(f"{label}: {code}: district field {v['props'].get('district')!r}")
        members[code[:8]].append(code)
    orphan = sorted(set(members) - set(districts))
    if orphan:
        fail(f"{label}: villages of districts without a district polygon: {', '.join(orphan)}")
    area_v = {c: area(v["polys"]) for c, v in villages.items()}
    worst_geom, worst_field, bad_edges = 0.0, 0.0, []
    for kec, d in sorted(districts.items()):
        codes = members.get(kec, [])
        if not codes:
            fail(f"{label}: district {kec} has no village polygon")
            continue
        if net_edges([d["polys"]]) != net_edges(villages[c]["polys"] for c in codes):
            bad_edges.append(kec)
        a_sum, a_kec = sum(area_v[c] for c in codes), area(d["polys"])
        rel = abs(a_sum - a_kec) / a_sum
        worst_geom = max(worst_geom, rel)
        if rel > 1e-9:
            fail(f"{label}: {kec}: district area {a_kec / 1e6:.6f} km² ≠ sum of its villages {a_sum / 1e6:.6f} km²")
        f_sum = sum(villages[c]["props"].get("area_km2") or 0 for c in codes)
        f_kec = d["props"].get("area_km2")
        diff = abs(f_sum - (f_kec or 0))
        worst_field = max(worst_field, diff)
        if f_kec is None or diff > 0.00005 * len(codes) + 1e-9:
            fail(f"{label}: {kec}: area_km2 {f_kec} ≠ sum of its villages' area_km2 {f_sum:.4f}")
        if d["props"].get("villages") != len(codes):
            fail(f"{label}: {kec}: villages field {d['props'].get('villages')} ≠ {len(codes)} polygons")
    if bad_edges:
        fail(f"{label}: district boundary is not the outline of its villages: {', '.join(bad_edges)}")
    else:
        ok(f"{label}: every district is the union of its villages (edges identical, area difference "
           f"{worst_geom:.1e}, area_km2 fields within {worst_field:.4f})")

    # holes in the regency (gaps) and its outline for the border check
    outline = set(net_edges(v["polys"] for v in villages.values()))
    holes = regency_holes(outline)
    allowed = entry.get("undefined_areas", 0) or 0
    if len(holes) > allowed:
        fail(f"{label}: {len(holes)} holes inside the regency but only {allowed} undefined areas: "
             + ", ".join(f"{h[1]:.5f},{h[0]:.5f} ({a:.0f} m²)" for h, a in holes[:5]))
    else:
        ok(f"{label}: no gap between villages ({len(holes)} holes, {allowed} undefined areas)")
    return outline, area_v


def regency_holes(outline):
    """Chain the outline edges into rings; rings with negative area (clockwise) are holes. Returns
    [(a point of the hole, area m²)]."""
    adj = defaultdict(list)
    for p, q in outline:
        adj[p].append(q)
        adj[q].append(p)
    used, holes = set(), []
    for start in list(adj):
        for nxt in adj[start]:
            e = (start, nxt) if start < nxt else (nxt, start)
            if e in used:
                continue
            ring, prev, cur = [start], start, nxt
            used.add(e)
            while cur != start:
                ring.append(cur)
                cands = [n for n in adj[cur] if ((cur, n) if cur < n else (n, cur)) not in used]
                if not cands:
                    break
                n = cands[0]
                used.add((cur, n) if cur < n else (n, cur))
                prev, cur = cur, n
            if cur != start:
                continue
            ring.append(start)
            holes.append(ring)
    # orientation is arbitrary after chaining: a ring is a hole when another ring of the outline contains it
    rings = sorted(holes, key=lambda r: -abs(ring_area(r)))
    out = []
    for i, r in enumerate(rings):
        pt = r[0]
        inside = sum(1 for o in rings[:i] if point_in_ring(midpoint(r), o))
        if inside % 2:
            out.append((pt, abs(ring_area(r))))
    return out


def midpoint(ring):
    (x1, y1), (x2, y2) = ring[0], ring[1]
    return ((x1 + x2) / 2, (y1 + y2) / 2)


def point_in_ring(pt, ring):
    x, y = pt
    inside = False
    for (x1, y1), (x2, y2) in zip(ring, ring[1:]):
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
            inside = not inside
    return inside


# ---------------------------------------------------------------- borders between regencies

def check_borders(outlines, names, tolerance):
    """An outline edge of one regency that is not an edge of any other regency, but whose two ends and middle all
    lie within `near` metres of the same neighbour's outline, runs along that neighbour without matching it. Edges
    that leave a point where three regencies meet are not caught (their far end is away from the neighbour)."""
    if len(outlines) < 2:
        emit("skip borders: only one regency in the folder")
        return
    near_m = max(2 * tolerance, 1.0)
    owner = defaultdict(list)
    for kab, edges_ in outlines.items():
        for e in edges_:
            owner[e].append(kab)
    cell = max(near_m * 1.5 / 110000, 0.0002)  # degrees; the 3 x 3 cells around a point reach beyond near_m
    grid = defaultdict(list)
    for kab, edges_ in outlines.items():
        for a, b in edges_:
            for gx in range(int(math.floor(min(a[0], b[0]) / cell)), int(math.floor(max(a[0], b[0]) / cell)) + 1):
                for gy in range(int(math.floor(min(a[1], b[1]) / cell)), int(math.floor(max(a[1], b[1]) / cell)) + 1):
                    grid[(gx, gy)].append((kab, a, b))
    shared = Counter()
    mismatch = defaultdict(list)
    for e, kabs in owner.items():
        if len(kabs) > 2:
            fail(f"border edge {e} is on the outline of {', '.join(kabs)}")
        if len(kabs) == 2:
            shared[tuple(sorted(kabs))] += 1
            continue
        kab = kabs[0]
        a, b = e
        mid = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
        for other, d_mid in distances(grid, mid, kab, cell).items():
            if d_mid > near_m:
                continue
            d_ends = [distances(grid, p, kab, cell, other).get(other, math.inf) for p in (a, b)]
            if max(d_ends) <= near_m:
                mismatch[tuple(sorted((kab, other)))].append((e, max(d_ends + [d_mid])))
                break
    for pair, n in sorted(shared.items()):
        note(f"{pair[0]}–{pair[1]}: {n} shared border edges")
    for pair, es in sorted(mismatch.items()):
        (p, _), worst = es[0][0], max(d for _, d in es)
        msg = (f"border {pair[0]} {names.get(pair[0], '')} – {pair[1]} {names.get(pair[1], '')}: {len(es)} edges run "
               f"along the neighbour without matching it (up to {worst:.2f} m apart), e.g. near {p[1]:.6f},{p[0]:.6f}")
        if tolerance > 0:
            fail(msg)
        else:  # a full-precision copy keeps BIG's coordinates as they are; the source itself differs here
            emit("note " + msg + " — in BIG's own full-precision data")
    if shared and not mismatch:
        ok(f"borders: {sum(shared.values())} edges shared by {len(shared)} neighbouring regency pairs, identical on "
           f"both sides")
    elif not shared:
        emit("note borders: the regencies in this folder do not touch each other")


def distances(grid, p, kab, cell, only=None):
    """Distance in metres from p to the nearest outline edge of every other regency nearby (or only `only`)."""
    gx, gy = int(math.floor(p[0] / cell)), int(math.floor(p[1] / cell))
    best = {}
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            for k, a, b in grid.get((gx + dx, gy + dy), ()):
                if k != kab and (only is None or k == only):
                    d = point_segment_m(p, a, b)
                    if d < best.get(k, math.inf):
                        best[k] = d
    return best


# ---------------------------------------------------------------- BIG district areas

def big_districts(kab):
    params = {"f": "json", "where": f"KDPKAB='{kab}'", "outFields": "KDCPUM,LUASWH",
              "returnGeometry": "false", "orderByFields": "KDCPUM"}
    url = BIG_DISTRICTS + "?" + urllib.parse.urlencode(params)
    for attempt in range(4):
        try:
            with urllib.request.urlopen(url, timeout=120) as r:
                data = json.loads(r.read())
            if "error" in data:
                raise ValueError(str(data["error"])[:200])
            break
        except Exception as e:  # network and service errors are retried
            if attempt == 3:
                raise
            time.sleep(5 * (attempt + 1))
    out = {}
    for f in data.get("features", []):
        a = f.get("attributes") or {}
        code, luas = a.get("KDCPUM"), a.get("LUASWH")
        if not isinstance(code, str) or not DISTRICT.match(code.strip()) or not isinstance(luas, (int, float)):
            raise ValueError(f"unexpected BIG district record {a!r}"[:200])
        out.setdefault(code.strip(), []).append(float(luas))
    return out


def try_big(kab):
    try:
        return big_districts(kab)
    except Exception as e:  # reported by check_big
        return e


def check_big(kab, districts, names, big):
    label = f"{kab} {names.get(kab, '?')}"
    if isinstance(big, Exception):
        fail(f"{label}: BIG district layer not reachable: {big}")
        return
    exact = rounding = 0
    for kec in sorted(set(big) | set(districts)):
        if kec not in districts:
            fail(f"{label}: BIG has district {kec}, the folder has none")
            continue
        if kec not in big:
            fail(f"{label}: BIG's district layer has no {kec}")
            continue
        if len(big[kec]) != 1:
            fail(f"{label}: BIG's district layer has {len(big[kec])} records for {kec}")
            continue
        ours, theirs = districts[kec]["props"].get("area_km2"), round(big[kec][0], 4)
        diff = round(abs((ours or 0) - theirs), 4)
        if diff == 0:
            exact += 1
        elif diff <= 0.0001:
            rounding += 1
            note(f"{kec} {names.get(kec, '')}: {ours} vs BIG {big[kec][0]:.6f} (rounding)")
        else:
            fail(f"{label}: {kec} {names.get(kec, '')}: area_km2 {ours} vs BIG LUASWH {big[kec][0]:.6f}")
    if exact + rounding == len(districts):
        ok(f"{label}: BIG district areas: {exact} equal to 4 decimals, {rounding} differ by rounding only")


# ---------------------------------------------------------------- render

TINT = {"Batas Definitif": "#d9ead3", "Hasil Kesepakatan": "#fff2cc", "Batas Indikatif": "#f4cccc"}
LEVEL = {"desa": (0.5, "#555555"), "kecamatan": (1.6, "#1f1f1f"), "kabupaten": (2.8, "#000000")}


class Projection:
    def __init__(self, points, box=1200, margin=24):
        xs, ys = [p[0] for p in points], [p[1] for p in points]
        self.x0, self.y1 = min(xs), max(ys)
        self.k = math.cos(math.radians((min(ys) + max(ys)) / 2))
        w, h = (max(xs) - self.x0) * self.k, self.y1 - min(ys)
        self.s = (box - 2 * margin) / max(w, h, 1e-9)
        self.m = margin
        self.width = max(int(w * self.s + 2 * margin), 760)
        self.height = int(h * self.s + 2 * margin) + 60

    def __call__(self, p):
        return f"{(p[0] - self.x0) * self.k * self.s + self.m:.1f},{(self.y1 - p[1]) * self.s + self.m:.1f}"


def styled_lines(regencies):
    """Polylines per (level, dashed): every edge once, at the highest level it belongs to; dashed when a village on
    either side has the status Batas Indikatif."""
    owners = defaultdict(list)
    for kab, villages in regencies.items():
        for code, v in villages.items():
            for poly in v["polys"]:
                for r in poly:
                    for e in edges(r):
                        owners[e].append(code)
    status = {code: v["status"] for villages in regencies.values() for code, v in villages.items()}

    def style(e):
        cs = owners[e]
        dashed = any("Batas Indikatif" in status[c] for c in cs)
        if len(cs) == 1 or cs[0][:5] != cs[1][:5]:
            return ("kabupaten", dashed)
        if cs[0][:8] != cs[1][:8]:
            return ("kecamatan", dashed)
        return ("desa", dashed)

    lines = defaultdict(list)
    done = set()
    for villages in regencies.values():
        for v in villages.values():
            for poly in v["polys"]:
                for r in poly:
                    run, run_style = [], None
                    for p, q in zip(r, r[1:]):
                        e = (p, q) if p < q else (q, p)
                        if p == q or e in done:
                            st = None
                        else:
                            done.add(e)
                            st = style(e)
                        if st != run_style or not run:
                            if run_style and len(run) > 1:
                                lines[run_style].append(run)
                            run, run_style = ([p, q] if st else []), st
                        else:
                            run.append(q)
                    if run_style and len(run) > 1:
                        lines[run_style].append(run)
    return lines


def svg(path, title, regencies, labels):
    pts = [p for villages in regencies.values() for v in villages.values() for poly in v["polys"] for p in poly[0]]
    proj = Projection(pts)
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{proj.width}" height="{proj.height}" '
           f'viewBox="0 0 {proj.width} {proj.height}" font-family="sans-serif">',
           f'<title>{esc(title)}</title>', f'<rect width="100%" height="100%" fill="#ffffff"/>']
    for st, colour in TINT.items():
        ds = []
        for villages in regencies.values():
            for v in villages.values():
                if v["status"][0] == st:
                    for poly in v["polys"]:
                        ds.append(" ".join("M" + " L".join(proj(p) for p in r[:-1]) + "Z" for r in poly))
        if ds:
            out.append(f'<path fill="{colour}" fill-rule="evenodd" stroke="none" d="{" ".join(ds)}"/>')
    lines = styled_lines(regencies)
    for level in ("desa", "kecamatan", "kabupaten"):
        width, colour = LEVEL[level]
        for dashed in (False, True):
            runs = lines.get((level, dashed))
            if not runs:
                continue
            dash = f' stroke-dasharray="{width * 4:g} {width * 3:g}"' if dashed else ""
            d = " ".join("M" + " L".join(proj(p) for p in run) for run in runs)
            out.append(f'<path fill="none" stroke="{colour}" stroke-width="{width:g}" stroke-linejoin="round"'
                       f'{dash} d="{d}"/>')
    for text, polys, size in labels:
        weights = [(abs(ring_area(poly[0])), centroid(poly[0])) for poly in polys]
        total = sum(w for w, _ in weights) or 1.0
        cx, cy = proj((sum(w * c[0] for w, c in weights) / total, sum(w * c[1] for w, c in weights) / total)).split(",")
        out.append(f'<text x="{cx}" y="{cy}" font-size="{size}" text-anchor="middle" fill="#1f1f1f" '
                   f'stroke="#ffffff" stroke-width="3" paint-order="stroke">{esc(text)}</text>')
    y = proj.height - 40
    x = proj.m
    for st, colour in TINT.items():
        out.append(f'<rect x="{x}" y="{y}" width="14" height="14" fill="{colour}" stroke="#555555"/>'
                   f'<text x="{x + 20}" y="{y + 12}" font-size="13">{esc(st)}</text>')
        x += 170
    out.append(f'<line x1="{x}" y1="{y + 7}" x2="{x + 40}" y2="{y + 7}" stroke="#1f1f1f" stroke-width="1.6" '
               f'stroke-dasharray="6.4 4.8"/><text x="{x + 48}" y="{y + 12}" font-size="13">ada sisi Batas '
               f'Indikatif</text>')
    out.append(f'<text x="{proj.m}" y="{proj.height - 10}" font-size="12" fill="#555555">{esc(title)} · '
               f'Sumber: Badan Informasi Geospasial · bukan batas hukum</text>')
    out.append("</svg>")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")
    note(f"wrote {path} ({os.path.getsize(path) / 1024:.0f} KB)")


def centroid(ring):
    a = cx = cy = 0.0
    for (x1, y1), (x2, y2) in zip(ring, ring[1:]):
        c = x1 * y2 - x2 * y1
        a += c
        cx += (x1 + x2) * c
        cy += (y1 + y2) * c
    if not a:
        return ring[0]
    return (cx / (3 * a), cy / (3 * a))


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def render(out_dir, loaded, names):
    os.makedirs(out_dir, exist_ok=True)
    for kab, (villages, districts) in loaded.items():
        labels = [(d["props"].get("name", code), d["polys"], 13) for code, d in sorted(districts.items())]
        svg(os.path.join(out_dir, f"{kab}.svg"), names.get(kab, kab), {kab: villages}, labels)
    province = sorted({kab[:2] for kab in loaded})
    labels = []
    for kab, (villages, _) in loaded.items():
        polys = [poly for v in villages.values() for poly in v["polys"]]
        labels.append((names.get(kab, kab).replace("Kabupaten ", ""), polys, 14))
    title = ", ".join(names.get(p, p) for p in province) + f" ({len(loaded)} kabupaten/kota)"
    svg(os.path.join(out_dir, "provinsi.svg"), title, {k: v for k, (v, _) in loaded.items()}, labels)


# ---------------------------------------------------------------- main

NAMES = {}


def _init(names):
    global NAMES
    NAMES = names


def regency_job(job):
    """One regency in a worker process: read, check, and return what the parent needs."""
    global _lines, failures
    data_dir, entry, keep_villages = job
    saved = (_lines, failures)  # restored below, so this also works in the parent process (--jobs=1)
    _lines, failures = [], []
    kab, outline, villages, districts = entry.get("code"), None, None, None
    if not isinstance(kab, str) or not REGENCY.match(kab):
        fail(f"manifest: bad regency code {kab!r}")
    elif kab not in NAMES:
        fail(f"manifest: {kab} is not a regency of data/wilayah")
    else:
        try:
            villages, districts = load_regency(data_dir, kab)
            outline, _ = check_regency(kab, entry, villages, districts, NAMES)
        except (OSError, ValueError, KeyError, TypeError) as e:
            fail(f"{kab}: cannot read: {e}")
            villages = districts = None
    props = {c: d["props"] for c, d in districts.items()} if districts else None
    lines, (_lines, failures) = _lines, saved
    return kab, lines, outline, (villages if keep_villages else None), (districts if keep_villages else props)


def main(argv):
    args, opts, i = [], {}, 0
    while i < len(argv):
        a = argv[i]
        if a == "--render" and i + 1 < len(argv):
            opts["render"] = argv[i + 1]
            i += 1
        elif a.startswith("--render="):
            opts["render"] = a.split("=", 1)[1]
        elif a.startswith("--wilayah="):
            opts["wilayah"] = a.split("=", 1)[1]
        elif a.startswith("--jobs="):
            opts["jobs"] = int(a.split("=", 1)[1])
        elif a == "--big":
            opts["big"] = True
        elif a.startswith("-"):
            sys.exit(__doc__)
        else:
            args.append(a)
        i += 1
    if len(args) != 1:
        sys.exit(__doc__)
    data_dir = args[0]
    wilayah = opts.get("wilayah") or os.path.join(ROOT, "data", "wilayah", "wilayah.json.gz")
    with gzip.open(wilayah, "rt", encoding="utf-8") as f:
        names = dict(json.load(f))
    with open(os.path.join(data_dir, "manifest.json"), encoding="utf-8") as f:
        manifest = json.load(f)
    entries = manifest.get("regencies") or []
    if not entries:
        sys.exit(f"{data_dir}/manifest.json lists no regency")
    jobs = max(1, min(opts.get("jobs") or os.cpu_count() or 1, len(entries)))
    print(f"{data_dir}: batas-wilayah {manifest.get('version')}, {len(entries)} regencies, tolerance "
          f"{manifest.get('tolerance_m')} m, {jobs} worker(s)", flush=True)
    work = [(data_dir, e, bool(opts.get("render"))) for e in entries]
    if jobs == 1:
        _init(names)
        results = map(regency_job, work)
        pool = None
    else:
        pool = multiprocessing.Pool(jobs, initializer=_init, initargs=(names,))
        results = pool.imap(regency_job, work)  # in manifest order, computed in parallel
    loaded, outlines = {}, {}
    for kab, lines, outline, villages, districts in results:
        for line, failed in lines:
            emit(line, failed)
        if outline is not None:
            outlines[kab] = outline
            loaded[kab] = (villages, districts)
    if pool:
        pool.close()
        pool.join()
    listed = {e.get("code") for e in entries}
    for sub in ("desa", "kecamatan"):
        for fname in sorted(os.listdir(os.path.join(data_dir, sub))):
            if fname.endswith(".geojson.gz") and fname[:-len(".geojson.gz")] not in listed:
                fail(f"{sub}/{fname} is not listed in the manifest")
    check_borders(outlines, names, float(manifest.get("tolerance_m") or 0))
    if opts.get("big"):
        def props(d):  # districts are full records when rendering, properties only otherwise
            return {c: (x if "props" in x else {"props": x}) for c, x in d.items()}
        with ThreadPoolExecutor(max(4, min(32, len(loaded)))) as ex:  # network bound: one request per regency
            fetched = list(ex.map(lambda kab: (kab, try_big(kab)), loaded))
        for kab, big in fetched:
            check_big(kab, props(loaded[kab][1]), names, big)
    if opts.get("render"):
        render(opts["render"], loaded, names)
    if failures:
        print(f"{len(failures)} check(s) failed")
        return 1
    print("all checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
