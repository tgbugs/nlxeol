'''
Merges Neurolex data with Scigraphs
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

for row in csv_rows:
    for row_element in row:
        if type(row_element) == list:
            row_element = row_element.set()
    while len(row) != len(new_labels):
        row.append('')

#print(csv_rows[0][3])
'''
#FINDS KEYS AND VALUES IN SCIGRAPH
for keys in a:
    r=keys.lower()
    for labels in csv_labels:
        l=labels.lower()
        if l in r:
            print(labels, keys)
'''
# Makes lists of lists into one list.
# WARNING! it will destroy order because it will create more elements. For reference only and not to hard code.
def nested_list_killer(one_list):
    new_list=[]
    for one_list_ele in one_list:
        if type(one_list_ele)==list:
            for temp in one_list_ele:
                new_list.append(temp)
        else:
            new_list.append(one_list_ele)
    return new_list

def bracket_destroyer(input):
    if '[' and ']' in input:
        input.replace('[','').replace(']','')
    return input

def no_repeats(csv, sci):
    #print(type(csv))
    #print('\n')

    #print('csv',10*" ",csv)
    #print('sci',10*" ",sci)
    csv=csv.replace('\""', '')
    csv=csv.replace('  ', ' ')
    sci=sci.replace('\""', '')
    sci=sci.replace('  ', ' ')
    new_csv=[]
    new_sci=[]
    final_draft=[]
    if not csv:
        #print ('final 1',sci)
        return sci
    if not sci:
        #print ('final 2',sci)
        return csv
    if sci in csv:
        #print('passed')
        return False
    if (" "+sci) or (sci+" ") in csv:
        return False
    if (sci + '.') in csv:
        #print('passed')
        return False

    #FIXME: I haven't been able to seperate properly if there are abbre.
    #FIXME temp_csv=list(csv.split('. '))

    #print('csv 1',10*" ",temp_csv)
    #for ele in temp_csv:
        #if '.' in ele:
            #new_csv.append(ele.replace('.',''))
        #else:
            #new_csv.append(ele)

    #FIXME temp_sci=list(sci.split ('. '))

    #for ele in temp_sci:
        #if '.' in ele:
            #new_sci.append(ele.replace('.',''))
        #else:
            #new_sci.append(ele)
    #FIXME temp2_csv=[]
    #for ele in temp_csv:
        #temp2_csv.append(ele.lower())

    #FIXME for ele1 in temp_sci:
        #ele=ele1.lower()
        #if ele not in temp2_csv:
            #final_draft.append(ele1)

    #final_draft=final_draft+temp_csv
    final_draft.append(csv,sci)
    final_draft=str(final_draft).strip('[]')
    final_draft=final_draft.replace(',',', ').replace(r"\'",r"'").replace('..','.')
    final_draft=final_draft.replace(',  ',', ')
    final_draft=final_draft.replace(r'\\','')#need two \\ to make it valid to read one
    final_draft=final_draft.replace(r'\\"', '')
    final_draft=final_draft.replace(r'\\\\', '')
    final_draft=final_draft.replace('.,','.')
    final_draft=final_draft.replace(r"\\", '')
    #final_draft = final_draft.replace("'''","\\'\\'\\'")
    #final_draft=final_draft.replace(r"//", '')



    #comma.join(final_draft)
    #print(new_sci)
    final_draft=final_draft.replace('S, J., Costa, V., Psaroulis, V., Arzoglou, L,','S. J., Costa, V., Psaroulis, V., Arzoglou, L.')
    #print('final',10*" ",final_draft)

    return final_draft
'''
    new_list=[]
    for e1 in input:
        if type(e1)==list:
            temp = list(set(e1))
            if len(e1)!=len(temp):
                print(e1)
                print(temp)
            new_list.append(list(set(e1)))
        else:
            new_list.append(e1)
    #print(new_list)
    return new_list
'''
#Will beautifully take two list of strings and tell you what strings they have in common.
def twins(csv, sci):
    a = set(csv)
    b = set(sci)
    #print('csv',a,'\n')
    #print('sci',b, '\n')
    c=set(a)&set(b)
    #print(c)
    g=[]
    for keys_1 in c:
        g.append(keys_1)
    num = g.index('')
    del g[num]
    #print('final',g)
    g = [x for x in g if x != []]
    return g



scigraph = ['http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#cell_ontology_ID', 'http://www.geneontology.org/formats/oboInOwl#hasVersion',
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
            'http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#hasFormerParentClass']

LABEL = ["acronym","category", "http://ontology.neuinfo.org/NIF/#createdDate", "http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#acronym", "http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#bamsID", "http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#birnlexPendingDifferentiaNote", "http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#birnlexRetiredDefinition", "http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#bonfireID", "http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#bonfire_ID", "http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#cell_ontology_ID", "http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#curationStatus", "http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#hasBirnlexCurator", "http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#hasCurationStatus", "http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#hasFormerParentClass", "http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#isReplacedByClass", "http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#neuroNamesAncillaryTerm", "http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#neuronamesID", "http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#umls_ID", "http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#MeshUid", "http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#UmlsCui", "http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#altDefinition", "http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#createdDate", "http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#curator", "http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#definitonSource", "http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#externalSourceId", "http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#externalSourceURI", "http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#hasAbbrevSource", "http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#hasExternalSource", "http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#modifiedDate", "http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#nifID", "http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#pendingActionNote", "http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#pendingMereotopologicalRelationNote", "http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#tempDefinition", "http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#usageNote", "http://purl.obolibrary.org/obo/IAO_0000115", "http://purl.obolibrary.org/obo/UBPROP_0000001", "http://purl.obolibrary.org/obo/UBPROP_0000003", "http://purl.obolibrary.org/obo/UBPROP_0000012", "http://purl.org/dc/elements/1.1/contributor", "http://purl.org/dc/elements/1.1/description", "http://purl.org/dc/elements/1.1/source", "http://www.geneontology.org/formats/oboInOwl#creation_date", "http://www.geneontology.org/formats/oboInOwl#editor_notes", "http://www.geneontology.org/formats/oboInOwl#hasBroadSynonym", "http://www.geneontology.org/formats/oboInOwl#hasDbXref", "http://www.geneontology.org/formats/oboInOwl#hasExactSynonym", "http://www.geneontology.org/formats/oboInOwl#hasOBONamespace", "http://www.geneontology.org/formats/oboInOwl#hasRelatedSynonym", "http://www.geneontology.org/formats/oboInOwl#hasVersion", "http://www.geneontology.org/formats/oboInOwl#id", "http://www.w3.org/2000/01/rdf-schema#comment", "http://www.w3.org/2002/07/owl#deprecated", "http://www.w3.org/2002/07/owl#versionInfo", "http://www.w3.org/2004/02/skos/core#changeNote", "http://www.w3.org/2004/02/skos/core#editorialNote", "http://www.w3.org/2004/02/skos/core#example", "http://www.w3.org/2004/02/skos/core#historyNote", "http://www.w3.org/2004/02/skos/core#scopeNote", "types"]
'''
#USEFUL BUT DON'T REMEMBER WHY.

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


#Scigraph doesn't have nlx_only data to retrieve and will cause an error. Thus, we take it out and add it back in later.
value_1=[]
k=[]
for keys_1 in data.keys():
    k.append(keys_1)

#num=k.index('nlx_only')
#del k[num]


''' My baby that is the backbone of comparing the curated csv files from Neurolex
    to the pulled out data from Scigraph to merge common data. We then add the rest of Scigraph
    data as its own potential csv columns in the imported json file.
'''
delList=[]
sci_dict=defaultdict(list)
nlx_dict=defaultdict(list)
bigSci=defaultdict(list)
littleSci=defaultdict(list)

for rows in csv_rows:
    for i in k:
        for j in data[i]:
            if j==rows[3]:
                temp=j
                if j in data['nlx_only']:
                    nlx_dict[rows[3]]=rows
                    continue
                node=g.getNode(i+':'+j)
                for key,value in node['nodes'][0]['meta'].items():#pulls items info out of web
                    if '[' and ']' in value:
                        value = value.replace('[','').replace(']','')
                    if '#definition' in key: #need plain definition
                        for val in value:
                            val = no_repeats(rows[8], val)
                            if val != False:
                                rows[8]=val
                                bigSci[rows[3]].append(littleSci[key].append(val))
                        if key in scigraph:
                            scigraph.remove(key)
                        continue
                    if 'definition' in key: #need plain definition
                        for val in value:
                            val = no_repeats(rows[8], val)
                            if val != False:
                                rows[8]=val
                                bigSci[rows[3]].append(littleSci[key].append(val))
                        if key in scigraph:
                            scigraph.remove(key)
                        continue
                        #FIXME
                    if '#label' in key:
                        for val in value:
                            val = no_repeats(rows[1], val)
                            if val != False:
                                rows[1]=val
                                bigSci[rows[3]].append(littleSci[key].append(val))
                        if key in scigraph:
                            scigraph.remove(key)
                        continue
                    if '#prefLabel' in key: #and "['"+rows[1]+"']"!=str(value):
                        for val in value:
                            val = no_repeats(rows[1], val)
                            if val != False:
                                rows[1]=val
                                bigSci[rows[3]].append(littleSci[key].append(val))
                        if key in scigraph:
                            scigraph.remove(key)
                        continue
                    if 'synonym' in key: #and "['"+rows[2]+"']"!=str(value):
                        for val in value:
                            if 'Vestibular ganglioin neuron' in val:
                                val=val.replace('Vestibular ganglioin neuron', '')
                            val = no_repeats(rows[2], val)
                            if val != False:
                                rows[2]=val
                                bigSci[rows[3]].append(littleSci[key].append(val))

                        if key in scigraph:
                            scigraph.remove(key)
                        continue
                    if 'abbreviation' in key: #and "['"+rows[12]+"']"!=str(value):
                        for val in value:
                            val = no_repeats(rows[12], val)
                            if val != False:
                                rows[12]=val
                                bigSci[rows[3]].append(littleSci[key].append(val))

                        if key in scigraph:
                            scigraph.remove(key)
                        continue
                    if 'abbrev' in key: #and "['"+rows[12]+"']"!=str(value):
                        for val in value:
                            val = no_repeats(rows[12], val)
                            if val != False:
                                rows[12]=val
                                bigSci[rows[3]].append(littleSci[key].append(val))

                        if key in scigraph:
                            scigraph.remove(key)
                        continue
                    if '#sao_ID' in key:
                        for val in value:
                            val = no_repeats(rows[3], val)
                            if val != False:
                                rows[3]=val
                                bigSci[rows[3]].append(littleSci[key].append(val))

                        if key in scigraph:
                            scigraph.remove(key)
                        continue
                    if '#definingCitation' in key:
                        for val in value:
                            val = no_repeats(rows[5], val)
                            if val != False:
                                rows[5]=val
                                bigSci[rows[3]].append(littleSci[key].append(val))

                        if key in scigraph:
                            scigraph.remove(key)
                        continue
                    if '#PMID' in key:
                        for val in value:
                            val = no_repeats(rows[4], val)
                            if val != False:
                                rows[4]=val
                                bigSci[rows[3]].append(littleSci[key].append(val))

                        if key in scigraph:
                            scigraph.remove(key)
                        continue
                    if '#hasDefinitionSource' in key:
                        for val in value:
                            val = no_repeats(rows[8], val)
                            if val != False:
                                rows[8]=val
                                bigSci[rows[3]].append(littleSci[key].append(val))

                        if key in scigraph:
                            scigraph.remove(key)
                        continue
                    if '#birnlexDefinition' in key:
                        for val in value:
                            val = no_repeats(rows[8], val)
                            if val != False:
                                rows[8]=val
                                bigSci[rows[3]].append(littleSci[key].append(val))

                        if key in scigraph:
                            scigraph.remove(key)
                        continue
                    if '#externallySourcedDefinition' in key:
                        for val in value:
                            val = no_repeats(rows[8], val)
                            if val != False:
                                rows[8]=val
                                bigSci[rows[3]].append(littleSci[key].append(val))

                        if key in scigraph:
                            scigraph.remove(key)
                        continue
                    if '#hasDefinitionSource' in key:
                        for val in value:
                            val = no_repeats(rows[8], val)
                            if val != False:
                                rows[8]=val
                                bigSci[rows[3]].append(littleSci[key].append(val))

                        if key in scigraph:
                            scigraph.remove(key)
                        continue
                    else:
                        #print(key)
                        #print(value)
                        Scigraph_info[key]=(value)
                        #print(key)
                for elements in LABEL:
                    if elements in Scigraph_info.keys():
                        continue
                    if elements not in Scigraph_info.keys():
                        Scigraph_info[elements]=('')
                        continue
                od = collections.OrderedDict(sorted(Scigraph_info.items()))
                #print(od)
                Sci_od_keys=[]
                for od_keys in od.keys():
                    Sci_od_keys.append(od_keys)#reference
                Sci_od_val=[]
                for od_values in od.values():
                    Sci_od_val.append(od_values)
                Sci_od_keys.append('PREFIX')
                Sci_od_val.append(i+':'+j)


                #TO FIND IF MATCHING INFO

                #start of temp code
                #print('SCI',Sci_od_val, '\n')
                #print('ROWS',rows, '\n')

                #csv_sci = new_labels + Sci_od_keys

                #print(csv_sci)
                #print('Sci',Sci_od_val)

                #Sci_od_val=nested_list_killer(Sci_od_val)
                #Sci_od_val=bracket_destroyer(Sci_od_val)

                #print(Sci_od_val)

                #common=twins(Sci_od_val, rows)

                #print('Sci',Sci_od_val)
                #print(common)

                #for i in common:
                #    for j in Sci_od_val:
                #        if i in j:
                #            f=Sci_od_val.index(j)
                #            h=f+14
                #            print ('SCI',Sci_od_val[f])
                #            print ('real list',csv_sci[h])
                #for i in common:
                #    for j in rows:
                #        if i in j:
                #            f=rows.index(j)
                #            print(f)
                #            print('rows',rows[f])

                #print(Sci_temp)
                #print('rows',rows)
                #for com_ele in common:
                   # for i in Sci_temp:
                        #if com_ele==Sci_temp:
                            #print()
                    #rows_num = rows.index(com_ele)
                    #print('sci',csv_sci[sci_num])
                    #print('rows',csv_sci[rows_num])
                #END OF COMPARE CODE

                y=rows+Sci_od_val
                #print(y)
                #y=no_repeats(y)
                #print(y)
                #rint('\n',rows[3])
                #print(len(y))
                finished_dict[temp].append(y)
                temp=0
                # Sanity check to make sure data isn't being double copied.
                Scigraph_info={}
                y=[]
                Sci_od_val=[]
                del od

#combines orignial csv labels from neurolex and adds the scigraph labels I found important
csv_sci = new_labels + Sci_od_keys
print(len(csv_sci))
#while len(lost_rows)!=len(csv_sci):
    #lost_rows.append('')
#print(csv_sci)
for lost in lost_rows:
    while len(lost)!=len(csv_sci):
        lost.append('')
    finished_dict[lost[3]].append(lost)



#FIXME IMPORTANT
#adds a list of the order of which all the info is in under the key 'LABEL'
finished_dict['LABELS']=csv_sci

for nlxIds, nlxRows in nlx_dict.items():
    while len(nlxRows) != len(csv_sci):
        nlxRows.append('')
    finished_dict[nlxIds]=nlxRows

SciList = []
for key,value in bigSci.items():
    SciList.append((key,value))


#FIXME
# Nice reference to long data compiling.
#print(finished_dict)
#print(com_list)
#print(littleSci)
print('stopped')

with open('Sci.json', 'wt') as f:
    json.dump(SciList , f)
#json will make this readable to others
with open('Neurolex_Scigraph.json', 'wt') as f:
    json.dump(finished_dict, f)


#This is the original TOTAL list of keys from scigraph... enjoy :)
#'definition', 'http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#cell_ontology_ID', 'http://www.geneontology.org/formats/oboInOwl#hasVersion', 'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#synonym', 'http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#neuroNamesAncillaryTerm', 'http://purl.obolibrary.org/obo/UBPROP_0000012', 'http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#birnlexDefinition', 'http://www.w3.org/2002/07/owl#deprecated', 'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#MeshUid', 'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#nifID', 'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#createdDate', 'http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#bamsID', 'http://www.geneontology.org/formats/oboInOwl#id', 'http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#curationStatus', 'http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#isReplacedByClass', 'http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#bonfire_ID', 'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#altDefinition', 'category', 'http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#birnlexPendingDifferentiaNote', 'http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#neuronamesID', 'http://purl.obolibrary.org/obo/UBPROP_0000001', 'http://www.geneontology.org/formats/oboInOwl#hasBroadSynonym', 'http://www.w3.org/2004/02/skos/core#scopeNote', 'http://www.w3.org/2004/02/skos/core#example', 'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#usageNote', 'http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#birnlexRetiredDefinition', 'acronym', 'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#externalSourceURI', 'http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#PMID', 'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#externallySourcedDefinition', 'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#pendingMereotopologicalRelationNote', 'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#modifiedDate', 'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#pendingActionNote', 'types', 'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#hasAbbrevSource', 'http://www.geneontology.org/formats/oboInOwl#hasExactSynonym', 'http://www.w3.org/2004/02/skos/core#historyNote', 'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#definingCitation', 'http://purl.obolibrary.org/obo/UBPROP_0000003', 'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#tempDefinition', 'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#externalSourceId', 'http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#umls_ID', 'http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#sao_ID', 'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#UmlsCui', 'http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#hasCurationStatus', 'http://purl.obolibrary.org/obo/IAO_0000115', 'http://ontology.neuinfo.org/NIF/#createdDate', 'http://www.w3.org/2004/02/skos/core#definition', 'http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#bonfireID', 'http://purl.org/dc/elements/1.1/description', 'http://www.w3.org/2000/01/rdf-schema#label', 'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#hasExternalSource', 'http://www.w3.org/2002/07/owl#versionInfo', 'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#acronym', 'http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#hasBirnlexCurator', 'http://www.geneontology.org/formats/oboInOwl#hasDbXref', 'http://www.w3.org/2004/02/skos/core#editorialNote', 'http://www.w3.org/2000/01/rdf-schema#comment', 'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#definingCitationURI', 'http://purl.org/dc/elements/1.1/source', 'http://www.geneontology.org/formats/oboInOwl#editor_notes', 'http://www.geneontology.org/formats/oboInOwl#hasRelatedSynonym', 'http://www.geneontology.org/formats/oboInOwl#creation_date', 'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#curator', 'http://www.w3.org/2004/02/skos/core#prefLabel', 'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#abbrev', 'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#definitonSource', 'http://www.geneontology.org/formats/oboInOwl#hasOBONamespace', 'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#hasDefinitionSource', 'http://ontology.neuinfo.org/NIF/BiomaterialEntities/NIF-Cell.owl#sao_ID', 'abbreviation', 'http://www.w3.org/2004/02/skos/core#changeNote', 'http://protege.stanford.edu/plugins/owl/protege#sao_ID', 'http://purl.org/dc/elements/1.1/contributor', 'synonym', 'http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#hasFormerParentClass'}
