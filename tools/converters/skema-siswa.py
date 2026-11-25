"""Convert data/skema-siswa/skema-siswa.txt (field schema + option lists, written by Arumi Studios) into
skema-siswa.json. Usage: python3 -I tools/converters/skema-siswa.py data/skema-siswa/skema-siswa.txt data/skema-siswa/skema-siswa.json
The text file is the source of truth; edit it, run this, bump the manifest version, run tools/data-check --write."""
import json
import re
import sys

src, dst = sys.argv[1], sys.argv[2]
lines = open(src, encoding='utf-8').read().splitlines()
groups, options, notes = [], {}, []
group = field = sec = cur = None


def attrs_of(text):
    out = {}
    for a in [x.strip() for x in text.split(';') if x.strip()]:
        if a.startswith(('hide_if', 'required_if')):
            k = a.split('(', 1)[0]
            out[k] = a[len(k) + 1:-1]
        elif '=' in a:
            k, v = a.split('=', 1)
            out[k] = v.strip('"')
        else:
            out[a] = True
    return out


for ln in lines:
    m = re.match(r'^=== GROUP: (\w+) - (.+?) \(\d+ fields\) ===$', ln)
    if m:
        group = {'key': m[1], 'label': m[2], 'fields': []}
        groups.append(group)
        sec = 'g'
        continue
    if ln.startswith('=== NOTES'):
        sec = 'n'
        continue
    if ln.startswith('=== OPTION LISTS'):
        sec = 'o'
        continue
    if sec == 'g':
        m = re.match(r'^(\d\d)\. (\w+) \| (.+?) \| (\w+) \|\s*(.*)$', ln)
        if m:
            field = {'no': int(m[1]), 'key': m[2], 'label': m[3], 'type': m[4], **attrs_of(m[5])}
            group['fields'].append(field)
            continue
        m = re.match(r'^\s+hint: (.+)$', ln)
        if m and field:
            field['hint'] = m[1]
            continue
        m = re.match(r'^\s+sub-column: (\w+) \| (.+?) \| (\w+) \|\s*(.*)$', ln)
        if m and field:
            field.setdefault('columns', []).append({'key': m[1], 'label': m[2], 'type': m[3], **attrs_of(m[4])})
            continue
    if sec == 'n' and ln.startswith('- '):
        notes.append(ln[2:])
        continue
    if sec == 'n' and ln.startswith('  ') and notes:
        notes[-1] += ' ' + ln.strip()
        continue
    if sec == 'o':
        m = re.match(r'^\[(\w+)\] \((\d+) options; used by: (.+?)\)(.*)$', ln)
        if m:
            cur = m[1]
            options[cur] = {'used_by': [x.strip() for x in m[3].split(',')], 'editable': 'editable' in m[4], 'values': []}
            continue
        m = re.match(r'^\s+\d+\. (.+)$', ln)
        if m and cur:
            options[cur]['values'].append(m[1])

for g in groups:
    for f in g['fields']:
        for item in [f, *f.get('columns', [])]:
            if 'options' in item and item['options'] not in options:
                sys.exit(f"unknown option list {item['options']} in {f['key']}")

out = {'name': 'Data siswa SMP (schema and option lists)', 'groups': groups, 'options': options, 'notes': notes}
with open(dst, 'w', encoding='utf-8') as fh:
    json.dump(out, fh, ensure_ascii=False, indent=1)
    fh.write('\n')
print(sum(len(g['fields']) for g in groups), 'fields,', len(options), 'option lists')
