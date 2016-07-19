#!/usr/bin/env python3

import rdflib
from pyontutils.utils import makeGraph, rowParse
from IPython import embed
import csv

class convertCurated(rowParse):
    def __init__(self, graph, rows, header):
        self.graph = graph
        self.set_LocationOfAxonArborization = set()
        self.set_LocationOfLocalAxonArborization = set()
        self.set_MolecularConstituents = set()
        self.set_NeurotransmitterReceptors = set()
        self.set_Neurotransmitter = set()
        self.set_BranchingMetrics = set()
        self.set_CellSomaShape = set()
        self.set_DendriteLocation = set()
        self.cat_id_dict = {}
        self.fake_url_prefix = 'http://fake.org/'
        eval_first = ['Id', 'Category']
        super().__init__(rows, header, order=eval_first)

    def _translate_category_id(self, category):  # FIXME this fails when referencing later defined cats
        if category in self.cat_id_dict:
            return self.cat_id_dict[category]
        else:
            return category

    def Category(self, value):
        self.category = self.fake_url_prefix + value.replace(' ','_')
        if self.id_ is None:
            self.Id(self.category)
        self.cat_id_dict[self.category] = self.id_

    def Label(self, value):
        print(value)
        self.graph.add_node(self.id_, rdflib.RDFS.label, value)
        pass
    def Synonym(self, value):
        print(value)
        #self.graph.add_node(self.id_, rdflib.RDFS.synonym, value)
        pass
    def Id(self, value):
        if not value:
            self.id_ = None
        else:
            self.id_ = self.fake_url_prefix + value  # TODO need proper curie prefixes
            self.graph.add_node(self.id_, rdflib.RDF.type, rdflib.OWL.Class)
        print(value)

    def PMID(self, value):
        #print(value)
        pass
    def DefiningCitation(self, value):
        #print(value)
        pass
    def SuperCategory(self, value):
        print(value)
        value = self.fake_url_prefix + ':Category:' + value.replace(' ','_')
        value = self._translate_category_id(value)  # FIXME out of order issues
        self.graph.add_node(self.id_, rdflib.RDFS.subClassOf, value)

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
        if value:
            print(value)
            
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
        if value:
            print(value)
        self.set_DendriteLocation.add(value)

        to_skip = {':Category:Dendrites spread from the cell body in all directions. Dendrites are smooth where they lie in the deep layer but where the dendrites cross the pyramidal (fusiform) cell layer into the molecular layer', ':Category:They become spiny. Functionally it has been demonstrated that they receive not only acoustic input in the deep layer but also proprioceptive input through the molecular layer.', ':Category:Brush of dendrites is short and lies near the cell body', ':Category:Dendrites lie parallel to auditory nerve fibers in the ventral cochlear nucleus', ':Category:Receptive field in the periphery', ':Category:Two primary dendrites', ':Category:One that projects laterally towards the roots of the VIIIth cranial nerve and is named the lateral dendrite', ':Category:And another which projects rostrally and ventrally and is called the ventral dendrite.', ':Category:Basal dendrites in neocortical layers 5 and 6;apical dendrites across neocortical layers 5 to 1.', ':Category:Basal dendrites branch within neocortical layers 5 and 6;apical dendrite extends across neocortical layers 5-1.', ':Category:Basal dendrites in Neocortex layer 5', ':Category:Apical dendrites across neocortical layers 5-1.', ':Category:Mostly neocortical layer 4', ':Category:Basal dendrites will be in the same layer as the soma and/or the subjacent layer. Apical dendrites rise toward the pia and into layer 1. For layer 6 neurons', ':Category:However,:Category:The apical dendrite will often not continue beyond layer 4/lower layer 3.', ':Category:Arborization within the glomerular neuropil and external plexiform layer', ':Category:Dendrties arborize in the external plexiform layer where they contact the secondary/lateral dendrites of mitral cells via reciprocal dendrodendritic synapses. The basal dendrite remains restricted to the granule cell layer.', ':Category:Proximal', ':Category:Intermediate', ':Category:Distal', ''}
        if value in to_skip:
            pass
        else:
            #put_the_value_in_the_graph(view)
            self.graph.add_node(self.category, 'http://DendriteLocation.org', value)
        pass
    def BranchingMetrics(self, value): 
        if value:
            print(value)
        self.set_BranchingMetrics.add(value)
        
        to_skip = {'other', 'this is a columnar cell without a true dendrite', ''}
        if value in to_skip:
            pass
        else:
            #put_the_value_in_the_graph(view)
            self.graph.add_node(self.category, 'http://BranchingMetrics.org', value)

        pass
    def AxonMyelination(self, value): 
        print(value)
        pass
    def AxonProjectionLaterality(self, value): 
        print(value)
        pass
    def LocationOfAxonArborization(self, value): 
        if value:
            print(value)
        NONE = 'None'
        fixes = {
            ':Category:NA':NONE,
            ':Category:None':NONE,
            ':Category:No axon':NONE,
            ':Category:Anaxonic - no axon':NONE,
            ':Category:This is an anaxonal cell; it lacks an axon':NONE,
        }
        if value in fixes:
            value = fixes[value]

        self.set_LocationOfAxonArborization.add(value)

        to_skip = {':Category:NA', ':Category:None', ':Category:No axon', ':Category:Anaxonic - no axon', ':Category:This is an axonal cell; it lacks an axon', ' : axon collaterals to other pyramidal cells. Mouse: no axon collaterals. Exit through the dorsal and intermediate acoustic striae to terminate in the contralateral inferior colliculus', ':Category:Axon descends in the medial lateral fasciculus and projects to caudal brainstem and all spinal segments', ':Category:For supragranular neurons', ':Category:This is almost exclusively cortical (except for some corticostriatal projections from layer 3). Infragranular neurons can project subcortically (LGN', ':Category:Superior colliculus', ':Category:Claustrum', ':Category:Amygdala) but also cortically', ':Category:Ipsi- or contralateral.', ':Category:Cell groups embedded in the lemniscus lateralis', ':Category:And the nucleus mesencephalicus lateralis', ':Category:Pars dorsalis in the midbrain', ':Category:Synaptic output is from cell body', ''}
        if value in to_skip:
            pass
        else:
            #put_the_value_in_the_graph(value)
            self.graph.add_node(self.category, 'http://LocationOfAxonArborization.org', value)
        pass
    def LocationOfLocalAxonArborization(self, value): 
        if value:
            print(value)
        NONE = 'None'
        CAP = ':Category:Olfactory cortex layer II'
        fixes = {
            ':Category:NA':NONE,
            ':Category:No axon':NONE,
            ':Category:None':NONE,
            ':Category:This is an anaxonal cell; it lacks an axon':NONE,
            ':Category:No local arborization':NONE,
            ':Category:OLFACTORY CORTEX LAYER II':CAP,
        } 
        if value in fixes:
            value = fixes[value]

        self.set_LocationOfLocalAxonArborization.add(value)

        to_skip = {':Category:NA', ':Category:No axon', ':Category:None', ':Category:This is an anaxonal cell; it lacks an axon', ':Category:No local arborization', ':Category:Few', ':Category:Lamina xxx', ':Category:Within extraglomerular regions', ':Category:Within the same granule cell domain as the cell body', ':Category:In some species (mice) but not in others (cats) octopus cells have local collaterals in the octopus cell area and contact granule cells in the granule cell lamina.', ':Category:For layer 6: layer 6 and 4 (J.S. Lund', ':Category:In primate and see A. Thomson for rodent); for layer 5: largely layer 5 but can extend to layer 3; for layer 3', ':Category:Largely layer 3', ':Category:But can extend to layer 5; layer 2', ':Category:Layer 2', ':Category:But can involve other layers.', ':Category:Synaptic output is from the cell body', ':Category:Pyramidal Cells', ':Category:Giant cells', ':Category:Cartwheel cells', ':Category:OLFACTORY CORTEX LAYER II', ''}
        if value in to_skip:
            pass
        else:
            #put_the_value_in_the_graph(value)
            self.graph.add_node(self.category, 'http://LocationOfLocalAxonArborization.org', value) 
        pass
    def OriginOfAxon(self, value): 
        print(value)
        pass
    def Neurotransmitter(self, value):
        if value:
            print(value)

        self.set_Neurotransmitter.add(value)

        to_skip = {':Category:Likely glutamate', 'Excitatiry neurotransmitter', ':Category:Unknown', ':Category:Not known', ''}
        if value in to_skip:
            pass
        else:
            #put_the_value_in_the_graph(value)
            self.graph.add_node(self.category, 'http://Neurotransmitter.org', value)

        pass
    def NeurotransmitterReceptors(self, value): 
        if value:
            print(value)
        
        Add_GABA = ':Category:GABA receptor'
        Add_Glutamate = ':Category:Glutamate receptor'
        Add_Acetylcholine = ':Category:Acetylcholine receptor'
        Add_Dopamine = ':Category:Dopamine receptor'
        Add_Serotonin = ':Category:Serotonin receptor'
        Add_GABA_B = ':Category:GABA-B receptor'

        fixes = {
            ':Category:GABA':Add_GABA,
            ':Category:Glutamate':Add_Glutamate,
            ':Category:Acetylcholine':Add_Acetylcholine,
            ':Category:Dopamine':Add_Dopamine,
            ':Category:Serotonin':Add_Serotonin,
            ':Category:GABA B':Add_GABA_B,
        }

        self.set_NeurotransmitterReceptors.add(value)

        to_skip = {':Category:?', ':Category:Unknown', ':Category:Not known', ''}
        if value in to_skip:
            pass
        else:
            #put_the_value_in_the_graph(value)
            self.graph.add_node(self.category, 'http://NeurotransmitterReceptors.org', value)
        pass
    def MolecularConstituents(self, value): 
        if value:
            print(value)

        self.set_MolecularConstituents.add(value)

        to_skip = {':Category:?', ':Category:Unknown', ''}
        if value in to_skip:
            pass
        else:
            #put_the_value_in_the_graph(value)
            self.graph.add_node(self.category, 'http://MolecularConstituents.org', value)
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
    PREFIXES = {'to':'do','NLX':'http://fake.org/:Category:'}
    new_graph = makeGraph(filename, PREFIXES)
    rows = None  #TODO look at line 15 of nlxeol/mysqlinsert.py for this
    with open('neuron_data_curated.csv', 'rt') as f:
        rows = [r for r in csv.reader(f)]
    header = [h.replace(' ', '_')  for h in rows[0]]  #TODO
    #embed()
    header[header.index('')] = 'Category'
    header[header.index('Species/taxa')] = 'Species_taxa'
    #header[header.index('Neurotransmitter/NeurotransmitterReceptors')] = 'Neurotransmitter_NeurotransmitterReceptors'
    header[header.index('Phenotypes:_ilx:has_location_phenotype')] = 'Phenotypes'
    # convert the header names so that ' ' is replaced with '_'
    state = convertCurated(new_graph, rows, header)
    [print(i) for i in sorted(state.set_LocationOfAxonArborization)]
    new_graph.write()


if __name__ == '__main__':
    main()
