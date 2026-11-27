#!/usr/bin/env python3
"""Build data/batas-wilayah: village (desa/kelurahan) and district (kecamatan) boundaries per regency, from the
national administrative boundary database of Badan Informasi Geospasial (BIG), keyed by the Kemendagri codes of
data/wilayah (F-035).

Two steps:

  python3 -I tools/converters/batas-wilayah.py fetch <raw_dir> 33.19 [33.20 ...]
      Downloads every village polygon of the given regencies at full precision from BIG's public ArcGIS REST
      service (layer BATAS_DESAKEL_AR) into <raw_dir>/<regency>.json.gz, the service's own JSON, unchanged
      except for gzip. It only sends GET requests to the one host below. Keep <raw_dir> outside the repository
      (65 MB for Jawa Tengah; F-035); run several regencies in parallel, e.g. xargs -P 4 (about 5 minutes for
      Jawa Tengah).

  python3 -I tools/converters/batas-wilayah.py build <raw_dir> data/wilayah/wilayah.json.gz \
          data/batas-wilayah [--tolerance=11] [--workers=N]
      Reads every <regency>.json.gz in <raw_dir> and writes, per regency, desa/<regency>.geojson.gz and
      kecamatan/<regency>.geojson.gz (GeoJSON, RFC 7946, WGS 84), one regency per worker (default: every CPU;
      about 30 s for Jawa Tengah on 4 CPUs). Always build all regencies of the set together: borders between
      regencies are cut and simplified together.

  python3 -I /opt/apps/_fondasi/tools/converters/batas-wilayah.py presisi <out_dir> 33.19 [33.20 ...] [--accept-new]
      On a server (F-035): full precision is not kept in Fondasi; the server fetches it from BIG itself. Fetches
      the regencies into <out_dir>/raw/, checks that BIG still serves exactly the content Fondasi's
      data/batas-wilayah was built from (content_sha256 per regency in its manifest), then builds full-precision
      GeoJSON (coordinates rounded to 6 decimals, about 0.1 m) into <out_dir>/desa/ and <out_dir>/kecamatan/
      with manifest.json and SHA256SUMS. It refuses a regency Fondasi does not list yet, or one BIG has changed
      since, unless --accept-new is given (then update Fondasi too).

Simplification keeps neighbours together: rings are cut into arcs at the points where more than two polygons
meet (as TopoJSON does), every shared arc is simplified once (Douglas-Peucker, tolerance in metres), and both
neighbours use the same simplified arc, so no gaps or overlaps appear between villages. Across regencies the
build runs in passes: pass 1 finds the points where neighbouring regencies must cut their border arcs the same
way, pass 2 repeats the simplification until both sides of every border arc are identical (arcs one regency had
to keep finer are kept as fine in its neighbour), pass 3 writes. Arcs that would make a ring collapse or cross
itself or another ring are refined step by step: half the tolerance, every point, then up to MAX_DECIMALS
decimals for arcs (and junctions) where rounding to DECIMALS alone makes the crossing. A district is the union of
its villages (BIG builds its district layer the same way, from KDCPUM): arcs inside the district cancel, the rest
are chained into rings.

The download is untrusted input: every field is checked with strict patterns (codes, status values, coordinate
ranges) and the script refuses to write when a code is not a village of the wilayah set, when a ring is not closed,
or when a ring still crosses itself (or another) at full precision; the message names the villages.
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
MAX_DECIMALS = 9  # arcs that would cross themselves at DECIMALS keep up to this many (F-035)
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


def crossing_segments(ring, first_only=False):
    """Indexes of the segments (ring[i], ring[i + 1]) that cross another segment of the same ring; segments are
    sorted into grid cells first, so full-precision rings with thousands of points stay fast."""
    n = len(ring) - 1
    if n < 4:
        return set()
    xs, ys = [p[0] for p in ring], [p[1] for p in ring]
    cell = max(max(xs) - min(xs), max(ys) - min(ys)) / max(1, int(math.sqrt(n))) or 1.0
    x0, y0 = min(xs), min(ys)
    grid = defaultdict(list)
    for i in range(n):
        (x1, y1), (x2, y2) = ring[i], ring[i + 1]
        for gx in range(int((min(x1, x2) - x0) / cell), int((max(x1, x2) - x0) / cell) + 1):
            for gy in range(int((min(y1, y2) - y0) / cell), int((max(y1, y2) - y0) / cell) + 1):
                grid[(gx, gy)].append(i)
    found, tested = set(), set()
    for segs in grid.values():
        for a in range(len(segs)):
            for b in range(a + 1, len(segs)):
                i, j = segs[a], segs[b]
                if j - i < 2 or (i == 0 and j == n - 1) or (i, j) in tested:
                    continue
                tested.add((i, j))
                if segments_cross(ring[i], ring[i + 1], ring[j], ring[j + 1]):
                    found |= {i, j}
                    if first_only:
                        return found
    return found


def self_crossing(ring):
    return bool(crossing_segments(ring, True))


def arc_crossings(arcs):
    """Pairs of arc ids (a <= b) with segments that cross each other (touching at a shared point does not count)."""
    segs = [(a, i) for a, pts in enumerate(arcs) for i in range(len(pts) - 1)]
    if not segs:
        return set()
    xs = [p[0] for pts in arcs for p in pts]
    ys = [p[1] for pts in arcs for p in pts]
    x0, y0 = min(xs), min(ys)
    cell = max(max(xs) - x0, max(ys) - y0) / max(1, int(math.sqrt(len(segs)))) or 1.0
    grid = defaultdict(list)
    for a, i in segs:
        (x1, y1), (x2, y2) = arcs[a][i], arcs[a][i + 1]
        for gx in range(int((min(x1, x2) - x0) / cell), int((max(x1, x2) - x0) / cell) + 1):
            for gy in range(int((min(y1, y2) - y0) / cell), int((max(y1, y2) - y0) / cell) + 1):
                grid[(gx, gy)].append((a, i))
    found = set()
    for cell_segs in grid.values():
        for u in range(len(cell_segs)):
            a, i = cell_segs[u]
            p1, p2 = arcs[a][i], arcs[a][i + 1]
            for v in range(u + 1, len(cell_segs)):
                b, j = cell_segs[v]
                if (min(a, b), max(a, b)) in found:
                    continue
                if segments_cross(p1, p2, arcs[b][j], arcs[b][j + 1]):
                    found.add((min(a, b), max(a, b)))
    return found


# ---------------------------------------------------------------- topology

class Topology:
    """Cuts rings into shared arcs, simplifies each arc once, and rebuilds rings from the arcs."""

    def __init__(self, rings, extra_junctions=frozenset(), labels=None):
        self.rings = rings  # list of closed rings (lists of (x, y) tuples)
        self.labels = labels or [str(i) for i in range(len(rings))]  # village code of each ring, for messages
        seen, junctions = {}, set()
        for ring in rings:
            pts = ring[:-1]
            n = len(pts)
            for i, p in enumerate(pts):
                pair = frozenset((pts[i - 1], pts[(i + 1) % n]))
                if p in seen and seen[p] != pair:
                    junctions.add(p)
                seen.setdefault(p, pair)
        junctions |= set(p for p in extra_junctions if p in seen)
        self.junctions = junctions
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

    def outline_arcs(self):
        """Arc ids used by one ring only: the outline of the whole set (regency border, coast)."""
        use = Counter(arc_id for refs in self.refs for arc_id, _ in refs)
        return [arc_id for arc_id, n in use.items() if n == 1]

    def outline_points(self):
        """Points on the outline: {point: neighbour pair} for plain points, and the outline points that are
        junctions inside the set."""
        pairs, inner_junctions = {}, set()
        for arc_id in self.outline_arcs():
            arc = self.arcs[arc_id]
            closed = arc[0] == arc[-1]
            for i, p in enumerate(arc):
                if p in self.junctions:
                    inner_junctions.add(p)
                elif 0 < i < len(arc) - 1:
                    pairs[p] = frozenset((arc[i - 1], arc[i + 1]))
                elif closed:
                    pairs[p] = frozenset((arc[1], arc[-2]))
        return pairs, inner_junctions

    def key(self, arc_id):
        """Identity of an arc that does not depend on direction or on which regency sees it."""
        arc = self.arcs[arc_id]
        if self._flip(arc):
            arc = arc[::-1]
        return hashlib.sha256(repr(arc).encode()).digest()

    @staticmethod
    def _flip(arc):
        closed = arc[0] == arc[-1]
        return (closed and len(arc) > 3 and arc[1] > arc[-2]) or (not closed and arc[0] > arc[-1])

    def simplify(self, tolerance, forced=None, fine_points=None):
        """forced: {arc key: tolerance} for arcs refined in an earlier round of the build (border arcs also when the
        neighbouring regency needed them finer); such arcs, and every arc this method refines, are simplified with
        keep_one, so the same tolerance gives the same arc on both sides of a border. fine_points: junctions that
        an earlier round gave MAX_DECIMALS (see below), in every arc that ends there."""
        self.refined = {}  # arc id -> tolerance used with keep_one (anything but the default)
        self.fine = {p for p in (fine_points or ()) if p in self.junctions}
        self.tolerance = tolerance
        if forced:
            for arc_id in range(len(self.arcs)):
                k = self.key(arc_id)
                if k in forced:
                    self.refined[arc_id] = forced[k]
        self.simple = [self._arc(i) for i in range(len(self.arcs))]
        # a ring made of one or two arcs can collapse to a line; keep one more point in each of its arcs
        for refs in self.refs if tolerance > 0 else []:
            if len(self.ring(refs)) < 4:
                for arc_id, _ in refs:
                    self.refined.setdefault(arc_id, tolerance)
                    self.simple[arc_id] = self._arc(arc_id)
        # a ring that crosses itself after simplification: halve the tolerance of the arcs that cross until it
        # does not (narrow strips, rivers); below 0.5 m the arc keeps every point. A ring that still crosses itself
        # then does so only because of rounding (BIG zigzags of a few millimetres: 34 rings of Jawa Tengah cross
        # themselves at 6 decimals, none as BIG serves them): those arcs get one more decimal per round for their
        # inner points, up to MAX_DECIMALS, and then their ends (junctions, shared with other arcs) get
        # MAX_DECIMALS in every arc that meets there. Full-precision builds (tolerance 0, presisi) go through the
        # same loop
        # Last, arcs of different rings (two parts of one village, or neighbours) that cross each other get the
        # same treatment, and the rings that use them are checked again.
        uses = defaultdict(set)  # arc id -> rings that use it
        for i, refs in enumerate(self.refs):
            for arc_id, _ in refs:
                uses[arc_id].add(i)
        todo = list(range(len(self.refs)))
        while True:
            while todo:
                bad = [i for i in todo if self.bad_ring(i)]
                if bad and not self._refine([a for i in bad for a in self._crossing_arcs(self.refs[i])]):
                    raise ValueError("a ring crosses itself even at full precision: " +
                                     ", ".join(sorted({self.labels[i] for i in bad})))
                todo = bad
            crossing = sorted({a for pair in arc_crossings(self.simple) for a in pair})
            if not crossing:
                break
            changed = self._refine(crossing)
            if not changed:
                raise ValueError("arcs cross each other even at full precision: " +
                                 ", ".join(sorted({self.labels[i] for a in crossing for i in uses[a]})))
            todo = sorted({i for a in changed for i in uses[a]})

    def _refine(self, arc_ids):
        """One step finer for each arc (half the tolerance, then every point, then one more decimal; an arc that
        is already finest gives its ends MAX_DECIMALS). Returns the ids of the arcs that changed."""
        finest = DECIMALS - MAX_DECIMALS  # refined value of an arc with every point and MAX_DECIMALS decimals
        changed, new_fine = set(), set()
        for arc_id in dict.fromkeys(arc_ids):
            tol = self.refined.get(arc_id, self.tolerance)
            if tol <= finest:
                arc = self.arcs[arc_id]
                new_fine |= {arc[0], arc[-1]} & self.junctions - self.fine
                continue
            self.refined[arc_id] = (0 if tol / 2 < 0.5 else tol / 2) if tol > 0 else tol - 1
            self.simple[arc_id] = self._arc(arc_id)
            changed.add(arc_id)
        if new_fine:
            self.fine |= new_fine
            for arc_id, arc in enumerate(self.arcs):
                if arc[0] in new_fine or arc[-1] in new_fine:
                    self.simple[arc_id] = self._arc(arc_id)
                    changed.add(arc_id)
        return changed

    def _arc(self, arc_id):
        arc = self.arcs[arc_id]
        ends = tuple(MAX_DECIMALS if p in self.fine else DECIMALS for p in (arc[0], arc[-1]))
        return self._simplify_arc(arc, self.refined.get(arc_id, self.tolerance), arc_id in self.refined, ends)

    def _crossing_arcs(self, refs):
        """Arcs of a ring that take part in a crossing (refining only these keeps the ring's other arcs, often
        borders shared with a neighbouring regency, as they are); every arc when the ring collapsed."""
        ring, seg_arc = [], []
        for arc_id, direction in refs:
            pts = self.simple[arc_id] if direction == 1 else list(reversed(self.simple[arc_id]))
            pts = pts if not ring else pts[1:]
            ring += pts
            seg_arc += [arc_id] * len(pts)
        crossing = crossing_segments(ring) if len(ring) >= 4 else ()
        if not crossing:  # collapsed: too few points, an edge used twice, no area or turned around
            return list(dict.fromkeys(a for a, _ in refs))
        return list(dict.fromkeys(seg_arc[i + 1] for i in sorted(crossing)))

    def bad_ring(self, i):
        """A simplified ring that cannot stand for the original: too few points, an edge used twice (a narrow
        strip that became a line), no area or the other orientation, or crossing itself."""
        ring = self.ring(self.refs[i])
        if len(ring) < 4 or len({frozenset(e) for e in zip(ring, ring[1:])}) < len(ring) - 1:
            return True
        if signed_area(ring) * signed_area(self.rings[i]) <= 0:
            return True
        return self_crossing(ring)

    @staticmethod
    def _simplify_arc(arc, tolerance, keep_one, ends=(DECIMALS, DECIMALS)):
        """tolerance > 0: Douglas-Peucker in metres; 0: every point; -1, -2, ...: every point, inner points with
        1, 2, ... more decimals than DECIMALS (arcs whose rounding would make a ring cross itself). ends: decimals
        of the first and last point, which other arcs share."""
        # simplify every arc in one canonical direction, so a border seen from both sides gives the same result
        if Topology._flip(arc):
            return list(reversed(Topology._simplify_arc(list(reversed(arc)), tolerance, keep_one, ends[::-1])))
        decimals = DECIMALS - min(int(tolerance), 0) if tolerance <= 0 else DECIMALS
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
        for i, (x, y) in enumerate(out):
            d = ends[0] if i == 0 else ends[1] if i == len(out) - 1 else decimals  # ends are shared: same rounding
            p = (round(x, d), round(y, d))
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
        if len(pts) > 1:  # an arc between two junctions less than 0.1 m apart rounds to one point: nothing to chain
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


_JOB = {}  # read-only context of a build, inherited by the forked workers


def _worker(fn, arg):
    """Run fn in a worker; an exit inside a worker becomes an error the parent reports (a pool would hang)."""
    try:
        return fn(arg)
    except SystemExit as e:
        raise RuntimeError(str(e)) from None
    except ValueError as e:
        raise RuntimeError(f"{arg}: {e}") from None


def _run(fn, items, workers):
    if workers <= 1 or len(items) <= 1:
        return [fn(i) for i in items]
    import multiprocessing
    with multiprocessing.get_context("fork").Pool(min(workers, len(items))) as pool:
        try:
            return pool.starmap(_worker, [(fn, i) for i in items])
        except RuntimeError as e:
            sys.exit(str(e))


def _regency_topology(fname):
    villages, undefined, digest = read_raw(os.path.join(_JOB["raw_dir"], fname), fname[:5])
    codes = sorted(villages)
    rings = [r for c in codes for part in villages[c] for r in part["rings"]]
    owner = [c for c in codes for part in villages[c] for _ in part["rings"]]
    return villages, undefined, digest, codes, rings, owner


def _pass1(fname):
    _, _, _, _, rings, _ = _regency_topology(fname)
    return Topology(rings).outline_points()


def _simplified(fname):
    villages, undefined, digest, codes, rings, owner = _regency_topology(fname)
    topo = Topology(rings, _JOB["cross"], owner)
    try:
        topo.simplify(_JOB["tolerance"], _JOB["forced"], _JOB["fine"])
    except ValueError as e:
        sys.exit(f"{fname[:5]}: {e}")
    border = []  # (arc key, simplified arc digest) of every outline arc
    for arc_id in topo.outline_arcs():
        simple = topo.simple[arc_id][::-1] if topo._flip(topo.arcs[arc_id]) else topo.simple[arc_id]
        border.append((topo.key(arc_id), hashlib.sha256(repr(simple).encode()).digest()))
    return villages, undefined, digest, codes, owner, topo, border


def _pass2(fname):
    topo, border = _simplified(fname)[-2:]
    return border, {topo.key(arc_id): t for arc_id, t in topo.refined.items()}, topo.fine


def _pass3(fname):
    kab, names, tolerance, out_dir = fname[:5], _JOB["names"], _JOB["tolerance"], _JOB["out_dir"]
    if kab not in names:
        sys.exit(f"{kab} is not a regency of the wilayah set")
    villages, undefined, digest, codes, owner, topo, border = _simplified(fname)
    unknown = [c for c in codes if c not in names]
    if unknown:
        sys.exit(f"{kab}: codes not in the wilayah set: {unknown[:5]}")
    expected = sorted(c for c in names if len(c) == 13 and c.startswith(kab + "."))
    missing = [c for c in expected if c not in villages]
    rings_of = defaultdict(list)
    for i, code in enumerate(owner):
        rings_of[code].append(i)

    worst, status_counts, desa_features, area_full = (0.0, None), Counter(), [], {}
    for code in codes:
        full = assemble([topo.ring(topo.refs[i], False) for i in rings_of[code]])
        simple_rings = [topo.ring(topo.refs[i]) for i in rings_of[code]]
        if any(topo.bad_ring(i) for i in rings_of[code]):
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
        status_counts.update(status)
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
            if len(r) < 4 or self_crossing(r):
                sys.exit(f"{kec}: district ring is degenerate or crosses itself ({len(r)} points, from "
                         f"{r[0]}; crossing segments {sorted(crossing_segments(r))[:6]})")
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
    more_decimals = sorted({owner[i] for i, refs in enumerate(topo.refs)
                            if any(topo.refined.get(a, 1) < 0 or {topo.arcs[a][0], topo.arcs[a][-1]} & topo.fine
                                   for a, _ in refs)})
    entry = {"code": kab, "name": names[kab], "villages": len(desa_features), "districts": len(kec_features),
             "villages_without_polygon": missing, "districts_without_polygon": missing_kec,
             "undefined_areas": undefined, "arcs": len(topo.arcs), "content_sha256": digest}
    if more_decimals:
        entry["villages_with_more_decimals"] = more_decimals
    print(f"{kab} {names[kab]}: {len(desa_features)} villages, {len(kec_features)} districts, "
          f"{len(missing)} villages without polygon, {undefined} undefined areas, {len(topo.arcs)} arcs", flush=True)
    return entry, border, worst, status_counts, len(topo.refined), \
        sum(1 for t in topo.refined.values() if t < 0), topo.fine


def build(raw_dir, wilayah_path, out_dir, tolerance, server_copy=None, matches=None, workers=None):
    names = dict(json.load(gzip.open(wilayah_path, "rt", encoding="utf-8")))
    files = sorted(f for f in os.listdir(raw_dir) if re.match(r"^\d{2}\.\d{2}\.json\.gz$", f))
    if not files:
        sys.exit(f"no <regency>.json.gz in {raw_dir}")
    for sub in ("desa", "kecamatan"):
        os.makedirs(os.path.join(out_dir, sub), exist_ok=True)
    workers = workers or os.cpu_count() or 1
    _JOB.clear()
    _JOB.update(raw_dir=raw_dir, names=names, tolerance=tolerance, out_dir=out_dir, cross=set(), forced={}, fine=set())
    # pass 1: points where neighbouring regencies must cut their border arcs the same way
    cross, seen = set(), {}
    for pairs, inner in _run(_pass1, files, workers):
        cross |= inner
        for p, pair in pairs.items():
            if p in seen and seen[p] != pair:
                cross.add(p)
            seen.setdefault(p, pair)
    seen = None
    _JOB["cross"] = cross
    # pass 2: border arcs that one regency had to keep finer (smaller tolerance, or more decimals) are kept as
    # fine in its neighbour too; every round starts from the arcs refined so far (inner arcs too, so a ring that
    # needed them finer does not refine its border arcs again), and an arc only gets finer, so the rounds end
    # when both sides of every shared border arc are identical
    for round_no in range(1, 21):
        border, wanted, mismatches, fine = {}, {}, 0, set(_JOB["fine"])
        for arcs, refined, fine_points in _run(_pass2, files, workers):
            fine |= fine_points
            for k, t in refined.items():
                wanted[k] = min(wanted.get(k, tolerance), t)
            for k, v in arcs:
                if k in border and border[k] != v:
                    mismatches += 1
                border.setdefault(k, v)
        forced = _JOB["forced"]
        new = {k: min(t, forced.get(k, t)) for k, t in wanted.items()}
        print(f"border round {round_no}: {mismatches} shared border arcs differ, {len(new)} kept finer, "
              f"{len(fine)} junctions with more decimals", flush=True)
        if not mismatches and new == forced and fine == _JOB["fine"]:
            break
        _JOB["forced"], _JOB["fine"] = new, fine
    else:
        sys.exit("shared border arcs still differ after 20 rounds")
    # pass 3: build each regency; shared border arcs must come out identical on both sides
    summary = {"regencies": [], "villages": 0, "districts": 0, "villages_without_polygon": [],
               "undefined_areas": 0, "status": Counter()}
    worst, border_arcs, shared_border_arcs, refined_arcs, decimal_arcs = (0.0, None), {}, 0, 0, 0
    fine_points = set()
    for entry, arcs, regency_worst, status, refined, more, fine in _run(_pass3, files, workers):
        fine_points |= fine
        kab = entry["code"]
        for key, value in arcs:
            if key in border_arcs:
                shared_border_arcs += 1
                if border_arcs[key] != value:
                    sys.exit(f"{kab}: a border arc shared with another regency was simplified differently")
            border_arcs[key] = value
        if matches is not None:
            entry["matches_fondasi"] = matches.get(kab, False)
        if regency_worst[0] > worst[0]:
            worst = regency_worst
        refined_arcs += refined
        decimal_arcs += more
        summary["regencies"].append(entry)
        summary["villages"] += entry["villages"]
        summary["districts"] += entry["districts"]
        summary["villages_without_polygon"] += entry["villages_without_polygon"]
        summary["undefined_areas"] += entry["undefined_areas"]
        summary["status"].update(status)
    summary["status"] = dict(sorted(summary["status"].items()))
    built = {r["code"] for r in summary["regencies"]}
    complete = sorted(p for p in {c[:2] for c in built}
                      if all(c in built for c in names if len(c) == 5 and c.startswith(p + ".")))
    summary["largest_area_change"] = {"code": worst[1], "percent": round(worst[0] * 100, 3)}
    summary["shared_regency_border_arcs"] = shared_border_arcs
    summary["arcs_with_smaller_tolerance"] = refined_arcs
    summary["arcs_with_more_decimals"] = decimal_arcs
    summary["junctions_with_more_decimals"] = len(fine_points)
    manifest = {
        "version": VERSION,
        "description": "Boundaries of villages (desa/kelurahan) and districts (kecamatan), one GeoJSON file per "
                       "regency and level, " + (f"simplified to about {tolerance:g} m with shared borders kept "
                       "together, also across regencies" if tolerance > 0 else "at full precision (coordinates "
                       "rounded to 6 decimals, about 0.1 m)") + "; keyed by the Kemendagri codes of the wilayah set. "
                       "Arcs where rounding would make a ring cross itself keep up to "
                       f"{MAX_DECIMALS} decimals (villages_with_more_decimals per regency).",
        "status": server_copy or ("partial: " + "".join(f"every regency of {names[p]} ({p}); " for p in complete) +
                                  "regencies listed in `regencies`; others are added on demand (F-035)"),
        "source": f"Badan Informasi Geospasial, Basis Data Batas Wilayah Administrasi {EDITION} (metadata date "
                  f"{VERSION}), layer BATAS_DESAKEL_AR of {SERVICE.rsplit('/MapServer', 1)[0]}; " +
                  ("fetched by this server into raw/" if server_copy else
                   "full-precision downloads kept outside the repository, their content_sha256 per regency "
                   "here and in sources/batas-wilayah/SOURCE.txt (Kudus kept there as a sample); servers fetch "
                   "full precision themselves with the presisi command (F-035)"),
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
        "shared_regency_border_arcs": shared_border_arcs,
        "arcs_with_smaller_tolerance": refined_arcs,
        "arcs_with_more_decimals": decimal_arcs,
        "junctions_with_more_decimals": len(fine_points),
        "notes": [
            "Only 'Batas Definitif' rests on a signed regulation. 'Hasil Kesepakatan' is agreed by the villages and "
            "checked by BIG; 'Batas Indikatif' is a working line. UU 4/2011 Pasal 16 ayat (2): show boundaries that "
            "are not definitive with a different line style or colour, and never present any of them as a legal "
            "boundary.",
            "Use for maps, filters and 'which village is this point in' hints; let users correct the village they "
            "chose. Credit: Sumber: Badan Informasi Geospasial.",
            "District areas equal BIG's own district layer (BATAS_KECAMATAN_AR) to four decimals, except in "
            "districts with undefined areas (TIPADM 999: islands or water without a village, `undefined_areas` per "
            "regency), which BIG's district polygon includes and no village does.",
            "Borders between regencies are cut at the same points and simplified the same way on both sides "
            "(`shared_regency_border_arcs`); arcs that would make a ring collapse or cross itself or another ring "
            "are kept finer (`arcs_with_smaller_tolerance`), so no two villages overlap. "
            "`largest_area_change_percent` compares the simplified with the full-precision area; small villages "
            "change most.",
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
        build(args[1], args[2], args[3], float(opts.get("tolerance", 11)), workers=int(opts.get("workers", 0)))
    elif len(args) >= 3 and args[0] == "presisi":
        presisi(args[1], args[2:], "--accept-new" in sys.argv[1:])
    else:
        sys.exit(__doc__)
