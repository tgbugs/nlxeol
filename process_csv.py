#!/usr/bin/env python3.7
"""Convert neurolex dump spreadsheets to rdf

Usage:
    process-csv [options]

Options:
    -d --debug    embed after complete

"""

import io
import os
import csv
import json
import yaml
import rdflib
from datetime import datetime, date
from collections import defaultdict
import requests
from IPython import embed
from sqlalchemy import create_engine, inspect
import pyontutils.core
from pyontutils.utils import rowParse
from pyontutils.core import makeGraph, createOntology
from pyontutils.namespaces import makePrefixes, PREFIXES, definition, hasRole, ilxtr
from pyontutils.qnamefix import cull_prefixes
from pyontutils.scigraph_client import Cypher
#from nlx_cat_map import nlxmapping


#_ = requests.get('https://raw.githubusercontent.com/SciCrunch/NIF-Ontology/master/scigraph/nifstd_curie_map.yaml').text
#prefixes = yaml.load(io.StringIO(_))  # temp fix for ucsd blocking :9000
prefixes = Cypher().getCuries()
prefixes['skos'] = 'http://www.w3.org/2004/02/skos/core#'

TODAY = date.isoformat(date.today())

with open('total_curie_fragment.json', 'rt') as f:
    fragment_curie_dict = json.load(f)

mloc = os.path.expanduser('~/git/NIF-Ontology/ttl/generated/NIF-NIFSTD-mapping.ttl')
_mapping = rdflib.Graph().parse(mloc, format='turtle')
_mappingg = makeGraph('', graph=_mapping)
new_translation = {o:s for s, o in _mapping.subject_objects(rdflib.OWL.sameAs)}
new_translation_values = set(new_translation.values())

def get_scr():
    scr_graph = rdflib.Graph()
    scr_graph.parse(os.path.expanduser('~/git/NIF-Ontology/scicrunch-registry.ttl'), format='turtle')
    return scr_graph

def get_nlxdb():
    DB_URI = 'mysql+mysqlconnector://{user}@{host}/{db}'
    engine = create_engine(DB_URI.format(user='neurolex', host='localhost', db='neurolexdb'))
    smw_query = engine.execute("select s_id, tid.smw_title, smw_ids.smw_title, value_xsd from smw_atts2 join smw_ids on p_id=smw_id join smw_ids as tid on tid.smw_id=s_id where tid.smw_title not like '%Resource:%';")
    smw_data = smw_query.fetchall()
    output = {}
    for s_id, category_b, pred_b, obj_b in smw_data:
        #category = convertCurated.neurolex_url + category_b.decode()
        category = ':Category:' + category_b.decode().replace('_',' ')
        pred = pred_b.decode()
        obj = obj_b.decode()

        if category not in output:
            output[category] = {}

        if pred not in output[category]:
            output[category][pred] = []

        output[category][pred].append(obj)

        output[category][pred].append(obj)

    return output


class basicConvert(rowParse):
    neurolex_url = 'http://neurolex.org/wiki/'
    def __init__(self, graph, rows, xrefs):
        self.graph = graph
        self.ncbitaxon_ids = set()
        self.pato_ids = set()
        self.chebi_ids = set()
        self.drugbank_ids = set()
        self.t3db_ids = set()
        self.uni_ids = set()  # expect 735 from registry dump  # FIXME there are 804...
        self.biobank_ids = set()
        self.bad_ids = set()
        self.fbbt_ids = set()  # get these from the link
        self.bams_ids = set()
        self.pro_ids = set()
        self.failed_resolution = set()
        self.skipped = set()

        self.xrefs = xrefs
        self.actual_xref_prefixes = tuple()
        self.actual_xrefs = tuple()

        self.line = 0
        #self.cat_id_dict = {}
        self.pre_ref_dict = defaultdict(set)
        self.to_call = []
        self.fake_url_prefix = 'ILX:'
        eval_first = ['FBBT_Link', 'Categories', 'Id', 'SuperCategory']#, 'CAO_Id']
        super().__init__(rows, order=eval_first)
        [func(*args) for func, args in self.to_call]

    def _add_node(self, s, p, o): #Call for non Category/Id
        if o in self.cat_id_dict:
            o = self.cat_id_dict[o]
            self.graph.add_trip(s, p, o)
        elif type(o) is str and ':Category:' in o: # FIXME needs a way to identify putative objectProperties
            if (self._add_node, (s, p, o)) in self.to_call:
                self.graph.add_trip(s, p, o)
                self.failed_resolution.add(o)
                #print('Failed to resolve reference to', o)
            else:
                self.to_call.append((self._add_node, (s, p, o)))
        else:
            self.graph.add_trip(s, p, o)

    def _add_altid(self, value, xref=False):
        prefix = value.split(':')[0]
        test = prefix in self.graph.namespaces
        if value and self.graph.expand(value) != self.graph.expand(self.id_) if test else True:
            if xref or (value in self.actual_xrefs) or (prefix in self.actual_xref_prefixes):
                self._add_node(self.id_, 'oboInOwl:hasDbXref', value)
            else:
                self._add_node(self.id_, 'oboInOwl:hasAlternativeId', value)
        else:
            pass  # xref is id

    def _resolve(self, value, edge):  # TODO fixme hierarchy vs node...
        value = value.strip(':')
        print(value)
        if value in self.cat_id_dict:
            value = self.cat_id_dict[value]
            print('YAY', repr(value))
            # fixes for case where an object is never present as a subject
            if value == rdflib.URIRef('http://ontology.neuinfo.org/NIF/BiomaterialEntities/NIF-GrossAnatomy.owl#nlx_20558'):
                value = rdflib.URIRef('http://uri.neuinfo.org/nif/nifstd/nlx_20558')

            self.graph.add_trip(self.id_, edge, value)

        else:
            def func(obj, this=self.id_):
                self._add_node(this, edge, obj)

            self.pre_ref_dict[value].add(func)

    def _skip(self, value):
        self.skipped.add(value)
        raise self.SkipError

    def FBBT_Link(self, value):  # since the ask query is full a idiocy
        if value and value != 'FBBT Link':
            #print(value)
            value = value.rsplit('=',1)[1]
            self.fbbt_ids.add(value)
            self._skip(value)
        elif value == 'FBBT Link':
            raise self.SkipError  # first chance we have to skip redef lines

    def CAO_Id(self, value):  # need to capture, deprecate and redirect
        if value and value != 'CAO Id':
            self._add_node(self.id_, rdflib.OWL.deprecated, True)
            self._add_node(self.id_, 'oboInOwl:replacedBy', value.replace('_', ':'))  # FIXME nothing can resolve these... DERP
            #raise self.SkipError

    def Categories(self, value): # FIXME called Categories in neurolex_full.csv
        self.line += 1
        if ':Category:Resource:' in value or value == 'Categories':
            raise self.SkipError
        elif not value:
            raise BaseException('Category is empty, this should not be possible! Row = %s' % self.line) #there was a type on your version here, you had empyt instead of empty
        self.category = self.neurolex_url + value.replace(' ','_').strip(':')  # fix for unknown url type
        self._category = value.split(':',2)[-1].replace(' ','_')

    def Id(self, value):
        if not value:
           self.id_ = self.category
            # self.id_ = None

        if value in self.xrefs:
            self._skip(value)  # TODO

        else:
            if value.startswith('DB'):
                self.cat_id_dict[self.category] = value  # in case someone referenced it...  # TODO check for ontology ids as well...
                self.drugbank_ids.add(value)
                self._skip(value)
            elif value.startswith('T3D'):
                self.cat_id_dict[self.category] = value  # in case someone referenced it...
                self.t3db_ids.add(value)
                self._skip(value)
            elif value.startswith('JAX:') or value.startswith('FMAID:'):
                value = value.replace(' ','') # FIXME
            elif value.startswith('Taxonomy ID: '):
                value = 'NCBITaxon:' + value.strip('Taxonomy ID: ')
            elif value.startswith('NCBITaxon: '):
                value = value.replace(' ' ,'')
                self.cat_id_dict[self.category] = value  # in case someone referenced it...
                self.ncbitaxon_ids.add(value)
                self._skip(value)
            elif value.startswith('PATO'):
                value = value.replace(' ',':')
                self.cat_id_dict[self.category] = value  # in case someone referenced it...
                self.pato_ids.add(value)
                self._skip(value)
            elif value.startswith('CHEBI'):
                value = value.replace('_',':')
                self.cat_id_dict[self.category] = value  # in case someone referenced it...
                self.chebi_ids.add(value)
                self._skip(value)
            elif value.startswith('BAMS'):
                self.cat_id_dict[self.category] = value  # in case someone referenced it...
                self.bams_ids.add(value)
                #self._skip(value)  # need some of these for neurons
            elif value.startswith('PRO:'):
                self.cat_id_dict[self.category] = value  # in case someone referenced it...
                self.pro_ids.add(value)
                self._skip(value)

            # TODO there are MANY external fragments here :/

            if value in fragment_curie_dict:
                self.id_ = fragment_curie_dict[value]
                pref = self.id_.split(':')[0]
                #if value == 'nlx_143534,nifext_102':
                if ',' in value:
                    id_, altid = value.split(',')
                    a, b = id_.split('_')
                    c, d = altid.split('_')
                    self.id_ = a.upper() + ':' + b  # XXX dangerzone!
                    self._add_altid(c.upper() + ':' + d)
                if pref in PREFIXES:
                    self.graph.add_known_namespaces(pref)
                    exp = self.graph.expand(self.id_)
                    if exp in new_translation:
                        self.id_ = _mapping.namespace_manager.qname(new_translation[exp])
                if self.id_ == 'NLXONLY':
                    if 'nlx_' in value:
                        self.id_ = value.replace('nlx_', 'NLX:')
                    elif 'oen_' in value:
                        self.id_ = value.replace('oen_', 'NLXOEN:')
                    else:
                        self.id_ = 'NIFSTD:' + value
                else:
                    #self._skip(value)  # for the time being we don't want these in interlex XXX we do need these right now
                    prefix, fragment = self.id_.split(':')
                    if prefix not in self.graph.namespaces:
                        self.graph.namespaces[prefix] = rdflib.Namespace(PREFIXES[prefix])
                        self.graph.g.namespace_manager.bind(prefix, PREFIXES[prefix])
            elif value.startswith('http://'): # coming from category
                self.id_ = value
            else:
                self.bad_ids.add(value)
                self._skip(value)
                #raise self.SkipError('SKIPPING RECORD DUE TO wtf? %s' % value)

        self.cat_id_dict[self.category] = self.id_
        self.graph.add_class(self.id_)

        self.graph.g.add((self.graph.expand(self.id_), ilxtr.neurolexCategory, rdflib.URIRef(self.category)))
            
        #else:
         #   self.id_ = self.fake_url_prefix + value  # TODO need proper curie prefixes
          #  self.graph.add_node(self.id_, rdflib.RDF.type, rdflib.OWL.Class)
        #print(value)

        if self.category in self.pre_ref_dict:
            for func in self.pre_ref_dict[self.category]:
                func(self.id_)

        # doing this here because self._category defined before self.id_ exists
        #self._add_node(self.id_, 'ilx:neurolex_category', self._category)

    def Label(self, value):
        if value:
            self._add_node(self.id_, rdflib.RDFS.label, value)
        
    def SuperCategory(self, value):
        if not value:
            return 

        if value == 'University':  # NOPENOPENOPE
            self.uni_ids.add(self.id_)  # TODO may need to use this to update ID to SRC: ...
            self.graph.g.remove((self.graph.expand(self.id_), rdflib.RDF.type, rdflib.OWL.Class))
            self._skip(self.id_)  # TODO need to check this against scicrunch-registry.ttl hasDbXref
        elif value ==  'Biobank':  # further nope
            self.biobank_ids.add(self.id_)
            self.graph.g.remove((self.graph.expand(self.id_), rdflib.RDF.type, rdflib.OWL.Class))
            self._skip(self.id_)

        value = self.neurolex_url + 'Category:' + value  # fix for :Category: being an unknown prefix
        #if 'University' in value:
            #print(value)
        if value in self.cat_id_dict:
            super_id = self.cat_id_dict[value]
            self._add_node(self.id_, rdflib.RDFS.subClassOf, super_id)
        else:
            def func(super_id, this=self.id_):
                self._add_node(this, rdflib.RDFS.subClassOf, super_id)

            self.pre_ref_dict[value].add(func)

    def Definition(self, value):
        #print(value)
        self.graph.add_trip(self.id_, definition, value)

    def Synonym(self, value):  # XXX warning only OK on the reduced subset
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
                        self._add_node(self.id_, 'NIFRID:synonym', half)

                    half = None

                v = v.strip()
                if v:
                    self._add_node(self.id_, 'NIFRID:synonym', v)

    def Has_part(self, value):
        if value:
            print(self.id_, 'has part', value)

    def Is_part_of(self, value):
        if value:
            for value in value.split(','):
                value = self.neurolex_url + value.replace(' ','_')  # fix for :Category: being an unknown prefix
                #print(self.id_, 'is part of', value)
                if value in self.cat_id_dict:
                    poid = self.cat_id_dict[value]
                    self.graph.add_hierarchy(poid, 'partOf:', self.id_)  # flipped as usual :/
                    #self._add_node(self.id_, 'ilx:partOf', poid)
                else:
                    def func(poid, this=self.id_):
                        #self._add_node(this, 'ilx:partOf', poid)
                        #self.graph.add_hierarchy(this, 'ilx:partOf', poid)
                        self.graph.add_hierarchy(poid, 'partOf:', this)  # flipped as usual :/

                    self.pre_ref_dict[value].add(func)


class convertCurated(basicConvert):
    def PMID(self, value):
        #print(value)
        pass

    def DefiningCitation(self, value):
        #print(value)
        pass

    def Species_taxa(self, value):  # Species_taxa in neuro_data_curated.csv
        if value:
            #value = self.neurolex_url + value[1:]  # fix for :Category: being an unknown prefix
            #value = value[1:]
            pass
        else:
            return

        pheno_edge = 'ilxtr:hasTaxonRank'
        self._resolve(value, pheno_edge)

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
            values = value.split(',')
            for value in values:
                self._resolve(value, hasRole)

    def Abbrev(self, value):
        #print(value)
        pass

    def Fasciculates_with(self, value): 
        #print(value)
        pass
    
    def CellSomaShape(self, value): 
        if value:
            #print(value)
            pass

        parent_phenotype = 'ilxtr:SomaMorphologicalPhenotype'

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
        

        to_skip = {}
        #to_skip = {'Category:Multipolar', 'Category:Fusiform', 'Category:Pyramidal', 'Category:Spherical', 'Category:Oval', 'Category:bipolar', 'Category:Granule', 'Category:Mitral', 'Oval', 'Fusiform', 'Category:Round', ''}

        if value in to_skip:
            pass
        else:
            self._resolve(value, 'http://CellSomaShape.org')
            
    def CellSomaSize(self, value): 
        if value:
            #print(value)
            pass

        parent_phenotype = 'ilxtr:SomaMorphologicalPhenotype'

    def FBbt_Id(self, value):
        if value:
            pass
            #print('FBbt id found', value, 'skipping!')

    def Located_in(self, value): 
        if value:
            #print(value)
            pass
        
        pheno_edge = 'ilxtr:hasSomaLocatedIn'
        self._resolve(value, pheno_edge)

    def SpineDensityOnDendrites(self, value): 
        if value:
            #print(value)
            pass
        
        parent_phenotype = 'ilxtr:DendriteMorphologicalPhenotype'
        
    def DendriteLocation(self, value): 
        if value:
            #print(value)
            pass

        pheno_edge = 'ilxtr:hasDendriteLocatedIn'

        to_skip = {}
        #to_skip = {':Category:Dendrites spread from the cell body in all directions. Dendrites are smooth where they lie in the deep layer but where the dendrites cross the pyramidal (fusiform) cell layer into the molecular layer', ':Category:They become spiny. Functionally it has been demonstrated that they receive not only acoustic input in the deep layer but also proprioceptive input through the molecular layer.', ':Category:Brush of dendrites is short and lies near the cell body', ':Category:Dendrites lie parallel to auditory nerve fibers in the ventral cochlear nucleus', ':Category:Receptive field in the periphery', ':Category:Two primary dendrites', ':Category:One that projects laterally towards the roots of the VIIIth cranial nerve and is named the lateral dendrite', ':Category:And another which projects rostrally and ventrally and is called the ventral dendrite.', ':Category:Basal dendrites in neocortical layers 5 and 6;apical dendrites across neocortical layers 5 to 1.', ':Category:Basal dendrites branch within neocortical layers 5 and 6;apical dendrite extends across neocortical layers 5-1.', ':Category:Basal dendrites in Neocortex layer 5', ':Category:Apical dendrites across neocortical layers 5-1.', ':Category:Mostly neocortical layer 4', ':Category:Basal dendrites will be in the same layer as the soma and/or the subjacent layer. Apical dendrites rise toward the pia and into layer 1. For layer 6 neurons', ':Category:However,:Category:The apical dendrite will often not continue beyond layer 4/lower layer 3.', ':Category:Arborization within the glomerular neuropil and external plexiform layer', ':Category:Dendrties arborize in the external plexiform layer where they contact the secondary/lateral dendrites of mitral cells via reciprocal dendrodendritic synapses. The basal dendrite remains restricted to the granule cell layer.', ':Category:Proximal', ':Category:Intermediate', ':Category:Distal', ''}
        if value in to_skip:
            pass
        else:
            self._resolve(value, pheno_edge)

    def BranchingMetrics(self, value): 
        if value:
            #print(value)
            pass

        parent_phenotype = 'ilxtr:DendriteMorphologicalPhenotype'

        to_skip = {'other', 'this is a columnar cell without a true dendrite', ''}
        if value in to_skip:
            pass
        else:
            self._resolve(value, 'http://BranchingMetrics.org')

    def AxonMyelination(self, value): 
        if value:
            #print(value)
            pass
        
        parent_phenotype = 'ilxtr:AxonMorphologicalPhenotype'

    def AxonProjectionLaterality(self, value): 
        if value:
            #print(value)
            pass

        pheno_edge = 'ilxtr:hasProjectionPhenotype'

    def LocationOfAxonArborization(self, value): 
        
        #print(value)

        pheno_edge = 'ilxtr:hasAxonLocatedIn'

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

        #to_skip = {':Category:NA', ':Category:None', ':Category:No axon', ':Category:Anaxonic - no axon', ':Category:This is an axonal cell; it lacks an axon', ' : axon collaterals to other pyramidal cells. Mouse: no axon collaterals. Exit through the dorsal and intermediate acoustic striae to terminate in the contralateral inferior colliculus', ':Category:Axon descends in the medial lateral fasciculus and projects to caudal brainstem and all spinal segments', ':Category:For supragranular neurons', ':Category:This is almost exclusively cortical (except for some corticostriatal projections from layer 3). Infragranular neurons can project subcortically (LGN', ':Category:Superior colliculus', ':Category:Claustrum', ':Category:Amygdala) but also cortically', ':Category:Ipsi- or contralateral.', ':Category:Cell groups embedded in the lemniscus lateralis', ':Category:And the nucleus mesencephalicus lateralis', ':Category:Pars dorsalis in the midbrain', ':Category:Synaptic output is from cell body', 'oriens', ''}
        to_skip = {}
        if value in to_skip:
            pass
        else:
            for v in value.split(','):
                v.strip()
                self._resolve(v, pheno_edge)
        
    def LocationOfLocalAxonArborization(self, value): 
        #if value:
            #for v in value.split(','):
             #   v.strip()
              #  if v:
               #     self._add_node(self.id_, 'http://LocationOfLocalAxonArborization', v)

        pheno_edge = 'ilxtr:hasAxonLocatedIn'  # FIXME
        

        NONE = 'None'
        CAP = ':Category:Olfactory cortex layer II'
        fixes = {
            ':Category:NA':NONE,
            ':Category:No axon':NONE,  # disjoint with hasAxon... ??
            ':Category:None':NONE,
            ':Category:This is an anaxonal cell; it lacks an axon':NONE,
            ':Category:No local arborization':NONE,
            ':Category:OLFACTORY CORTEX LAYER II':CAP,
        } 
        if value in fixes:
            value = fixes[value]

        to_skip = {}
        #to_skip = {':Category:NA', ':Category:No axon', ':Category:None', ':Category:This is an anaxonal cell; it lacks an axon', ':Category:No local arborization', ':Category:Few', ':Category:Lamina xxx', ':Category:Within extraglomerular regions', ':Category:Within the same granule cell domain as the cell body', ':Category:In some species (mice) but not in others (cats) octopus cells have local collaterals in the octopus cell area and contact granule cells in the granule cell lamina.', ':Category:For layer 6: layer 6 and 4 (J.S. Lund', ':Category:In primate and see A. Thomson for rodent); for layer 5: largely layer 5 but can extend to layer 3; for layer 3', ':Category:Largely layer 3', ':Category:But can extend to layer 5; layer 2', ':Category:Layer 2', ':Category:But can involve other layers.', ':Category:Synaptic output is from the cell body', ':Category:Pyramidal Cells', ':Category:Giant cells', ':Category:Cartwheel cells', ':Category:OLFACTORY CORTEX LAYER II', ''}
        if value in to_skip:
            pass
        else:
            for v in value.split(','):
                v.strip()
                if v:
                    self._resolve(v, pheno_edge)

    def OriginOfAxon(self, value): 
        pheno_edge = 'ilxtr:hasAxonOrigin'

    def Neurotransmitter(self, value):
        if value:
            pass

        pheno_edge = 'ilxtr:hasNeurotransmitterPhenotype'

        to_skip = {':Category:Likely glutamate', 'Excitatiry neurotransmitter', ':Category:Unknown', ':Category:Not known', ''}
        if value in to_skip:
            pass
        else:
            values = value.split(',')
            for value in values:
                self._resolve(value, pheno_edge)

    def NeurotransmitterReceptors(self, value): 
        if value:
            pass

        pheno_edge = 'ilxtr:hasMolecularPhenotype'
        
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
            values  = value.split(',')
            for value in values:
                if value in fixes:
                    value = fixes[value]
                self._resolve(value, pheno_edge)

    def MolecularConstituents(self, value): 
        if value:
            #print(value)
            pass

        pheno_edge = 'ilxtr:hasMolecularPhenotype'

        to_skip = {':Category:?', ':Category:Unknown', ''}
        if value in to_skip:
            pass
        else:
            values = value.split(',')
            for value in values:
                self._resolve(value, pheno_edge)

    def Curator_Notes(self, value): 
        #print(value)
        pass

    def Phenotypes(self, value): 
        #print(value)
        
        basket = "ilxtr:BasketPhenotype"
        Lbasket = "ilxtr:LargeBasketPhenotype"
        Nbasket = "ilxtr:NestBasketPhenotype"
        Sbasket = "ilxtr:SmallBasketPhenotype"
        bitufted = "ilxtr:BituftedPhenotype"
        bipolar = "ilxtr:BipolarPhenotype"
        chandelier = "ilxtr:ChandelierPhenotype"
        DBouquet = "ilxtr:DoubleBouquetPhenotype"
        Martinotti = "ilxtr:MartinottiPhenotype"
        neurogliaform = "ilxtr:NeurogliaformPhenotype"
        pyramidal = "ilxtr:PyramidalPhenotype"
        spiking = "ilxtr:SpikingPhenotype"
        somat = 'PR:000015665'

        fixes = {
            'ilx:has_morphological_phenotype basket':basket,
            'ilx:has_morphological_phenotype bipolar':bipolar,
            'ilx:has_morphological_phenotype chandelier':chandelier,
            'ilx:has_morphological_phenotype double bouquet':DBouquet,
            'ilx:has_morphological_phenotype Martinotti':Martinotti,
            'ilx:has_morphological_phenotype neurogliaform':neurogliaform,
            'ilx:has_morphological_phenotype pyramidal':pyramidal,
            'ilx:has_expression_phenotype somatostatin':somat,

            
                }
        pheno_edge = 'ilxtr:hasPhenotype'

        #to_skip = {'ilx:has_morphological_phenotype basket', 'ilx:has_morphological_phenotype bipolar', 'ilx:has_morphological_phenotype chandelier', 'ilx:has_morphological_phenotype double bouquet', 'ilx:has_morphological_phenotype Martinotti', 'ilx:has_morphological_phenotype neurogliaform', 'ilx:has_morphological_phenotype pyramidal', ''}
        #if value in to_skip:
            #pass
        #else:
        values = [_.strip() for _ in value.split(',')]
        for value in values:
            if not value:
                continue
            #put_the_value_in_the_graph(value)
            #self.graph.add_node(self.category, 'http://Phenotypes.org', value)  # TODO
            #if value in fixes:
                #value = fixes[value]
            #print(value)
            pred, val = value.split(' ', 1)
            if value in fixes:
                val = fixes[value]
            pred = predfix(pred)
            if 'UBERON' in val:
                val = self.graph.expand(val)
            #print(pred, val)
            self._add_node(self.id_, pred, val)
            #self._resolve(value, pheno_edge)
            pass

    def Notes(self, value): 
        pass

    def ModifiedDate(self, value):
        # in theory we can use this to skip over records we don't actually need because no one has changed them since they were imported from the ontology
        pass


class altIds(basicConvert):
    cat_id_dict = {}
    special_cases = 'IAO:0000025', 'NLXWIKI:Birnlex_1816', 'NLXWIKI:COGPO:00124', 'NLXWIKI:OBI:0000832', 'NIFGA:nlx_20558'
    actual_xrefs = ('REO:0000002',  # antibody reagent, not antibody
                    'ModelDB:65417',  # models matching, not actual term page
                   )
    actual_xref_prefixes = 'ModelDB', 'NITRC', 'BAMS'
    def Id(self, value):  # special cases
        super().Id(value)
        if self.id_ in self.special_cases:
            self.graph.g.remove((self.graph.expand(self.id_), rdflib.RDF.type, rdflib.OWL.Class))
            if self.id_ in self.special_cases[1:]:  # XXX hack
                if self.id_ == 'NLXWIKI:Birnlex_1816':
                    self.id_ = 'BIRNLEX:1816'
                elif self.id_ == 'NLXWIKI:COGPO:00124':
                    self.id_ = 'COGPO1:00124'
                elif self.id_ == 'NLXWIKI:OBI:0000832':
                    self.id_ = 'OBI:0000832'
                elif self.id_ == 'NIFGA:nlx_20558':
                    self.id_ = 'NLX:20558'
                    self._add_altid('NLXANAT:1005032')  # one of the ones lost in transition so grab it while we're at it
                self.graph.g.add((self.graph.expand(self.id_), rdflib.RDF.type, rdflib.OWL.Class))
            else:
                raise self.SkipError
        

    def SuperCategory(self, value):  # actually need this to skip unis and biobanks
        return
        if not value:
            return 

        if value == 'University':  # NOPENOPENOPE
            self.uni_ids.add(self.id_)  # TODO may need to use this to update ID to SRC: ...
            self.graph.g.remove((self.graph.expand(self.id_), rdflib.RDF.type, rdflib.OWL.Class))
            self._skip(self.id_)  # TODO need to check this against scicrunch-registry.ttl hasDbXref
        elif value ==  'Biobank':  # further nope
            self.biobank_ids.add(self.id_)
            self.graph.g.remove((self.graph.expand(self.id_), rdflib.RDF.type, rdflib.OWL.Class))
            self._skip(self.id_)

    def Label(self, value):
        pass
    def Definition(self, value):
        pass
    def Synonym(self, value):
        pass
    def Has_part(self, value):
        pass
    def Is_part_of(self, value):
        pass

    def BamsID(self, value):  # XXX NOTE this column is garbage, the underlying fields were doubles that got rendered with a comma by semantic media wiki on export *screaming* use BamsLink instead
        pass

    def BamsLink(self, value):
        if value:
            for v in value.split(','):
                _, id_ = v.split('aidi=')
                self._add_altid('BAMS:' + id_)

    def CAO_Id(self, value):
        if value:
            if value.startswith('COGPO_'):  # DERP
                return self.Xref(value)
            self._add_altid(value.replace('_', ':'))

    def DICOMID(self, value):
        if ' ' in value:
            value = value.replace(' ', '')
        if 'DICOMID' in value:
            _, n = value.split(':')
            value = 'DICOM:' + n

        self._add_altid(value)

    def FBbt_Id(self, value):
        if value:
            self._add_altid('FBBT:' + value)

    def GbifID(self, value):
        if value:
            self._add_altid('GBIF:' + value)

    def ItisID(self, value):
        if value:
            self._add_altid('ITISTSN:' + value)

    def NeuronamesID(self, value):
        if value:
            if value == '228':
                self._add_altid('NeuroNames:854', xref=True)  # XXX ERRATA
            elif value == '229':
                self._add_altid('NeuroNames:3232', xref=True)  # XXX ERRATA

    def Nifid(self, value):
        self._add_altid(value)

    def TaxID(self, value):
        if value:
            self._add_altid('NCBITaxon:' + value)

    @staticmethod
    def _special_cases(v):
        # exact matches
        if v == 'Biological imaging ontology FBbi:00000115':
            v = 'FBbi:00000115'
        elif v == 'BioPAX Interaction':
            v = 'http://www.biopax.org/release/biopax-level3.owl#Interaction'
        elif v == 'Radlex RID5649':
            v = 'RadLex:RID5649'
        elif v == 'Category:Sensory reception role':  # fixed the has role issue in interlex already
            v = 'BAMSN:BAMSC974'
        elif v == 'TAXRANK:0000000':
            v = 'NCBITaxon:taxonomic_rank'
        elif v == 'C537111 (MeSH ID)':
            v = 'MESH:C537111'
        elif v == 'MESH ID:http://purl.bioontology.org/ontology/MSH/D001930':
            v = 'MESH:D001930'
        # prefixes
        elif v.startswith('Nlx'):
            v = 'n' + v[1:]
        elif v.startswith('sao-'):
            v = 'SAO:' + v[4:]
        elif v.startswith('sao'):
            v = 'SAO:' + v[3:]
        elif v.startswith('FMAID:'):
            v = 'FMA:' + v[6:]
        elif v.startswith('PAR:1279'):
            v = v.split(' ', 1)[0]
        elif v.startswith('BAMSC'):
            v = 'BAMSN:' + v
        elif v.startswith('BAMSID:'):
            v = 'BAMS:' + v.split(':')[-1]
        elif v.startswith('BAMSID '):
            v = 'BAMS:' + v.split(' ')[-1]
        elif v.startswith('Modeldb'):
            v = v.replace('Modeldb', 'ModelDB')
        elif v.startswith('COGPO_'):
            v = 'COGPO1:' + v.split('_')[-1]
        elif v.startswith('EFO_'):
            v = v.split(' ')[0]
            v = 'EFO:' + v.split('_')[-1]
        elif v.startswith('SBO:'):
            v = v.split(' ')[0]
        elif v.startswith('MeSH'):
            v = v.replace('MeSH', 'MESH')  # follow uberon
        elif any(v.startswith(_) for _ in ('C', 'D', 'Q')) and v[1].isdigit():
            v = 'MESH:' + v
        elif 'FBbi#FBbi_' in v:
            v = 'FBbi:' + v.split('_')[-1]
        return v

    def Xref(self, value):
        if value:
            for v in value.split(','):

                if v.startswith('DICOM'):
                    return self.DICOMID(value)

                v = self._special_cases(v)

                if v == 'http://sig.biostr.washington.edu/fma3.0#Inner_nuclear_layer_of_retina':
                    self._add_altid('FMA:58686')
                elif v == 'http://sig.biostr.washington.edu/fma3.0#Inner_plexiform_layer_of_retina':
                    self._add_altid('FMA:58704')
                elif v == 'http://sig.biostr.washington.edu/fma3.0#Ganglionic_layer_of_retina':
                    self._add_altid('FMA:58687')

                if v.startswith('NITRC_'):
                    v = v.replace('NITRC_', 'NITRC:')
                elif v.startswith('http'):
                    pass
                elif v in fragment_curie_dict:
                    exp = self.graph.expand(fragment_curie_dict[v])
                    if exp in new_translation:
                        v = _mapping.namespace_manager.qname(new_translation[exp])
                elif '_' in v and ':' not in v:
                    p, nums = v.rsplit('_', 1)
                    p = p.replace('_', '').upper()
                    if p == 'OEN':
                        p = 'NLXOEN'
                    _v = p + ':' + nums
                    if p in PREFIXES:
                        v = _v
                    elif p in self.graph.namespaces:
                        v = _v
                    else:
                        test = _mappingg.expand(_v)
                        if test in new_translation_values:
                            v = test
                self._add_altid(v.strip())

    def _row_post(self):
        s = self.graph.expand(self.id_)
        pos = list(self.graph.g.predicate_objects(s))
        if len(pos) <= 1:
            for p, o in pos:
                self.graph.g.remove((s, p, o))
        super()._row_post()


def predfix(pred):
    asdf = pred.split('_')
    tail = [_.capitalize() for _ in asdf[1:]]
    out = ''.join(asdf[:1] + tail)
    out = out.replace('ilx:', 'ilxtr:')
    return out

def main():  # xrefs
    gps = {
        'ITISTSN':'http://www.itis.gov/servlet/SingleRpt/SingleRpt?search_topic=TSN&search_value=',
        'NITRC':'http://www.nitrc.org/search/?type_of_search=group&cat=',
        'GBIF':'http://www.gbif.org/species/',
        'REO':'http://purl.obolibrary.org/obo/REO_',
        'NEMO':'http://purl.bioontology.org/NEMO/ontology/NEMO.owl#NEMO_',
        #'OMICS':'http://omicstools.com/id/',  # they seoed themselves >_< and this is not real
        'DICOM':'http://uri.interlex.org/dicom/uris/terms/',
        'NLXOEN':'http://uri.neuinfo.org/nif/nifstd/oen_',
        'ModelDB':'https://senselab.med.yale.edu/modeldb/ModelList.cshtml?id=',
        'BAMS':'http://brancusi.usc.edu/bkms/brain/show-braing2.php?aidi=',  # FIXME dead
        'NeuroNames':'http://braininfo.rprc.washington.edu/centraldirectory.aspx?ID=',
        'NeuroNamesHier':'http://braininfo.rprc.washington.edu/centraldirectory.aspx?type=h&ID=',  # XXX this is what NIFSTD has listed, some of these are incorrect eg on BIRNLEX:1099 and BIRNLEX:1111
        'MA':'http://purl.obolibrary.org/obo/MA_',
        'PAR':'http://uri.interlex.org/fakeobo/uris/obo/PAR_',  # http://www.psidev.info/psi-par#minimum_requirements tons of dead links except for this one http://psidev.cvs.sourceforge.net/viewvc/psidev/psi/mi/controlledVocab/proteomeBinder/psi-par.obo # cvs -z3 -d:pserver:anonymous@psidev.cvs.sourceforge.net:/cvsroot/psidev co -P psi
        #'SBO':'http://biomodels.net/SBO/SBO_',  # FIXME these do not resolve despite being used in the ontology source...
        'SBO':'http://www.ebi.ac.uk/sbo/main/SBO:',  # these resolve... sigh obo...
        'BAMSN':'https://bams1.org/bkms/BAMS.owl#',  # FIXME dead source is https://bams1.org/public/files/neuron-ontology.xml I have a copy. using the BAMSN namespace so that we don't klobber the id with the colon sigh
        'MESH':'https://meshb.nlm.nih.gov/record/ui?ui=',  # for now use the browser as the landing page, not sure 
        'RadLex':'http://www.radlex.org/RID/',  # match uberon
        'FBbi':'http://purl.obolibrary.org/obo/FBbi_',
          }
    # FIXME REO_0000002 is NOT conceptually equivalent to BIRNLEX:2110
    PREFIXES_ = {'OBO':'http://whatisthis.org/', **gps, 
                **makePrefixes('oboInOwl', 'NLXWIKI', 'NLX', 'NCBITaxon', 'CAO', 'FMA', 'EFO', 'OBI', 'COGPO1', 'CHEBI')}
    graph = createOntology('nlx-xrefs',
                           path='/',   # FIXME trailing slash...
                           local_base=os.path.expanduser('~/git/nlxeol'),
                           prefixes=PREFIXES_,)
    with open('neurolex_full.csv', 'rt') as f:
        rows = [r for r in csv.reader(f)]

    scr_graph = get_scr()
    xrefs = set([s_o[1].toPython()
                 for s_o in scr_graph.subject_objects(rdflib.term.URIRef('http://www.geneontology.org/formats/oboInOwl#hasDbXref'))])
    asdf = altIds(graph, [r for r in rows if 'Resource:' not in r[0]], xrefs)
    pyontutils.utils.PREFIXES.update(gps)
    ng = cull_prefixes(graph.g, prefixes=pyontutils.utils.PREFIXES)
    ng.filename = graph.filename
    ng.write()
    #embed()

def neurons_main():  # old
    from docopt import docopt
    args = docopt(__doc__)

    # TODO extracly only NLX only with superclasses for fariba
    # FIXME there is an off by 1 error
    #nlxdb = get_nlxdb()

    #scr_graph = get_scr()
    #existing_xrefs = set([s_o[1].toPython() for s_o in scr_graph.subject_objects(rdflib.term.URIRef('http://www.geneontology.org/formats/oboInOwl#hasDbXref'))])

    ONT_PATH = 'http://github.com/tgbugs/nlxeol/'
    #filename = 'neurolex_basic'
    filename = 'neuron_data_curated'
    PREFIXES = {'to':'do',
                'OBO':'http://whatisthis.org/',
                'NLXWIKI':'http://neurolex.org/wiki/',
                #'ILX':'http://uri.interlex.org/base/ilx_',
                #'ilx':'http://uri.interlex.org/base/',
                'owl':'http://www.w3.org/2002/07/owl#',
                'skos':'http://www.w3.org/2004/02/skos/core#',
                'oboInOwl':'http://www.geneontology.org/formats/oboInOwl#',
                'PRO':'http://purl.obolibrary.org/obo/PR_',  # sigh
                #'PATO':'http://purl.obolibrary.org/obo/PATO_',

                }
    PREFIXES.update(makePrefixes('UBERON', 'CHEBI', 'PR', 'PATO', 'NIFGA', 'NIFMOL', 'NIFSUB',
                                 'NLX', 'NLXOEN', 'hasRole', 'ilxtr', 'BIRNLEX', 'NIFRID', 'NIFSTD'))

    ontid = ONT_PATH + filename + '.ttl'
    new_graph = makeGraph(filename, PREFIXES)
    new_graph.add_ont(ontid,
                      'Conversion of the neurolex database to ttl',
                      'Neurolex dump',
                      'This file is automatically generated from nlxeol/process_csv.py',
                      TODAY)
 
    with open('neurolex_full.csv', 'rt') as f:
        rows0 = [r for r in csv.reader(f)]
    wat = {}
    class catid(rowParse):
        graph = makeGraph('asdf', PREFIXES)
        xrefs = {}
        actual_xrefs = tuple()
        actual_xref_prefixes = tuple()
        pre_ref_dict = {}
        t3db_ids = set()
        cat_id_dict = {}
        skipped = set()
        pato_ids = set()
        bad_ids = set()
        chebi_ids = set()
        drugbank_ids = set()
        pro_ids = set()
        bams_ids = set()
        ncbitaxon_ids = set()
        _add_altid = altIds._add_altid
        _add_node = basicConvert._add_node
        def _skip(self, value):
            self.skipped.add(value)
            raise self.SkipError

        def Categories(self, value):
            self.category = value.strip(':')
            
        def Id(self, value):
            return basicConvert.Id(self, value)

        #def Id(self, value):
            #if value:
                #self.id_ = 'NLXWIKI:' + value
            #else:
                #self.id_ = None  # how?
        def _row_post(self):
            if self.id_:
                wat[self.category] = self.id_
            else:
                print('missing id for', self.cat)
    asdf = catid(rows0)
    #embed()
    wat.update({k:asdf.graph.expand(v) if ':' in v else v for k,v in asdf.cat_id_dict.items()})

    with open('neuron_data_curated.csv', 'rt') as f:
        rows = [r for r in csv.reader(f)]
    new_rows = [list(r) for r in zip(*[c for c in zip(*rows) if any([r for r in c if r != c[0]])])]
    no_data_cols = set(rows[0]) - set(new_rows[0])
    print(no_data_cols)

    #header[header.index('Phenotypes:_ilx:has_location_phenotype')] = 'Phenotypes'
    # convert the header names so that ' ' is replaced with '_'
    #state = basicConvert(new_graph, new_rows, existing_xrefs)
    #convertCurated.cat_id_dict = nlxmapping

    #from pyontutils.core import OntTerm
    #from pyontutils.utils import Async, deferred

    #def noDep(k, uri):
        #term = OntTerm(uri)
        #if not term.validated:
            #return term
        #else: # TODO
            #return uri


    #watNoDep = {k:v for k, v in Async()(deferred(noDep)(k, v) for k, v in wat.items())}  # TODO (k, deferred(v))??
    convertCurated.cat_id_dict = wat #watNoDep
    state = convertCurated(new_graph, new_rows, set())
    new_graph.del_namespace('PRO')
    new_graph.write()
    if args['--debug']:
        embed()
    return

    #_ = [print(i) for i in sorted([datetime.strptime(t, '%d %B %Y') for _ in state._set_ModifiedDate for t in _.split(',') if _])]
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

    #return

    new_graph.write(convert=True)

    embed()

if __name__ == '__main__':
    neurons_main()
