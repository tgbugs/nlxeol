#!/usr/bin/env python3
"""
    Sync the scicrunch registry to a ttl
    file for loading into scigraph for autocomplete.
"""
import re
import numpy
import collections
from heatmaps.scigraph_client import Graph, Vocabulary
import json
import csv
from collected import data #imports data from a previous py file
from collections import defaultdict, namedtuple
import os
import rdflib
from datetime import date
from IPython import embed
from sqlalchemy import create_engine, inspect
from rdflib import Namespace,URIRef

#FIXME the strings are combining in data_compare

ns=Namespace


values = [] #clumped total info of each element as a list of lists
pref = defaultdict(list)
temp = defaultdict(list)
record=[]
neighborList = []


#FIXME supercategory is element num 7
with open('Neurolex_Scigraph.json') as data_file:
    js = json.load(data_file)

keys = tuple(js)
prefix = tuple(data)

#FIXME: probably will be list for Namespace
#person1 = Namespace("http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#Bill_Bug")


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

    def write(self):
        with open('/tmp/' + self.name + '.ttl', 'wb') as f:
            f.write(self.g.serialize(format='turtle'))
        with open('/tmp/ttl_files', 'wt') as f: f.write('/tmp/' + self.name + '.ttl')

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
            value = rdflib.Literal(value)  # trust autoconv
        self.g.add( (target, edge, value) )


field_to_edge = {
    'subClassOf':'rdfs:subClassof',#FIXME I made this up
    'abbrev':'obo_annot:abbrev',
    'Abbrev':'obo_annot:abbrev_troy',
    'alt_id':'oboInOwl:hasDbXref',
    #'definition':'obo:IAO_0000115',  # FIXME alternate is skos:definition...
    #'Definition':'skos:definition',
    'Definition':'obo_annot:Definition_troy',
    'Id':'rdf:type',
    'Label':'obo_annot:Label_troy',
    'old_id':'oboInOwl:hasDbXref',  # old vs alt id?
    'superclass':'rdfs:subClassOf',  # translation required
    'Synonym':'obo_annot:synonym_troy',
    'SuperCategory':'FIXME:SuperCategory',
    'type':'FIXME:type',  # bloody type vs superclass :/ ask james
    'category':'rdfs:category',
    'categories':'rdfs:categories',
    'Categories':'rdfs:categories',
    'Species':'rdfs:species',
    'DefiningCriteria':'rdfs:DefiningCriteria',
    'DefiningCitation':'rdfs:DefiningCitation',
    'Has_role':'rdfs:Has_Role',
    'PMID':'obo_annot:PMID_troy',
    'FBbt_Id':'obo_annot:FBbt_merge',
    'FBBT_Link':'rdfs:temp',
    'http://ontology.neuinfo.org/NIF/#createdDate':'rdfs:temp',
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
    'http://www.w3.org/2004/02/skos/core#historyNote':'obo_annot:historyNote_scigraph',
    'http://www.w3.org/2004/02/skos/core#scopeNote':'obo_annot:scopeNote_scigraph',
    'types':'obo_annot:types_scigraph',
    'PREFIX':'obo_annot:prefixWithID_merge',
    'acronym':'obo_annot:acronym_scigraph',
    'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#acronym':'obo_annot:acronym_scigraph',
}
field_to_edge = {k: rdflib.URIRef(k) if k.startswith('http') else v for k,v in field_to_edge.items()}


def make_node(id_, field, value):
    if field == 'id':
        value = 'owl:Class'
    return id_, field_to_edge[field], value


field_mapping = {
    'Lable':'label',
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


def _main():
    DB_URI = 'mysql+mysqlconnector://{user}:{password}@{host}:{port}/{db}'
    config = mysql_conn_helper('mysql5-stage.crbs.ucsd.edu', 'nif_eelg', 'nif_eelg_secure')
    engine = create_engine(DB_URI.format(**config))
    config = None  # all weakrefs should be gone by now?
    del(config)  # i wonder whether this actually cleans it up when using **config
    insp = inspect(engine)
    #names = [c['name'] for c in insp.get_columns('registry')]
    #resource_columns = [c['name'] for c in insp.get_columns('resource_columns')]
    #resource_data = [c['name'] for c in insp.get_columns('resource_data')]
    #resource_fields = [c['name'] for c in insp.get_columns('resource_fields')]
    #resources = [c['name'] for c in insp.get_columns('resources')]
    #conn.execute('SELECT * from registry;')
    if 1:
    #with engine.connect() as conn:
        conn = engine
        tables = ('resource_columns', 'resource_data', 'resource_fields', 'resources')
        data = {t:([c['name'] for c in insp.get_columns(t)], conn.execute('SELECT * from %s limit 20;' % t).fetchall()) for t in tables}
        all_fields = [n[0] for n in conn.execute('SELECT distinct(name) FROM resource_fields;').fetchall()]

        #query = conn.execute('SELECT r.rid, r.original_id, r.type, rc.name, rc.value from resources as r JOIN'
                            #' resource_columns as rc ON r.id=rc.rid'
                            #' WHERE rc.name IN %s limit 1000;' % str(tuple([n for n in field_mapping if n != 'MULTI'])))  # XXX DANGER THIS QUERY IS O(x^n) :x
                            #' ORDER BY r.rid limit 2000;'

        #query = conn.execute('SELECT r.rid, r.original_id, r.type, rc.name, rc.value from resource_columns as rc JOIN'
                             #' resources as r ON rc.rid=r.id'
                             #' WHERE rc.name IN %s;' % str(tuple([n for n in field_mapping if n != 'MULTI'])))  # XXX DANGER why does > 2000 limit break stuff?

        #join = query.fetchall()

        #embed()
        #return
        #print('running join')
        print('running 1')
        r_query = conn.execute('SELECT id, rid, original_id, type FROM resources WHERE id < 16000;')  # avoid the various test entries :(
        print('fetching 1 ')
        r = r_query.fetchall()
        print('running 2')
        rc_query = conn.execute('SELECT rid, name, value, version FROM resource_columns as rc WHERE rc.rid < 16000 AND rc.name IN %s;' % str(tuple([n for n in field_mapping if n != 'MULTI'])))
        print('fetching 2')
        rc = rc_query.fetchall()

        #embed()
        #return

    r.append( (-100, 'NIF:nlx_63400', 'nlx_63400', 'Resource') )
    r.append( (-101, 'NIF:nlx_152342', 'nlx_152342', 'Organization') )
    r.append( (-102, 'NIF:nlx_152328', 'nlx_152328', 'Organization') )
    r.append( (-103, 'NIF:NEMO_0569000', 'NEMO_0569000', 'Institution') )
    r.append( (-104, 'NIF:birnlex_2431', 'birnlex_2431', 'Institution') )
    r.append( (-105, 'NIF:SIO_000688', 'SIO_000688', 'Institution') )
    r.append( (-106, 'NIF:birnlex_2085', 'birnlex_2085', 'Institution') )
    rc.append( (-100, 'Resource Name', 'Resource', 1) )
    rc.append( (-101, 'Resource Name', 'Commercial Organization', 1) )
    rc.append( (-102, 'Resource Name', 'Organization', 1) )
    rc.append( (-103, 'Resource Name', 'University', 1) )
    rc.append( (-104, 'Resource Name', 'Government granting agency', 1) )
    rc.append( (-105, 'Resource Name', 'Institute', 1) )
    rc.append( (-106, 'Resource Name', 'Institution', 1) )
    rc.append( (-101, 'Supercategory', 'NIF:nlx_152328', 1) )  # TODO extract this more intelligently from remap supers please


def main():
    g = makeGraph('cell-merge', PREFIXES)
    gn = Graph()
    keyList=[]
    record = defaultdict(list)
    fixmeRecord = []

    for prefix, outer_identifiers in data.items():

        if 'nlx_only' == prefix:
            continue

        for id_ in outer_identifiers:
            PrefixWithID = prefix + ':' + id_
            columns = js[id_][0]
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

                if '#' or 'NIFNEURNT' or 'NIFNEURCIR' in value:
                    continue
                if len(record[sub]) > 1:
                    fixmeRecord.append((sub,record[sub]))

                node = make_node(PrefixWithID, 'subClassOf' , value)
                g.add_node(*node)

            for index, label in enumerate(js['LABELS']):
                mid = label

                if 'nlx_only' == prefix:
                    right = columns
                else:
                    right = columns[index]
                if not right:
                    continue
                if ' ' in mid:
                    mid=mid.replace(' ','_')
                #if 'http' in mid:
                    #mid = rdflib.URIRef(mid)
                    #print(mid)

                #right can be either a tuple, string, or list and need to be treated for different occurrences
                if type(right)==tuple:
                    for e in right:

                        if not e:
                            continue
                        if type(e)==bool:
                            continue
                        if ',' in e:
                            e=e.replace(',','')
                        if 'http' in e:
                            node = make_node(PrefixWithID, mid, rdflib.term.URIRef(e))#for values with urls
                        else:
                            node = make_node(PrefixWithID, mid, e)

                if type(right)==list:
                    right = tuple(right)

                    for e in right:

                        if not e:
                            continue
                        if type(e)==bool:
                            continue

                        if ',' in e:
                            e=e.replace(',','')
                        if 'http' in e:
                            if 'http://neurolex.org/wiki/Nlx_anat_1005030' in e:
                                e='http://neurolex.org/wiki/Nlx_anat_1005030'
                            if 'http://www.nature.com/nrn/journal/v6/n4/glossary/nrn1646.html#df1' in e:
                                e='http://www.nature.com/nrn/journal/v6/n4/glossary/nrn1646.html#df1'
                            node = make_node(PrefixWithID, mid, rdflib.term.URIRef(e))
                        else:
                            node = make_node(PrefixWithID, mid, e)

                if type(right)==str:
                    e=right
                    #for e in right.split(","):
                    if ',' in e:
                        e=e.replace(',','')
                    if '"' in e:
                        e=e.replace('"','')
                    if " '" in e:
                        e=e.replace(" '","")
                    if "'" in e:
                        e=e.replace("'","")
                    if r'\"' in e:
                        e=e.replace(r'\"','')
                    #typos from previous people
                    if '#' in e:
                        if 'http:ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#NeuroNames_defSource' in e:
                            e='http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#NeuroNames_defSource'
                        if 'http:ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#UMLS_defSource' in e:
                            e='http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#UMLS_defSource'
                        if 'http:ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#MeSH_defSource' in e:
                            e='http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#MeSH_defSource'
                        if 'http:ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#NeuroNames_abbrevSource' in e:
                            e='http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#NeuroNames_abbrevSource'
                        if 'http:ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#American_Heritage_Dictionary_4th_ed_defSource' in e:
                            e='http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#American_Heritage_Dictionary_4th_ed_defSource'
                        if 'http:purl.org/nbirn/birnlex/ontology/annotation/UMLS_annotation_properties.owl#UMLS_defSource' in e:
                            e='http://purl.org/nbirn/birnlex/ontology/annotation/UMLS_annotation_properties.owl#UMLS_defSource'
                        if 'http://neurolex.org/wiki/Nlx_anat_1005030' in e:
                            e='http://neurolex.org/wiki/Nlx_anat_1005030'
                        if 'http://www.nature.com/nrn/journal/v6/n4/glossary/nrn1646.html#df1' in e:
                            e='http://www.nature.com/nrn/journal/v6/n4/glossary/nrn1646.html#df1'
                        if 'http:ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#The_Sylvius_Project_defSource' in e:
                            e='http:ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#The_Sylvius_Project_defSource'
                        if 'http:ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#Wikipedia_defSource' in e:
                            e='http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#Wikipedia_defSource'

                        node = make_node(PrefixWithID, mid, rdflib.term.URIRef(e))
                    else:
                        node = make_node(PrefixWithID, mid, e)

                #print(node)
                g.add_node(*node)
                continue
    g.write()

if __name__ == '__main__':
    main()
    #embed()