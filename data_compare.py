import re
import numpy
from heatmaps.scigraph_client import Graph, Vocabulary
import json
import csv
from collected import data #imports data from a previous py file
from collections import defaultdict

count=0
my_names={}
meta_names={}
pre_csv={}
master_csv={}
coms={}
g=Graph()
k=[]
finished_dict=defaultdict(list)
labels=[]
elements=[]


with open('cell_layer_data.csv', 'rt') as f:
    csv_labels=[r[0:14] for r in csv.reader(f)][0]#only 14 columns to work with
#print('labels--->', csv_labels)

with open('cell_layer_data.csv', 'rt') as f:
    csv_rows=([r[0:14] for r in csv.reader(f)][1:])
with open('brain_region_data.csv', 'rt') as f:
    csv_rows+= ([r[0:14] for r in csv.reader(f)][1:])
with open('neuron_data_curated.csv', 'rt') as f:
    csv_rows+= ([r[0:14] for r in csv.reader(f)][1:])
with open('lost_cat.csv', 'rt') as f:
    csv_rows+= ([r[0:14] for r in csv.reader(f)][1:])


comcat={}
for rows in csv_rows:
    for j in data['NIFCELL']:
            if j==rows[3]:
                #print(j)
                node=g.getNode('NIFCELL'+':'+j)
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
                        master_csv[key]=(value)

                comcat['Neuorlex']=rows
                finished_dict[rows[3]].extend([comcat, master_csv])
                master_csv={}
                #print(finished_dict)
    for j in data['NIFGA']:
            if j==rows[3]:
                #print(j)
                node=g.getNode('NIFGA'+':'+j)
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
                        master_csv[key]=(value)

                comcat['Neuorlex']=rows
                finished_dict[rows[3]].extend([comcat, master_csv])
                master_csv={}
                #print(finished_dict)
    for j in data['nlx_only']:
            if j==rows[3]:
                #print(j)
                node=g.getNode('nlx_only'+':'+j)
                #print(node)
                if node==None:
                    pass
                else:
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
                            master_csv[key]=(value)

                    comcat['Neuorlex']=rows
                    finished_dict[rows[3]].extend([comcat, master_csv])
                    master_csv={}
                    #print(finished_dict)
    for j in data['OBO']:
            if j==rows[3]:
                #print(j)
                node=g.getNode('OBO'+':'+j)
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
                        master_csv[key]=(value)

                comcat['Neuorlex']=rows
                finished_dict[rows[3]].extend([comcat, master_csv])
                master_csv={}
                #print(finished_dict)
    for j in data['NIFNEURCIR']:
            if j==rows[3]:
                #print(j)
                node=g.getNode('NIFNEURCIR'+':'+j)
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
                        master_csv[key]=(value)

                comcat['Neuorlex']=rows
                finished_dict[rows[3]].extend([comcat, master_csv])
                master_csv={}
                #print(finished_dict)

# ['Categories', 'Label', 2'Synonym', 'Id', 'PMID', 'DefiningCitation', 'SuperCategory', 7'Species',
# 'Definition', 'DefiningCriteria', 10'Has role', 'FBbt Id', 'Abbrev', 'FBBT Link']



#need to condense the ifs of the original while just having the 4 compariable for the remaining if statements; need to map the rows to there sisters

print(finished_dict)
S=json.dumps(finished_dict)
#print(sudo)
#print(master_csv)
print('stopped')


















