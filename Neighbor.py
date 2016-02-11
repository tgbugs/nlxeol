import json
from collected import data
import csv
from heatmaps.scigraph_client import Graph, Vocabulary
import re
from collections import defaultdict, namedtuple
from IPython import embed

g = Graph()

with open('Neurolex_Scigraph.json') as data_file:
    js = json.load(data_file)


with open('species_data.csv', 'rt') as f:
    species_rows = [r for r in csv.reader(f)]
    species_labels = species_rows[0]
    species_labels[0] = 'Categories'
    species_rows = species_rows[1:]
with open('brain_region_data.csv', 'rt') as f:
    brain_rows = [r for r in csv.reader(f)]
    brain_labels = brain_rows[0]
    brain_labels[0] = 'Categories'
    brain_rows = brain_rows[1:]
with open('neuron_data_curated.csv', 'rt') as f:
    neuron_rows = [r for r in csv.reader(f)]
    neuron_labels = neuron_rows[0]
    neuron_labels[0] = 'Categories'
    neuron_rows = neuron_rows[1:]
with open('cell_layer_data.csv', 'rt') as f:
    cell_rows = [r for r in csv.reader(f)]
    cell_labels = cell_rows[0]
    cell_labels[0] = 'Categories'
    cell_rows = cell_rows[1:]


keys = tuple(js.keys())
#prefix = tuple(data)
record=[]

for prefix, outer_identifiers in data.items():
    if 'nlx_only' == prefix:
        continue

    for id_ in outer_identifiers:
        pre = prefix + ':' + id_

        for prefixIndex, prefixValue in enumerate(js['LABELS']):
            if prefixValue == 'PREFIX':
                PrefixWithID = js[id_][0][prefixIndex]
                #FIXME why is there more than 1 neighbor?
                neighbor = [e for e in g.getNeighbors(PrefixWithID, depth=1,direction='INCOMING')['edges'] if e['sub']==PrefixWithID]
                print(neighbor)
                for edge in neighbor:
                    key = edge['pred']
                    value = edge['obj']
                    sub= edge['sub']
                    record.append((key, value, sub))

print(record)
