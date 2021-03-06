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

'''
.namespace to map long names
.graph to make tuples

ns=Namespace
person = ns("http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#Bill_Bug") + ns("http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#Bill_Bug")
print(person)
rawInput = ns("http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#raw_import")
nueroNames = ns("http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#NeuroNames_abbrevSource")
'''
values = [] #clumped total info of each element as a list of lists
pref = defaultdict(list)
temp = defaultdict(list)



#FIXME supercategory is element num 7
with open('Neurolex_Scigraph.json') as data_file:
    js = json.load(data_file)

keys = tuple(js)
prefix = tuple(data)

#FIXME: probably will be list for Namespace
#person1 = Namespace("http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#Bill_Bug")



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
    'abbrev':'obo_annot:abbrev',
    'Abbrev':'obo_annot:abbrev',
    'alt_id':'oboInOwl:hasDbXref',
    #'definition':'obo:IAO_0000115',  # FIXME alternate is skos:definition...
    'Definition':'skos:definition',
    'Id':'rdf:type',
    'Label':'rdfs:label',
    'old_id':'oboInOwl:hasDbXref',  # old vs alt id?
    'superclass':'rdfs:subClassOf',  # translation required
    'Synonym':'obo_annot:synonym',  # FIXME
    'SuperCategory':'FIXME:SuperCategory',
    'type':'FIXME:type',  # bloody type vs superclass :/ ask james
    'category':'rdfs:category',
    'categories':'rdfs:categories',
    'Categories':'rdfs:categories',
    'Species':'rdfs:species',
    'DefiningCriteria':'rdfs:DefiningCriteria',
    'DefiningCitation':'rdfs:DefiningCitation',
    'Has_role':'rdfs:Has_Role',
    'PMID':'rdfs:PMID',
    'FBbt_Id':'rdfs:FBbt_Id',
    'FBBT_Link':'rdfs:FBBT_Link',
    'acronym':'rdfs:acronym',
    'http://ontology.neuinfo.org/NIF/#createdDate':'rdfs:createdDate',
    'http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#PMID':'rdfs:PMID',
    'http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#bamsID':'rdfs:bamsID',
    'http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#birnlexDefinition':'rdfs:birnlexDefinition',
    'http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#birnlexPendingDifferentiaNote':'rdfs:birnlexPendingDifferentiaNote',
    'http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#birnlexRetiredDefinition':'rdfs:birnlexRetiredDefinition',
    'http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#bonfireID':'rdfs:bonfireID',
    'http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#bonfire_ID':'rdfs:bonfire_ID',
    'http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#cell_ontology_ID':'rdfs:cell_ontology_ID',
    'http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#curationStatus':'rdfs:curationStatus',
    'http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#hasBirnlexCurator':'rdfs:hasBirnlexCurator',
    'http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#hasCurationStatus':'rdfs:hasCurationStatus',
    'http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#hasFormerParentClass':'rdfs:hasFormerParentClass',
    'http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#isReplacedByClass':'rdfs:isReplacedByClass',
    'http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#neuroNamesAncillaryTerm':'rdfs:neuroNamesAncillaryTerm',
    'http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#neuronamesID':'rdfs:neuronamesID',
    'http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#sao_ID':'rdfs:sao_ID',
    'http://ontology.neuinfo.org/NIF/Backend/BIRNLex_annotation_properties.owl#umls_ID':'rdfs:umls_ID',
    'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#MeshUid':'rdfs:MeshUid',
    'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#UmlsCui':'rdfs:UmlsCui',
    'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#abbrev':'rdfs:abbrev',
    'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#acronym':'rdfs:acronym',
    'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#altDefinition':'rdfs:altDefinition',
    'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#createdDate':'rdfs:createdDate',
    'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#curator':'rdfs:curator',
    'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#definingCitation':'rdfs:definingCitation',
    'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#definingCitationURI':'rdfs:definingCitationURI',
    'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#definitonSource':'rdfs:definitonSource',
    'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#externalSourceId':'rdfs:externalSourceId',
    'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#externalSourceURI':'rdfs:externalSourceURI',
    'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#externallySourcedDefinition':'rdfs:externallySourcedDefinition',
    'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#hasAbbrevSource':'rdfs:hasAbbrevSource',
    'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#hasDefinitionSource':'rdfs:hasDefinitionSource',
    'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#hasExternalSource':'rdfs:hasExternalSource',
    'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#modifiedDate':'rdfs:modifiedDate',
    'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#nifID':'rdfs:nifID',
    'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#pendingActionNote':'rdfs:pendingActionNote',
    'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#pendingMereotopologicalRelationNote':'rdfs:pendingMereotopologicalRelationNote',
    'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#tempDefinition':'rdfs:tempDefinition',
    'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#usageNote':'rdfs:usageNote',
    'http://ontology.neuinfo.org/NIF/BiomaterialEntities/NIF-Cell.owl#sao_ID':'rdfs:sao_ID',
    'http://protege.stanford.edu/plugins/owl/protege#sao_ID':'rdfs:sao_ID',
    'http://purl.obolibrary.org/obo/IAO_0000115':'rdfs:IAO_0000115',
    'http://purl.obolibrary.org/obo/UBPROP_0000001':'rdfs:UBPROP_0000001',
    'http://purl.obolibrary.org/obo/UBPROP_0000003':'rdfs:UBPROP_0000003',
    'http://purl.obolibrary.org/obo/UBPROP_0000012':'rdfs:UBPROP_0000012',
    'http://purl.org/dc/elements/1.1/contributor':'rdfs:contributor',
    'http://purl.org/dc/elements/1.1/description':'rdfs:description',
    'http://purl.org/dc/elements/1.1/source':'rdfs:source',
    'http://www.geneontology.org/formats/oboInOwl#creation_date':'rdfs:creation_date',
    'http://www.geneontology.org/formats/oboInOwl#editor_notes':'rdfs:editor_notes',
    'http://www.geneontology.org/formats/oboInOwl#hasBroadSynonym':'rdfs:hasBroadSynonym',
    'http://www.geneontology.org/formats/oboInOwl#hasDbXref':'rdfs:hasDbXref',
    'http://www.geneontology.org/formats/oboInOwl#hasExactSynonym':'rdfs:hasExactSynonym',
    'http://www.geneontology.org/formats/oboInOwl#hasOBONamespace':'rdfs:hasOBONamespace',
    'http://www.geneontology.org/formats/oboInOwl#hasRelatedSynonym':'rdfs:hasRelatedSynonym',
    'http://www.geneontology.org/formats/oboInOwl#hasVersion':'rdfs:hasVersion',
    'http://www.geneontology.org/formats/oboInOwl#id':'rdfs:oboInOwl_id',
    'http://www.w3.org/2000/01/rdf-schema#comment':'rdfs:comment',
    'http://www.w3.org/2002/07/owl#deprecated':'rdfs:deprecated',
    'http://www.w3.org/2002/07/owl#versionInfo':'rdfs:versionInfo',
    'http://www.w3.org/2004/02/skos/core#changeNote':'rdfs:changeNote',
    'http://www.w3.org/2004/02/skos/core#definition':'rdfs:definition',
    'http://www.w3.org/2004/02/skos/core#editorialNote':'rdfs:editorialNote',
    'http://www.w3.org/2004/02/skos/core#example':'rdfs:example',
    'http://www.w3.org/2004/02/skos/core#historyNote':'rdfs:historyNote',
    'http://www.w3.org/2004/02/skos/core#scopeNote':'rdfs:scopeNote',
    'synonym':'rdf:synonym',
    'types':'rdf:types',
    'PREFIX':'rdf:PREFIX',


}

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
    #FIXME, keep the rest, but need a new function from my own dictionary to build my records
    g = makeGraph('cell-merge', PREFIXES)
    #for i  in range(0,len(keys)):
        #for j in range(0,len(js['LABELS'][0])):
    #print(js.keys())
    keyList=[]
    for prefix, outer_identifiers in data.items():
        if 'nlx_only' == prefix:
            continue
        for id_ in outer_identifiers:
            pre = prefix + ':' + id_
            #if id_ not in js.keys():
                #keyList.append(id_)
                #continue
            #if id_ == "nifext_128":
                #id_ == "sao1736323572"
            columns = js[id_][0]
            #print('num columns', len(columns), id_)
            for index, label in enumerate(js['LABELS']):
                mid = label
                #print(mid)
                if 'nlx_only' == prefix:
                    right = columns
                else:
                    right = columns[index]
                #print(right)
                if not right:
                    continue
                #print(pre, mid, right)
                if ':' in right:
                    right=right.replace(':','')
                if ' ' in mid:
                    mid=mid.replace(' ','_')
                if type(right)==list:
                    right=str(right)
                node = make_node(pre, mid, right)
                #print(node)
                g.add_node(*node)
                continue
    g.write()
    #print(g)
    #print(keyList)

        #for inner_identifier, columns in js.items():
            #mid = js['LABELS'][0][j]
            #print(mid)
            #right = js[keys[i]][0][j]
            #for pre in prefix:
                #for IDs in data[pre]:
                #print(prefix, outer_identifiers, inner_identifier, columns, index, label)
'''
if IDs in js[keys[i]][0][3]:
    if 'nlx_only' in pre:
        continue
    if right != '':
        #output = make_records(r, rc, field_mapping)
        print('Fetching and data prep done.')
        #for id_, rec in output.items():
            #for field, value in rec:
                #print(field, value)
        node = make_node(pre, mid, right)
        print(node)
        #g.add_node(*node)
        print(g)
'''
    #g.write()
    #embed()

if __name__ == '__main__':
    main()
