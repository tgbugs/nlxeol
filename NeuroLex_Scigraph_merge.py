import re
import numpy
import collections
from heatmaps.scigraph_client import Graph, Vocabulary
import json
import csv
from collected import data #imports data from a previous py file
from collections import defaultdict, namedtuple
import os
import rdflib
from datetime import date
from IPython import embed
from sqlalchemy import create_engine, inspect
from rdflib import Namespace,URIRef

g = Graph()
v = Vocabulary

with open('species_data.csv', 'rt') as f: #opens file as reading text
    species_rows = [r for r in csv.reader(f)] #prime rows
    Identifiers = species_rows[0]#identifiers
    Identifiers[0] = 'Categories'#needed new identity
    rows = species_rows[1:]#meat of the file
with open('brain_region_data.csv', 'rt') as f:
    brain_rows = [r for r in csv.reader(f)]
    rows += brain_rows[1:]
with open('neuron_data_curated.csv', 'rt') as f:
    neuron_rows = [r for r in csv.reader(f)]
    rows += neuron_rows[1:]
with open('cell_layer_data.csv', 'rt') as f:
    cell_rows = [r for r in csv.reader(f)]
    rows += cell_rows[1:]

#for prefixes, ids in data.items():
    #if ids in rows:

