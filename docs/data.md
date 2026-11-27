# Shared data: how it works (F-003)

## Layout of a set

```
data/<set>/
  manifest.json     version (YYYY-MM-DD, the source's date), description, status, source, licence, counts, fields
  SHA256SUMS        checksum of every other file (tools/data-check --write)
  <files>           gzipped JSON (large lists, one file per province where useful) or plain JSON (small lists)
```

- Field names are short and stable; labels keep the official Indonesian spelling. Codes are the official ones
  (Kemendagri region codes, NPSN, Dapodik reference IDs) — never invented. Where an official code is not yet
  verified, the set stays `planned`.
- A converter in `tools/converters/` (or a written procedure in the manifest when the source is a PDF or a
  page) rebuilds the set from the source. Sources are untrusted: parse with strict patterns, never execute.
- `tools/data-check` (CI) verifies every manifest and checksum.

## Changing a set

1. Put the raw source outside the repository (or in `sources/<set>/` when it is small and its licence allows).
2. Run the converter; check counts against the source; bump `version`.
3. `tools/data-check --write`, then `tools/data-check`.
4. `CHANGELOG.md` line; commit `feat(data): <set> <version>`; PR.

## Using a set in an app (any stack)

```bash
FONDASI_DIR=/path/to/fondasi /path/to/fondasi/tools/fondasi-sync wilayah     # copies data/wilayah at Fondasi's HEAD
/path/to/fondasi/tools/fondasi-sync sekolah 3f2c1a9                          # or at a given commit/tag
/path/to/fondasi/tools/fondasi-sync --check                                  # CI in the app: copies untouched
```

The app gets `data/fondasi/<set>/` and a line in `fondasi.lock` (`<set> <version> <commit>`), commits both and
imports the files with its own importer, keyed on the manifest version (re-import only when it changes; SPMB's
`referensi:import --bawaan` is the model). In a Claude cloud session, attach Fondasi first
(`add_repo arumiforge/fondasi`, cloned at `/home/user/fondasi`); `fondasi-sync` finds it there.

## Full-precision boundaries on a server (`batas-wilayah`, F-035)

`data/batas-wilayah` carries boundaries simplified to about 11 m, which is enough for maps and filters. Full
precision (about 0.1 m; ≈ 0.5 MB per regency, ≈ 370 MB gzipped for Indonesia) is not stored in Fondasi or anywhere
else: the server fetches it from BIG itself, and Fondasi only pins which content is expected.

```bash
git -C /opt/apps/_fondasi pull
python3 -I /opt/apps/_fondasi/tools/converters/batas-wilayah.py presisi /opt/apps/<app>/<env>/data/batas-wilayah 33.19
```

- It fetches each regency from `geoservices.big.go.id` (the server must reach it; seconds per regency), compares
  the content with `content_sha256` in Fondasi's `data/batas-wilayah/manifest.json`, then writes
  `desa/<regency>.geojson.gz`, `kecamatan/<regency>.geojson.gz`, the raw download in `raw/`, `manifest.json`
  (every regency with `matches_fondasi`) and `SHA256SUMS`. Same fields as the simplified set.
- It refuses a regency Fondasi does not list yet, or one BIG has changed since Fondasi was built: add or refresh
  that regency in Fondasi first (`fetch` + `build`, PR), pull, and run again. `--accept-new` overrides this for an
  urgent case; the manifest then shows `matches_fondasi: false` and Fondasi must be updated afterwards.
- Needs only `python3` (present on Ubuntu servers). Mount the folder read-only into the app container, or import it
  with the app's importer keyed on `manifest.json` → `regencies[].content_sha256`. The folder can be rebuilt at
  any time, so it needs no backup.

## Using boundaries in apps (`batas-wilayah`, F-035)

Copy the set with `fondasi-sync batas-wilayah` and load only the regencies the app serves. Before relying on a
build (Fondasi's or a server's `presisi` copy), check it:

```bash
python3 -I tools/checks/batas-wilayah.py data/batas-wilayah --big --render /tmp/peta
```

It checks that every village and district of `data/wilayah` in each listed regency has a polygon, that each
district is exactly the union of its villages (same edges, same area: no gaps or overlaps), that there are no holes
beyond BIG's undefined areas, that neighbouring regencies in the folder share their border point for point, and with
`--big` that every district's `area_km2` equals BIG's district layer (`BATAS_KECAMATAN_AR`, `LUASWH`) to 4 decimals.
`--render` writes one SVG per regency and one for the province for a visual check (thin village lines, thick
district lines, dashed where a village has `Batas Indikatif`, fills tinted by status; a review picture, not the
style apps use, which is below). It exits with 1 when a check
fails, runs one worker per CPU, and needs only `python3`.

### ±11 m or full precision

The simplified set (about 11 m) is enough for anything a person looks at or chooses from:

- maps of a regency, district or village, choropleths and counts per area;
- region pickers and filters ("sekolah di Kecamatan Jati");
- the "which village is this point in" hint below;
- areas: `area_km2` is always computed from the full-precision polygon, so it is exact in both sets.

Use full precision (`presisi`, see the section above; about 0.15–1.7 MB per regency and level gzipped, measured on
Kudus, Pati and Jepara) only when a decision depends on the exact line:

- a point that lies within about 15 m of a simplified boundary (the answer may flip), when the app must decide
  automatically and cannot ask the user;
- clipping or overlaying with other measured data (parcels, roads, buildings) or computing areas of clipped parts;
- maps printed or zoomed beyond about 1:25,000, where the 11 m steps become visible.

Even full precision is BIG's cartographic line, not a surveyed legal boundary. Neither set settles a dispute.

### Showing the boundary status

UU 4/2011 Pasal 16 ayat (2): where a boundary has not been settled, a provisional boundary is used and drawn with a
distinct symbol or colour. Every village carries BIG's `status`:

| `status` | Line | What it means |
| --- | --- | --- |
| `Batas Definitif` | solid | set by a signed regulation (`basis` names it) |
| `Hasil Kesepakatan` | dashed | agreed by the villages and checked by BIG, not yet in a regulation |
| `Batas Indikatif` | dashed | a working line |

- Only `Batas Definitif` is drawn solid. `status` is a list when parts of one village differ: treat a list as not
  definitive. A line shared by a definitive and a non-definitive village is drawn dashed (draw the dashed layer last,
  over a thin background-coloured casing, so the solid line underneath does not show through the gaps).
- Never call any of them a legal boundary (F-035), in labels, tooltips, exports or printed maps. Show the legend
  and a short note, for example: "Garis penuh: batas yang sudah ditetapkan. Garis putus-putus: batas sementara. Batas
  di peta ini hanya gambaran, bukan batas hukum."
- Credit the source wherever the map appears (map attribution, printouts, exported images):
  **Sumber: Badan Informasi Geospasial**.

### "Which village is this point in" — a suggestion only

Apps may suggest a village from a point (a pin on the map, a phone's location, a school's coordinates):

- Test the point against the village polygons of its regency (ray casting on the outer ring minus holes); no
  server call is needed for one regency.
- Show the result as a suggestion the user confirms or changes, e.g. "Menurut peta, titik ini ada di Desa Jati
  Wetan, Kecamatan Jati. Ubah bila salah." The user's choice wins; never block a form because the point and the
  chosen village differ.
- No suggestion when the point is in no polygon (sea, lakes, undefined areas, a coast smoothed by simplification) or
  when the location is less accurate than about 100 m; ask the user to choose instead.
- Within about 15 m of a boundary, say that the point is near a boundary, or use full precision on the server.
- A home location is personal data (UU PDP, `docs/web-baseline.md`): test it in the browser where possible and store
  the chosen village code, not the coordinates, unless the app needs them.

### File sizes and loading

Simplified set, one file per regency and level (gzipped / unpacked):

| Regency | Villages | `desa/` | `kecamatan/` |
| --- | --- | --- | --- |
| 33.19 Kudus | 132 | 65 KB / 0.3 MB | 20 KB / 0.08 MB |
| 33.20 Jepara (with Karimunjawa) | 195 | 147 KB / 0.6 MB | 85 KB / 0.3 MB |
| 33.18 Pati | 406 | 199 KB / 0.9 MB | 55 KB / 0.2 MB |

About 0.5 KB per village gzipped, so roughly 4–6 MB for all of Jawa Tengah (8,563 villages; estimate). Load one
regency at a time; on phones load `kecamatan/` first and `desa/` when the user zooms in or picks a district.

Serve the files gzipped as they are, either with `Content-Encoding: gzip` so the browser unpacks them:

```nginx
location /peta/ {                       # the app requests /peta/desa/33.19.geojson
    gzip_static on;                     # serves desa/33.19.geojson.gz with Content-Encoding: gzip
    gzip off;                           # never compress twice
    types { application/geo+json geojson; }
}
```

(Caddy: `file_server { precompressed gzip }`; an app route: send the `.gz` bytes with `Content-Encoding: gzip`
and `Content-Type: application/geo+json`.) Or serve the `.gz` file as plain bytes and unpack it in the browser
(`DecompressionStream`: Chrome 80, Firefox 113, Safari 16.4). The loader below works either way: it unpacks only
when the bytes it received still start with the gzip signature (a second unpack would fail, and the
`Content-Encoding` header cannot be read on cross-origin requests).

```js
async function loadGeoJSONGz(url) {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  const bytes = new Uint8Array(await res.arrayBuffer());
  const packed = bytes[0] === 0x1f && bytes[1] === 0x8b;
  const body = packed ? new Blob([bytes]).stream().pipeThrough(new DecompressionStream('gzip')) : bytes;
  return new Response(body).json();
}
const definitive = (f) => f.properties.status === 'Batas Definitif';
const desa = await loadGeoJSONGz('/peta/desa/33.19.geojson.gz');
```

Leaflet (non-definitive lines last, over a casing):

```js
const base = { color: '#444', weight: 1, fill: false };
L.geoJSON(desa, { filter: definitive, style: base }).addTo(map);
L.geoJSON(desa, { filter: (f) => !definitive(f), style: { ...base, color: '#fff', weight: 3 } }).addTo(map);
L.geoJSON(desa, {
  filter: (f) => !definitive(f), style: { ...base, dashArray: '6 4' },
  onEachFeature: (f, layer) => layer.bindTooltip(f.properties.name),
}).addTo(map);
map.attributionControl.addAttribution('Sumber: Badan Informasi Geospasial');
```

MapLibre GL JS (`data` can also be the URL when the server sends `Content-Encoding: gzip`):

```js
map.addSource('desa', { type: 'geojson', data: desa, attribution: 'Sumber: Badan Informasi Geospasial' });
const solid = ['==', ['get', 'status'], 'Batas Definitif'];
const other = ['!', solid];
map.addLayer({ id: 'desa-definitif', type: 'line', source: 'desa', filter: solid,
  paint: { 'line-color': '#444', 'line-width': 1 } });
map.addLayer({ id: 'desa-alas', type: 'line', source: 'desa', filter: other,
  paint: { 'line-color': '#fff', 'line-width': 3 } });
map.addLayer({ id: 'desa-sementara', type: 'line', source: 'desa', filter: other,
  paint: { 'line-color': '#444', 'line-width': 1, 'line-dasharray': [4, 3] } });
```

Use the casing colour of the map background (white on a plain background; skip the casing over satellite imagery
and use a different colour for the dashed line instead).

## Getting data from sources this environment cannot reach

Some sources (EMIS, PDDikti, Disdikbud Jateng, the curriculum site) are blocked from cloud sessions. They are
fetched in a **Claude in Chrome** session on the developer's computer, following a brief in
[data-requests.md](data-requests.md): the browser session saves the raw files, the developer drops them into a
cloud session (or commits them to `sources/<set>/` on a branch), and a cloud session runs the converter.
