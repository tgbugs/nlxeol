#!/usr/bin/env python3

from pyontutils.neuron_lang import *
import rdflib
from IPython import embed

g = rdflib.Graph()
g.parse('/tmp/neuron_data_curated.ttl', format='turtle')

neurons = []
for class_ in g.subjects(rdflib.RDF.type, rdflib.OWL.Class):
    pes = []
    for p, o in g.predicate_objects(class_):
        if isinstance(o, rdflib.Literal):
            print('TODO', o)
            continue
        try:
            pes.append(Phenotype(o, p))
        except TypeError as e:
            print(e)
    if pes:
        n = Neuron(*pes)
        n._origLabel = list(g.objects(class_, rdflib.RDFS.label))[0]
        neurons.append(n)
        #print(n)

WRITEPYTHON(sorted(set(neurons)))
embed()

