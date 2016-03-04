#!/usr/bin/env python3

import csv
from heatmaps.scigraph_client import Graph, Vocabulary
from collections import defaultdict




NIF_Directory = defaultdict(list)
a=0
v=Vocabulary()
g=Graph()
count=0
need=0


with open('cell_layer_data.csv', 'rt') as cell_open:
    cell_IDs= [r[3] for r in csv.reader(cell_open)][1:]
with open('brain_region_data.csv', 'rt') as brain_open:
    cell_IDs+= [r[3] for r in csv.reader(brain_open)][1:]
with open('neuron_data_curated.csv', 'rt') as neuron_open:
    cell_IDs+= [r[3] for r in csv.reader(neuron_open)][1:]
with open('lost_cat.csv', 'rt') as f:
    cell_IDs += [r[3] for r in csv.reader(f)][1:]

n=len(cell_IDs)

Curie_Prefixes= v.getCuriePrefixes()[1:]
Curie_Prefixes.append('nlx_only')
print(Curie_Prefixes)

for IDs in cell_IDs:
    for Prefixes in Curie_Prefixes:
        have=(Prefixes+':'+IDs)
        have=v.findById(have)
        if have!=None:
            #print(IDs)
            NIF_Directory[Prefixes].append(IDs)
            count=count+1
            #print(count)
            break
    if have==None:
        NIF_Directory['nlx_only'].append(IDs)
        need=need+1


print('We need', need, 'IDs')
print('We have', count, 'In NIF')
print(NIF_Directory)
print('done!')