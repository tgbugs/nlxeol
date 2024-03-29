#!/usr/bin/env python3
#!/usr/bin/env pypy3
"""Convert neuron classes from processed neurolex rdf into neurons

Usage:
    lift-neuron-triples [options]

Options:
    -d --debug    drop into debugger at end

"""

from pprint import pprint
from pathlib import Path
from neurondm.lang import *
from neurondm.core import log as _log
from neurondm.phenotype_namespaces import BBP, CUT, Layers, Regions
#from pyontutils.core import OntTerm, OntId  # via neurondm.lang
from pyontutils.utils import TermColors as tc
from pyontutils.config import auth
from pyontutils.scigraph import Graph
from pyontutils.namespaces import NIFRID, ilxtr
from pyontutils.namespaces import hasRole, definition
from pyontutils.namespaces import makePrefixes, makeNamespaces
from pyontutils.closed_namespaces import rdf, rdfs, owl
import rdflib
from process_csv import neurons_main
from docopt import docopt
args = docopt(__doc__)

log = _log.getChild('lnt')

config = Config(name='neuron_data_lifted',
                ignore_existing=True,
                imports=['NIFRAW:neurons/ttl/phenotype-core.ttl',
                         'NIFRAW:neurons/ttl/phenotypes.ttl'])
config.load_existing()
query = OntTerm.query
query.services[0].graph.parse(Path(auth.get_path('ontology-local-repo'), 'ttl/neurolex-fixes.ttl').as_posix(), format='ttl')
query.services[1].setup(instrumented=OntTerm)
sgg = query.services[1].sgg  #Graph()
BIRNLEX, = makeNamespaces('BIRNLEX')
repby = sgg.getEdges('IAO:0100001', limit=99999)
nifga_uberon = {e['sub']:e['obj'] for e in repby['edges'] if 'UBERON' in e['obj']}

do_union_locs = [OntId(i).u for i in
                 [
                     # taste buds have multiple locations
                     'NIFEXT:98',
                     'NIFEXT:99',
                     'SAO:709770772',  # hair cell, vestibular system was included because it is in the name
                     'NLX:151801',  # also hair cell
                     'NLX:144208',  # head direction, functional, thus many places
                     'NLXCELL:20081206',  # cajal ret, which exists in development and maybe adult? so union
                     'NLXCELL:091005',  # olfactory/pyriform cortex issues
                 ]]
# oval nucleus issues
# location terms are probably the same
# see https://github.com/SciCrunch/NIF-Ontology/issues/124#issuecomment-530649025
# the rest are handled below by location
bnstonfu = set(OntTerm(i).asPhenotype() for i in ['UBERON:0011176', 'UBERON:0023958'])
# visual cortex part of issue see
# https://github.com/obophenotype/uberon/pull/1512/files
visualfix = set(OntTerm(i).asPhenotype() for i in ['UBERON:0001950', 'UBERON:0002436'])
# https://github.com/obophenotype/uberon/issues/1513
cochfix = set(OntTerm(i).asPhenotype() for i in ['UBERON:0002227', 'UBERON:0001844'])
# if we were to merge all the graphs this would work, too much trouble at the moment
# this is a reminder that layers orthogonal to regions still needs work ...
# maybe use of hasPart is appropriate for this?
l5bfix = set(OntTerm(i).asPhenotype(predicate='ilxtr:hasSomaLocatedIn')
             for i in ['UBERON:0001950', 'NLX:151718', 'UBERON:0001384'])
apcfix = set(OntTerm(i).asPhenotype(predicate='ilxtr:hasSomaLocatedIn')
             for i in ['NLX:12056', 'UBERON:0002894'])
fixes = bnstonfu, visualfix, cochfix, l5bfix, apcfix

mapping = dict(acetylcholine=OntTerm('SAO:185580330', label='Acetylcholine'),
               norepinephrine=OntTerm('NIFEXT:5013', label='Norepinephrine'),
               DB00368=OntTerm('NIFEXT:5013', label='Norepinephrine'),  # DB skipped in pcsv
               DB00067=OntTerm('NIFEXT:5124', label='Vasopressin'),
               histamine=OntTerm('NIFEXT:5016', label='Histamine'),
               stellate=OntTerm('SAO:9271919883', label='Stellate'),  # may need a pheno repr of this?
               oxytocin=OntTerm('CHEBI:7872', label='oxytocin'),
               dopamine=OntTerm('CHEBI:18243', label='dopamine'),
               vasopressin=OntTerm('NIFEXT:5124', label='Vasopressin'),  # FIXME not in chebit?
               bistratified=OntTerm('ilxtr:BistratifiedPhenotype', label='Bistratified Phenotype'),
               motor=OntTerm('ilxtr:MotorPhenotype', label='Motor Phenotype'),
               postsubiculum=OntTerm('UBERON:0035971', label='postsubiculum'),
               medulla=OntTerm('UBERON:0001896', label='medulla oblongata'),
               rod=ilxtr.RodMorphologicalPhenotype,
               cone=ilxtr.ConeMorphologicalPhenotype,
)
mapping.update({
    'cortical layer 2-3': Layers.L23,
    'cortical layer 5-6': Layers.L56,
    #'visual cortex primary  layer 5': (Layers.L5, Regions.V1), #OntTerm('NLX:143939'),
    'small pyramidal': OntTerm('ilxtr:SmallPyramidalPhenotype', label='Small Pyramidal Phenotype'),
    'cerebellar nuclei': OntTerm('UBERON:0002130', label='cerebellar nuclear complex'),
    'abducens nucleus': OntTerm('UBERON:0002682', label='abducens nucleus'),
    'accessory nucleus': OntTerm('UBERON:0020358', label='accessory XI nerve nucleus'),
    'accumbens nucleus core': OntTerm('UBERON:0012170', label='core of nucleus accumbens'),
    'accumbens nucleus shell': OntTerm('UBERON:0012171', label='shell of nucleus accumbens'),
    'anterior piriform cortex': OntTerm('NLX:12056', label='Anterior piriform cortex'),  # TODO add to uberon?
    'superior colliculus stratum opticum': OntTerm('NLX:144109', label='Superior colliculus stratum opticum'),  # TODO add to uberon?
    'dorsal motor nucleus of the vagus nerve': OntTerm('UBERON:0002870', label='dorsal motor nucleus of vagus nerve'),
    'spinal cord intermediate horn': OntTerm('UBERON:0004676', label='spinal cord lateral horn'),  # synonym match
    'nitric oxide synthase brain': OntTerm('PR:000011326', label='nitric oxide synthase, brain'),
    })

# classification types
#  unfortunately for all of these classification type neurons the real
#  way we should be dealing with them is by constructing little local
#  naming systems, but that is a pain, technically the modelling is
#  correct, but it does conflate all types with a matching number
#  when we query, which isn't necessarily a bad thing it just has
#  arbitrary rather than biological meaning
ctypes = {
    'type 1': 'ilxtr:cell-classification-types/1',  # is it safe to I?
    'type 2': 'ilxtr:cell-classification-types/2',  # is it safe to II?
    'type 3': 'ilxtr:cell-classification-types/3',  # is it safe to III?
    'type 4': 'ilxtr:cell-classification-types/4',
    'type 5': 'ilxtr:cell-classification-types/5',
    'type 6': 'ilxtr:cell-classification-types/6',
    'type 7': 'ilxtr:cell-classification-types/7',
}
# yes we are normalizing Roman numerals to Arabic numerals, deal with it
ctypes['type I'] = ctypes['type 1']
ctypes['type II'] = ctypes['type 2']
ctypes['type III'] = ctypes['type 3']

mapping.update({k:OntTerm(v, label=k) for k, v in ctypes.items()})

direct_fix= dict(
    instrinsic=CUT.inter,
    interneuron=CUT.inter,
    ivy=BBP.IVY,
    thick=BBP.Th,
    trilaminar=BBP.TRI,
    tufted=BBP.Tu,
    nonpyramidal=NegPhenotype(ilxtr.PyramidalPhenotype, ilxtr.hasMorphologicalPhenotype),
)
direct_fix.update({
    'visual cortex primary layer 5': (Layers.L5, Regions.V1),
    'visual cortex primary layer 2-3': (Layers.L23, Regions.V1),
    OntId('NLX:143939').iri: (Layers.L5, Regions.V1),
})

direct_fix = {k:v if isinstance(v, tuple) else (v,) for k, v in direct_fix.items()}

pofix = {
    ('ilxtr:hasConnectionPhenotype', 'cone'): Phenotype('SAO:1103104164', 'ilxtr:hasConnectionPhenotype'),
    ('ilxtr:hasConnectionPhenotype', 'rod'): Phenotype('NLXCELL:100212', 'ilxtr:hasConnectionPhenotype'),

    # FIXME for motor would prefer to define this as hasProjectionTargetCellType some muscle ...
    (OntId('RO:0000087', label='has role').curie, OntTerm('NLX:54005', label='Motor role of nerve cell').iri):
    Phenotype(ilxtr.MotorPhenotype, ilxtr.hasCircuitRolePhenotype),
    ('ilxtr:hasCircuitRolePhenotype', 'motor'): Phenotype(ilxtr.MotorPhenotype, ilxtr.hasCircuitRolePhenotype),

    (OntId('RO:0000087', label='has role').curie, OntTerm('NLX:153', label='Sensory reception role').iri):
    # FIXME not clear that these should be in the defining criteria or whether they should be entailed criteria
    # ie, there is a larger question here, which is what subsets of phenotypes are sufficient to distinguish
    # a neuron type without requiring information from other modalities
    # NOTE: SensoryPhenotype is not a circuit role in the sense that it is not a projection phenotype
    # in the same way as the intrinsic and principle are ... maybe it is a dendrite phenotype?
    # eh, sensory neurons are weird
    Phenotype(ilxtr.SensoryPhenotype, ilxtr.hasCircuitRolePhenotype),
    ('ilxtr:hasCircuitRolePhenotype', 'sensory'): Phenotype(ilxtr.SensoryPhenotype, ilxtr.hasCircuitRolePhenotype),
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
        return ilxtr.IntrinsicPhenotype
    elif o == 'smooth':
        return False, ilxtr.SpinyPhenotype
    elif o == 'common spiny':  # common is a dead word, that probably indicates frequency of occurance
        return ilxtr.SpinyPhenotype
    elif o == 'spiny':
        return ilxtr.SpinyPhenotype
    elif o == 'inverted pyramidal':
        return ilxtr.InvertedPyramidalPhenotype
    elif o == 'parvalbumin':
        return OntTerm('PR:000013502', label='parvalbumin alpha').u
        #return OntTerm('NIFEXT:6', label='Parvalbumin').u
    elif o == 'calbindin':
        return OntTerm('PR:000004967', label='calbindin').u
    elif o == 'GABA':
        return OntTerm('SAO:229636300', label='GABA').u
    elif o == 'calretinin':
        return OntTerm('PR:000004968', label='calretinin').u
        #return OntTerm('NIFEXT:5', label='Calretinin').u
    elif o == 'melanopsin':  # FIXME synonym?
        return OntTerm('PR:000001243', label='opsin-4').u
    elif o == 'hydroxysteroid dehydrogenase type 2':  # FIXME synonym?
        return OntTerm('PR:000008772', label='corticosteroid 11-beta-dehydrogenase isozyme 2').u
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
need_to_indicator = set()
match_report = {}
for class_ in g.subjects(rdflib.RDF.type, rdflib.OWL.Class):
    pes = []
    layers = []
    locations = []
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
        elif p == ilxtr.neurolexCategory:
            continue
        elif p == hasRole and o == BIRNLEX['2533']:
            p, o = ilxtr.hasCircuitRolePhenotype, ilxtr.ProjectionPhenotype
        elif p == hasRole and o == BIRNLEX['2534']:
            p, o = ilxtr.hasCircuitRolePhenotype, ilxtr.IntrinsicPhenotype
        elif p in (ilxtr.hasSomaLocatedIn, ilxtr.hasAxonLocatedIn,
                   ilxtr.hasSomaLocatedInLayer, ilxtr.hasDendriteLocatedIn):
            stahp = False
            if p == ilxtr.hasAxonLocatedIn:
                _oid = OntId(o)
                if _oid.prefix == 'NLXCELL':
                    p, o = ilxtr.hasForwardConnectionPhenotype, o  # FIXME probably needs to be union of in these cases
                    stahp = True
                elif _oid.prefix == 'NIFEXT':
                    if OntId(_NEURON_CLASS) in _oid.asInstrumented()('rdfs:subClassOf', depth=10):
                        p, o = ilxtr.hasForwardConnectionPhenotype, o
                        stahp = True

            if not stahp:
                if type(o) == rdflib.URIRef and 'UBERON' not in o:
                    o = OntTerm(o).asPreferred().URIRef

                if isinstance(o, rdflib.Literal):
                    _so = str(o)
                    #if _so == 'accessory nucleus' or _so == 'anterior piriform cortex':
                        #breakpoint()
                    newo = oconvert(_so)
                    if newo != _so:
                        if isinstance(newo, Phenotype) or isinstance(newo, LogicalPhenotype):
                            pes.append(newo)
                            continue
                        if not isinstance(newo, rdflib.URIRef):
                            todo_report.add((o, p))
                            #print(tc.yellow(f'WARNING: literal for location! {o}'))
                            log.warning(f'literal for location! {o}')
                            continue

                        o = newo
                    elif _so not in match_report:
                        matches = list(OntTerm.query(term=_so, prefix='UBERON'))
                        if matches:
                            if len(matches) == 1:
                                matches = matches[0]

                            match_report[_so] = matches

                        log.warning(f'literal for location! {o}')
                        #print(tc.yellow(f'WARNING: literal for location! {o}'))
                        continue
                    else:
                        log.debug(f'{o!r}')

                if isinstance(o, OntTerm):
                    term = o
                else:
                    term = OntTerm(o)

                o = term.asPreferred()

                #if term.validated and term.deprecated:
                    #rb = term('replacedBy:') #['replacedBy:']
                    #if rb and rb[0] is not None:
                        #o = OntTerm(rb[0])

        elif p in graphBase._molecular_predicates:
            if isinstance(o, rdflib.Literal):
                maybe_o = oconvert(o)
                if maybe_o:
                    o = maybe_o
                else:
                    raise ValueError(o)

            term = OntTerm(o)
            o = term.asIndicator()
            if o == term:
                need_to_indicator.add(o)

        elif p == ilxtr.hasClassificationPhenotype:
            maybe_o = oconvert(o)
            if maybe_o:
                o = maybe_o

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
                    try:
                        omatch = next(query(label=o))
                    except StopIteration:
                        omatch = next(query(term=o))  # ok to go more general since we aren't autoinserting
                    #omatch.set_next_repr('curie', 'label')
                    #print(tc.blue(f'TODO: {Neuron.ng.qname(p):<40}{o}\n\t{omatch!r}'))
                    t = omatch
                    if 'oboInOwl:id' in t.predicates:  # uberon replacement from ilx
                        t = OntTerm(t.predicates['oboInOwl:id'])
                        t('partOf:', 'rdfs:subClassOf', asTerm=True)
                        if OntId('UBERON:0002301', label='layer of neocortex') in t.predicates['rdfs:subClassOf']:
                            region = t.predicates['partOf:']
                            t.predicates['rdfs:subClassOf']

                    match_report[o] = t
                    todo_report.add((o, p))  # stick it in for reference on the predicate
                    continue  # save them, but they are too diverse
                    o = t
            except StopIteration:
                todo_report.add((o, p))
                #print(tc.blue(f'TODO: {Neuron.ng.qname(p):<40}{o}'))
                continue
        try:
            if p == ilxtr.hasSomaLocatedInLayer:
                if isinstance(o, graphBase):  # pheno or logical
                    pes.append(o)
                elif isinstance(o, tuple) and all(isinstance(e, graphBase) for e in o):
                    pes.extend(o)
                else:
                    pheno = Phenotype(o, p)
                    layers.append(pheno)
            elif p == ilxtr.hasSomaLocatedIn:
                if isinstance(o, graphBase):  # pheno or logical
                    pes.append(o)
                elif isinstance(o, tuple) and all(isinstance(e, graphBase) for e in o):
                    pes.extend(o)
                else:
                    pheno = Phenotype(o, p)
                    locations.append(pheno)
            elif isinstance(o, tuple) and not o[0]:
                pes.append(NegPhenotype(o[1], p))
            else:
                label = o.label if isinstance(o, OntTerm) else None
                #log.debug(f'{o!r} {p!r}')
                pes.append(Phenotype(o, p, label=label, override=bool(label)))
        except TypeError as e:
            log.exception(e)
            log.error(f'{OntTerm(o)} {OntTerm(p)}')
            #print(*map(lambda s:tc.red(str(s)), (__file__, e.__traceback__.tb_lineno, OntTerm(p), OntTerm(o), '\n', e)))

    if locations:
        if class_ in do_union_locs or set(locations) in fixes:
            pes += [LogicalPhenotype(OR, *locations)]
        else:
            pes += locations

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
                #print(tc.yellow(f'WARNING: mismatch! {class_}\n{s[0]}\n{l[0]}'))
                log.warning('mismatch! {class_}\n{s[0]}\n{l[0]}')
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
    elif origLabel:
        Neuron.out_graph.add((class_, rdfs.label, origLabel))
        

Neuron.write_python()
Neuron.write()
for o, p in sorted(todo_report, key=lambda t:t[::-1]):
    s = repr(str(o)) + ': ,'
    print(f'{s:<65}  # ' + repr(OntId(iri=p)))

OntTerm.repr_args = 'curie', 'label', #'definition'
pprint({str(k):v for k, v in match_report.items()})
snti = sorted(need_to_indicator)
pref = [t.asPreferred() for t in snti]
other = {t:list(query(term=t.label)) if t.label else [t] for t in pref}
pprint(other)
if args['--debug']:
    breakpoint()
