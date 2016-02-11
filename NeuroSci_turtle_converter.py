import json
import csv
import json
from IPython import embed
from collections import *
from heatmaps.scigraph_client import Graph, Vocabulary
from collected import data
from rdflib import *
import rdflib
from rdflib.namespace import RDF
g = Graph()
v = Vocabulary()
v.getCuriePrefixes()
'''
.namespace to map long names
.graph to make tuples
'''
ns=Namespace
person = ns("http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#Bill_Bug") + ns("http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#Bill_Bug")
#print(person)
rawInput = ns("http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#raw_import")
nueroNames = ns("http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#NeuroNames_abbrevSource")

values = [] #clumped total info of each element as a list of lists
pref = defaultdict(list)
temp = defaultdict(list)



#FIXME supercategory is element num 7
with open('Neurolex_Scigraph.json') as data_file:
    js = json.load(data_file)

keys = tuple(js)
prefix = tuple(data)

#FIXME: probably will be list for Namespace
#person1 = Namespace("http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#Bill_Bug")


#length of labels is 0-84 or 85 elements
for i  in range(0,len(keys)):
    for j in range(0,len(js['LABELS'][0])):
        mid = ns(js['LABELS'][0][j])
        #print(mid)
        right = ns(js[keys[i]][0][j])
        for pre in prefix:
            for IDs in data[pre]:
                if IDs in js[keys[i]][0][3]:
                    if 'nlx_only' in pre:
                        continue
                    if right != '':
                        print('yep')
                        #g.add_node((pre, mid, right))
                        continue






embed()
#person.ruleBase
#print(person)

#print('person', person)
#print('rawInput', rawInput)

#print('rawInput', rawInput)



#print(data['LABELS'][0][6]) #sanity check
'''

if '#raw_import' in #list:
    test = Namespace("#list")

print(test)'''