# Transcription of Kepka BKPDM 020/2026 (checked)

Kepka BKPDM 020/2026 is a scan without a text layer. These files are a transcription made for the data set
`capaian-pembelajaran` (F-032): tesseract (`ind`, 300 dpi) gave a draft, and every line was then read and corrected
against the page images (diacritics and other characters checked on zoomed crops). Raw OCR text is not kept here.
The SD phases A–C of Lampiran I are also compared with sinaubareng's independent word-by-word transcription
(`tools/converters/capaian-pembelajaran-agama.py` reports every difference).

One file per section (`1.1-islam.txt` … `2.6-khonghucu.txt`). Format:

- `# <number> <heading as printed>` starts the section; `## A. Rasional`, `## B. Tujuan`, `## C. Karakteristik`,
  `## D. Capaian Pembelajaran`; `### <n>. Fase X (…)` a phase; `#### <n.m>. <element>` an element heading in the CP.
- `[p. N]` on its own line: PDF page N starts here (the page number printed on the page is the same).
- One paragraph or list item per line. Words broken at a line end are joined; a hyphen that belongs to the word
  (Al-Qur’an, sungguh-sungguh) is kept.
- `+ ` at the start of a line: the paragraph continues from before the page break.
- Tables: one row per line, `| cell | cell |`, the header row first; a row continued on the next page starts with
  `|+ `. A header row repeated at the top of a page is left out. An empty first cell repeats the cell above
  (merged cells). `<br>` is a line break inside a cell.
- Text as printed, including capitals, punctuation and printing errors (those are listed in the data set's errata).
  Italics are not kept. Apostrophes and ‘ain as printed in the typeface: ’ and ‘. Pinyin as printed: the scan marks
  the third tone with a breve (Kŏngzĭ, Wŭjīng); a missing space before Chinese characters is kept (bādé八德).
