#!/usr/bin/env python3

import csv
from heatmaps.scigraph_client import Graph, Vocabulary

a=0
v=Vocabulary()
g=Graph()
NIF_Directory={}

with open('cell_layer_data.csv', 'rt') as cell_open:
    cell_IDs= [r[3] for r in csv.reader(cell_open)][1:]
with open('brain_region_data.csv') as brain_open:
    cell_IDs+= [r[3] for r in csv.reader(brain_open)][1:]
print(cell_IDs)

n=len(cell_IDs)
print('We have',n,'IDs')
print('')
Curie_Prefixes= v.getCuriePrefixes()[1:65]
print(Curie_Prefixes)



count=0
need=0
for i in Curie_Prefixes:
    for j in cell_IDs:
        have=(i+':'+j)
        have=v.findById(have)
        if have!=None:
            NIF_Directory[j]=i
            count=count+1
            print(count)


for u in cell_IDs:
    if u not in NIF_Directory:
        NIF_Directory[u]=''
        print(u)
        need=need+1


print('We need', need, 'IDs')
print('We have', count, 'In NIF')
print(NIF_Directory)
print('done!')