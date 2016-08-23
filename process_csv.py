#!/usr/bin/env python3.5

import io
import os
import csv
import json
import yaml
import rdflib
from datetime import datetime
from collections import defaultdict
import requests
from IPython import embed
from pyontutils.utils import makeGraph, rowParse
from pyontutils.scigraph_client import Cypher

#_ = requests.get('https://raw.githubusercontent.com/SciCrunch/NIF-Ontology/master/scigraph/nifstd_curie_map.yaml').text
#prefixes = yaml.load(io.StringIO(_))  # temp fix for ucsd blocking :9000
prefixes = Cypher().getCuries()
with open ('total_curie_fragment.json', 'rt') as f:
    fragment_curie_dict = json.load(f)

scr_graph = rdflib.Graph()
scr_graph.parse(os.path.expanduser('~/git/NIF-Ontology/scicrunch-registry.ttl'), format='turtle')

class convertCurated(rowParse):
    def __init__(self, graph, rows):
        self.graph = graph
        self.chebi_ids = set()
        self.drugbank_ids = set()
        self.t3db_ids = set()
        self.uni_ids = set()  # expect 735 from registry dump  # FIXME there are 804...
        self.bad_ids = set()
        self.failed_resolution = set()
        
        self.line = 0
        self.cat_id_dict = {}
        self.pre_ref_dict = defaultdict(set)
        self.to_call = []
        self.fake_url_prefix = 'ILX:'
        self.neurolex_url = 'http://neurolex.org/wiki/'
        eval_first = ['FBbt_Id', 'Categories', 'Id', 'SuperCategory']
        super().__init__(rows, order=eval_first)
        [func(*args) for func, args in self.to_call]

    def _add_node(self, s, p, o): #Call for non Category/Id
        if o in self.cat_id_dict:
            o = self.cat_id_dict[o]
            self.graph.add_node(s, p, o)
        elif ':Category:' in o: # FIXME needs a way to identify putative objectProperties
            if (self._add_node, (s, p, o)) in self.to_call:
                self.graph.add_node(s, p, o)
                self.failed_resolution.add(o)
                #print('Failed to resolve reference to', o)
            else:
                self.to_call.append((self._add_node, (s, p, o)))
        else:
            self.graph.add_node(s, p, o)

    def Categories(self, value): # FIXME called Categories in neurolex_full.csv
        self.line += 1
        if ':Category:Resource:' in value or value == 'Categories':
            raise self.SkipError
        elif not value:
            raise BaseException('Category is empyt, this should not be possible! Row = %s' % self.line) #there was a type on your version here, you had empyt instead of empty
        self.category = self.neurolex_url + value.replace(' ','_')  # fix for unknown url type

    def Id(self, value):
        if not value:
           self.id_ = self.category
            # self.id_ = None

        else:
            if value.startswith('DB'):
                self.cat_id_dict[self.category] = value  # in case someone referenced it...  # TODO check for ontology ids as well...
                self.drugbank_ids.add(value)
                raise self.SkipError
            elif value.startswith('T3D'):
                self.cat_id_dict[self.category] = value  # in case someone referenced it...
                self.t3db_ids.add(value)
                raise self.SkipError
            elif value.startswith('JAX:') or value.startswith('FMAID:'):
                value = value.replace(' ','') # FIXME
            elif value.startswith('Taxonomy ID: '):
                value = 'NCBITaxon:' + value.strip('Taxonomy ID: ')
            elif value.startswith('NCBITaxon: '):
                value = value.replace(' ' ,'')
            elif value.startswith('PATO'):
                value = value.replace(' ',':')
            elif value.startswith('CHEBI'):
                value = value.replace('_',':')
                self.cat_id_dict[self.category] = value  # in case someone referenced it...
                self.chebi_ids.add(value)
                raise self.SkipError

            if value in fragment_curie_dict:
                self.id_ = fragment_curie_dict[value]
                if self.id_ == 'NLXONLY':
                    self.id_ = 'NLX:' + value
                else:
                    prefix, fragment = self.id_.split(':')
                    if prefix not in self.graph.namespaces:
                        self.graph.namespaces[prefix] = rdflib.Namespace(prefixes[prefix])
                        self.graph.g.namespace_manager.bind(prefix, prefixes[prefix])
            elif value.startswith('http://'): # coming from category
                self.id_ = value
            else:
                self.bad_ids.add(value)
                raise self.SkipError('SKIPPING RECORD DUE TO wtf? %s' % value)

        self.cat_id_dict[self.category] = self.id_
        self.graph.add_node(self.id_, rdflib.RDF.type, rdflib.OWL.Class)
        self.graph.add_node(self.id_, 'OBOANN:neurolex_category', self.category)
            
        #else:
         #   self.id_ = self.fake_url_prefix + value  # TODO need proper curie prefixes
          #  self.graph.add_node(self.id_, rdflib.RDF.type, rdflib.OWL.Class)
        #print(value)

        if self.category in self.pre_ref_dict:
            for func in self.pre_ref_dict[self.category]:
                func(self.id_)

    def Label(self, value):
        if value:
            self._add_node(self.id_, rdflib.RDFS.label, value)
        
    def Synonym(self, value):
        if value:
            half = None
            for v in value.split(','):
                if '(' in v and ')' not in v:
                    half = v
                    continue

                if half:
                    if ')' in v:
                        v = half + ',' + v
                        print('Bad split on comma detected!', v)
                    else:
                        half.strip()
                        self._add_node(self.id_, 'OBOANN:synonym', half)

                    half = None

                v = v.strip()
                if v:
                    self._add_node(self.id_, 'OBOANN:synonym', v)

    def PMID(self, value):
        #print(value)
        pass

    def DefiningCitation(self, value):
        #print(value)
        pass

    def SuperCategory(self, value):
        if not value:
            return 

        if value == 'University':  # NOPENOPENOPE
            self.uni_ids.add(self.id_)  # TODO may need to use this to update ID to SRC: ...
            #raise self.SkipError  # TODO need to check this against scicrunch-registry.ttl hasDbXref

        value = self.neurolex_url + ':Category:' + value  # fix for :Category: being an unknown prefix
        #if 'University' in value:
            #print(value)
        if value in self.cat_id_dict:
            super_id = self.cat_id_dict[value]
            self._add_node(self.id_, rdflib.RDFS.subClassOf, super_id)
        else:
            def func(super_id, this=self.id_):
                self._add_node(this, rdflib.RDFS.subClassOf, super_id)

            self.pre_ref_dict[value].add(func)

    def Species(self, value):  # Species_taxa in neuro_data_curated.csv
        if value:
            value = self.neurolex_url + value  # fix for :Category: being an unknown prefix
        else:
            return

        pheno_edge = 'ilx:hasTaxonRank'
        if value in self.cat_id_dict:
            spec_id = self.cat_id_dict[value]
            self._add_node(self.id_, pheno_edge, value)
        else:
            def func(spec_id, this=self.id_):
                self._add_node(this, pheno_edge, spec_id)

            self.pre_ref_dict[value].add(func)

    def Definition(self, value):
        #print(value)
        pass

    def DefiningCriteria(self, value):
        #print(value)
        pass

    def Has_role(self, value):
        #print(value)
        
        to_skip = {':Category:Neuroendocrine motor cell role', ''} #I skipped this because it is already included in the phenotypes. 
# some of the others have been included as well like Principal neuron role, Motor role of nerve cell, Intrinsic neuron role, sensory reception role, but I can't skip those because I only included them in the phenotypes of the Mammals and Vertebrata, not Drosophila or other insects/invertebrate

        if value in to_skip:
            pass
        else:
            #put_the_value_in_the_graph(view)
            self.graph.add_node(self.category, 'http://Has_Role.org', value)

    def FBbt_Id(self, value):
        if value:
            #print('FBbt id found', value, 'skipping!')
            raise self.SkipError

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
            #print(value)
            pass

        parent_phenotype = 'ilx:SomaMorphologicalPhenotype'

        multipolar_fix = 'Category:Multipolar Soma Quality'
        fusiform_fix = 'Category:Fusiform Soma Quality'
        pyramidal_fix = 'Category:Pyramidal Soma Quality'
        spherical_fix = 'Category:Spherical Soma Quality'
        oval_fix = 'Category:Oval Soma Quality'
        bipolar_fix = 'Category:Bipolar Soma Quality'
        granule_fix = 'Category:Granule Soma Quality'
        mitral_fix = 'Category:Mitral Soma Quality'
        round_fix = 'Category:Round Soma Quality'

        if value == 'Category:Round, Oval, Fusiform': 
            locations = s.split(", ")
            for location in locations:
                print(location)
                self.CellSomaShape(location)
            return    

        fixes = {
                'Category:Multipolar':multipolar_fix,
                'Category:Fusiform':fusiform_fix,
                'Category:Pyramidal':pyramidal_fix,
                'Category:Spherical':spherical_fix,
                'Category:Oval':oval_fix,
                'Category:bipolar':bipolar_fix,
                'Category:Granule':granule_fix,
                'Category:Mitral':mitral_fix,
                'Oval':oval_fix,
                'Fusiform':fusiform_fix,
                'Category:Round':round_fix
        }                
        if value in fixes:
            value = fixes[value]
        

        to_skip = {'Category:Multipolar', 'Category:Fusiform', 'Category:Pyramidal', 'Category:Spherical', 'Category:Oval', 'Category:bipolar', 'Category:Granule', 'Category:Mitral', 'Oval', 'Fusiform', 'Category:Round', ''}

        if value in to_skip:
            pass
        else:
            #put_the_value_in_the_graph(view)
            self.graph.add_node(self.category, 'http://CellSomaShape.org', value)
            
    def CellSomaSize(self, value): 
        if value:
            #print(value)
            pass

        parent_phenotype = 'ilx:SomaMorphologicalPhenotype'

        pass
    def Located_in(self, value): 
        if value:
            #print(value)
            pass
        
        pheno_edge = 'ilx:hasSomaLocatedIn'

    def SpineDensityOnDendrites(self, value): 
        if value:
            #print(value)
            pass
        
        parent_phenotype = 'ilx:DendriteMorphologicalPhenotype'
        
    def DendriteLocation(self, value): 
        if value:
            #print(value)
            pass

        pheno_edge = 'ilx:hasDendriteLocatedIn'

        to_skip = {':Category:Dendrites spread from the cell body in all directions. Dendrites are smooth where they lie in the deep layer but where the dendrites cross the pyramidal (fusiform) cell layer into the molecular layer', ':Category:They become spiny. Functionally it has been demonstrated that they receive not only acoustic input in the deep layer but also proprioceptive input through the molecular layer.', ':Category:Brush of dendrites is short and lies near the cell body', ':Category:Dendrites lie parallel to auditory nerve fibers in the ventral cochlear nucleus', ':Category:Receptive field in the periphery', ':Category:Two primary dendrites', ':Category:One that projects laterally towards the roots of the VIIIth cranial nerve and is named the lateral dendrite', ':Category:And another which projects rostrally and ventrally and is called the ventral dendrite.', ':Category:Basal dendrites in neocortical layers 5 and 6;apical dendrites across neocortical layers 5 to 1.', ':Category:Basal dendrites branch within neocortical layers 5 and 6;apical dendrite extends across neocortical layers 5-1.', ':Category:Basal dendrites in Neocortex layer 5', ':Category:Apical dendrites across neocortical layers 5-1.', ':Category:Mostly neocortical layer 4', ':Category:Basal dendrites will be in the same layer as the soma and/or the subjacent layer. Apical dendrites rise toward the pia and into layer 1. For layer 6 neurons', ':Category:However,:Category:The apical dendrite will often not continue beyond layer 4/lower layer 3.', ':Category:Arborization within the glomerular neuropil and external plexiform layer', ':Category:Dendrties arborize in the external plexiform layer where they contact the secondary/lateral dendrites of mitral cells via reciprocal dendrodendritic synapses. The basal dendrite remains restricted to the granule cell layer.', ':Category:Proximal', ':Category:Intermediate', ':Category:Distal', ''}
        if value in to_skip:
            pass
        else:
            #put_the_value_in_the_graph(view)
            self.graph.add_node(self.category, 'http://DendriteLocation.org', value)

    def BranchingMetrics(self, value): 
        if value:
            #print(value)
            pass

        parent_phenotype = 'ilx:DendriteMorphologicalPhenotype'

        to_skip = {'other', 'this is a columnar cell without a true dendrite', ''}
        if value in to_skip:
            pass
        else:
            #put_the_value_in_the_graph(view)
            self.graph.add_node(self.category, 'http://BranchingMetrics.org', value)

    def AxonMyelination(self, value): 
        if value:
            #print(value)
            pass
        
        parent_phenotype = 'ilx:AxonMorphologicalPhenotype'

    def AxonProjectionLaterality(self, value): 
        if value:
            #print(value)
            pass

        pheno_edge = 'ilx:hasProjectionPhenotype'

    def LocationOfAxonArborization(self, value): 
        
        #print(value)

        pheno_edge = 'ilx:hasAxonLocatedIn'

        NONE = 'None'
        Fix_location = ':Category:CA3 oriens'
        if value == ':Category:CA3 alveus/oriens':
            locations = s.split("/")
            for location in locations:
                print(location)
                self.LocationOfAxonArborization(location)
            return


        fixes = {
            ':Category:NA':NONE,
            ':Category:None':NONE,
            ':Category:No axon':NONE,
            ':Category:Anaxonic - no axon':NONE,
            ':Category:This is an anaxonal cell; it lacks an axon':NONE,
            'oriens':Fix_location
        }
        if value in fixes:
            value = fixes[value]

        to_skip = {':Category:NA', ':Category:None', ':Category:No axon', ':Category:Anaxonic - no axon', ':Category:This is an axonal cell; it lacks an axon', ' : axon collaterals to other pyramidal cells. Mouse: no axon collaterals. Exit through the dorsal and intermediate acoustic striae to terminate in the contralateral inferior colliculus', ':Category:Axon descends in the medial lateral fasciculus and projects to caudal brainstem and all spinal segments', ':Category:For supragranular neurons', ':Category:This is almost exclusively cortical (except for some corticostriatal projections from layer 3). Infragranular neurons can project subcortically (LGN', ':Category:Superior colliculus', ':Category:Claustrum', ':Category:Amygdala) but also cortically', ':Category:Ipsi- or contralateral.', ':Category:Cell groups embedded in the lemniscus lateralis', ':Category:And the nucleus mesencephalicus lateralis', ':Category:Pars dorsalis in the midbrain', ':Category:Synaptic output is from cell body', 'oriens', ''}
        if value in to_skip:
            pass
        else:
            #put_the_value_in_the_graph(value)
            for v in value.split(','):
                v.strip()
                self._add_node(self.id_, 'http://LocationOfAxonArborization.org', v) 
        
    def LocationOfLocalAxonArborization(self, value): 
        #if value:
            #for v in value.split(','):
             #   v.strip()
              #  if v:
               #     self._add_node(self.id_, 'http://LocationOfLocalAxonArborization', v)

        pheno_edge = 'ilx:hasAxonLocatedIn'
        

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

        to_skip = {':Category:NA', ':Category:No axon', ':Category:None', ':Category:This is an anaxonal cell; it lacks an axon', ':Category:No local arborization', ':Category:Few', ':Category:Lamina xxx', ':Category:Within extraglomerular regions', ':Category:Within the same granule cell domain as the cell body', ':Category:In some species (mice) but not in others (cats) octopus cells have local collaterals in the octopus cell area and contact granule cells in the granule cell lamina.', ':Category:For layer 6: layer 6 and 4 (J.S. Lund', ':Category:In primate and see A. Thomson for rodent); for layer 5: largely layer 5 but can extend to layer 3; for layer 3', ':Category:Largely layer 3', ':Category:But can extend to layer 5; layer 2', ':Category:Layer 2', ':Category:But can involve other layers.', ':Category:Synaptic output is from the cell body', ':Category:Pyramidal Cells', ':Category:Giant cells', ':Category:Cartwheel cells', ':Category:OLFACTORY CORTEX LAYER II', ''}
        if value in to_skip:
            pass
        else:
            #put_the_value_in_the_graph(value)
            for v in value.split(','):
                v.strip()
                if v:
                    self._add_node(self.id_, 'http://LocationOfLocalAxonArborization', v) 

    def OriginOfAxon(self, value): 
        #print(value)

        pheno_edge = 'ilx:hasAxonOrigin'

    def Neurotransmitter(self, value):
        if value:
            #print(value)
            pass

        pheno_edge = 'ilx:hasExpressionPhenotype'

        to_skip = {':Category:Likely glutamate', 'Excitatiry neurotransmitter', ':Category:Unknown', ':Category:Not known', ''}
        if value in to_skip:
            pass
        else:
            #put_the_value_in_the_graph(value)
            self.graph.add_node(self.category, 'http://Neurotransmitter.org', value)

    def NeurotransmitterReceptors(self, value): 
        if value:
            #print(value)
            pass

        pheno_edge = 'ilx:hasExpressionPhenotype'
        
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

        to_skip = {':Category:?', ':Category:Unknown', ':Category:Not known', ':Category:GABA', ':Category:Glutamate', ':Category:Acetylcholine', ':Category:Dopamine', ':Category:Serotonin', ':Category:GABA B', ''}
        if value in to_skip:
            pass
        else:
            #put_the_value_in_the_graph(value)
            self.graph.add_node(self.category, 'http://NeurotransmitterReceptors.org', value)

    def MolecularConstituents(self, value): 
        if value:
            #print(value)
            pass

        pheno_edge = 'ilx:hasExpressionPhenotype'

        to_skip = {':Category:?', ':Category:Unknown', ''}
        if value in to_skip:
            pass
        else:
            #put_the_value_in_the_graph(value)
            self.graph.add_node(self.category, 'http://MolecularConstituents.org', value)

    def Curator_Notes(self, value): 
        #print(value)
        pass

    def Phenotypes(self, value): 
        #print(value)
        
        basket = "ilx:BasketPhenotype"
        Lbasket = "ilx:LargeBasketPhenotype"
        Nbasket = "ilx:NestBasketPhenotype"
        Sbasket = "ilx:SmallBasketPhenotype"
        bitufted = "ilx:BituftedPhenotype"
        bipolar = "ilx:BipolarPhenotype"
        chandelier = "ilx:ChandelierPhenotype"
        DBouquet = "ilx:DoubleBouquetPhenotype"
        Martinotti = "ilx:MartinottiPhenotype"
        neurogliaform = "ilx:NeurogliaformPhenotype"
        pyramidal = "ilx:PyramidalPhenotype"
        spiking = "ilx:SpikingPhenotype"

        fixes = {
                'ilx:has_morphological_phenotype basket':basket,
                'ilx:has_morphological_phenotype bipolar':bipolar,
                'ilx:has_morphological_phenotype chandelier':chandelier,
                'ilx:has_morphological_phenotype double bouquet':DBouquet,
                'ilx:has_morphological_phenotype Martinotti':Martinotti,
                'ilx:has_morphological_phenotype neurogliaform':neurogliaform,
                'ilx:has_morphological_phenotype pyramidal':pyramidal,
                }

        to_skip = {'ilx:has_morphological_phenotype basket', 'ilx:has_morphological_phenotype bipolar', 'ilx:has_morphological_phenotype chandelier', 'ilx:has_morphological_phenotype double bouquet', 'ilx:has_morphological_phenotype Martinotti', 'ilx:has_morphological_phenotype neurogliaform', 'ilx:has_morphological_phenotype pyramidal', ''}
        if value in to_skip:
            pass
        else:
            #put_the_value_in_the_graph(value)
            self.graph.add_node(self.category, 'http://Phenotypes.org', value)

    def Notes(self, value): 
        pass

    def ModifiedDate(self, value):
        # in theory we can use this to skip over records we don't actually need because no one has changed them since they were imported from the ontology
        pass


def main():
    filename = 'hello world'
    PREFIXES = {'to':'do',
                'NLX':'http://neurolex.org/wiki/',
                'ILX':'http://uri.interlex.org/base/ilx_',
                'ilx':'http://uri.interlex.org/base/',
                'OBOANN':'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#',
                }
    new_graph = makeGraph(filename, PREFIXES)
    #with open('neuron_data_curated.csv', 'rt') as f:
    with open('neurolex_full.csv', 'rt') as f:
        rows = [r for r in csv.reader(f)]
    new_rows = [list(r) for r in zip(*[c for c in zip(*rows) if any([r for r in c if r != c[0]])])]
    no_data_cols = set(rows[0]) - set(new_rows[0])
    print(no_data_cols)

    #header[header.index('Phenotypes:_ilx:has_location_phenotype')] = 'Phenotypes'
    # convert the header names so that ' ' is replaced with '_'
    state = convertCurated(new_graph, new_rows)
    #embed()
    #return

    _ = [print(i) for i in sorted([datetime.strptime(t, '%d %B %Y') for _ in state._set_ModifiedDate for t in _.split(',') if _])]
    _ = [print(i) for i in sorted(state.chebi_ids)]
    _ = [print(i) for i in sorted(state.drugbank_ids)]
    _ = [print(i) for i in sorted(state.t3db_ids)]
    _ = [print(i) for i in sorted(state.uni_ids)]
    _ = [print(i) for i in sorted(state.bad_ids)]
    #_ = [print(i) for i in sorted(state.failed_resolution)]
    #_ = [print(i) for i in sorted(state._set_LocationOfAxonArborization)]

    # deal with unis TODO needs to be embeded in state.Id or something incase of reference
    unis = {None:[]}
    lookup_new_id = {}
    for id_ in sorted([_.split(':')[1] for _ in state.uni_ids]):
        matches = [_ for _ in scr_graph.triples((None, None, rdflib.Literal(id_)))]
        if len(matches) > 1:
            print(matches)
        elif not matches:
            unis[None].append(id_)
            lookup_new_id[id_] = None
        else:
            match = matches[0]
            unis[match[0].rsplit('/',1)[1].replace('_',':')] = id_
            lookup_new_id[id_] = match[0].rsplit('/',1)[1].replace('_',':')

    embed()
    #return

    new_graph.write()


if __name__ == '__main__':
    main()
