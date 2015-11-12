#!/usr/bin/env python3

import csv
import re
from heatmaps.scigraph_client import Graph, Vocabulary
from collections import namedtuple
from IPython import embed
import numpy

a=0
v=Vocabulary()
g=Graph()
NIF_Directory={}

with open('cell_layer_data.csv', 'rt') as cell_open:
    cell_IDs= [r[3] for r in csv.reader(cell_open)][1:]
print(cell_IDs)

n=len(cell_IDs)
print('We have',n,'IDs')
print('')
Curie_Prefixes= v.getCuriePrefixes()[1:65]

#NIF_Directory{}=
#Curie_Prefixes=Curie_Prefixes.sort()
#print (Curie_Prefixes)

k=0
count=0
need=0
for i in Curie_Prefixes:
    for j in cell_IDs:
        have=(i+':'+j)
        have=v.findById(have)
        if have!=None:
            NIF_Directory[j]=i
            count=count+1

needed=()
for u in cell_IDs:
    if u not in NIF_Directory:
        NIF_Directory[u]=''
        print(u)
        need=need+1




print('We need', need, 'IDs')
print('We have', count, 'In NIF')
print(NIF_Directory)