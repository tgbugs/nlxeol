#!/usr/bin/env python3

import csv
import re
from heatmaps.scigraph_client import Graph, Vocabulary
from collections import namedtuple
from IPython import embed
import numpy


v=Vocabulary()
g=Graph()


with open('cell_layer_data.csv', 'rt') as cell_open:
    cell_IDs= [r[3] for r in csv.reader(cell_open)][1:]
print(cell_IDs)
print('')
if '_' in cell_IDs:
    cell_IDs=cell_IDs.replace('_',' ')
print('')
Curie_Prefixes= v.getCuriePrefixes()[1:65]
#Curie_Prefixes=Curie_Prefixes.sort()
#print (Curie_Prefixes)

'''
for i in Curie_Prefixes:
    for j in cell_IDs:
        print(i,j)
        #if v.findById(i,j)!=None:
         #   print('hello')

embed()
'''