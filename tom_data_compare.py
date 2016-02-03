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


#FIXME
#with open('cell_layer_data.csv', 'rt') as f:
    #cell_labels= [r[0:14] for r in csv.reader(f)][0]#only 14 columns to work with
#print(new_labels, '\n')

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
            'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#curator',
            'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#abbrev',
            'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#definitonSource', 'http://www.geneontology.org/formats/oboInOwl#hasOBONamespace',
            'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#hasDefinitionSource',
            'http://ontology.neuinfo.org/NIF/BiomaterialEntities/NIF-Cell.owl#sao_ID', 'http://www.w3.org/2004/02/skos/core#changeNote',
            'http://protege.stanford.edu/plugins/owl/protege#sao_ID', 'http://purl.org/dc/elements/1.1/contributor', 'synonym',
            'http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#hasFormerParentClass')


print(cell_labels)
cli = {l:i for i, l in enumerate(cell_labels)}
bli = {l:i for i, l in enumerate(brain_labels)}
lli = {l:i for i, l in enumerate(layer_labels)}

cell_cats = {a[cli['Categories']]:a[cli['Id']] for a in cell_rows}
brain_cats = {a[bli['Categories']]:a[bli['Id']] for a in brain_rows}
layer_cats = {a[lli['Categories']]:a[lli['Id']] for a in layer_rows}

def c_trans(row):
    try:
        row[cli['SuperCategory']] = cell_cats[':Category:' + row[cli['SuperCategory']]]
    except KeyError as e:
        print(e)
    return row

def b_trans(row):
    try:
        row[bli['SuperCategory']] = brain_cats[':Category:' + row[bli['SuperCategory']]]
    except KeyError as e:
        print(e)
    return row

def l_trans(row):
    try:
        row[lli['SuperCategory']] = layer_cats[':Category:' + row[lli['SuperCategory']]]
    except KeyError as e:
        print(e)
    return row

cell_rows_dict = {a[cli['Id']]:c_trans(a) for a in cell_rows}
brain_rows_dict = {a[bli['Id']]:b_trans(a) for a in brain_rows}
layer_rows_dict = {a[lli['Id']]:l_trans(a) for a in layer_rows}
#print(cell_rows_dict.keys())


output = {}
missing = []
for prefix, outer_identifiers in data.items():
        for outer_identifier in outer_identifiers:
            record = []
            if outer_identifier in cell_rows_dict:
                record.extend(cell_rows_dict[outer_identifier])
            elif outer_identifier in brain_rows_dict:
                record.extend(brain_rows_dict[outer_identifier])
            elif outer_identifier in layer_rows_dict:
                record.extend(layer_rows_dict[outer_identifier])
            else:
                raise TypeError('WHAT ????????????????')
                #missing.append(outer_identifier)
                #record.extend(['' for a in new_labels])

            if prefix != 'nlx_only':
                node = g.getNode(prefix + ':' + outer_identifier)
                metadict = node['nodes'][0]['meta']
                for key in scigraph:
                    record.append(metadict.get(key, ''))
            else:
                record.extend(['' for a in scigraph])
            output[outer_identifier] = record

                #for key, value in node['nodes'][0]['meta'].items():#pulls items info out of web

#FIXME IMPORTANT
#adds a list of the order of which all the info is in under the key 'LABEL'
#finished_dict['LABELS'].append(csv_sci)
output['LABELS'] = cell_labels + list(scigraph)
print(missing)



#FIXME
# Nice reference to long data compiling.
#print(finished_dict)
#print(com_list)
print('stopped')

#json will make this readable to others
with open('Neurolex_Scigraph.json', 'wt') as f:
    json.dump(output, f)

