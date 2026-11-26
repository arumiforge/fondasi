# Third-party notices

Fondasi is proprietary (`LICENSE`). Data sets and tools below come from or are derived from third parties.

| Item | Source | Licence / terms |
| --- | --- | --- |
| `data/wilayah/` | [cahyadsn/wilayah](https://github.com/cahyadsn/wilayah) `db/wilayah.sql`, codes and names per Kepmendagri No 300.2.2-2138 Tahun 2025; converted by `tools/converters/wilayah.mjs` | MIT, Copyright (c) 2025 cahya dsn (text below) |
| `data/sekolah/` | Public district lists of referensi.data.kemendikdasmen.go.id (Kemendikdasmen Dapodik reference data), crawled and converted by `tools/converters/sekolah.py` | Public government data, no personal data |
| `data/kaldik-jateng/`, `sources/kaldik-jateng/` | Peraturan Kepala Dinas Pendidikan Provinsi Jawa Tengah on the education calendar 2025/2026 and 2026/2027, pdk.jatengprov.go.id | Public government documents |
| `data/libur-nasional/`, `sources/libur-nasional/` | SKB 3 Menteri on national holidays and cuti bersama 2026 and 2027, published by Kemenko PMK (www.kemenkopmk.go.id) | Public government documents |
| `data/kaldik-madrasah-jateng/`, `sources/kaldik-madrasah-jateng/` | Keputusan Kepala Kantor Wilayah Kementerian Agama Provinsi Jawa Tengah Nomor 1681 Tahun 2026 (copy received from the user) | Public government document |
| `sources/atletik/o2sn/` | Panduan O2SN 2026 SD, SMP, SMA (copies received from the user; not converted yet) | Public government documents |
| `sources/wilayah/` | Keputusan Menteri Dalam Negeri Nomor 300.2.2-2430 Tahun 2025 (copy received from the user), used to check `data/wilayah` | Public government document |
| `data/kodepos/` | [cahyadsn/wilayah_kodepos](https://github.com/cahyadsn/wilayah_kodepos) `db/wilayah_kodepos.sql`; converted by `tools/converters/kodepos.py` | MIT, Copyright (c) 2024 Cahya DSN (`data/kodepos/LICENSE.txt`) |
| `data/atletik-*/`, `sources/atletik/` | World Athletics Book C C1.1/C2.1 Competition & Technical Rules (2026), IAAF Scoring Tables for Combined Events (2016), worldathletics.org | Copyright World Athletics; facts with references and private raw copies by decision F-027 |
| `server/setup.sh` installs | Docker (Docker Inc. apt repository), cloudflared (Cloudflare apt repository), Cockpit (Ubuntu) | Installed on the server from their vendors; not redistributed here |

### cahyadsn/wilayah (MIT)

```
Copyright (c) 2025 by cahya dsn; cahyadsn@gmail.com

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

