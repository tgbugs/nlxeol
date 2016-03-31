'''
Merges Neurolex data with Scigraphs
'''
import collections
from collected2 import data2
from heatmaps.scigraph_client import Graph
import json
import csv
from collected import data #imports data from a previous py file
from collections import defaultdict
from LABELS_keys import LABEL
from scigraph_keys import scigraph

sci = scigraph

Scigraph_info={}
g=Graph()
k=[]
finished_dict=defaultdict(list)
x={}
y=[]


with open('neuron_data_curated.csv', 'rt') as f:
    new_labels=([r[0:] for r in csv.reader(f)][0])#only 14 columns to work with
    new_labels[0] = 'Category'
print(new_labels, '\n')

with open('cell_layer_data.csv', 'rt') as f:
    csv_rows = ([r[0:] for r in csv.reader(f)][1:])
with open('brain_region_data.csv', 'rt') as f:
    csv_rows += ([r[0:] for r in csv.reader(f)][1:])
with open('neuron_data_curated.csv', 'rt') as f:
    csv_rows += ([r[0:] for r in csv.reader(f)][1:])#47,66
with open('species_data.csv', 'rt') as f:
    csv_rows += ([r[0:] for r in csv.reader(f)][1:])

with open('lost_cat.csv', 'rt') as f:
    lost_rows = ([r[0:] for r in csv.reader(f)][1:])

#gives row the standard length
for row in csv_rows:
    for row_element in row:
        if type(row_element) == list:
            row_element = row_element.set()
    while len(row) != len(new_labels):
        row.append('')

def no_repeats(csv, sci):

    csv=csv.replace('\""', '')
    csv=csv.replace('  ', ' ')
    sci=sci.replace('\""', '')
    sci=sci.replace('  ', ' ')

    final_draft=[]
    if not csv:
        return sci
    if not sci:
        return csv
    if sci in csv:
        return False
    if (" "+sci) or (sci+" ") in csv:
        return False
    if (sci + '.') in csv:
        return False

    final_draft.append(csv, sci)
    final_draft=str(final_draft).strip('[]')
    final_draft=final_draft.replace(',',', ').replace(r"\'",r"'").replace('..','.')
    final_draft=final_draft.replace(',  ',', ')
    final_draft=final_draft.replace(r'\\','')#need two \\ to make it valid to read one
    final_draft=final_draft.replace(r'\\"', '')
    final_draft=final_draft.replace(r'\\\\', '')
    final_draft=final_draft.replace('.,','.')
    final_draft=final_draft.replace(r"\\", '')
    final_draft=final_draft.replace('S, J., Costa, V., Psaroulis, V., Arzoglou, L,','S. J., Costa, V., Psaroulis, V., Arzoglou, L.')

    return final_draft

#Will beautifully take two list of strings and tell you what strings they have in common.
def twins(csv, sci):
    a = set(csv)
    b = set(sci)
    c=set(a)&set(b)
    g=[]

    for keys_1 in c:
        g.append(keys_1)
    num = g.index('')
    del g[num]
    g = [x for x in g if x != []]

    return g

#Scigraph doesn't have nlx_only data to retrieve and will cause an error. Thus, we take it out and add it back in later.
value_1=[]
k=[]
for keys_1 in data2.keys():
    k.append(keys_1)


''' My baby that is the backbone of comparing the curated csv files from Neurolex
    to the pulled out data from Scigraph to merge common data. We then add the rest of Scigraph
    data as its own potential csv columns in the imported json file.
'''
nlx_dict=defaultdict(list)
bigSci=defaultdict(list)
littleSci=defaultdict(list)

merged_terms = {'#definition':8, 'definition':8, 'label':1, '#prefLabel':1, 'synonym':2, 'abbreviation':12, 'abbrev':12,'#sao_ID':3,
                '#definingCitation':5, '#PMID':4, '#hasDefinitionSource':8, '#birnlexDefinition':8,
                '#externallySourcedDefinition':8}


def merge(merged_terms, key, value):
    k=False
    for term, num in merged_terms.items():
        if term in key: #need plain definition
            for val in value:
                val = no_repeats(rows[num], val)
                if val != False:
                    rows[num]=val
                    bigSci[rows[3]].append(littleSci[key].append(val))
            if key in sci:
                print(key)
                sci.remove(key)
            k = True
    if k == False:
        Scigraph_info[key]=(value)


for rows in csv_rows:
    for i in k:
        for j in data2[i]:
            if j==rows[3]:
                temp=j
                if temp == "":
                    continue
                if temp == None:
                    continue
                if j in data2['nlx_only']:
                    nlx_dict[rows[3]]=rows
                    continue
                node=g.getNode(i+':'+j)
                for key,value in node['nodes'][0]['meta'].items():#pulls items info out of web
                    if '[' and ']' in value:
                        value = value.replace('[','').replace(']','')
                    #Golden Boy
                    merge(merged_terms, key, value)

                for elements in LABEL:
                    if elements in Scigraph_info.keys():
                        continue
                    if elements not in Scigraph_info.keys():
                        Scigraph_info[elements]=('')
                        continue

                od = collections.OrderedDict(sorted(Scigraph_info.items()))
                Sci_od_keys=[]
                for od_keys in od.keys():
                    Sci_od_keys.append(od_keys)#reference
                Sci_od_val=[]
                for od_values in od.values():
                    Sci_od_val.append(od_values)


                Sci_od_keys.append('PREFIX')
                Sci_od_val.append(i+':'+j)
                y=rows+Sci_od_val
                finished_dict[temp].append(y)
                temp=0

                # Sanity check to make sure data isn't being double copied.
                Scigraph_info={}
                y=[]
                Sci_od_val=[]
                del od

#combines orignial csv labels from neurolex and adds the scigraph labels I found important
csv_sci = new_labels + Sci_od_keys



#FIXME IMPORTANT
#adds a list of the order of which all the info is in under the key 'LABEL'
finished_dict['LABELS']=csv_sci
print(finished_dict['LABELS'])

for i in range(0,len(nlx_dict.keys())):
    while len(nlx_dict[i]) != len(csv_sci):
        nlx_dict[i].append('')
    finished_dict[nlx_dict[i][3]].append(nlx_dict[i])

for i in range(0,15):
    while len(lost_rows[i])!=len(csv_sci):
        lost_rows[i].append('')
    finished_dict[lost_rows[i][3]].append(lost_rows[i])
#FIXME
finished_dict.pop("", None)


SciList = []
for key,value in bigSci.items():
    SciList.append((key,value))

print('stopped')

with open('sci.json', 'wt') as f:
    json.dump(SciList , f)

#json will make this readable to others
with open('Neurolex_Scigraph.json', 'wt') as f:
    json.dump(finished_dict, f)


#This is the original TOTAL list of keys from scigraph... enjoy :)
#'definition', 'http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#cell_ontology_ID', 'http://www.geneontology.org/formats/oboInOwl#hasVersion', 'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#synonym', 'http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#neuroNamesAncillaryTerm', 'http://purl.obolibrary.org/obo/UBPROP_0000012', 'http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#birnlexDefinition', 'http://www.w3.org/2002/07/owl#deprecated', 'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#MeshUid', 'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#nifID', 'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#createdDate', 'http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#bamsID', 'http://www.geneontology.org/formats/oboInOwl#id', 'http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#curationStatus', 'http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#isReplacedByClass', 'http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#bonfire_ID', 'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#altDefinition', 'category', 'http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#birnlexPendingDifferentiaNote', 'http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#neuronamesID', 'http://purl.obolibrary.org/obo/UBPROP_0000001', 'http://www.geneontology.org/formats/oboInOwl#hasBroadSynonym', 'http://www.w3.org/2004/02/skos/core#scopeNote', 'http://www.w3.org/2004/02/skos/core#example', 'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#usageNote', 'http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#birnlexRetiredDefinition', 'acronym', 'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#externalSourceURI', 'http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#PMID', 'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#externallySourcedDefinition', 'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#pendingMereotopologicalRelationNote', 'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#modifiedDate', 'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#pendingActionNote', 'types', 'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#hasAbbrevSource', 'http://www.geneontology.org/formats/oboInOwl#hasExactSynonym', 'http://www.w3.org/2004/02/skos/core#historyNote', 'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#definingCitation', 'http://purl.obolibrary.org/obo/UBPROP_0000003', 'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#tempDefinition', 'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#externalSourceId', 'http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#umls_ID', 'http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#sao_ID', 'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#UmlsCui', 'http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#hasCurationStatus', 'http://purl.obolibrary.org/obo/IAO_0000115', 'http://ontology.neuinfo.org/NIF/#createdDate', 'http://www.w3.org/2004/02/skos/core#definition', 'http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#bonfireID', 'http://purl.org/dc/elements/1.1/description', 'http://www.w3.org/2000/01/rdf-schema#label', 'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#hasExternalSource', 'http://www.w3.org/2002/07/owl#versionInfo', 'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#acronym', 'http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#hasBirnlexCurator', 'http://www.geneontology.org/formats/oboInOwl#hasDbXref', 'http://www.w3.org/2004/02/skos/core#editorialNote', 'http://www.w3.org/2000/01/rdf-schema#comment', 'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#definingCitationURI', 'http://purl.org/dc/elements/1.1/source', 'http://www.geneontology.org/formats/oboInOwl#editor_notes', 'http://www.geneontology.org/formats/oboInOwl#hasRelatedSynonym', 'http://www.geneontology.org/formats/oboInOwl#creation_date', 'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#curator', 'http://www.w3.org/2004/02/skos/core#prefLabel', 'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#abbrev', 'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#definitonSource', 'http://www.geneontology.org/formats/oboInOwl#hasOBONamespace', 'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#hasDefinitionSource', 'http://ontology.neuinfo.org/NIF/BiomaterialEntities/NIF-Cell.owl#sao_ID', 'abbreviation', 'http://www.w3.org/2004/02/skos/core#changeNote', 'http://protege.stanford.edu/plugins/owl/protege#sao_ID', 'http://purl.org/dc/elements/1.1/contributor', 'synonym', 'http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#hasFormerParentClass'}
