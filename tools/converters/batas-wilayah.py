#!/usr/bin/env python3
"""Build data/batas-wilayah: village (desa/kelurahan) and district (kecamatan) boundaries per regency, from the
national administrative boundary database of Badan Informasi Geospasial (BIG), keyed by the Kemendagri codes of
data/wilayah (F-035).

Two steps:

  python3 -I tools/converters/batas-wilayah.py fetch sources/batas-wilayah 33.19 [33.20 ...]
      Downloads every village polygon of the given regencies at full precision from BIG's public ArcGIS REST
      service (layer BATAS_DESAKEL_AR) into <raw_dir>/<regency>.json.gz, the service's own JSON, unchanged
      except for gzip. It only sends GET requests to the one host below.

  python3 -I tools/converters/batas-wilayah.py build sources/batas-wilayah data/wilayah/wilayah.json.gz \
          data/batas-wilayah [--tolerance=11]
      Reads every <regency>.json.gz in <raw_dir> and writes, per regency, desa/<regency>.geojson.gz and
      kecamatan/<regency>.geojson.gz (GeoJSON, RFC 7946, WGS 84).

  python3 -I /opt/apps/_fondasi/tools/converters/batas-wilayah.py presisi <out_dir> 33.19 [33.20 ...] [--accept-new]
      On a server (F-035): full precision is not kept in Fondasi; the server fetches it from BIG itself. Fetches
      the regencies into <out_dir>/raw/, checks that BIG still serves exactly the content Fondasi's
      data/batas-wilayah was built from (content_sha256 per regency in its manifest), then builds full-precision
      GeoJSON (coordinates rounded to 6 decimals, about 0.1 m) into <out_dir>/desa/ and <out_dir>/kecamatan/
      with manifest.json and SHA256SUMS. It refuses a regency Fondasi does not list yet, or one BIG has changed
      since, unless --accept-new is given (then update Fondasi too).

Simplification keeps neighbours together: rings are cut into arcs at the points where more than two polygons
meet (as TopoJSON does), every shared arc is simplified once (Douglas-Peucker, tolerance in metres), and both
neighbours use the same simplified arc, so no gaps or overlaps appear between villages. A district is the union of
its villages (BIG builds its district layer the same way, from KDCPUM): arcs inside the district cancel, the rest
are chained into rings.

The download is untrusted input: every field is checked with strict patterns (codes, status values, coordinate
ranges) and the script refuses to write when a code is not a village of the wilayah set, when a ring is not closed,
or when a simplified ring crosses itself.
"""
import gzip
import hashlib
import json
import math
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from collections import Counter, defaultdict

SERVICE = "https://geoservices.big.go.id/rbi/rest/services/BATASWILAYAH/BATAS_DESAKEL_AR/MapServer/0/query"
EDITION = "Edisi Juni 2026"
VERSION = "2026-06-15"  # metadata date of the edition (BIG CSW record on data.go.id)
PAGE = 1000
FIELDS = ["OBJECTID", "KDEPUM", "KDCPUM", "KDPKAB", "KDPPUM", "WADMKD", "WADMKC", "WADMKK", "TIPADM", "Status",
          "UUPP", "LUASWH", "REMARK"]
STATUSES = {"Batas Definitif", "Batas Indikatif", "Hasil Kesepakatan"}
REGENCY = re.compile(r"^\d{2}\.\d{2}$")
VILLAGE = re.compile(r"^\d{2}\.\d{2}\.\d{2}\.\d{4}$")
EARTH_RADIUS = 6371007.2  # authalic radius of WGS 84, metres
DECIMALS = 6  # about 0.1 m
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")


def content_sha256(features):
    """Checksum of what BIG served (attributes and rings of every feature, in OBJECTID order), independent of
    when it was fetched: equal checksums mean the same edition and the same revisions."""
    h = hashlib.sha256()
    for f in sorted(features, key=lambda f: f["attributes"]["OBJECTID"]):
        h.update(json.dumps([f["attributes"], f["geometry"]["rings"]], sort_keys=True,
                            separators=(",", ":"), ensure_ascii=False).encode())
        h.update(b"\n")
    return h.hexdigest()


# ---------------------------------------------------------------- fetch

def get_json(params):
    url = SERVICE + "?" + urllib.parse.urlencode(params)
    for attempt in range(4):
        try:
            with urllib.request.urlopen(url, timeout=180) as r:
                body = r.read()
            data = json.loads(body)
            if "error" in data:
                raise ValueError(str(data["error"])[:200])
            return data, body
        except Exception as e:  # network errors and service errors are retried
            if attempt == 3:
                sys.exit(f"BIG service failed for {params.get('where')}: {e}")
            time.sleep(5 * (attempt + 1))


def fetch(raw_dir, regencies):
    os.makedirs(raw_dir, exist_ok=True)
    hashes = {}
    for kab in regencies:
        if not REGENCY.match(kab):
            sys.exit(f"not a regency code: {kab}")
        where = f"KDPKAB='{kab}'"
        count, _ = get_json({"f": "json", "where": where, "returnCountOnly": "true"})
        expected = count["count"]
        features, first = [], None
        for offset in range(0, expected, PAGE):
            page, _ = get_json({"f": "json", "where": where, "outFields": ",".join(FIELDS), "returnGeometry": "true",
                                "orderByFields": "OBJECTID", "resultOffset": offset, "resultRecordCount": PAGE})
            first = first or page
            features += page["features"]
        if len(features) != expected or len({f["attributes"]["OBJECTID"] for f in features}) != expected:
            sys.exit(f"{kab}: expected {expected} features, got {len(features)} (or duplicates)")
        out = {"source": SERVICE, "where": where, "fetched": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
               "spatialReference": first["spatialReference"], "fields": FIELDS,
               "content_sha256": content_sha256(features), "features": features}
        hashes[kab] = out["content_sha256"]
        path = os.path.join(raw_dir, f"{kab}.json.gz")
        with gzip.GzipFile(path, "wb", mtime=0) as g:
            g.write(json.dumps(out, ensure_ascii=False, separators=(",", ":")).encode())
        print(f"{kab}: {expected} polygons -> {path}")
    return hashes


# ---------------------------------------------------------------- geometry helpers

def signed_area(ring):  # shoelace on lon/lat; > 0 means counter-clockwise
    s = 0.0
    for (x1, y1), (x2, y2) in zip(ring, ring[1:]):
        s += x1 * y2 - x2 * y1
    return s / 2


WGS84_A, WGS84_F = 6378137.0, 1 / 298.257223563
WGS84_E = math.sqrt(WGS84_F * (2 - WGS84_F))


def _q(phi):  # authalic latitude helper (Snyder 1987, eq. 3-12)
    e, s = WGS84_E, math.sin(phi)
    return (1 - e * e) * (s / (1 - e * e * s * s) - math.log((1 - e * s) / (1 + e * s)) / (2 * e))


QP = _q(math.pi / 2)


def geodesic_area(ring):
    """Square metres on the WGS 84 ellipsoid, sign ignored: latitudes go to authalic latitudes, then the
    trapezoid formula on the authalic sphere (equal-area, so the result is the ellipsoidal area)."""
    s = 0.0
    beta = [math.asin(_q(math.radians(y)) / QP) for _, y in ring]
    for i in range(len(ring) - 1):
        s += math.radians(ring[i + 1][0] - ring[i][0]) * (2 + math.sin(beta[i]) + math.sin(beta[i + 1]))
    return abs(s) * (WGS84_A ** 2 * QP / 2) / 2


def polygon_area(polygon):  # [outer, hole, ...]
    return geodesic_area(polygon[0]) - sum(geodesic_area(h) for h in polygon[1:])


def point_in_ring(pt, ring):
    x, y = pt
    inside = False
    for (x1, y1), (x2, y2) in zip(ring, ring[1:]):
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
            inside = not inside
    return inside


def to_metres(points):
    lat0 = math.radians(sum(p[1] for p in points) / len(points))
    kx = math.cos(lat0) * math.pi * EARTH_RADIUS / 180
    ky = math.pi * EARTH_RADIUS / 180
    return [(p[0] * kx, p[1] * ky) for p in points]


def douglas_peucker(points, tolerance, keep_one=False):
    """Indexes to keep of an open polyline; the ends are always kept."""
    xy = to_metres(points)
    keep = {0, len(points) - 1}
    stack = [(0, len(points) - 1, keep_one)]
    while stack:
        a, b, force = stack.pop()
        if b - a < 2:
            continue
        (ax, ay), (bx, by) = xy[a], xy[b]
        dx, dy = bx - ax, by - ay
        norm = math.hypot(dx, dy)
        best, best_d = None, -1.0
        for i in range(a + 1, b):
            px, py = xy[i]
            d = abs(dy * (px - ax) - dx * (py - ay)) / norm if norm else math.hypot(px - ax, py - ay)
            if d > best_d:
                best, best_d = i, d
        if best_d > tolerance or force:
            keep.add(best)
            stack += [(a, best, False), (best, b, False)]
    return sorted(keep)


def segments_cross(p1, p2, p3, p4):
    def orient(a, b, c):
        v = (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
        return (v > 0) - (v < 0)
    o1, o2, o3, o4 = orient(p1, p2, p3), orient(p1, p2, p4), orient(p3, p4, p1), orient(p3, p4, p2)
    return o1 != o2 and o3 != o4 and 0 not in (o1, o2, o3, o4)


def self_crossing(ring):
    n = len(ring) - 1
    segs = [(ring[i], ring[i + 1]) for i in range(n)]
    for i in range(n):
        for j in range(i + 2, n):
            if i == 0 and j == n - 1:
                continue
            if segments_cross(*segs[i], *segs[j]):
                return True
    return False


# ---------------------------------------------------------------- topology

class Topology:
    """Cuts rings into shared arcs, simplifies each arc once, and rebuilds rings from the arcs."""

    def __init__(self, rings):
        self.rings = rings  # list of closed rings (lists of (x, y) tuples)
        seen, junctions = {}, set()
        for ring in rings:
            pts = ring[:-1]
            n = len(pts)
            for i, p in enumerate(pts):
                pair = frozenset((pts[i - 1], pts[(i + 1) % n]))
                if p in seen and seen[p] != pair:
                    junctions.add(p)
                seen.setdefault(p, pair)
        self.arcs, self.index, self.refs = [], {}, []
        for ring in rings:
            self.refs.append([self._add(arc) for arc in self._cut(ring[:-1], junctions)])

    @staticmethod
    def _cut(pts, junctions):
        cuts = [i for i, p in enumerate(pts) if p in junctions]
        if not cuts:  # a ring with no junction is one closed arc, started at its smallest point
            i = pts.index(min(pts))
            return [pts[i:] + pts[:i] + [pts[i]]]
        start = cuts[0]
        rotated = pts[start:] + pts[:start]
        cuts = [c - start if c >= start else c - start + len(pts) for c in cuts] + [len(pts)]
        rotated.append(rotated[0])
        return [rotated[a:b + 1] for a, b in zip(cuts, cuts[1:])]

    def _add(self, arc):
        key, rev = tuple(arc), tuple(reversed(arc))
        if key in self.index:
            return (self.index[key], 1)
        if rev in self.index:
            return (self.index[rev], -1)
        self.index[key] = len(self.arcs)
        self.arcs.append(arc)
        return (len(self.arcs) - 1, 1)

    def simplify(self, tolerance):
        self.simple = [self._simplify_arc(a, tolerance, False) for a in self.arcs]
        # a ring made of one or two arcs can collapse to a line; keep one more point in each of its arcs
        for refs in self.refs:
            if len(self.ring(refs)) < 4:
                for arc_id, _ in refs:
                    self.simple[arc_id] = self._simplify_arc(self.arcs[arc_id], tolerance, True)

    @staticmethod
    def _simplify_arc(arc, tolerance, keep_one):
        if tolerance <= 0:
            out = arc
        elif arc[0] == arc[-1]:  # closed: split at the point farthest from the start
            far = max(range(len(arc)), key=lambda i: (arc[i][0] - arc[0][0]) ** 2 + (arc[i][1] - arc[0][1]) ** 2)
            a = douglas_peucker(arc[:far + 1], tolerance, True)
            b = douglas_peucker(arc[far:], tolerance, True)
            out = [arc[i] for i in a] + [arc[far + i] for i in b[1:]]
        else:
            out = [arc[i] for i in douglas_peucker(arc, tolerance, keep_one)]
        rounded = []
        for x, y in out:
            p = (round(x, DECIMALS), round(y, DECIMALS))
            if not rounded or rounded[-1] != p:
                rounded.append(p)
        return rounded

    def ring(self, refs, simplified=True):
        arcs = self.simple if simplified else self.arcs
        out = []
        for arc_id, direction in refs:
            pts = arcs[arc_id] if direction == 1 else list(reversed(arcs[arc_id]))
            out += pts if not out else pts[1:]
        return out


def assemble(rings):
    """Group closed rings (any orientation) into RFC 7946 polygons: outer counter-clockwise, holes clockwise."""
    outers = [r for r in rings if signed_area(r) < 0]  # Esri: outer rings are clockwise
    holes = [r for r in rings if signed_area(r) > 0]
    polys = [[list(reversed(o))] for o in outers]
    for h in holes:
        hosts = [p for p in polys if all(point_in_ring(pt, p[0]) for pt in h[:3])] or \
                [p for p in polys if point_in_ring(h[0], p[0])]
        if not hosts:
            raise ValueError("hole outside every outer ring")
        min(hosts, key=lambda p: geodesic_area(p[0])).append(list(reversed(h)))
    return polys


def chain(directed):
    """Chain directed arcs (lists of points) end to start into closed rings."""
    by_start = defaultdict(list)
    for pts in directed:
        by_start[pts[0]].append(pts)
    rings = []
    while any(by_start.values()):
        start = next(k for k, v in by_start.items() if v)
        pts = by_start[start].pop()
        ring = list(pts)
        while ring[-1] != ring[0]:
            nxt = by_start.get(ring[-1])
            if not nxt:
                raise ValueError("district boundary does not close")
            ring += nxt.pop()[1:]
        rings.append(ring)
    return rings


def geometry(polys):
    coords = [[[list(p) for p in ring] for ring in poly] for poly in polys]
    return {"type": "Polygon", "coordinates": coords[0]} if len(coords) == 1 else \
        {"type": "MultiPolygon", "coordinates": coords}


# ---------------------------------------------------------------- build

def read_raw(path, kab):
    raw = json.load(gzip.open(path, "rt", encoding="utf-8"))
    if raw.get("spatialReference", {}).get("wkid") != 4326:
        sys.exit(f"{path}: spatial reference is not WGS 84")
    villages, undefined = defaultdict(list), 0
    digest = content_sha256(raw["features"])
    for f in raw["features"]:
        a = f["attributes"]
        if a.get("TIPADM") == 999:
            undefined += 1
            continue
        code = (a.get("KDEPUM") or "").strip()
        if not VILLAGE.match(code) or not code.startswith(kab + ".") or a.get("KDCPUM") != code[:8]:
            sys.exit(f"{path}: bad village code {code!r} / {a.get('KDCPUM')!r}")
        if a.get("TIPADM") not in (1, 2) or a.get("Status") not in STATUSES:
            sys.exit(f"{path}: {code}: unexpected TIPADM {a.get('TIPADM')!r} or status {a.get('Status')!r}")
        rings = []
        for r in f["geometry"]["rings"]:
            ring = [(float(x), float(y)) for x, y, *_ in r]
            if len(ring) < 4 or ring[0] != ring[-1]:
                sys.exit(f"{path}: {code}: ring not closed")
            if not all(94 <= x <= 142 and -12 <= y <= 7 for x, y in ring):
                sys.exit(f"{path}: {code}: coordinate outside Indonesia")
            rings.append(ring)
        villages[code].append({"attrs": a, "rings": rings})
    return villages, undefined, digest


def clean_text(s):
    s = re.sub(r"\s+", " ", (s or "")).strip()
    return s or None


def build(raw_dir, wilayah_path, out_dir, tolerance, server_copy=None, matches=None):
    names = dict(json.load(gzip.open(wilayah_path, "rt", encoding="utf-8")))
    files = sorted(f for f in os.listdir(raw_dir) if re.match(r"^\d{2}\.\d{2}\.json\.gz$", f))
    if not files:
        sys.exit(f"no <regency>.json.gz in {raw_dir}")
    for sub in ("desa", "kecamatan"):
        os.makedirs(os.path.join(out_dir, sub), exist_ok=True)
    summary = {"regencies": [], "villages": 0, "districts": 0, "villages_without_polygon": [],
               "undefined_areas": 0, "status": Counter()}
    worst = (0.0, None)
    for fname in files:
        kab = fname[:5]
        if kab not in names:
            sys.exit(f"{kab} is not a regency of the wilayah set")
        villages, undefined, digest = read_raw(os.path.join(raw_dir, fname), kab)
        unknown = sorted(c for c in villages if c not in names)
        if unknown:
            sys.exit(f"{kab}: codes not in the wilayah set: {unknown[:5]}")
        expected = sorted(c for c in names if len(c) == 13 and c.startswith(kab + "."))
        missing = [c for c in expected if c not in villages]

        codes = sorted(villages)
        all_rings, owner = [], []
        for code in codes:
            for part in villages[code]:
                for ring in part["rings"]:
                    all_rings.append(ring)
                    owner.append(code)
        topo = Topology(all_rings)
        topo.simplify(tolerance)
        rings_of = defaultdict(list)
        for i, code in enumerate(owner):
            rings_of[code].append(i)

        desa_features, area_full = [], {}
        for code in codes:
            full = assemble([topo.ring(topo.refs[i], False) for i in rings_of[code]])
            simple_rings = [topo.ring(topo.refs[i]) for i in rings_of[code]]
            for r in simple_rings:
                if len(r) < 4 or (tolerance > 0 and self_crossing(r)):
                    sys.exit(f"{code}: simplified ring is degenerate or crosses itself")
            simple = assemble(simple_rings)
            a_full = sum(polygon_area(p) for p in full)
            a_simple = sum(polygon_area(p) for p in simple)
            area_full[code] = a_full
            diff = abs(a_simple - a_full) / a_full
            if diff > worst[0]:
                worst = (diff, code)
            attrs = [p["attrs"] for p in villages[code]]
            status = sorted({a["Status"] for a in attrs})
            basis = sorted({b for a in attrs for b in [clean_text(a.get("UUPP"))] if b})
            props = {"code": code, "name": names[code], "district": code[:8],
                     "type": "kelurahan" if code[9] == "1" else "desa",
                     "status": status[0] if len(status) == 1 else status,
                     "basis": basis[0] if len(basis) == 1 else (basis or None),
                     "area_km2": round(a_full / 1e6, 4)}
            summary["status"].update(status)
            desa_features.append({"type": "Feature", "properties": props, "geometry": geometry(simple)})

        kec_features = []
        for kec in sorted({c[:8] for c in codes}):
            members = [c for c in codes if c[:8] == kec]
            use = Counter()
            for c in members:
                for i in rings_of[c]:
                    for arc_id, d in topo.refs[i]:
                        use[(arc_id, d)] += 1
            directed = []
            for (arc_id, d), n in use.items():
                net = n - use.get((arc_id, -d), 0)
                pts = topo.simple[arc_id] if d == 1 else list(reversed(topo.simple[arc_id]))
                directed += [pts] * max(net, 0)
            rings = chain(directed)
            for r in rings:
                if len(r) < 4 or (tolerance > 0 and self_crossing(r)):
                    sys.exit(f"{kec}: district ring is degenerate or crosses itself")
            props = {"code": kec, "name": names[kec], "villages": len(members),
                     "area_km2": round(sum(area_full[c] for c in members) / 1e6, 4)}
            kec_features.append({"type": "Feature", "properties": props, "geometry": geometry(assemble(rings))})
        expected_kec = sorted(c for c in names if len(c) == 8 and c.startswith(kab + "."))
        missing_kec = [c for c in expected_kec if c not in {f["properties"]["code"] for f in kec_features}]

        for sub, feats in (("desa", desa_features), ("kecamatan", kec_features)):
            body = json.dumps({"type": "FeatureCollection", "features": feats}, ensure_ascii=False,
                              separators=(",", ":"))
            with gzip.GzipFile(os.path.join(out_dir, sub, f"{kab}.geojson.gz"), "wb", mtime=0) as g:
                g.write(body.encode())
        summary["regencies"].append({"code": kab, "name": names[kab], "villages": len(desa_features),
                                     "districts": len(kec_features), "villages_without_polygon": missing,
                                     "districts_without_polygon": missing_kec, "undefined_areas": undefined,
                                     "arcs": len(topo.arcs), "content_sha256": digest})
        if matches is not None:
            summary["regencies"][-1]["matches_fondasi"] = matches.get(kab, False)
        summary["villages"] += len(desa_features)
        summary["districts"] += len(kec_features)
        summary["villages_without_polygon"] += missing
        summary["undefined_areas"] += undefined
        print(f"{kab} {names[kab]}: {len(desa_features)} villages, {len(kec_features)} districts, "
              f"{len(missing)} villages without polygon, {undefined} undefined areas, {len(topo.arcs)} arcs")
    summary["status"] = dict(sorted(summary["status"].items()))
    summary["largest_area_change"] = {"code": worst[1], "percent": round(worst[0] * 100, 3)}
    manifest = {
        "version": VERSION,
        "description": "Boundaries of villages (desa/kelurahan) and districts (kecamatan), one GeoJSON file per "
                       "regency and level, " + (f"simplified to about {tolerance:g} m with shared borders kept "
                       "together" if tolerance > 0 else "at full precision (coordinates rounded to 6 decimals, "
                       "about 0.1 m)") + "; keyed by the Kemendagri codes of the wilayah set.",
        "status": server_copy or "partial: regencies listed in `regencies`; others are added on demand (F-035)",
        "source": f"Badan Informasi Geospasial, Basis Data Batas Wilayah Administrasi {EDITION} (metadata date "
                  f"{VERSION}), layer BATAS_DESAKEL_AR of {SERVICE.rsplit('/MapServer', 1)[0]}; " +
                  ("fetched by this server into raw/" if server_copy else
                   "full-precision download kept in sources/batas-wilayah/; servers fetch full precision "
                   "themselves with the presisi command (F-035)"),
        "licence": "Informasi Geospasial Dasar, open by law (UU 4/2011 Pasal 12 huruf e and Pasal 42); credit "
                   "\"Sumber: Badan Informasi Geospasial\" (F-035)",
        "procedure": "tools/converters/batas-wilayah.py presisi <out_dir> <regency...>" if server_copy else
                     "tools/converters/batas-wilayah.py fetch <raw_dir> <regency...>, then build <raw_dir> "
                     "data/wilayah/wilayah.json.gz data/batas-wilayah --tolerance=" + f"{tolerance:g}",
        "tolerance_m": tolerance,
        "coordinate_decimals": DECIMALS,
        "crs": "WGS 84 (EPSG:4326), RFC 7946: outer rings counter-clockwise, holes clockwise",
        "files": {"desa/<regency>.geojson.gz": "one Feature per village",
                  "kecamatan/<regency>.geojson.gz": "one Feature per district, the union of its villages"},
        "fields": {
            "desa": {"code": "village code xx.xx.xx.xxxx (wilayah)", "name": "official name from wilayah",
                     "district": "district code xx.xx.xx", "type": "desa or kelurahan (from the code)",
                     "status": "boundary status as BIG writes it: Batas Definitif, Hasil Kesepakatan or Batas "
                               "Indikatif",
                     "basis": "regulation the boundary rests on, as BIG writes it (null when none)",
                     "area_km2": "area of the full-precision polygon on the WGS 84 ellipsoid"},
            "kecamatan": {"code": "district code xx.xx.xx", "name": "official name from wilayah",
                          "villages": "number of villages with a polygon",
                          "area_km2": "sum of the villages' full-precision areas"}},
        "regencies": summary["regencies"],
        "villages": summary["villages"],
        "districts": summary["districts"],
        "status_counts": summary["status"],
        "largest_area_change_percent": summary["largest_area_change"],
        "notes": [
            "Only 'Batas Definitif' rests on a signed regulation. 'Hasil Kesepakatan' is agreed by the villages and "
            "checked by BIG; 'Batas Indikatif' is a working line. UU 4/2011 Pasal 16 ayat (2): show boundaries that "
            "are not definitive with a different line style or colour, and never present any of them as a legal "
            "boundary.",
            "Use for maps, filters and 'which village is this point in' hints; let users correct the village they "
            "chose. Credit: Sumber: Badan Informasi Geospasial.",
            "District areas equal BIG's own district layer (BATAS_KECAMATAN_AR) to four decimals.",
        ],
    }
    with open(os.path.join(out_dir, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(json.dumps(summary, ensure_ascii=False, indent=1))
    return summary


def presisi(out_dir, regencies, accept_new):
    ref_path = os.path.join(ROOT, "data", "batas-wilayah", "manifest.json")
    ref = json.load(open(ref_path, encoding="utf-8"))
    known = {r["code"]: r.get("content_sha256") for r in ref["regencies"]}
    hashes = fetch(os.path.join(out_dir, "raw"), regencies)
    problems = []
    for kab, digest in hashes.items():
        if kab not in known:
            problems.append(f"{kab}: Fondasi's data/batas-wilayah {ref['version']} does not list this regency yet")
        elif digest != known[kab]:
            problems.append(f"{kab}: BIG now serves other content than Fondasi's data/batas-wilayah {ref['version']} "
                            f"was built from (new edition or revision)")
        else:
            print(f"{kab}: same content as Fondasi's data/batas-wilayah {ref['version']}")
    if problems and not accept_new:
        for p in problems:
            print("REFUSED " + p, file=sys.stderr)
            os.remove(os.path.join(out_dir, "raw", p[:5] + ".json.gz"))  # never built later by accident
        sys.exit("Add or refresh these regencies in Fondasi first (fetch, build, PR), pull /opt/apps/_fondasi and run "
                 "this again; or pass --accept-new to build from what BIG serves now.")
    for p in problems:
        print("ACCEPTED " + p, file=sys.stderr)
    raw_dir = os.path.join(out_dir, "raw")
    matches = {}
    for fname in sorted(os.listdir(raw_dir)):
        if re.match(r"^\d{2}\.\d{2}\.json\.gz$", fname):
            raw = json.load(gzip.open(os.path.join(raw_dir, fname), "rt", encoding="utf-8"))
            matches[fname[:5]] = known.get(fname[:5]) == content_sha256(raw["features"])
    status = (f"server copy at full precision, checked against Fondasi data/batas-wilayah {ref['version']}" +
              ("" if all(matches.values()) else "; regencies with matches_fondasi false were accepted with "
               "--accept-new"))
    build(raw_dir, os.path.join(ROOT, "data", "wilayah", "wilayah.json.gz"), out_dir, 0,
          server_copy=status, matches=matches)
    sums = []
    for base, _, names in os.walk(out_dir):
        for n in names:
            rel = os.path.relpath(os.path.join(base, n), out_dir)
            if rel != "SHA256SUMS":
                with open(os.path.join(base, n), "rb") as f:
                    sums.append(f"{hashlib.sha256(f.read()).hexdigest()}  {rel}")
    with open(os.path.join(out_dir, "SHA256SUMS"), "w") as f:
        f.write("\n".join(sorted(sums, key=lambda l: l.split("  ", 1)[1])) + "\n")
    print(f"done: {out_dir}")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    opts = dict(a[2:].split("=", 1) for a in sys.argv[1:] if a.startswith("--") and "=" in a)
    if len(args) >= 3 and args[0] == "fetch":
        fetch(args[1], args[2:])
    elif len(args) == 4 and args[0] == "build":
        build(args[1], args[2], args[3], float(opts.get("tolerance", 11)))
    elif len(args) >= 3 and args[0] == "presisi":
        presisi(args[1], args[2:], "--accept-new" in sys.argv[1:])
    else:
        sys.exit(__doc__)
