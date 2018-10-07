#!/usr/bin/env pypy3
#!/usr/bin/env python3.6

from pprint import pprint
from pyontutils.neurons.lang import *
from pyontutils.core import OntTerm, OntId
from pyontutils.utils import TermColors as tc
from pyontutils.scigraph import Graph
from pyontutils.namespaces import NIFRID, ilxtr
from pyontutils.namespaces import hasRole, definition
from pyontutils.namespaces import makePrefixes, makeNamespaces
from pyontutils.closed_namespaces import rdf, rdfs, owl
from pyontutils.phenotype_namespaces import BBP, CUT, Layers, Regions
import rdflib
from IPython import embed
from process_csv import _main
config = Config(name='neuron_data_lifted',
                ignore_existing=True,
                imports=['https://raw.githubusercontent.com/SciCrunch/NIF-Ontology/neurons/ttl/generated/neurons/phenotype-direct.ttl',
                         'https://raw.githubusercontent.com/SciCrunch/NIF-Ontology/neurons/ttl/phenotype-core.ttl',
                         'https://raw.githubusercontent.com/SciCrunch/NIF-Ontology/neurons/ttl/phenotypes.ttl'])
config.load_existing()
query = OntTerm.query
sgg = Graph()
BIRNLEX, = makeNamespaces('BIRNLEX')
repby = sgg.getEdges('IAO:0100001', limit=99999)
nifga_uberon = {e['sub']:e['obj'] for e in repby['edges'] if 'UBERON' in e['obj']}

mapping = dict(acetylcholine=OntTerm('SAO:185580330', label='Acetylcholine'),
               norepinephrine=OntTerm('NIFEXT:5013', label='Norepinephrine'),
               DB00368=OntTerm('NIFEXT:5013', label='Norepinephrine'),  # DB skipped in pcsv
               histamine=OntTerm('NIFEXT:5016', label='Histamine'),
               stellate=OntTerm('SAO:9271919883', label='Stellate'),  # may need a pheno repr of this?
               oxytocin=OntTerm('CHEBI:7872', label='oxytocin'),
               dopamine=OntTerm('CHEBI:18234', label='dopamine'),
               bistratified=OntTerm('ilxtr:BistratifiedPhenotype', label='Bistratified Phenotype'),
               motor=OntTerm('ilxtr:MotorPhenotype', label='Motor Phenotype'),
)
mapping.update({
    'cortical layer 2-3': Layers.L23,
    'cortical layer 5-6': Layers.L56,
    #'visual cortex primary  layer 5': (Layers.L5, Regions.V1), #OntTerm('NLX:143939'),
    'small pyramidal': OntTerm('ilxtr:SmallPyramidalPhenotype', label='Small Pyramidal Phenotype'),
    'cerebellar nuclei': OntTerm('UBERON:0002130', label='cerebellar nuclear complex'),
    'abducens nucleus': OntTerm('UBERON:0002682', label='abducens nucleus'),
})

direct_fix= dict(
    instrinsic=CUT.inter,
    interneuron=CUT.inter,
    ivy=BBP.IVY,
    thick=BBP.Th,
    trilaminar=BBP.TRI,
)
direct_fix.update({
    OntId('NLX:143939').iri: (Layers.L5, Regions.V1),
})

direct_fix = {k:v if isinstance(v, tuple) else (v,) for k, v in direct_fix.items()}

pofix = {
    ('ilxtr:hasContactWith', 'cone'): Phenotype('SAO:1103104164', 'ilxtr:hasContactWith'),
}
def poconvert(p, o):
    po = OntId(p).curie, str(o)
    if po in pofix:
        return pofix[po]

def oconvert(o):
    o = o.strip()

    if o == 'on':
        return ilxtr.ONspikesWithPhotons
    elif o == 'off':
        return ilxtr.OFFspikesWithoutPhotons
    elif o == 'principal':
        return ilxtr.ProjectionPhenotype
    elif o == 'projection':
        return ilxtr.ProjectionPhenotype
    elif o == 'intrinsic':
        return ilxtr.InterneuronPhenotype
    elif o == 'smooth':
        return False, ilxtr.SpinyPhenotype
    elif o == 'spiny':
        return ilxtr.SpinyPhenotype
    elif o == 'parvalbumin':
        return OntTerm('NIFEXT:6', label='Parvalbumin').u
    elif o == 'calbindin':
        return OntTerm('PR:000004967', label='calbindin').u
    elif o == 'GABA':
        return OntTerm('SAO:229636300', label='GABA').u
    elif o == 'calretinin':
        return OntTerm('NIFEXT:5', label='Calretinin').u
    elif o in mapping:
        v = mapping[o]
        if isinstance(v, OntTerm):
            return v.URIRef
        else:
            return v
    #elif o == 'medium':
        #return ilxtr.mediumQQQPhenotype
    elif o in ('broad', 'medium', 'small', 'large', 'simple', 'nociception', 'beaded'):  # TODO
        # FIXME there is the usual binding problem here, where these modify either
        # a neuron phenotype or a dendrite phenotype
        return 'TODO'

g = rdflib.Graph()
g.parse('/tmp/neuron_data_curated.ttl', format='turtle')

neurons = []
todo_report = set()
match_report = {}
for class_ in g.subjects(rdflib.RDF.type, rdflib.OWL.Class):
    pes = []
    layers = []
    origLabel = None
    for p, o in g.predicate_objects(class_):
        if p == rdf.type:
            Neuron.out_graph.add((class_, p, o))
            continue
        elif p in (definition,
                   NIFRID.synonym):
            Neuron.out_graph.add((class_, p, o))
            continue
        elif p == rdfs.label:
            origLabel = o
            continue
        elif p == hasRole and o == BIRNLEX['2533']:
            p, o = ilxtr.hasCircuitRolePhenotype, ilxtr.ProjectionPhenotype
        elif p == hasRole and o == BIRNLEX['2534']:
            p, o = ilxtr.hasCircuitRolePhenotype, ilxtr.InterneuronPhenotype
        elif p == ilxtr.hasSomaLocatedIn:
            term = OntTerm(o)
            if term.validated and term.deprecated:
                rb = term('replacedBy:')['replacedBy:']
                if rb and rb[0] is not None:
                    o = OntTerm(rb[0])

        pf = poconvert(p, o)
        if pf is not None:
            pes.append(pf)
            continue
        elif str(o) in direct_fix:
            pes.extend(direct_fix[str(o)])
            continue
        elif isinstance(o, rdflib.Literal):
            try:
                ofix = oconvert(o)
                if ofix is not None and ofix != 'TODO':
                    o = ofix
                elif ofix == 'TODO':
                    #print(tc.blue(f'TODO: {Neuron.ng.qname(p):<40}{o}'))
                    todo_report.add((o, p))
                    continue
                else:
                    omatch = next(query(label=o)).OntTerm
                    #omatch.set_next_repr('curie', 'label')
                    #print(tc.blue(f'TODO: {Neuron.ng.qname(p):<40}{o}\n\t{omatch!r}'))
                    t = omatch
                    if 'oboInOwl:id' in t.predicates:  # uberon replacement from ilx
                        t = OntTerm(t.predicates['oboInOwl:id'])
                        t('partOf:', 'rdfs:subClassOf', as_term=True)
                        if OntId('UBERON:0002301', label='layer of neocortex') in t.predicates['rdfs:subClassOf']:
                            region = t.predicates['partOf:']
                            t.predicates['rdfs:subClassOf']

                    match_report[o] = t
                    continue  # save them, but they are too diverse
                    o = t
            except StopIteration:
                todo_report.add((o, p))
                #print(tc.blue(f'TODO: {Neuron.ng.qname(p):<40}{o}'))
                continue
        try:
            if p == ilxtr.hasLayerLocationPhenotype:
                if isinstance(o, graphBase):  # pheno or logical
                    pes.append(o)
                elif isinstance(o, tuple) and all(isinstance(e, graphBase) for e in o):
                    pes.extend(o)
                else:
                    pheno = Phenotype(o, p)
                    layers.append(pheno)
            elif isinstance(o, tuple) and not o[0]:
                pes.append(NegPhenotype(o[1], p))
            else:
                label = o.label if isinstance(o, OntTerm) else None
                pes.append(Phenotype(o, p, label=label, override=bool(label)))
        except TypeError as e:
            print(__file__, e.__traceback__.tb_lineno, p, o, e)

    if pes or layers:
        s = [p for p in pes if p.e == ilxtr.hasSomaLocatedIn]
        _l = [p for p in pes if p.e == ilxtr.hasLocationPhenotype]
        l = [nifga_uberon[p.p] if
             p.p in nifga_uberon else
             p for p in _l]
        if s and l:
            s0 = s[0]
            l0 = l[0]
            if str(s0.p) != str(l0.p):  # FIXME should not have to str these!
                print(tc.yellow(f'WARNING: mismatch! {class_}\n{s[0]}\n{l[0]}'))
                #raise ValueError(f'mismatch! {class_}\n{s[0]}\n{l[0]}')
                pes.remove(s0)
                pes.remove(l0)
                # swap  # FIXME why are we doing this? TODO deal with redundant
                pes.append(Phenotype(s0.p, l0.e))
                #pes.append(Phenotype(l0.p, s0.e))
            else:
                pes.remove(l[0])

        if layers and len(layers) > 1:
            pes += [LogicalPhenotype(OR, *layers)]
        else:
            pes += layers

        try:
            n = Neuron(*pes, id_=class_, label=origLabel, override=True)
        except BaseException as e:
            print(class_)
            [print(pe) for pe in pes]
            raise e
        neurons.append(n)
        #print(n)

Neuron.write_python()
Neuron.write()
for o, p in sorted(todo_report, key=lambda t:t[::-1]):
    s = repr(str(o)) + ': ,'
    print(f'{s:<65}  # ' + repr(OntId(iri=p)))

OntTerm.repr_args = 'curie', 'label', #'definition'
pprint({str(k):v for k, v in match_report.items()})
embed()
