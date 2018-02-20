#!/usr/bin/env pypy3
import csv
from IPython import embed

with open('neurolex_full.csv', 'rt') as f:
    _rows = csv.reader(f)
    fh = next(_rows)
    frows = {r[0]:r for r in _rows if r[0] != 'Categories'}

with open('neuron_data_curated.csv', 'rt') as f:
    _rows = csv.reader(f)
    h = next(_rows)
    rows = [r for r in _rows]

cats = list(zip(*rows))[0]
add_header = []
skip = ('Category', 'Species', 'Has improper value for')
for cat in cats:
    fr = frows[cat]
    for head, value in zip(fh, fr):
        if head in skip or head in add_header or head in h or not value:
            continue
        else:
            add_header.append(head)

new_rows = [h + add_header]
for row in rows:
    nr = [_ for _ in row]
    fr = frows[row[0]]
    for add in add_header:
        nr.append(fr[fh.index(add)])
    new_rows.append(nr)

with open('neuron_data_curated.csv', 'wt') as f:
    writer = csv.writer(f)
    writer.writerows(new_rows)

embed()
