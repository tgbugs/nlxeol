#!/usr/bin/env python3
import re
import csv
from collections import namedtuple
from IPython import embed

with open('neuron_data_curated.csv', 'rt') as f:
    rows = [r[:4] for r in csv.reader(f)]
with open('brain_region_data.csv', 'rt') as f:
    rows += [r[:4] for r in csv.reader(f)][1:]
with open('cell_layer_data.csv', 'rt') as f:
    rows += [r[:4] for r in csv.reader(f)][1:]

rows[0][0] = 'Category name'
Columns = namedtuple('Columns', [n.replace(' ', '_').replace('/', '_') for n in rows[0]])

print(Columns)
#n_to_id_dict = {r[0][1:]:r[3] for r in rows}
def wrap_string(string):
    #return '&neurons;' + string.replace(' ','_')
    return string.replace(' ','_')

na_id_dict = {wrap_string(tup.Category_name[1:])+'"':wrap_string(tup.Id)+'"' if tup.Id else 'NO_ID' + wrap_string(tup.Category_name[1:]) for tup in map(Columns._make, rows[1:])}
na_to_label = {wrap_string(tup.Category_name[1:]):tup.Label if tup.Label else 'NO_LABEL' + tup.Category_name.split(':')[2].replace('_',' ') for tup in map(Columns._make, rows[1:])}

#print(na_id_dict)

def sub(x):
    #print(x.group())
    return na_id_dict[x.group()]

with open('Neurons.owl','rt') as f:
    lines = f.readlines()

#expression = r'\b(' + '|'.join([k.replace(')',r'\)').replace('(',r'\(') for k in na_id_dict]) + r')\b'  # apparenlty the )\b causes errors
expression = r'' + '|'.join([k.replace(')',r'\)').replace('(',r'\(') for k in na_id_dict]) + r''
pattern = re.compile(expression)  # what happens if key order changes?!
results = []
for string in lines:
    if 'neurons#' in string:
        string = string.replace('#','/')

    string = string.replace("&apos;","'")  # this was an irritating bug to deal with because python autoconverts it :/

    result = pattern.sub(sub, string)
    results.append(result)
    if result == string and '&neurons' in result and 'Category' in result:
        n=len(result)
        temp=string
        temp=string.replace('">',' ')
        temp=temp.replace('_', ' ')
        print(temp[44:85])
    if '<owl:Class' in string:
        try:
            name = string.split(';')[1].split('"')[0]
        except IndexError:
            print(string)
            raise
        if "&apos;" in name:
            embed()
        if name in na_to_label:
            label_line = '        <rdfs:label rdf:datatype="&xsd;string">{label}</rdfs:label>\n'.format(label=na_to_label[name])
            results.append(label_line)
        #elif name.startswith('Axon') or name.startswith('Dendrite') or name.startswith('Soma'):
            #pass
        #elif name == 'Brain_Region' or name == 'Neuron' or name == 'Neuropeptide' or name == 'Neurotransmitter' or name == 'Taxon':
            #pass
        #else:
        #elif '(dorsal)' in name:
            #raise BaseException(name)

with open('Neurons_new.owl', 'wt') as f:
    f.writelines(results)
    pass

embed()



