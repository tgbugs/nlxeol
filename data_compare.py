'''
I have a list of the needed headers.

Need to DO:
1.expand my header from the list I just made.
2.get info I got from scigraph to line up to columns

Tuesday 12-437
'''



import re
import numpy
import collections
from heatmaps.scigraph_client import Graph, Vocabulary
import json
import csv
from collected import data #imports data from a previous py file
from collections import defaultdict

count=0
my_names={}
meta_names={}
pre_csv={}
Scigraph_info={}
coms={}
g=Graph()
k=[]
finished_dict=defaultdict(list)
labels=[]
elements=[]
x={}
y=[]
comcat={}
temp=defaultdict(list)


with open('cell_layer_data.csv', 'rt') as f:
    new_labels=([r[0:14] for r in csv.reader(f)][0])#only 14 columns to work with

with open('cell_layer_data.csv', 'rt') as f:
    csv_rows=([r[0:14] for r in csv.reader(f)][1:])
with open('brain_region_data.csv', 'rt') as f:
    csv_rows+= ([r[0:14] for r in csv.reader(f)][1:])
with open('neuron_data_curated.csv', 'rt') as f:
    csv_rows+= ([r[0:14] for r in csv.reader(f)][1:])#47,66

with open('lost_cat.csv', 'rt') as f:
    lost_rows= ([r[0:14] for r in csv.reader(f)][1:])

'''
#FINDS KEYS AND VALUES IN SCIGRAPH
for keys in a:
    r=keys.lower()
    for labels in csv_labels:
        l=labels.lower()
        if l in r:
            print(labels, keys)
'''

scigraph = ('http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#cell_ontology_ID', 'http://www.geneontology.org/formats/oboInOwl#hasVersion',
            'http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#neuroNamesAncillaryTerm',
            'http://purl.obolibrary.org/obo/UBPROP_0000012', 'http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#birnlexDefinition', 'http://www.w3.org/2002/07/owl#deprecated',
            'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#MeshUid',
            'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#nifID', 'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#createdDate',
            'http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#bamsID', 'http://www.geneontology.org/formats/oboInOwl#id',
            'http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#curationStatus', 'http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#isReplacedByClass',
            'http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#bonfire_ID', 'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#altDefinition', 'category',
            'http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#birnlexPendingDifferentiaNote', 'http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#neuronamesID',
            'http://purl.obolibrary.org/obo/UBPROP_0000001', 'http://www.geneontology.org/formats/oboInOwl#hasBroadSynonym', 'http://www.w3.org/2004/02/skos/core#scopeNote', 'http://www.w3.org/2004/02/skos/core#example',
            'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#usageNote', 'http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#birnlexRetiredDefinition', 'acronym',
            'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#externalSourceURI', 'http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#PMID',
            'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#externallySourcedDefinition', 'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#pendingMereotopologicalRelationNote',
'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#modifiedDate', 'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#pendingActionNote', 'types',
            'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#hasAbbrevSource', 'http://www.geneontology.org/formats/oboInOwl#hasExactSynonym', 'http://www.w3.org/2004/02/skos/core#historyNote',
            'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#definingCitation', 'http://purl.obolibrary.org/obo/UBPROP_0000003', 'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#tempDefinition',
            'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#externalSourceId', 'http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#umls_ID',
            'http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#sao_ID', 'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#UmlsCui',
            'http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#hasCurationStatus', 'http://purl.obolibrary.org/obo/IAO_0000115', 'http://ontology.neuinfo.org/NIF/#createdDate',
            'http://www.w3.org/2004/02/skos/core#definition', 'http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#bonfireID', 'http://purl.org/dc/elements/1.1/description',
            'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#hasExternalSource',
            'http://www.w3.org/2002/07/owl#versionInfo', 'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#acronym',
            'http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#hasBirnlexCurator',
            'http://www.geneontology.org/formats/oboInOwl#hasDbXref', 'http://www.w3.org/2004/02/skos/core#editorialNote',
            'http://www.w3.org/2000/01/rdf-schema#comment', 'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#definingCitationURI',
            'http://purl.org/dc/elements/1.1/source', 'http://www.geneontology.org/formats/oboInOwl#editor_notes',
            'http://www.geneontology.org/formats/oboInOwl#hasRelatedSynonym', 'http://www.geneontology.org/formats/oboInOwl#creation_date',
            'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#curator', 'http://www.w3.org/2004/02/skos/core#prefLabel',
            'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#abbrev',
            'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#definitonSource', 'http://www.geneontology.org/formats/oboInOwl#hasOBONamespace',
            'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#hasDefinitionSource',
            'http://ontology.neuinfo.org/NIF/BiomaterialEntities/NIF-Cell.owl#sao_ID', 'http://www.w3.org/2004/02/skos/core#changeNote',
            'http://protege.stanford.edu/plugins/owl/protege#sao_ID', 'http://purl.org/dc/elements/1.1/contributor', 'synonym',
            'http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#hasFormerParentClass')

'''
num=0
temp=defaultdict(list)
for i in csv_rows:
    for j in i:
        #print(j)
        temp[csv_sci[num]]=(j)
        num += 1
    num=0
print(temp, "\n")
print(num)
'''

value_1=[]
k=[]
for keys_1 in data.keys():
    #print(keys_1)
    k.append(keys_1)

num=k.index('nlx_only')
del k[num]


sci_dict=defaultdict(list)
for rows in csv_rows:
    for i in k:
        for j in data[i]:
            if j==rows[3]:
                node=g.getNode(i+':'+j)
                #print(node)
                for key,value in node['nodes'][0]['meta'].items():#pulls items info out of web
                    if 'definition' in key and "['"+rows[8]+"']"!=str(value):
                        rows[8]=str(rows[8])+','+str(value)
                    if '#label' in key and "['"+rows[1]+"']"!=str(value):   #master_csv['Categories'].extend([value,cat[num]])
                        rows[1]=str(rows[1])+','+str(value)
                    if '#synonym' in key and "['"+rows[2]+"']"!=str(value):
                        rows[2]=str(rows[2])+','+str(value)
                    if 'abbreviation' in key and "['"+rows[12]+"']"!=str(value):
                        rows[12]=str(rows[12])+','+str(value)
                    else:
                        Scigraph_info[key]=(value)
                for elements in scigraph:
                    if elements in Scigraph_info.keys():
                        pass
                    if elements not in Scigraph_info.keys():
                        Scigraph_info[elements]=('')
                        pass
                #print('Scigraph_info',Scigraph_info)
                od = collections.OrderedDict(sorted(Scigraph_info.items()))
                Sci_od_keys=[]
                for od_keys in od.keys():
                    Sci_od_keys.append(od_keys)#reference
                #print(Sci_od_keys)
                Sci_od_val=[]
                for od_values in od.values():
                    Sci_od_val.append(od_values)
                #print(Sci_od_val)
                y=rows+Sci_od_val
                finished_dict[rows[3]].append(y)
                #finished_dict[rows[3]].extend([x, y,])
                Scigraph_info={}
                y=[]
                Sci_od_val=[]
                del od

for lost in lost_rows:
    finished_dict[lost[3]].append(lost)

#print(type(Sci_od_keys), type(Sci_od_keys))
csv_sci = new_labels + Sci_od_keys
finished_dict['LABELS'].append(csv_sci)
#print(csv_sci)#needs to be the first row of the new dictionary
#print(finished_dict)
#print(sci_dict)
print('stopped')


with open('Neurolex_Scigraph.json', 'wt') as f:
    json.dump(finished_dict, f)

#'definition', 'http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#cell_ontology_ID', 'http://www.geneontology.org/formats/oboInOwl#hasVersion', 'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#synonym', 'http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#neuroNamesAncillaryTerm', 'http://purl.obolibrary.org/obo/UBPROP_0000012', 'http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#birnlexDefinition', 'http://www.w3.org/2002/07/owl#deprecated', 'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#MeshUid', 'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#nifID', 'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#createdDate', 'http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#bamsID', 'http://www.geneontology.org/formats/oboInOwl#id', 'http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#curationStatus', 'http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#isReplacedByClass', 'http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#bonfire_ID', 'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#altDefinition', 'category', 'http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#birnlexPendingDifferentiaNote', 'http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#neuronamesID', 'http://purl.obolibrary.org/obo/UBPROP_0000001', 'http://www.geneontology.org/formats/oboInOwl#hasBroadSynonym', 'http://www.w3.org/2004/02/skos/core#scopeNote', 'http://www.w3.org/2004/02/skos/core#example', 'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#usageNote', 'http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#birnlexRetiredDefinition', 'acronym', 'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#externalSourceURI', 'http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#PMID', 'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#externallySourcedDefinition', 'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#pendingMereotopologicalRelationNote', 'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#modifiedDate', 'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#pendingActionNote', 'types', 'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#hasAbbrevSource', 'http://www.geneontology.org/formats/oboInOwl#hasExactSynonym', 'http://www.w3.org/2004/02/skos/core#historyNote', 'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#definingCitation', 'http://purl.obolibrary.org/obo/UBPROP_0000003', 'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#tempDefinition', 'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#externalSourceId', 'http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#umls_ID', 'http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#sao_ID', 'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#UmlsCui', 'http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#hasCurationStatus', 'http://purl.obolibrary.org/obo/IAO_0000115', 'http://ontology.neuinfo.org/NIF/#createdDate', 'http://www.w3.org/2004/02/skos/core#definition', 'http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#bonfireID', 'http://purl.org/dc/elements/1.1/description', 'http://www.w3.org/2000/01/rdf-schema#label', 'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#hasExternalSource', 'http://www.w3.org/2002/07/owl#versionInfo', 'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#acronym', 'http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#hasBirnlexCurator', 'http://www.geneontology.org/formats/oboInOwl#hasDbXref', 'http://www.w3.org/2004/02/skos/core#editorialNote', 'http://www.w3.org/2000/01/rdf-schema#comment', 'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#definingCitationURI', 'http://purl.org/dc/elements/1.1/source', 'http://www.geneontology.org/formats/oboInOwl#editor_notes', 'http://www.geneontology.org/formats/oboInOwl#hasRelatedSynonym', 'http://www.geneontology.org/formats/oboInOwl#creation_date', 'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#curator', 'http://www.w3.org/2004/02/skos/core#prefLabel', 'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#abbrev', 'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#definitonSource', 'http://www.geneontology.org/formats/oboInOwl#hasOBONamespace', 'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#hasDefinitionSource', 'http://ontology.neuinfo.org/NIF/BiomaterialEntities/NIF-Cell.owl#sao_ID', 'abbreviation', 'http://www.w3.org/2004/02/skos/core#changeNote', 'http://protege.stanford.edu/plugins/owl/protege#sao_ID', 'http://purl.org/dc/elements/1.1/contributor', 'synonym', 'http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#hasFormerParentClass'}

















