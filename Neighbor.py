import json
from collected import data
import csv
from heatmaps.scigraph_client import Graph, Vocabulary
import re
from collections import defaultdict, namedtuple
from IPython import embed

g = Graph()

with open('Neurolex_Scigraph.json') as data_file:
    js = json.load(data_file)


with open('species_data.csv', 'rt') as f:
    species_rows = [r for r in csv.reader(f)]
    species_labels = species_rows[0]
    species_labels[0] = 'Categories'
    species_rows = species_rows[1:]
with open('brain_region_data.csv', 'rt') as f:
    brain_rows = [r for r in csv.reader(f)]
    brain_labels = brain_rows[0]
    brain_labels[0] = 'Categories'
    brain_rows = brain_rows[1:]
with open('neuron_data_curated.csv', 'rt') as f:
    neuron_rows = [r for r in csv.reader(f)]
    neuron_labels = neuron_rows[0]
    neuron_labels[0] = 'Categories'
    neuron_rows = neuron_rows[1:]
with open('cell_layer_data.csv', 'rt') as f:
    cell_rows = [r for r in csv.reader(f)]
    cell_labels = cell_rows[0]
    cell_labels[0] = 'Categories'
    cell_rows = cell_rows[1:]


keys = tuple(js.keys())
#prefix = tuple(data)
record=defaultdict(list)

SuperCategory=defaultdict(list)
#def SuperCategoryMaker(SuperCategory, values):
fixmeRecord=[]



for prefix, outer_identifiers in data.items():
    if 'nlx_only' == prefix:
        continue
    for id_ in outer_identifiers:
        PrefixWithID = prefix + ':' + id_
        #FIXME why is there more than 1 neighbor?
        neighbor = [e for e in g.getNeighbors(PrefixWithID, depth=1,direction='INCOMING')['edges'] if e['sub']==PrefixWithID and e['pred']=='subClassOf']
        #print(neighbor)
        for edge in neighbor:
            key = edge['pred']
            value = edge['obj']
            sub = edge['sub']
            record[sub].append(value)
            if len(record[sub]) > 1:
                fixmeRecord.append((sub,record[sub]))

for i in js['LABELS']:
    print(r"'"+i+r"'"+":"+r"'"+'rdfs:temp'+r"'"+",")




#print(fixmeRecord)
print('stopped')
'''
dict_keys(['', 'Retina ganglion cell', 'Olfactory bulb', 'Retina photoreceptor cone cell', 'Lobe parts of the cerebellar cortex', 'Frontal lobe', 'Regional part of a lobe of the cerebellum', 'Composite part spanning multiple base regional parts of brain', 'Regional Parts of the Hemisphere Lobules', 'Superficial feature part of occipital lobe', 'Hemispheric parts of the cerebellar cortex', 'Hemispheric Lobule VII', 'Nucleus raphe magnus', 'Regional part of cerebellar white matter', 'Limbic lobe', 'Nucleus of CNS', 'Temporal lobe', 'Superficial feature part of pons', 'Sulcus', 'Superficial feature part of the cerebellum', 'Paravermis parts of the cerebellar cortex', 'Neocortex stellate cell', 'Occipital lobe', 'Gross anatomical parts of the cerebellum', 'Spinal cord ventral horn interneuron V0', 'Cell layer', 'Telencephalon', 'Vermic Lobule VII', 'Cerebellar cortex', 'Vermal parts of the cerebellum', 'Glial-like cell', 'Septal pellucidum', 'Dorsal root ganglion A alpha-beta non-nociceptive neuron', 'Regional Parts of the Vermal Lobules', 'Cerebrospinal axis', 'Regional part of brain', 'Retina amacrine cell', 'Neuron', 'Hemisphere parts of cerebral cortex', 'Regional part of cerebellar cortex', 'Aggregate regional part of brain', 'Chemoarchitectural part', 'Regional Parts of the Paravermal Lobules', 'Cytoarchitectural fields of hippocampal formation', 'Lobular parts of the cerebellar cortex', 'Cytoarchitectural part of dentate gyrus', 'Regional part of cerebellum', 'Circumventricular organ', 'Neocortex pyramidal cell', 'Defined neuron class', 'Parietal lobe', 'Lobe parts of cerebral cortex', 'Functional part of brain', 'Lobe of cerebral cortex', 'Chemoarchitectural part of neostriatum', 'Retina bipolar cell', 'Sub-lobar region'])
'''