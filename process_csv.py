#!/usr/bin/env python3

from pyontutils.utils import makeGraph, rowParse
from IPython import embed
import csv

class convertCurated(rowParse):
    def __init__(self, graph, rows, header):
        super().__init__(rows, header)#, order=[0])

    def Label(self, value):
        #print(value)
        pass
    def Synonym(self, value):
        #print(value)
        pass
    def Id(self, value):
        #print(value)
        pass
    def PMID(self, value):
        #print(value)
        pass
    def DefiningCitation(self, value):
        #print(value)
        pass
    def SuperCategory(self, value):
        print(value)
        #pass
    def Species_taxa(self, value):
        #print(value)
        pass
    def Definition(self, value):
        #print(value)
        pass
    def DefiningCriteria(self, value):
        #print(value)
        pass
    def Has_role(self, value):
        #print(value)
        pass
    def FBbt_Id(self, value):
        #print(value)
        pass
    def Abbrev(self, value):
        #print(value)
        pass
    def FBBT_Link(self, value):
        #print(value)
        pass
    def Fasciculates_with(self, value): 
        #print(value)
        pass
    def CellSomaShape(self, value): 
        #print(value)
        pass
    def CellSomaSize(self, value): 
        #print(value)
        pass
    def Located_in(self, value): 
        #print(value)
        pass
    def SpineDensityOnDendrites(self, value): 
        #print(value)
        pass
    def DendriteLocation(self, value): 
        #print(value)
        pass
    def BranchingMetrics(self, value): 
        #print(value)
        pass
    def AxonMyelination(self, value): 
        #print(value)
        pass
    def AxonProjectionLaterality(self, value): 
        #print(value)
        pass
    def LocationOfAxonArborization(self, value): 
        #print(value)
        pass
    def LocationOfLocalAxonArborization(self, value): 
        #print(value)
        pass
    def DefiningCitation(self, value):
        #print(value)
        pass
    def OriginOfAxon(self, value): 
        #print(value)
        pass
    def Neurotransmitter_NeurotransmitterReceptors(self, value): 
        #print(value)
        pass
    def MolecularConstituents(self, value): 
        #print(value)
        pass
    def Curator_Notes(self, value): 
        #print(value)
        pass
    def Phenotypes(self, value): 
        #print(value)
        pass
    def Notes(self, value): 
        #print(value)
        pass
    # TODO look at pyontutils/parcellation.py line 128 for reference

def main():
    filename = 'hello world'
    PREFIXES = {'to':'do'}
    new_graph = makeGraph(filename, PREFIXES)
    rows = None  #TODO look at line 15 of nlxeol/mysqlinsert.py for this
    with open('neuron_data_curated.csv', 'rt') as f:
        rows = [r for r in csv.reader(f)]
    header = [h.replace(' ', '_')  for h in rows[0]]  #TODO
    #embed()
    header[header.index('Species/taxa')] = 'Species_taxa'
    header[header.index('Neurotransmitter/NeurotransmitterReceptors')] = 'Neurotransmitter_NeurotransmitterReceptors'
    header[header.index('Phenotypes:_ilx:has_location_phenotype')] = 'Phenotypes'
    # convert the header names so that ' ' is replaced with '_'
    convertCurated(new_graph, rows, header)

if __name__ == '__main__':
    main()

