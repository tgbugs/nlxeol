#!/usr/bin/env python3

import csv
import rdflib
from pyontutils.utils import makeGraph, rowParse
from IPython import embed

class convertCurated(rowParse):
    def __init__(self, graph, rows, header):
        self.graph = graph
        self.set_LocationOfAxonArborization = set()
        self.cat_id_dict = {}
        self.to_call = []
        self.fake_url_prefix = 'http://fake.org/'
        eval_first = ['FBbt_Id', 'Id', 'Category']
        super().__init__(rows, header, order=eval_first)
        [func(*args) for func, args in self.to_call]

    def _add_node(self, s, p, o):  # call for non Category/Id
        if o in self.cat_id_dict:
            o = self.cat_id_dict[o]
            self.graph.add_node(s, p, o)
        elif ':Category:' in o:  # FIXME need a way to identify putative objectProperties
            if (self._add_node, (s, p, o)) in self.to_call:
                self.graph.add_node(s, p, o)
                print('Failed to resolve reference to', o)
            else:
                self.to_call.append((self._add_node, (s, p, o)))
        else:
            self.graph.add_node(s, p, o)

    #def _translate_category_id(self, category):  # FIXME this fails when referencing later defined cats
        #if category in self.cat_id_dict:
            #return self.cat_id_dict[category]
        #else:
            #return category

    def Category(self, value):
        self.category = self.fake_url_prefix + value.replace(' ','_')
        if self.id_ is None:
            self.Id(self.category)
        self.cat_id_dict[self.category] = self.id_

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
                    if ')' in v:  # suuuper bad if you have (1,2,3) kind of things :/ probably need a special rule just for those
                        v = half + ',' + v
                        print('Bad split on comma detected!', v)
                    else:
                        half.strip()
                        self._add_node(self.id_, 'OBOANN:synonym', half)
                    
                    half = None

                v = v.strip()
                if v:
                    self._add_node(self.id_, 'OBOANN:synonym', v)

    def Id(self, value):
        if not value:
            self.id_ = None
        else:
            self.id_ = self.fake_url_prefix + value  # TODO need proper curie prefixes
            self.graph.add_node(self.id_, rdflib.RDF.type, rdflib.OWL.Class)
        #print(value)

    def PMID(self, value):
        #print(value)
        pass
    def DefiningCitation(self, value):
        #print(value)
        pass

    def SuperCategory(self, value):
        value = self.fake_url_prefix + ':Category:' + value.replace(' ','_')
        self._add_node(self.id_, rdflib.RDFS.subClassOf, value)

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
        #if value:
            #print(value)
        NONE = 'None'
        fixes = {
            ':Category:NA':NONE,
            ':Category:None':NONE,
            ':Category:No axon':NONE,
        }
        if value in fixes:
            value = fixes[value]

        self.set_LocationOfAxonArborization.add(value)

        to_skip = {':Category:NA', ':Category:None', ':Category:No axon', ''}

        if value in to_skip:
            pass
        else:
            #put_the_value_in_the_graph(value)
            for v in value.split(','):
                v.strip()
                self._add_node(self.id_, 'http://LocationOfAxonArborization', v)

    def LocationOfLocalAxonArborization(self, value): 
        if value:
            for v in value.split(','):
                v.strip()
                if v:
                    self._add_node(self.id_, 'http://LocationOfLocalAxonArborization', v)

    def DefiningCitation(self, value):
        #print(value)
        pass
    def OriginOfAxon(self, value): 
        #print(value)
        pass
    def Neurotransmitter(self, value):
        #if value:
            #print(value)
        pass
    def NeurotransmitterReceptors(self, value): 
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
    PREFIXES = {'to':'do','NLX':'http://fake.org/:Category:',
                'OBOANN':'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#',  # FIXME needs to die a swift death
               }
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
    #[print(i) for i in sorted(state.set_LocationOfAxonArborization)]
    new_graph.write()


if __name__ == '__main__':
    main()

