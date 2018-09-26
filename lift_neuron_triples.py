#!/usr/bin/env python3

from pyontutils.neurons.lang import *
from pyontutils.core import OntTerm
from pyontutils.namespaces import NIFRID, ilxtr
from pyontutils.namespaces import hasRole, definition
from pyontutils.namespaces import makePrefixes, makeNamespaces
from pyontutils.closed_namespaces import rdf, rdfs, owl
import rdflib
from IPython import embed
from process_csv import _main
Config(name='neuron_data_lifted',
       imports=['https://raw.githubusercontent.com/SciCrunch/NIF-Ontology/neurons/ttl/generated/neurons/phenotype-direct.ttl',
                'https://raw.githubusercontent.com/SciCrunch/NIF-Ontology/neurons/ttl/phenotype-core.ttl',
                'https://raw.githubusercontent.com/SciCrunch/NIF-Ontology/neurons/ttl/phenotypes.ttl'])

query = OntTerm.query
#_main()

BIRNLEX, = makeNamespaces('BIRNLEX')

def oconvert(o):
    o = o.strip()
    if o == 'on':
        return ilxtr.ONspikesWithPhotons
    elif o == 'off':
        return ilxtr.OFFspikesWithoutPhotons
    elif o == 'principal':
        return ilxtr.ProjectionPhenotype
    elif o == 'intrinsic':
        return ilxtr.InterneuronPhenotype
    elif o == 'smooth':
        return False, ilxtr.SpinyPhenotype
    elif o == 'spiny':
        return ilxtr.SpinyPhenotype
    #elif o == 'medium':
        #return ilxtr.mediumQQQPhenotype
    elif o in ('broad', 'medium', 'small', 'large', 'simple', 'nociception'):  # TODO
        return 'TODO'

g = rdflib.Graph()
g.parse('/tmp/neuron_data_curated.ttl', format='turtle')

neurons = []
for class_ in g.subjects(rdflib.RDF.type, rdflib.OWL.Class):
    pes = []
    layers = []
    for p, o in g.predicate_objects(class_):
        if p == rdf.type:
            Neuron.out_graph.add((class_, p, o))
            continue
        elif p in (definition, rdfs.label, NIFRID.synonym):
            Neuron.out_graph.add((class_, p, o))
            continue
        elif p == hasRole and o == BIRNLEX['2533']:
            p, o = ilxtr.hasCircuitRolePhenotype, ilxtr.ProjectionPhenotype
        elif p == hasRole and o == BIRNLEX['2534']:
            p, o = ilxtr.hasCircuitRolePhenotype, ilxtr.InterneuronPhenotype
        elif p == ilxtr.hasSomaLocatedIn:
            term = OntTerm(o)
            if term.validated and term.deprecated:
                rb = term('replacedBy:')['replacedBy:']
                if rb:
                    o = OntTerm(rb[0])

        if isinstance(o, rdflib.Literal):
            try:
                ofix = oconvert(o)
                if ofix is not None and ofix != 'TODO':
                    o = ofix
                elif ofix == 'TODO':
                    print(f'TODO: {Neuron.ng.qname(p):<40}{o}')
                    continue
                else:
                    omatch = next(query(label=o)).OntTerm
                    print(f'TODO: {Neuron.ng.qname(p):<40}{o}\n\t{omatch!r}')
                    o = omatch
            except StopIteration:
                print(f'TODO: {Neuron.ng.qname(p):<40}{o}')
                continue
        try:
            if p == ilxtr.hasLayerLocationPhenotype:
                layers.append(Phenotype(o, p))
            elif isinstance(o, tuple) and not o[0]:
                pes.append(NegPhenotype(o[1], p))
            else:
                pes.append(Phenotype(o, p))
        except TypeError as e:
            print(p, o, e)
    if pes or layers:
        s = [p for p in pes if p.e == ilxtr.hasSomaLocatedIn]
        l = [p for p in pes if p.e == ilxtr.hasLocationPhenotype]
        if s and l:
            s0 = s[0]
            l0 = l[0]
            if str(s0.p) != str(l0.p):  # FIXME should not have to str these!
                print(f'WARNING: mismatch! {class_}\n{s[0]}\n{l[0]}')
                #raise ValueError(f'mismatch! {class_}\n{s[0]}\n{l[0]}')
                pes.remove(s0)
                pes.remove(l0)
                # swap
                pes.append(Phenotype(s0.p, l0.e))
                pes.append(Phenotype(l0.p, s0.e))
            else:
                pes.remove(l[0])

        if layers and len(layers) > 1:
            pes += [LogicalPhenotype(OR, *layers)]
        else:
            pes += layers

        origLabel = list(g.objects(class_, rdflib.RDFS.label))[0]
        try:
            n = Neuron(*pes, id_=class_, label=origLabel)
        except BaseException as e:
            print(class_)
            [print(pe) for pe in pes]
            raise e
        neurons.append(n)
        #print(n)

Neuron.write_python()
Neuron.write()
embed()

