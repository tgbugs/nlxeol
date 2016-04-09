#!/usr/bin/env python3
"""
    Sync the scicrunch registry to a ttl
    file for loading into scigraph for autocomplete.
"""
#FIXME: make nlx_only work
from heatmaps.scigraph_client import Graph, Vocabulary
import json
import csv
from collected import data #imports data from a previous py file
from collections import defaultdict, namedtuple
import os
import rdflib
from datetime import date
from IPython import embed
import requests
from sqlalchemy import create_engine, inspect
from rdflib import Namespace,URIRef
from Prefix_ID_Cat_List import Cat_to_preID

graph = Graph()
ns=Namespace
cheatList = []

values = [] #clumped total info of each element as a list of lists
pref = defaultdict(list)
temp = defaultdict(list)
record=[]
neighborList = []

#FIXME supercategory is element num 7
with open('Neurolex_Scigraph.json') as data_file:#loads in merged file with the keys as numbers
    js = json.load(data_file)

keys = tuple(js)
prefix = tuple(data)

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

PREFIXES = {
            'obo_annot':'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#',
            'owl':'http://www.w3.org/2002/07/owl#',
            #'rdfs':'rdfs',
            'rdf':'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
            'rdfs':'http://www.w3.org/2000/01/rdf-schema#',
            #'': 'http://uri.neuinfo.org/nif/nifstd/',
            'NIFCELL': 'http://ontology.neuinfo.org/NIF/BiomaterialEntities/NIF-Cell.owl#',
            '':'http://ontology.neuinfo.org/NIF/BiomaterialEntities/NIF-Cell.owl#',
            #: 'http://ontology.neuinfo.org/NIF/BiomaterialEntities/NIF-Cell.owl#',
            'OIO': 'http://www.geneontology.org/formats/oboInOwl#',
            'UO': 'http://purl.obolibrary.org/obo/UO_',
            'OBOANN': 'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#',
            'NIFMOLINF': 'http://ontology.neuinfo.org/NIF/BiomaterialEntities/NIF-Molecule-Role-Inferred.owl#',
            'BFO': 'http://purl.obolibrary.org/obo/BFO_',
            'QUALBB': 'http://ontology.neuinfo.org/NIF/Backend/quality_bfo_bridge.owl#',
            'nlx_only': 'http://uri.neuinfo.org/nif/nifstd/',
            'NEMO': 'http://purl.bioontology.org/NEMO/ontology/NEMO.owl#NEMO_',
            'NIFCHEM': 'http://ontology.neuinfo.org/NIF/BiomaterialEntities/NIF-Chemical.owl#',
            'NIFFUN': 'http://ontology.neuinfo.org/NIF/Function/NIF-Function.owl#',
            'EFO': 'http://www.ebi.ac.uk/efo/EFO_',
            'BIRNOBO': 'http://ontology.neuinfo.org/NIF/Backend/BIRNLex-OBO-UBO.owl#',
            'OBO': 'http://purl.obolibrary.org/obo/',
            'SCR': 'http://scicrunch.org/resolver/SCR_',
            'NIFANN': 'http://ontology.neuinfo.org/NIF/BiomaterialEntities/NIF-Annotation-Standard.owl#',
            'NIFMOLROLE': 'http://ontology.neuinfo.org/NIF/BiomaterialEntities/NIF-Molecule-Role-Bridge.owl#',
            'NIFGOCC': 'http://ontology.neuinfo.org/NIF/BiomaterialEntities/NIF-GO-CC-Bridge.owl#',
            'NIFNEURMOR': 'http://ontology.neuinfo.org/NIF/BiomaterialEntities/NIF-Neuron-Morphology-Bridge.owl#',
            'PATO3': 'http://purl.org/obo/owl/PATO#PATO_',
            'NIFRES': 'http://ontology.neuinfo.org/NIF/DigitalEntities/NIF-Resource.owl#',
            'NIFNCBI': 'http://ontology.neuinfo.org/NIF/BiomaterialEntities/NIF-NCBITax-Bridge.owl#',
            'PATO2': 'http://purl.obolibrary.org/obo/PATO#PATO_',
            'NIFSCID': 'http://ontology.neuinfo.org/NIF/DigitalEntities/NIF-Scientific-Discipline.owl#',
            'GO': 'http://purl.obolibrary.org/obo/GO_',
            'UBERON': 'http://purl.obolibrary.org/obo/UBERON_',
            'NIFUNCL': 'http://ontology.neuinfo.org/NIF/BiomaterialEntities/NIF-Unclassified.owl#',
            'NIFNEURCIR': 'http://ontology.neuinfo.org/NIF/BiomaterialEntities/NIF-Neuron-Circuit-Role-Bridge.owl#',
            'ILX': 'http://uri.interlex.org/base/ilx_',
            'SAOCORE': 'http://ontology.neuinfo.org/NIF/BiomaterialEntities/SAO-CORE_properties.owl#',
            'MBA': 'http://api.brain-map.org/api/v2/data/Structure/',
            'BFO1': 'http://www.ifomis.org/bfo/1.1',
            'OLD_SO': 'http://purl.obolibrary.org/obo/SO#SO_',
            'NIFGA': 'http://ontology.neuinfo.org/NIF/BiomaterialEntities/NIF-GrossAnatomy.owl#',
            'NIFGG': 'http://ontology.neuinfo.org/NIF/DigitalEntities/NIF-Government-Granting-Agency.owl#',
            'DOID': 'http://purl.obolibrary.org/obo/DOID_',
            'SIO': 'http://semanticscience.org/resource/SIO_',
            'ERO': 'http://purl.obolibrary.org/obo/ERO_', 'BIRNOBI': 'http://ontology.neuinfo.org/NIF/Backend/BIRNLex-OBI-proxy.owl#',
            'NIFNEURBR': 'http://ontology.neuinfo.org/NIF/BiomaterialEntities/NIF-Neuron-BrainRegion-Bridge.owl#',
            'NIFSUB': 'http://ontology.neuinfo.org/NIF/BiomaterialEntities/NIF-Subcellular.owl#',
            'NEMOANN': 'http://purl.bioontology.org/NEMO/ontology/NEMO_annotation_properties.owl',
            'PR': 'http://purl.obolibrary.org/obo/PR_',
            'HP': 'http://purl.obolibrary.org/obo/HP_',
            'NIFERO': 'http://ontology.neuinfo.org/NIF/BiomaterialEntities/NIF-Eagle-I-Bridge.owl#',
            'BIRNANN': 'http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#',
            'NIFQUAL': 'http://ontology.neuinfo.org/NIF/Backend/NIF-Quality.owl#',
            'PATO': 'http://purl.obolibrary.org/obo/PATO_', 'OLD_CHEBI': 'http://purl.obolibrary.org/obo/chebi.owl#CHEBI_',
            'CL': 'http://purl.obolibrary.org/obo/CL_', 'NIFBE': 'http://ontology.neuinfo.org/NIF/Backend/nif_backend.owl#',
            'IAO': 'http://purl.obolibrary.org/obo/IAO_',
            'NIFMOL': 'http://ontology.neuinfo.org/NIF/BiomaterialEntities/NIF-Molecule.owl#',
            'COGPO': 'http://www.cogpo.org/ontologies/COGPO_',
            'NIFNCBISLIM': 'http://ontology.neuinfo.org/NIF/NIF-NCBITaxonomy-Slim.owl#',
            'FMA': 'http://purl.org/sig/ont/fma/fma', 'COGAT': 'http://www.cognitiveatlas.org/ontology/cogat.owl#',
            'PW': 'http://purl.obolibrary.org/obo/PW_',
            'NIFNEURNT': 'http://ontology.neuinfo.org/NIF/BiomaterialEntities/NIF-Neuron-NT-Bridge.owl#',
            'RO': 'http://purl.obolibrary.org/obo/RO_',
            'NIFINV': 'http://ontology.neuinfo.org/NIF/DigitalEntities/NIF-Investigation.owl#',
            'NIFDYS': 'http://ontology.neuinfo.org/NIF/Dysfunction/NIF-Dysfunction.owl#',
            'NCBITaxon': 'http://purl.obolibrary.org/obo/NCBITaxon_', 'SO': 'http://purl.obolibrary.org/obo/SO_',
            'NIFNEURON': 'http://ontology.neuinfo.org/NIF/BiomaterialEntities/NIF_Neuron_MolecularConstituent_Bridge.owl#',
            'CLO': 'http://purl.obolibrary.org/obo/CLO_', 'NIFORG': 'http://ontology.neuinfo.org/NIF/BiomaterialEntities/NIF-Organism.owl#'}
#FIXME: old prefixe
'''
PREFIXES = {
    'owl':'http://www.w3.org/2002/07/owl#',
    'rdf':'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
    'rdfs':'http://www.w3.org/2000/01/rdf-schema#',
    'skos':'http://www.w3.org/2004/02/skos/core#',
    '':'http://scicrunch.org/resolver/',  # generate base from this directly?
    'obo':'http://purl.obolibrary.org/obo/',
    'FIXME':'http://fixme.org/',
    'NIF':'http://uri.neuinfo.org/nif/nifstd/',  # for old ids??
    'obo_annot':'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#',  #FIXME OLD??
    'oboInOwl':'http://www.geneontology.org/formats/oboInOwl#',  # these aren't really from OBO files but they will be friendly known identifiers to people in the community
    'NIFGA':'http://ontology.neuinfo.org/NIF/BiomaterialEntities/NIF-GrossAnatomy.owl#',
    'NIFCELL': 'http://ontology.neuinfo.org/NIF/BiomaterialEntities/NIF-Cell.owl#',
    'nlx_only': 'http://uri.neuinfo.org/nif/nifstd/',
    # ontologies,
    'HP': 'http://purl.obolibrary.org/obo/HP_',
    'RO': 'http://purl.obolibrary.org/obo/RO_',
    'OBO': 'http://purl.obolibrary.org/obo/',
    'OIO': 'http://www.geneontology.org/formats/oboInOwl#',
    'IAO': 'http://purl.obolibrary.org/obo/IAO_',
    'SO' : 'http://purl.obolibrary.org/obo/SO_',
    'OLD_SO' : 'http://purl.obolibrary.org/obo/SO#SO_',
    'BFO': 'http://purl.obolibrary.org/obo/BFO_',
    'DOID': 'http://purl.obolibrary.org/obo/DOID_,',
    'PATO': 'http://purl.obolibrary.org/obo/PATO_',
    'PATO2': 'http://purl.obolibrary.org/obo/PATO#PATO_',  #AAAAAAAAAAA
    'PATO3': 'http://purl.org/obo/owl/PATO#PATO_',  #AAAAAAAAAAAAAAAAAA
    'PR': 'http://purl.obolibrary.org/obo/PR_' ,
    'PW' : 'http://purl.obolibrary.org/obo/PW_',
    'CL' : 'http://purl.obolibrary.org/obo/CL_',
    'CLO' : 'http://purl.obolibrary.org/obo/CLO_',
    'GO' : 'http://purl.obolibrary.org/obo/GO_',
    'SIO' : 'http://semanticscience.org/resource/SIO_',
    'EFO' : 'http://www.ebi.ac.uk/efo/EFO_',
    'UBERON' : 'http://purl.obolibrary.org/obo/UBERON_',
    'ERO' : 'http://purl.obolibrary.org/obo/ERO_',
    'NCBITaxon' : 'http://purl.obolibrary.org/obo/NCBITaxon_',
    'UO': 'http://purl.obolibrary.org/obo/UO_',
    'OLD_CHEBI': 'http://purl.obolibrary.org/obo/chebi.owl#CHEBI_',
    'FMA': 'http://purl.org/sig/ont/fma/fma',

    # NIF Import closure
    'BIRNANN': 'http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#',
    'BIRNOBI': 'http://ontology.neuinfo.org/NIF/Backend/BIRNLex-OBI-proxy.owl#',
    'BIRNOBO': 'http://ontology.neuinfo.org/NIF/Backend/BIRNLex-OBO-UBO.owl#',
    'NIFBE': 'http://ontology.neuinfo.org/NIF/Backend/nif_backend.owl#',
    'NIFQUAL': 'http://ontology.neuinfo.org/NIF/Backend/NIF-Quality.owl#',
    'OBOANN': 'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#',
    'NIFANN': 'http://ontology.neuinfo.org/NIF/BiomaterialEntities/NIF-Annotation-Standard.owl#',
    'NIFCELL': 'http://ontology.neuinfo.org/NIF/BiomaterialEntities/NIF-Cell.owl#',
    'NIFCHEM': 'http://ontology.neuinfo.org/NIF/BiomaterialEntities/NIF-Chemical.owl#',
    'NIFGA': 'http://ontology.neuinfo.org/NIF/BiomaterialEntities/NIF-GrossAnatomy.owl#',
    'NIFMOL': 'http://ontology.neuinfo.org/NIF/BiomaterialEntities/NIF-Molecule.owl#',
    'NIFORG': 'http://ontology.neuinfo.org/NIF/BiomaterialEntities/NIF-Organism.owl#',
    'NIFSUB': 'http://ontology.neuinfo.org/NIF/BiomaterialEntities/NIF-Subcellular.owl#',
    'NIFUNCL': 'http://ontology.neuinfo.org/NIF/BiomaterialEntities/NIF-Unclassified.owl#',
    'SAOCORE': 'http://ontology.neuinfo.org/NIF/BiomaterialEntities/SAO-CORE_properties.owl#',
    'NIFGG': 'http://ontology.neuinfo.org/NIF/DigitalEntities/NIF-Government-Granting-Agency.owl#',
    'NIFINV': 'http://ontology.neuinfo.org/NIF/DigitalEntities/NIF-Investigation.owl#',
    'NIFRES': 'http://ontology.neuinfo.org/NIF/DigitalEntities/NIF-Resource.owl#',
    'NIFSCID': 'http://ontology.neuinfo.org/NIF/DigitalEntities/NIF-Scientific-Discipline.owl#',
    'NIFDYS': 'http://ontology.neuinfo.org/NIF/Dysfunction/NIF-Dysfunction.owl#',
    'NIFFUN': 'http://ontology.neuinfo.org/NIF/Function/NIF-Function.owl#',
    'NEMOANN': 'http://purl.bioontology.org/NEMO/ontology/NEMO_annotation_properties.owl',
    'NEMO': 'http://purl.bioontology.org/NEMO/ontology/NEMO.owl#NEMO_',
    'BFO1': 'http://www.ifomis.org/bfo/1.1',
    'COGAT': 'http://www.cognitiveatlas.org/ontology/cogat.owl#',
    'COGPO': 'http://www.cogpo.org/ontologies/COGPO_',  # doesn't resolve

    # Inferred or Slim
    'NIFMOLINF': 'http://ontology.neuinfo.org/NIF/BiomaterialEntities/NIF-Molecule-Role-Inferred.owl#',
    'NIFNCBISLIM': 'http://ontology.neuinfo.org/NIF/NIF-NCBITaxonomy-Slim.owl#',

    # Bridge
    'QUALBB': 'http://ontology.neuinfo.org/NIF/Backend/quality_bfo_bridge.owl#',
    'NIFNEURON': 'http://ontology.neuinfo.org/NIF/BiomaterialEntities/NIF_Neuron_MolecularConstituent_Bridge.owl#',
    'NIFERO': 'http://ontology.neuinfo.org/NIF/BiomaterialEntities/NIF-Eagle-I-Bridge.owl#',
    'NIFGOCC': 'http://ontology.neuinfo.org/NIF/BiomaterialEntities/NIF-GO-CC-Bridge.owl#',
    'NIFMOLROLE': 'http://ontology.neuinfo.org/NIF/BiomaterialEntities/NIF-Molecule-Role-Bridge.owl#',
    'NIFNCBI': 'http://ontology.neuinfo.org/NIF/BiomaterialEntities/NIF-NCBITax-Bridge.owl#',
    'NIFNEURBR': 'http://ontology.neuinfo.org/NIF/BiomaterialEntities/NIF-Neuron-BrainRegion-Bridge.owl#',
    'NIFNEURCIR': 'http://ontology.neuinfo.org/NIF/BiomaterialEntities/NIF-Neuron-Circuit-Role-Bridge.owl#',
    'NIFNEURMOR': 'http://ontology.neuinfo.org/NIF/BiomaterialEntities/NIF-Neuron-Morphology-Bridge.owl#',
    'NIFNEURNT': 'http://ontology.neuinfo.org/NIF/BiomaterialEntities/NIF-Neuron-NT-Bridge.owl#'
}
'''
ONTOLOGY_BASE = 'some silly iri'

ONTOLOGY_DEF = {
    'iri':'http://ontology.neuinfo.org/SciCrunchRegistry/scicrunch-registry.ttl',
    'label':'scicrunch registry exported ontology',
    'comment':'This file is automatically generated from the SciCrunch resource registry on a weekly basis.',
    'version':date.today().strftime('%Y-%m-%d'),
}

remap_supers = {
    'Resource':'NIF:nlx_63400',  # FIXME do not want to use : but broken because of defaulting to add : to all scr ids (can fix just not quite yet)
    'Commercial Organization':'NIF:nlx_152342',
    'Organization':'NIF:nlx_152328',
    'University':'NIF:NEMO_0569000',  # UWOTM8

    'Institution':'NIF:birnlex_2085',
    'Institute':'NIF:SIO_000688',
    'Government granting agency':'NIF:birnlex_2431',
}

def mysql_conn_helper(host, db, user, port=3306):
    kwargs = {
        'host':host,
        'db':db,
        'user':user,
        'port':port,
        'password':None,  # no you may NOT pass it in
    }
    with open(os.path.expanduser('~/.mypass'), 'rt') as f:
        entries = [l.strip().split(':', 4) for l in f.readlines()]
    for e_host, e_port, e_db, e_user, e_pass in entries:
        e_port = int(e_port)
        if host == e_host:
            print('yes:', host)
            if  port == e_port:
                print('yes:', port)
                if db == e_db or e_db == '*':  # FIXME bad * expansion
                    print('yes:', db)
                    if user == e_user:
                        print('yes:', user)
                        kwargs['password'] = e_pass  # last entry wins
    e_pass = None
    if kwargs['password'] is None:
        raise ConnectionError('No password as found for {user}@{host}:{port}/{db}'.format(**kwargs))

    return kwargs

def make_records(resources, res_cols, field_mapping):
    resources = {id:(scrid, oid, type) for id, scrid, oid, type in resources}
    res_cols_latest = {}
    versions = {}
    for rid, value_name, value, version in res_cols:
        if rid not in versions:
            versions[(rid, value_name)] = version  # XXX WARNING assumption is that for these fields resources will only ever have ONE but there is no gurantee :( argh myslq

        if version >= versions[(rid, value_name)]:
            res_cols_latest[(rid, value_name)] = (rid, value_name, value)

    res_cols = list(res_cols_latest.values())

    output = {}
        #rc_query = conn.execute('SELECT rid, name, value FROM resource_columns as rc WHERE rc.name IN %s' % str(tuple([n for n in field_mapping if n != 'MULTI'])))
    #for rid, original_id, type_, value_name, value in join_results:
    for rid, value_name, value in res_cols:
        #print(rid, value_name, value)
        scrid, oid, type_ = resources[rid]
        if scrid.startswith('SCR_'):
            scrid = ':' + scrid  # FIXME
        if scrid not in output:
            output[scrid] = []
        #if 'id' not in [a for a in zip(*output[rid])][0]:
            output[scrid].append(('id', scrid))  # add the empty prefix
            output[scrid].append(('old_id', oid))
            output[scrid].append(('type', type_))

        if value_name in field_mapping['MULTI']:
            values = [v.strip() for v in value.split(',')]  # XXX DANGER ZONE
            name = field_mapping['MULTI'][value_name]
            for v in values:
                output[scrid].append((name, v))  # TODO we may want functions here
        else:
            if field_mapping[value_name] == 'definition':
                value = value.replace('\r\n','\n').replace('\r','\n').replace("'''","' ''")  # the ''' replace is because owlapi ttl parser considers """ to match ''' :/ probably need to submit a bug
            elif field_mapping[value_name] == 'superclass':
                if value in remap_supers:
                    value = remap_supers[value]
            output[scrid].append((field_mapping[value_name], value))  # TODO we may want functions here

    return output

class makeGraph:
    def __init__(self, name, prefixes):
        self.name = name
        self.namespaces = {p:rdflib.Namespace(ns) for p, ns in prefixes.items()}
        self.g = rdflib.Graph()
        [self.g.namespace_manager.bind(p, ns) for p, ns in prefixes.items()]

    def printMe(self):
        with open('/tmp/' + self.name + '.ttl', 'wb') as f:
            rowtest = [r for r in csv.reader(f)]
        for r in rowtest:
            print(r)

    def write(self):
        with open('/tmp/' + self.name + '.ttl', 'wb') as f:
            f.write(self.g.serialize(format='turtle'))
        with open('/tmp/ttl_files', 'wt') as f: f.write('/tmp/' + self.name + '.ttl')
        os.system('java -cp ' +
        os.path.expanduser('~/git/ttl-convert/target/'
                            'ttl-convert-1.0-SNAPSHOT-jar-with-dependencies.jar') +
                            ' scicrunch.App ' + '/tmp/ttl_files')

    def expand(self, curie):
        #print(curie)
        prefix, suffix = curie.split(':')
        if prefix not in self.namespaces:
            raise KeyError('Namespace prefix does exist:', prefix)
        return self.namespaces[prefix][suffix]

    def check_thing(self, thing):
        if type(thing) != rdflib.term.URIRef:
            try:
                return self.expand(thing)
            except (KeyError, ValueError) as e:
                if thing.startswith('http') and ' ' not in thing:  # so apparently some values start with http :/
                    return rdflib.URIRef(thing)
                else:
                    raise TypeError('Unknown format:', thing)
        else:
            return thing

    def add_node(self, target, edge, value):
        target = self.check_thing(target)
        edge = self.check_thing(edge)
        try:
            if value.startswith(':') and ' ' in value:  # not a compact repr AND starts with a : because humans are insane
                value = ' ' + value
            value = self.check_thing(value)
        except TypeError:
            if type(value) == str:
                value = rdflib.Literal(value, datatype = rdflib.XSD.string)
            else:
                value = rdflib.Literal(value)  # trust autoconv
        self.g.add( (target, edge, value) )



field_to_edge = {
    'http://ontology.neuinfo.org/NIF/BiomaterialEntities/NIF-Cell.owl#':'dude',
    #'NIFCELL':'',
    'rdf:type':'rdf:type',
    'subClassOf':'rdfs:subClassof',#FIXME I made this up
    'abbrev':'rdfs:abbrev',
    'Abbrev':'obo_annot:abbrev', # 'rdfs:Abbrev',
    'alt_id':'oboInOwl:hasDbXref',
    #'definition':'obo:IAO_0000115',  # FIXME alternate is skos:definition...
    #'Definition':'skos:definition',
    'Definition':'rdfs:Definition',
    'Id':'rdf:type',
    'NLXID':'rdfs:nlx_only',
    'Label':'rdfs:label',#'rdfs:Label',
    'old_id':'oboInOwl:hasDbXref',  # old vs alt id?
    'superclass':'rdfs:subClassOf',  # translation required
    'Synonym':'obo_annot:synonym', #'rdfs:synonym',
    'SuperCategory':'rdfs:SuperCategory',
    'type':'rdfs:type',  # bloody type vs superclass :/ ask james
    'Category':'rdfs:Category',
    'categories':'rdfs:categories',
    'Categories':'rdfs:Categories',
    'Species':'rdfs:species',
    'DefiningCriteria':'rdfs:DefiningCriteria',
    'DefiningCitation':'rdfs:DefiningCitation',
    'Has_role':'rdfs:Has_Role',
    'PMID':'rdfs:PMID',
    'FBbt_Id':'rdfs:FBbt_Id',
    'FBBT_Link':'rdfs:temp',
    'Species/taxa':'rdfs:temp',
    'CellSomaShape':'rdfs:CellSomaShape',
    'LocationOfLocalAxonArborization':'rdfs:LocationOfLocalAxonArborization',
    'CellSomaSize':'rdfs:CellSomaSize',
    'http://ontology.neuinfo.org/NIF/#createdDate':'rdfs:temp',
    'OriginOfAxon':'rdfs:OriginOfAxon',
    'category':'rdfs:category',
    'Located_in':'rdfs:Located_in',
    'SpineDensityOnDendrites':'rdfs:SpineDensityOnDendrites',
    'AxonMyelination':'rdfs:AxonMyelination',
    'AxonProjectionLaterality':'rdfs:AxonProjectionLaterality',
    'LocationOfAxonArborization':'rdfs:temp',
    'MolecularConstituents':'rdfs:MolecularConstituents',
    'DendriteLocation':'rdfs:DendriteLocation',
    'BranchingMetrics':'rdfs:BranchingMetrics',
    'Neurotransmitter/NeurotransmitterReceptors':'rdfs:Neurotransmitter/NeurotransmitterReceptors',
    'Curator_Notes':'rdfs:Curator_Notes',
    'Fasciculates_with':'rdfs:Fasciculates_with',


    #FIXME: merged edges
    'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#synonym':'rdfs:synonym',
    'synonym':'rdfs:synonym',

    'abbreviation':'rdfs:Abbrev',
    'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#abbrev':'rdfs:Abbrev',

    'http://www.w3.org/2004/02/skos/core#definition':'rdfs:Definition',
    'definition':'rdfs:Definition',
    'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#externallySourcedDefinition':'rdfs:Definition',
    'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#hasDefinitionSource':'rdfs:Definition',
    'http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#birnlexDefinition':'rdfs:Definition',

    'http://www.w3.org/2000/01/rdf-schema#label':'rdfs:Label',
    'http://www.w3.org/2004/02/skos/core#prefLabel':'rdfs:Label',

    'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#definingCitation':'rdfs:DefiningCitation',
    'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#definingCitationURI':'rdfs:DefiningCitation',

    'http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#sao_ID':'rdfs:Id',
    'http://protege.stanford.edu/plugins/owl/protege#sao_ID':'rdfs:Id',
    'http://ontology.neuinfo.org/NIF/BiomaterialEntities/NIF-Cell.owl#sao_ID':'rdfs:Id',

    'http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#PMID':'rdfs:PMID',
    #FIXME: end of new edges


    'http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#bamsID':'rdfs:temp',
    'http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#birnlexPendingDifferentiaNote':'rdfs:temp',
    'http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#birnlexRetiredDefinition':'rdfs:temp',
    'http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#bonfireID':'rdfs:temp',
    'http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#bonfire_ID':'rdfs:temp',
    'http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#cell_ontology_ID':'rdfs:temp',
    'http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#curationStatus':'rdfs:temp',
    'http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#hasBirnlexCurator':'rdfs:temp',
    'http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#hasCurationStatus':'rdfs:temp',
    'http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#hasFormerParentClass':'rdfs:temp',
    'http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#isReplacedByClass':'rdfs:temp',
    'http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#neuroNamesAncillaryTerm':'rdfs:temp',
    'http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#neuronamesID':'rdfs:temp',
    'http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#umls_ID':'rdfs:temp',
    'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#MeshUid':'rdfs:temp',
    'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#UmlsCui':'rdfs:temp',
    'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#altDefinition':'rdfs:temp',
    'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#createdDate':'rdfs:temp',
    'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#curator':'rdfs:temp',
    'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#definitonSource':'rdfs:temp',
    'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#externalSourceId':'rdfs:temp',
    'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#externalSourceURI':'rdfs:temp',
    'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#hasAbbrevSource':'rdfs:temp',
    'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#hasExternalSource':'rdfs:temp',
    'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#modifiedDate':'rdfs:temp',
    'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#nifID':'rdfs:temp',
    'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#pendingActionNote':'rdfs:temp',
    'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#pendingMereotopologicalRelationNote':'rdfs:temp',
    'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#tempDefinition':'rdfs:temp',
    'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#usageNote':'rdfs:temp',
    'http://purl.obolibrary.org/obo/IAO_0000115':'rdfs:temp',
    'http://purl.obolibrary.org/obo/UBPROP_0000001':'rdfs:temp',
    'http://purl.obolibrary.org/obo/UBPROP_0000003':'rdfs:temp',
    'http://purl.obolibrary.org/obo/UBPROP_0000012':'rdfs:temp',
    'http://purl.org/dc/elements/1.1/contributor':'rdfs:temp',
    'http://purl.org/dc/elements/1.1/description':'rdfs:temp',
    'http://purl.org/dc/elements/1.1/source':'rdfs:temp',
    'http://www.geneontology.org/formats/oboInOwl#creation_date':'rdfs:temp',
    'http://www.geneontology.org/formats/oboInOwl#editor_notes':'rdfs:temp',
    'http://www.geneontology.org/formats/oboInOwl#hasBroadSynonym':'rdfs:temp',
    'http://www.geneontology.org/formats/oboInOwl#hasDbXref':'rdfs:temp',
    'http://www.geneontology.org/formats/oboInOwl#hasExactSynonym':'rdfs:temp',
    'http://www.geneontology.org/formats/oboInOwl#hasOBONamespace':'rdfs:temp',
    'http://www.geneontology.org/formats/oboInOwl#hasRelatedSynonym':'rdfs:temp',
    'http://www.geneontology.org/formats/oboInOwl#hasVersion':'rdfs:temp',
    'http://www.geneontology.org/formats/oboInOwl#id':'rdfs:temp',
    'http://www.w3.org/2000/01/rdf-schema#comment':'rdfs:temp',
    'http://www.w3.org/2002/07/owl#deprecated':'rdfs:temp',
    'http://www.w3.org/2002/07/owl#versionInfo':'rdfs:temp',
    'http://www.w3.org/2004/02/skos/core#changeNote':'rdfs:temp',
    'http://www.w3.org/2004/02/skos/core#editorialNote':'rdfs:temp',
    'http://www.w3.org/2004/02/skos/core#example':'rdfs:temp',
    'http://www.w3.org/2004/02/skos/core#historyNote':'rdfs:historyNote_scigraph',
    'http://www.w3.org/2004/02/skos/core#scopeNote':'rdfs:scopeNote_scigraph',
    'types':'rdfs:types',
    'PREFIX':'rdfs:prefixWithID_merge',
    'acronym':'rdfs:acronym_scigraph',
    'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#acronym':'rdfs:acronym_scigraph',
}
field_to_edge = {k: rdflib.URIRef(k) if k.startswith('http') else v for k,v in field_to_edge.items()}


def make_node(id_, field, value):
    field = field_to_edge[field]
    if field == 'rdf:type':
        value = 'owl:Class'
    return id_, field, value


field_mapping = {
    'Label':'label',
    'Description':'definition',
    'Synonyms':'synonyms',
    'Alternate IDs':'alt_ids',
    'Supercategory':'superclass',
    #'Keywords':'keywords'  # don't think we need this
    'MULTI':{'Synonyms':'synonym',
             'Alternate IDs':'alt_id',
             'Abbreviation':'abbrev',
            },
}

badcats = {
 ':Category:':'owl:Thing',
 ':Category:Cell layer':'nlx_149357',
 ':Category:Defined neuron class':'nlx_55759',
 ':Category:Glial-like cell':':Category:Glial-like cell',  # UWOTM8
 ':Category:Hemisphere parts of cerebral cortex':'birnlex_1796',
 ':Category:Lobe parts of cerebral cortex':'birnlex_922',
 ':Category:Magnocellular neurosecretory cell':'nlx_cell_20090501',
 ':Category:Neuron':'sao1417703748',
 ':Category:Organism':'birnlex_2',
 ':Category:Regional part of brain':'birnlex_1167',
 ':Category:Retina ganglion cell B':'BAMSC1010',
 ':Category:Retina ganglion cell C':'BAMSC1011',
 ':Category:Sulcus':'nlx_144078',
 ':Category:Superior colliculus stellate neuron':'BAMSC1129',
 ':Category:Superior colliculus wide field vertical cell':'BAMSC1125',
 ':Category:spinal cord ventral horn interneuron V2':'nlx_cell_100207',
}

#tried to inialize graph so default will dissapear
def initializeGraph(g):
    for i in PREFIXES:
        if None == i or '' == i :
            continue
        node = make_node(PREFIXES[i], 'rdf:type', 'owl:Class')
        g.add_node(*node)
    g.write()


def main():
    g = makeGraph('cell-merge', PREFIXES)
    gn = Graph()
    record = defaultdict(list)
    fixmeRecord = []

    ncttl = requests.get('http://ontology.neuinfo.org/NIF/ttl/NIF-Cell.ttl').text
    ncttl = '\n'.join([l for l in ncttl.split('\n') if 'owl:imports' not in l])
    g.g.parse(data = ncttl, format='turtle')

   #g.g.parse('http://ontology.neuinfo.org/NIF/BiomaterialEntities/NIF-Cell.owl', format='xml')

    #initializeGraph(g)
    for prefix, outer_identifiers in data.items():
        outer_identifiers.sort()

        for id_ in outer_identifiers:

            PrefixWithID = prefix + ':' + id_

            if prefix in ['NIFGA']:
                continue
            if prefix in ['FMAID', 'nlx_only']:
                node = {'nodes':[{'meta':{}}]}
                continue
            else:
                node=graph.getNode(PrefixWithID)#skipped for nlx_only
            cheatList.append(PrefixWithID)
            try:
                columns = js[id_][0]

            except KeyError:
                columns = [''] * 100

            #for keys, values in node['nodes'][0]['meta'].items():
            neighbor = [e for e in gn.getNeighbors(PrefixWithID, depth=1,direction='INCOMING')['edges'] if e['sub']==PrefixWithID and e['pred']=='subClassOf']
            if neighbor in neighborList: #checks for duplicates
                continue
            else:
                neighborList.append(neighbor)
            for edge in neighbor:
                key = edge['pred']
                value = edge['obj']
                sub = edge['sub']
                record[sub].append(value)
                if '#' in value or 'NIFNEURNT' in value or 'NIFNEURCIR' in value:
                    continue
                if len(record[sub]) > 1:
                    fixmeRecord.append((sub,record[sub]))
                node = make_node(PrefixWithID, 'subClassOf' , value.strip())
                g.add_node(*node)

            for index, label in enumerate(js['LABELS']):
                #print(list(enumerate(js['LABELS'])))
                mid = label
                right = columns[index]
                if right == '':
                   continue
                if mid == 'SuperCategory':
                    test = ':Category:' + right
                    if test in badcats:
                        right = badcats[test]
                if ' ' in mid:
                    mid=mid.replace(' ','_')

                if type(right)==str and ':Category:' in right:
                    if ':Category:' in right and ',' not in right and '.' not in right and '(' not in right:
                        right = PrefixWithID
                        node = make_node(PrefixWithID, mid, right)
                        g.add_node(*node)
                    #FIXME: this is where I change category to prefix + ID
                    elif ':Category:' in right and ',' in right and '.' not in right and '(' not in right:
                        e = right.split(',')
                        i = ''
                        temp = 'hey'
                        for n,ele in enumerate(e):

                            for items in Cat_to_preID:
                                if ele == items[1]:
                                    e[n] = items[0]

                            node = make_node(PrefixWithID, mid, e[n])
                            g.add_node(*node)

                elif type(right)==list:
                    right = tuple(right)

                    for e in right:
                        if type(e)==bool:
                            continue
                        if not e:
                            continue
                        if type(e)==list:
                            for i in e:
                                node = make_node(PrefixWithID, mid, i.strip())
                                g.add_node(*node)

                        e=e.replace('  ',' ').replace("'''","' ''").replace('\\','').replace("\\","")
                        if 'http' in e:
                            if 'http://neurolex.org/wiki/Nlx_anat_1005030' in e:
                                e='http://neurolex.org/wiki/Nlx_anat_1005030'
                            if 'http://www.nature.com/nrn/journal/v6/n4/glossary/nrn1646.html#df1' in e:
                                e='http://www.nature.com/nrn/journal/v6/n4/glossary/nrn1646.html#df1'
                            node = make_node(PrefixWithID, mid, rdflib.term.URIRef(e))
                            g.add_node(*node)

                        else:
                            node = make_node(PrefixWithID, mid, e.strip())
                            g.add_node(*node)


                else:
                    right=right.replace('  ',' ').replace("'''","' ''").replace('\\','').replace("\\","")
                    e=right
                    e=e.replace('  ',' ')
                    if '#' in e:

                        if 'http://neurolex.org/wiki/Nlx_anat_1005030' in e:
                            e='http://neurolex.org/wiki/Nlx_anat_1005030'
                        if 'http://www.nature.com/nrn/journal/v6/n4/glossary/nrn1646.html#df1' in e:
                            e='http://www.nature.com/nrn/journal/v6/n4/glossary/nrn1646.html#df1'

                        node = make_node(PrefixWithID, mid, rdflib.term.URIRef(e))
                        g.add_node(*node)

                    else:
                        node = make_node(PrefixWithID, mid, e.strip())
                        g.add_node(*node)
                continue
    g.write()
    for r in g.g:
        print (r)

if __name__ == '__main__':
    main()
#print(cheatList)