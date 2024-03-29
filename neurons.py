#!/usr#/bin/env python3
"""
    DO IT BY HAND BECAUSES NEWLINES EVERYWHERE AND I DONT FEEL LIKE WRITING A PARSER
"""
import requests
import csv
import numpy as np
import heatmaps.services
from IPython import embed

map_nlx_to_scigraph = {  # from column names
            'Abbrev': '',
            'AxonMyelination': '',
            'AxonProjectionLaterality': '',
            'BranchingMetrics': '',
            'CellSomaShape': '',
            'CellSomaSize': '',
            'DefiningCitation': '',
            'DefiningCriteria': '',
            'Definition': 'definitions',
            'DendriteLocation': '',
            'FBBT Link': '',
            'FBbt Id': '',
            'Fasciculates with': '',
            'Has role': '',
            'Id': 'fragment',
            'Label': 'labels',
            'Located in': '',
            'LocationOfAxonArborization': '',
            'LocationOfLocalAxonArborization': '',
            'MolecularConstituents': '',
            'Neurotransmitter/NeurotransmitterReceptors': '',
            'OriginOfAxon': '',
            'PMID': '',
            'Species': 'taxon',
            'SpineDensityOnDendrites': '',
            'SuperCategory': '',
            'Synonym': 'synonyms',
}

map_nlx_to_cell = {  # from column names
            'Abbrev': '',
            'AxonMyelination': '',
            'AxonProjectionLaterality': '',
            'BranchingMetrics': '',
            'CellSomaShape': '',
            'CellSomaSize': '',
            'DefiningCitation': 'definingCitation',
            'DefiningCriteria': '',
            'Definition': 'definition',
            'DendriteLocation': '',
            'FBBT Link': '',
            'FBbt Id': '',
            'Fasciculates with': '',
            'Has role': '',
            'Id': 'fragment',
            'Label': 'label',
            'Located in': '',  # soma
            'LocationOfAxonArborization': '',
            'LocationOfLocalAxonArborization': '',
            'MolecularConstituents': '',
            'Neurotransmitter?NeurotransmitterReceptors': '',
            'OriginOfAxon': '',
            'PMID': '',
            'Species': 'taxon',
            'SpineDensityOnDendrites': '',
            'SuperCategory': 'subClassOf',
            'Synonym': 'synonym',
}



def DO_NOT_USE():
    query1 = "http://neurolex.org/wiki/Special:Ask/-5B-5BCategory:Neuron-5D-5D/-3FLabel/-3FSynonym/-3FId/-3FPMID/-3FDefiningCitation/-3FSuperCategory/-3FSpecies/-3FDefinition/-3FDefiningCriteria/-3FHas role/-3FFBbt Id/-3FAbbrev/-3FFBBT Link/format%3Dcsv/sep%3D,/limit%3D800"
    query2 = "http://neurolex.org/wiki/Special:Ask/-5B-5BCategory:Neuron-5D-5D/-3FFasciculates with/-3FCellSomaShape/-3FCellSomaSize/-3FLocated in/-3FSpineDensityOnDendrites/-3FDendriteLocation/-3FBranchingMetrics/-3FAxonMyelination/-3FAxonProjectionLaterality/-3FLocationOfAxonArborization/-3FLocationOfLocalAxonArborization/-3FOriginOfAxon/-3FNeurotransmitter-3FNeurotransmitterReceptors/-3FMolecularConstituents/format%3Dcsv/sep%3D,/limit%3D800"
    r_csv1 = requests.get(query1)
    r_csv2 = requests.get(query2)
    csv1 = r_csv1.text
    csv2 = r_csv2.text
    lines = []
    # fix the madness that occurs in the Amacrine neuron page (no evidence of that newline exists ANYWHERE)
    csv2 = csv2.replace("dendrite.\n Adapted from Swanson, 2013.", "dendrite. Adapted from Swanson, 2013.")
    for c1line, c2line in zip(csv1.split('\n'), csv2.split('\n')):  # somewhere there is a \n in quotes
        print('QUERY1',c1line)
        print('QUERY2',c2line)
        line = c1line + ',' + c2line
        lines.append(line)

    csv = '\n'.join(lines)

    with open('full_neurons.csv','wt') as f:
        f.write(csv)

def main():
    with open('neuron_data.csv', 'rt') as f:
        lines = [l for l in csv.reader(f)]

    lines = np.array(lines)
    labels = lines[:,1]
    syns = lines[:,2]
    ts = heatmaps.services.term_service()
    records = [] 
    for l, ss, in zip(labels, syns):
        tr = ts.get_term_record(l)
    if not tr:
        for syn in ss.split(','):
            if syn:
                tr = ts.get_term_record(syn)
                if tr:
                    tr[0]['TRIGGERING SYN'] = syn
                    break
        records.append(tr)
            
                

    embed()

if __name__ == '__main__':
    main()
