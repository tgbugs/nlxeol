import re
import numpy
from heatmaps.scigraph_client import Graph, Vocabulary
import json
import csv
from IPython import embed
from collected import data #imports data from a previous py file

'''update collected!
'''

my_names={}
meta_names={}

with open('cell_layer_data.csv', 'rt') as f:
    info=[r[1:15] for r in csv.reader(f)]
#print(info)

g=Graph()
print(g)
d=['NIFCELL'+':'+v for v in data['NIFCELL']]
print(d)

node=g.getNode('NIFCELL:nlx_cell_20090313')
print(node)
