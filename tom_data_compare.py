#!/usr/bin/env python3
'''
Need to DO:
Find a way to use what I learned from common and use it to merge rows and sci respectfully and do it
automatically

Tuesday 3.5
Th 1hr + 2:30-6:05
'''

import re
import numpy
import collections
from heatmaps.scigraph_client import Graph, Vocabulary
import json
import csv
from collected import data #imports data from a previous py file
from collections import defaultdict, namedtuple
from IPython import embed

g = Graph()

with open('species_data.csv', 'rt') as f:
    species_rows = [r for r in csv.reader(f)]
    species_labels = species_rows[0]
    species_labels[0] = 'Categories'
    species_rows = species_rows[1:]
with open('cell_layer_data.csv', 'rt') as f:
    layer_rows = [r for r in csv.reader(f)]
    layer_labels = layer_rows[0]
    layer_labels[0] = 'Categories'
    layer_rows = layer_rows[1:]
with open('brain_region_data.csv', 'rt') as f:
    brain_rows = [r for r in csv.reader(f)]
    brain_labels = brain_rows[0]
    brain_labels[0] = 'Categories'
    brain_rows = brain_rows[1:]
with open('neuron_data_curated.csv', 'rt') as f:
    cell_rows = [r for r in csv.reader(f)]
    cell_labels = cell_rows[0]
    cell_labels[0] = 'Categories'
    cell_rows = cell_rows[1:]

badcats = {
 ':Category:':'owl:Thing',
 ':Category:Cell layer':'nlx_149357',
 ':Category:Defined neuron class':'nlx_55759',
 ':Category:Glial-like cell':':Category:Glial-like cell',  # UWOTM8
 ':Category:Hemisphere parts of cerebral cortex':'birnlex_1796',
 ':Category:Lobe parts of cerebral cortex':'birnlex_922',
 ':Category:Magnocellular neurosecretory cell':'nlx_cell_20090501',
 ':Category:Neuron':'sao1417703748',
 ':Category:Organism':'birnlex_2',
 ':Category:Regional part of brain':'birnlex_1167',
 ':Category:Retina ganglion cell B':'BAMSC1010',
 ':Category:Retina ganglion cell C':'BAMSC1011',
 ':Category:Sulcus':'nlx_144078',
 ':Category:Superior colliculus stellate neuron':'BAMSC1129',
 ':Category:Superior colliculus wide field vertical cell':'BAMSC1125',
 ':Category:spinal cord ventral horn interneuron V2':'nlx_cell_100207',
}

print(cell_labels)
cli = {l:i for i, l in enumerate(cell_labels)}
bli = {l:i for i, l in enumerate(brain_labels)}
lli = {l:i for i, l in enumerate(layer_labels)}
sli = {l:i for i, l in enumerate(species_labels)}

cell_cats = {a[cli['Categories']]:a[cli['Id']] for a in cell_rows}
brain_cats = {a[bli['Categories']]:a[bli['Id']] for a in brain_rows}
layer_cats = {a[lli['Categories']]:a[lli['Id']] for a in layer_rows}
species_cats = {a[sli['Categories']]:a[sli['Id']] for a in species_rows}
all_cats = {}
all_cats.update(badcats)
all_cats.update(cell_cats)
all_cats.update(brain_cats)
all_cats.update(layer_cats)
all_cats.update(species_cats)

def multi_split(field):
    if ',' in field:
        return [all_cats[v.strip()] for v in field.split()]
    else:
        return all_cats[field]

missing = set()
def c_trans(row):
    try:
        row[cli['SuperCategory']] = all_cats[':Category:' + row[cli['SuperCategory']]]

        row[cli['Species/taxa']] = multi_split(row[cli['Species/taxa']])
        row[cli['Located in']] = multi_split(row[cli['Located in']])
        row[cli['LocationOfAxonArborization']] = multi_split(row[cli['LocationOfAxonArborization']])
        row[cli['DendriteLocation']] = multi_split(row[cli['DendriteLocation']])
        row[cli['LocationOfLocalAxonArborization']] = multi_split(row[cli['LocationOfLocalAxonArborization']])

    except KeyError as e:
        missing.add(e.args[0])
        #print(e)
    return row

def b_trans(row):
    try:
        row[bli['SuperCategory']] = all_cats[':Category:' + row[bli['SuperCategory']]]
    except KeyError as e:
        missing.add(e.args[0])
        #print(e)
    return row

def l_trans(row):
    try:
        row[lli['SuperCategory']] = all_cats[':Category:' + row[lli['SuperCategory']]]
    except KeyError as e:
        missing.add(e.args[0])
        #print(e)
    return row

def s_trans(row):
    try:
        row[sli['SuperCategory']] = all_cats[':Category:' + row[lli['SuperCategory']]]
    except KeyError as e:
        missing.add(e.args[0])
        #print(e)
    return row

cell_rows_dict = {a[cli['Id']]:c_trans(a) for a in cell_rows}
brain_rows_dict = {a[bli['Id']]:b_trans(a) for a in brain_rows}
layer_rows_dict = {a[lli['Id']]:l_trans(a) for a in layer_rows}
species_rows_dict = {a[sli['Id']]:s_trans(a) for a in species_rows}
print(missing)
#print(cell_rows_dict.keys())

def add_elements(record, rows, labels, id_):
    if id_ in rows:
        for label, element in zip(labels, rows[id_]):
            if element:
                record.append((label, element))

output = {}
scigraph = set()
for prefix, outer_identifiers in data.items():
    for outer_identifier in outer_identifiers:
        record = []
        # right now DNE duplicate rows
        record.append(('curie', prefix + ':' + outer_identifier))
        if outer_identifier in cell_rows_dict:
            add_elements(record, cell_rows_dict, cell_labels, outer_identifier)
        elif outer_identifier in brain_rows_dict:
            add_elements(record, brain_rows_dict, brain_labels, outer_identifier)
        elif outer_identifier in layer_rows_dict:
            add_elements(record, layer_rows_dict, layer_labels, outer_identifier)
        else:
            raise TypeError('WHAT ????????????????')
            #missing.append(outer_identifier)
            #record.extend(['' for a in new_labels])

        if prefix != 'nlx_only':
            node = g.getNode(record[0][1])  # FIXME [0][1] always the curie
            op = [e for e in g.getNeighbors(record[0][1], depth=1)['edges'] if e['sub'] == record[0][1]]
            print(op)
            metadict = node['nodes'][0]['meta']
            for key, value in metadict.items():
                record.append((key, value))
                scigraph.add(key)
            for edge in op:
                key = edge['pred']
                value = edge['obj']
                record.append((key, value))

        output[outer_identifier] = record

                #for key, value in node['nodes'][0]['meta'].items():#pulls items info out of web

#FIXME IMPORTANT
#adds a list of the order of which all the info is in under the key 'LABEL'
#finished_dict['LABELS'].append(csv_sci)
output['LABELS'] = sorted(set(cell_labels + brain_labels + layer_labels + list(scigraph)))


#FIXME
# Nice reference to long data compiling.
#print(finished_dict)
#print(com_list)
print('stopped')

#json will make this readable to others
with open('Neurolex_Scigraph.json', 'wt') as f:
    json.dump(output, f)

#embed()
