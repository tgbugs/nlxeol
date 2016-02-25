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
'''
bad
('NIFGA:birnlex_2687', ':Category:Lateral amygdaloid nucleus'),
'''
ns=Namespace
cheatList = []

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

Cat_to_preID = [('NIFGA:birnlex_4129', ':Category:Dentate gyrus granule cell layer'), ('NIFGA:nlx_anat_1008005', ':Category:Dentate gyrus granule cell layer inner blade'), ('NIFGA:nlx_anat_1008006', ':Category:Dentate gyrus granule cell layer outer blade'), ('NIFGA:birnlex_4127', ':Category:Dentate gyrus molecular layer'), ('NIFGA:nlx_anat_1008004', ':Category:Dentate gyrus molecular layer inner'), ('NIFGA:nlx_anat_1008003', ':Category:Dentate gyrus molecular layer middle'), ('NIFGA:nlx_153848', ':Category:Dorsal cochlear nucleus pyramidal cell layer'), ('NIFGA:nlx_anat_090820', ':Category:Entorhinal cortex layer 1'), ('NIFGA:nlx_anat_090821', ':Category:Entorhinal cortex layer 2'), ('NIFGA:nlx_93650', ':Category:Entorhinal cortex layer 3'), ('NIFGA:nlx_39987', ':Category:Entorhinal cortex layer 4'), ('NIFGA:nlx_58', ':Category:Entorhinal cortex layer 5'), ('NIFGA:nlx_98', ':Category:Entorhinal cortex layer 6'), ('NIFGA:birnlex_779', ':Category:Granular layer of cerebellar cortex'), ('NIFGA:birnlex_1211', ':Category:Hippocampal molecular layer'), ('NIFGA:birnlex_790', ':Category:Inner granular layer of cerebellar cortex'), ('NIFGA:nlx_152619', ':Category:Lateral geniculate nucleus parvocellular layer'), ('NIFGA:birnlex_810', ':Category:Molecular layer of cerebellar cortex'), ('NIFGA:nlx_89', ':Category:Molecular layer of dorsal cochlear nucleus'), ('NIFGA:nlx_anat_090807', ':Category:Neocortex layer 1'), ('NIFGA:nlx_anat_090808', ':Category:Neocortex layer 2'), ('NIFGA:nlx_anat_090809', ':Category:Neocortex layer 3'), ('NIFGA:nlx_anat_090810', ':Category:Neocortex layer 4'), ('NIFGA:nlx_anat_090811', ':Category:Neocortex layer 5'), ('NIFGA:nlx_anat_090812', ':Category:Neocortex layer 6'), ('NIFGA:nlx_anat_1005002', ':Category:Olfactory bulb (accessory) mitral cell body layer'), ('NIFGA:nlx_152609', ':Category:Olfactory cortex layer 1'), ('NIFGA:nlx_152610', ':Category:Olfactory cortex layer 2'), ('NIFGA:birnlex_797', ':Category:Outer granular layer of cerebellar cortex'), ('NIFGA:nlx_anat_091003', ':Category:Piriform cortex layer 1'), ('NIFGA:nlx_anat_091006', ':Category:Piriform cortex layer 2'), ('NIFGA:nlx_anat_091007', ':Category:Piriform cortex layer 2a'), ('NIFGA:nlx_anat_091008', ':Category:Piriform cortex layer 2b'), ('NIFGA:nlx_anat_091009', ':Category:Piriform cortex layer 3'), ('NIFGA:nlx_152661', ':Category:Primary motor cortex layer 1'), ('NIFGA:nlx_144263', ':Category:Primary motor cortex layer 5'), ('NIFGA:nlx_144264', ':Category:Primary motor cortex layer 6'), ('NIFGA:birnlex_818', ':Category:Purkinje cell layer of cerebellar cortex'), ('NIFGA:nlx_93816', ':Category:Retina inner nuclear layer'), ('NIFGA:nlx_20558', ':Category:Retina inner plexiform layer'), ('NIFGA:birnlex_1359', ':Category:Stratum lacunosum moleculare'), ('NIFGA:nlx_144108', ':Category:Superior colliculus stratum zonale'), ('NIFGA:nlx_anat_1005034', ':Category:Superior colliculus superficial gray layer'), ('NIFGA:birnlex_1689', ':Category:Abducens nerve fibers'), ('NIFGA:birnlex_1277', ':Category:Abducens nerve root'), ('NIFGA:birnlex_1366', ':Category:Abducens nucleus'), ('NIFGA:birnlex_2686', ':Category:Accessory basal amygdaloid nucleus'), ('NIFGA:birnlex_2634', ':Category:Accessory cuneate nucleus'), ('NIFGA:birnlex_1626', ':Category:Accessory medullary lamina'), ('NIFGA:birnlex_916', ':Category:Accessory nerve fiber bundle'), ('NIFGA:birnlex_1581', ':Category:Adenohypophysis'), ('NIFGA:nlx_anat_20090509', ':Category:Aggregate regional part of brain'), ('NIFGA:birnlex_907', ':Category:Alar central lobule'), ('NIFGA:nlx_143557', ':Category:Allocortex'), ('NIFGA:birnlex_1510', ':Category:Alveus'), ('NIFGA:birnlex_1044', ':Category:Amiculum of dentate nucleus'), ('NIFGA:birnlex_1241', ':Category:Amygdala'), ('NIFGA:birnlex_1376', ':Category:Angular gyrus'), ('NIFGA:birnlex_1391', ':Category:Annectant gyrus'), ('NIFGA:nlx_anat_20081256', ':Category:Ansoparamedian fissure'), ('NIFGA:birnlex_2698', ':Category:Anterior amygdaloid area'), ('NIFGA:birnlex_936', ':Category:Anterior cingulate cortex'), ('NIFGA:birnlex_1603', ':Category:Anterior cingulate gyrus'), ('NIFGA:birnlex_731', ':Category:Anterior column of fornix'), ('NIFGA:birnlex_969', ':Category:Anterior commissure anterior part'), ('NIFGA:birnlex_1279', ':Category:Anterior horn of lateral ventricle'), ('NIFGA:birnlex_1005', ':Category:Anterior hypothalamic region'), ('NIFGA:nlx_144257', ':Category:Anterior limb of internal capsule'), ('NIFGA:birnlex_1118', ':Category:Anterior lobe of the cerebellum'), ('NIFGA:birnlex_1264', ':Category:Anterior median eminence'), ('NIFGA:birnlex_1445', ':Category:Anterior median oculomotor nucleus'), ('NIFGA:birnlex_1692', ':Category:Anterior nuclear group'), ('NIFGA:birnlex_1226', ':Category:Anterior nucleus of hypothalamus'), ('NIFGA:birnlex_1119', ':Category:Anterior nucleus of hypothalamus central part'), ('NIFGA:birnlex_1139', ':Category:Anterior nucleus of hypothalamus dorsal part'), ('NIFGA:birnlex_1125', ':Category:Anterior nucleus of hypothalamus posterior part'), ('NIFGA:birnlex_1085', ':Category:Anterior olfactory nucleus'), ('NIFGA:birnlex_1096', ':Category:Anterior perforated substance'), ('NIFGA:nlx_144456', ':Category:Anterior pretectal nucleus'), ('NIFGA:birnlex_913', ':Category:Anterior quadrangular lobule'), ('NIFGA:birnlex_1657', ':Category:Anterior transverse temporal gyrus'), ('NIFGA:birnlex_1358', ':Category:Anterodorsal nucleus'), ('NIFGA:birnlex_1600', ':Category:Anterodorsal nucleus of medial geniculate body'), ('NIFGA:birnlex_1365', ':Category:Anteromedial nucleus'), ('NIFGA:birnlex_2572', ':Category:Anteroventral cochlear nucleus'), ('NIFGA:birnlex_1372', ':Category:Anteroventral nucleus'), ('NIFGA:birnlex_1401', ':Category:Anteroventral periventricular nucleus'), ('NIFGA:nlx_anat_20090101', ':Category:Arbor Vitae'), ('NIFGA:birnlex_1638', ':Category:Arcuate nucleus of hypothalamus'), ('NIFGA:birnlex_2635', ':Category:Arcuate nucleus of medulla'), ('NIFGA:birnlex_1379', ':Category:Area X'), ('NIFGA:birnlex_2636', ':Category:Area postrema'), ('NIFGA:birnlex_862', ':Category:Banks of superior temporal sulcus'), ('NIFGA:nlx_81', ':Category:Barrel cortex'), ('NIFGA:birnlex_2692', ':Category:Basal amygdaloid nucleus'), ('NIFGA:birnlex_1560', ':Category:Basal forebrain'), ('NIFGA:birnlex_826', ':Category:Basal ganglia'), ('NIFGA:birnlex_1629', ':Category:Basal nuclear complex'), ('NIFGA:birnlex_1107', ':Category:Basal nucleus'), ('NIFGA:birnlex_1043', ':Category:Basal part of pons'), ('NIFGA:birnlex_2679', ':Category:Basolateral nuclear complex'), ('NIFGA:nlx_77783', ':Category:Bed nuclei of the stria terminalis oval nucleus'), ('NIFGA:birnlex_724', ':Category:Bed nucleus of stria terminalis'), ('NIFGA:birnlex_1217', ':Category:Body of caudate nucleus'), ('NIFGA:birnlex_739', ':Category:Body of fornix'), ('NIFGA:birnlex_1287', ':Category:Body of lateral ventricle'), ('NIFGA:birnlex_929', ':Category:Brachium of inferior colliculus'), ('NIFGA:birnlex_1065', ':Category:Brachium of superior colliculus'), ('NIFGA:birnlex_1565', ':Category:Brainstem'), ('NIFGA:birnlex_1197', ':Category:CA1'), ('NIFGA:nlx_anat_1005038', ':Category:CA1 alveus'), ('NIFGA:birnlex_4123', ':Category:CA1 stratum lacunosum moleculare'), ('NIFGA:birnlex_4116', ':Category:CA1 stratum oriens'), ('NIFGA:birnlex_4110', ':Category:CA1 stratum pyramidale'), ('NIFGA:birnlex_4119', ':Category:CA1 stratum radiatum'), ('NIFGA:birnlex_1362', ':Category:CA2'), ('NIFGA:birnlex_4124', ':Category:CA2 stratum lacunosum moleculare'), ('NIFGA:birnlex_4115', ':Category:CA2 stratum oriens'), ('NIFGA:birnlex_4111', ':Category:CA2 stratum pyramidale'), ('NIFGA:birnlex_4120', ':Category:CA2 stratum radiatum'), ('NIFGA:birnlex_1204', ':Category:CA3'), ('NIFGA:nlx_anat_1005039', ':Category:CA3 alveus'), ('NIFGA:birnlex_4125', ':Category:CA3 stratum lacunosum moleculare'), ('NIFGA:birnlex_4117', ':Category:CA3 stratum oriens'), ('NIFGA:birnlex_4112', ':Category:CA3 stratum pyramidale'), ('NIFGA:birnlex_4121', ':Category:CA3 stratum radiatum'), ('NIFGA:birnlex_1214', ':Category:Capsule of medial geniculate body'), ('NIFGA:birnlex_732', ':Category:Capsule of red nucleus'), ('NIFGA:birnlex_967', ':Category:Caudal anterior cingulate cortex'), ('NIFGA:birnlex_780', ':Category:Caudal central oculomotor nucleus'), ('NIFGA:birnlex_1083', ':Category:Caudal middle frontal gyrus'), ('NIFGA:birnlex_2637', ':Category:Caudal part of spinal trigeminal nucleus'), ('NIFGA:birnlex_1144', ':Category:Caudal part of ventral lateral nucleus'), ('NIFGA:birnlex_1681', ':Category:Caudal part of ventral posterolateral nucleus'), ('NIFGA:birnlex_792', ':Category:Caudal pontine reticular nucleus'), ('NIFGA:birnlex_1373', ':Category:Caudate nucleus'), ('NIFGA:nlx_anat_100312', ':Category:Caudoputamen'), ('NIFGA:birnlex_2682', ':Category:Central amygdaloid nucleus'), ('NIFGA:birnlex_956', ':Category:Central dorsal nucleus'), ('NIFGA:birnlex_2638', ':Category:Central gray substance of medulla'), ('NIFGA:birnlex_799', ':Category:Central gray substance of pons'), ('NIFGA:birnlex_961', ':Category:Central lateral nucleus'), ('NIFGA:birnlex_920', ':Category:Central lobule'), ('NIFGA:birnlex_971', ':Category:Central medial nucleus'), ('NIFGA:birnlex_1035', ':Category:Central nucleus of inferior colliculus'), ('NIFGA:birnlex_786', ':Category:Central oculomotor nucleus'), ('NIFGA:birnlex_1081', ':Category:Central tegmental tract of midbrain'), ('NIFGA:birnlex_1683', ':Category:Central tegmental tract of pons'), ('NIFGA:birnlex_805', ':Category:Centromedian nucleus'), ('NIFGA:nlx_anat_20081236', ':Category:Cerebellar Paravermis'), ('NIFGA:birnlex_1566', ':Category:Cerebellar cortex'), ('NIFGA:birnlex_1575', ':Category:Cerebellar hemisphere'), ('NIFGA:birnlex_970', ':Category:Cerebellar penducular complex'), ('NIFGA:birnlex_1562', ':Category:Cerebellar white matter'), ('NIFGA:birnlex_1489', ':Category:Cerebellum'), ('NIFGA:birnlex_1261', ':Category:Cerebral aqueduct'), ('NIFGA:birnlex_1494', ':Category:Cerebral cortex'), ('NIFGA:birnlex_1218', ':Category:Cerebral crus'), ('NIFGA:birnlex_1202', ':Category:Cerebral peduncle'), ('NIFGA:birnlex_711', ':Category:Cerebral white matter'), ('NIFGA:birnlex_1042', ':Category:Cerebrum'), ('NIFGA:nlx_anat_20090501', ':Category:Chemoarchitectural part'), ('NIFGA:nlx_anat_20090502', ':Category:Chemoarchitectural part of neostriatum'), ('NIFGA:nlx_27388', ':Category:Choroid plexus of fourth ventricle'), ('NIFGA:nlx_32548', ':Category:Choroid plexus of lateral ventricle'), ('NIFGA:nlx_18606', ':Category:Choroid plexus of third ventricle'), ('NIFGA:birnlex_934', ':Category:Cingulate cortex'), ('NIFGA:birnlex_798', ':Category:Cingulate gyrus'), ('NIFGA:nlx_anat_20090312', ':Category:Circumventricular organ'), ('NIFGA:birnlex_1515', ':Category:Claustral amygdaloid area'), ('NIFGA:birnlex_1522', ':Category:Claustrum'), ('NIFGA:birnlex_1151', ':Category:Cochlear nuclear complex'), ('NIFGA:nlx_144259', ':Category:Commissural nucleus of the solitary tract'), ('NIFGA:birnlex_2639', ':Category:Commissural nucleus of vagus nerve'), ('NIFGA:birnlex_1304', ':Category:Composite part spanning multiple base regional parts of brain'), ('NIFGA:nlx_anat_20090306', ':Category:Core of nucleus accumbens'), ('NIFGA:nlx_anat_090903', ':Category:Corona radiata'), ('NIFGA:birnlex_2700', ':Category:Cortical amygdaloid nucleus'), ('NIFGA:birnlex_2680', ':Category:Corticomedial nuclear complex'), ('NIFGA:birnlex_1016', ':Category:Corticotectal tract'), ('NIFGA:nlx_28532', ':Category:Cranial nerve nucleus'), ('NIFGA:birnlex_926', ':Category:Culmen'), ('NIFGA:birnlex_1242', ':Category:Cuneate fasciculus of medulla'), ('NIFGA:birnlex_2640', ':Category:Cuneate nucleus'), ('NIFGA:birnlex_1430', ':Category:Cuneiform nucleus'), ('NIFGA:birnlex_1238', ':Category:Cuneocerebellar tract'), ('NIFGA:birnlex_1396', ':Category:Cuneus cortex'), ('NIFGA:birnlex_1192', ':Category:Cytoarchitectural fields of hippocampal formation'), ('NIFGA:birnlex_4126', ':Category:Cytoarchitectural part of dentate gyrus'), ('NIFGA:birnlex_1568', ':Category:Deep cerebellar nuclear complex'), ('NIFGA:birnlex_1255', ':Category:Densocellular part of medial dorsal nucleus'), ('NIFGA:birnlex_1178', ':Category:Dentate gyrus'), ('NIFGA:birnlex_1482', ':Category:Dentate gyrus hilus'), ('NIFGA:birnlex_4127', ':Category:Dentate gyrus molecular layer'), ('NIFGA:birnlex_1171', ':Category:Dentate nucleus'), ('NIFGA:birnlex_1104', ':Category:Dentatothalamic tract'), ('NIFGA:birnlex_1551', ':Category:Diagonal band'), ('NIFGA:birnlex_1503', ':Category:Diencephalon'), ('NIFGA:birnlex_1022', ':Category:Distal part of hypophysis'), ('NIFGA:nlx_anat_100310', ':Category:Dorsal accessory olive'), ('NIFGA:birnlex_1698', ':Category:Dorsal acoustic stria'), ('NIFGA:birnlex_2569', ':Category:Dorsal cochlear nucleus'), ('NIFGA:nlx_144463', ':Category:Dorsal commissural nucleus'), ('NIFGA:birnlex_1250', ':Category:Dorsal external arcuate fiber bundle'), ('NIFGA:birnlex_777', ':Category:Dorsal hypothalamic area'), ('NIFGA:birnlex_986', ':Category:Dorsal longitudinal fasciculus'), ('NIFGA:birnlex_898', ':Category:Dorsal longitudinal fasciculus of hypothalamus'), ('NIFGA:birnlex_1257', ':Category:Dorsal longitudinal fasciculus of medulla'), ('NIFGA:birnlex_893', ':Category:Dorsal longitudinal fasciculus of midbrain'), ('NIFGA:birnlex_1707', ':Category:Dorsal longitudinal fasciculus of pons'), ('NIFGA:birnlex_2642', ':Category:Dorsal motor nucleus of vagus nerve'), ('NIFGA:birnlex_1595', ':Category:Dorsal nucleus of lateral geniculate body'), ('NIFGA:birnlex_894', ':Category:Dorsal nucleus of lateral lemniscus'), ('NIFGA:birnlex_1608', ':Category:Dorsal nucleus of medial geniculate body'), ('NIFGA:birnlex_2575', ':Category:Dorsal nucleus of trapezoid body'), ('NIFGA:birnlex_793', ':Category:Dorsal oculomotor nucleus'), ('NIFGA:birnlex_982', ':Category:Dorsal raphe nucleus'), ('NIFGA:birnlex_704', ':Category:Dorsal septal nucleus'), ('NIFGA:birnlex_992', ':Category:Dorsal tegmental nucleus'), ('NIFGA:nlx_anat_20090407', ':Category:Dorsal tegmental nucleus pars dorsalis'), ('NIFGA:nlx_anat_20090408', ':Category:Dorsal tegmental nucleus pars ventralis'), ('NIFGA:birnlex_1718', ':Category:Dorsal trigeminal tract'), ('NIFGA:birnlex_1558', ':Category:Dorsomedial nucleus of hypothalamus'), ('NIFGA:birnlex_1135', ':Category:Emboliform nucleus'), ('NIFGA:nlx_anat_091033', ':Category:Endopiriform nucleus'), ('NIFGA:birnlex_1508', ':Category:Entorhinal cortex'), ('NIFGA:birnlex_1710', ':Category:Epithalamus'), ('NIFGA:birnlex_1047', ':Category:External nucleus of inferior colliculus'), ('NIFGA:nlx_anat_200905010', ':Category:Extrastriate cortex'), ('NIFGA:birnlex_1513', ':Category:Facial nerve root'), ('NIFGA:birnlex_903', ':Category:Facial nucleus'), ('NIFGA:birnlex_872', ':Category:Fasciculus'), ('NIFGA:birnlex_1129', ':Category:Fasciolar gyrus'), ('NIFGA:birnlex_1146', ':Category:Fastigial nucleus'), ('NIFGA:birnlex_1502', ':Category:Fimbria of hippocampus'), ('NIFGA:birnlex_904', ':Category:Flocculonodular lobe'), ('NIFGA:birnlex_1329', ':Category:Flocculus'), ('NIFGA:birnlex_1509', ':Category:Forebrain'), ('NIFGA:birnlex_705', ':Category:Fornix'), ('NIFGA:birnlex_1256', ':Category:Fourth ventricle'), ('NIFGA:nlx_anat_20090601', ':Category:Frontal cortex'), ('NIFGA:birnlex_928', ':Category:Frontal lobe'), ('NIFGA:birnlex_751', ':Category:Frontal operculum'), ('NIFGA:birnlex_1716', ':Category:Frontal pole'), ('NIFGA:birnlex_1243', ':Category:Fronto-orbital gyrus'), ('NIFGA:nlx_144261', ':Category:Fundus striati'), ('NIFGA:birnlex_1641', ':Category:Fusiform gyrus'), ('NIFGA:nlx_144462', ':Category:Genu of corpus callosum'), ('NIFGA:birnlex_1158', ':Category:Globose nucleus'), ('NIFGA:birnlex_1234', ':Category:Globus pallidus'), ('NIFGA:birnlex_1610', ':Category:Globus pallidus external segment'), ('NIFGA:birnlex_1555', ':Category:Globus pallidus internal segment'), ('NIFGA:birnlex_1274', ':Category:Glossopharyngeal nerve fiber bundle'), ('NIFGA:birnlex_1282', ':Category:Gracile fasciculus of medulla'), ('NIFGA:birnlex_2643', ':Category:Gracile nucleus'), ('NIFGA:birnlex_996', ':Category:Gross anatomical parts of the cerebellum'), ('NIFGA:birnlex_1103', ':Category:Gyrus rectus'), ('NIFGA:birnlex_1611', ':Category:Habenula'), ('NIFGA:birnlex_1176', ':Category:Habenulo-interpeduncular tract of diencephalon'), ('NIFGA:birnlex_895', ':Category:Habenulo-interpeduncular tract of midbrain'), ('NIFGA:birnlex_1212', ':Category:Head of caudate nucleus'), ('NIFGA:birnlex_1796', ':Category:Hemisphere of cerebral cortex'), ('NIFGA:nlx_anat_20081202', ':Category:Hemispheric Lobule II'), ('NIFGA:nlx_anat_20081203', ':Category:Hemispheric Lobule III'), ('NIFGA:nlx_anat_20081204', ':Category:Hemispheric Lobule IV'), ('NIFGA:nlx_anat_20081212', ':Category:Hemispheric Lobule IX'), ('NIFGA:nlx_anat_20081205', ':Category:Hemispheric Lobule V'), ('NIFGA:nlx_anat_20081206', ':Category:Hemispheric Lobule VI'), ('NIFGA:nlx_anat_20081207', ':Category:Hemispheric Lobule VII'), ('NIFGA:nlx_anat_20081208', ':Category:Hemispheric Lobule VIIA'), ('NIFGA:nlx_anat_20081209', ':Category:Hemispheric Lobule VIIBi'), ('NIFGA:nlx_anat_20081210', ':Category:Hemispheric Lobule VIIBii'), ('NIFGA:nlx_anat_20081213', ':Category:Hemispheric Lobule X'), ('NIFGA:nlx_anat_20081211', ':Category:Hemispheric lobule VIII'), ('NIFGA:birnlex_1339', ':Category:Hemispheric part of the anterior lobe of the cerebellum'), ('NIFGA:nlx_anat_20081260', ':Category:Hemispheric part of the flocculonodular lobe of the cerebellum'), ('NIFGA:nlx_anat_20081261', ':Category:Hemispheric part of the posterior lobe of the cerebellum'), ('NIFGA:birnlex_1334', ':Category:Hemispheric parts of the cerebellar cortex'), ('NIFGA:birnlex_1561', ':Category:Hilum of dentate nucleus'), ('NIFGA:birnlex_942', ':Category:Hindbrain'), ('NIFGA:birnlex_715', ':Category:Hippocampal formation'), ('NIFGA:birnlex_721', ':Category:Hippocampus'), ('NIFGA:nlx_anat_20081255', ':Category:Horizontal fissure'), ('NIFGA:birnlex_1288', ':Category:Hypoglossal nerve fiber bundle'), ('NIFGA:birnlex_2644', ':Category:Hypoglossal nucleus'), ('NIFGA:birnlex_1353', ':Category:Hypophysis'), ('NIFGA:birnlex_734', ':Category:Hypothalamus'), ('NIFGA:nlx_49940', ':Category:Induseum griseum'), ('NIFGA:birnlex_4021', ':Category:Inferior calcarine sulcus'), ('NIFGA:birnlex_861', ':Category:Inferior central nucleus'), ('NIFGA:birnlex_1691', ':Category:Inferior cerebellar peduncle'), ('NIFGA:birnlex_806', ':Category:Inferior colliculus'), ('NIFGA:birnlex_873', ':Category:Inferior frontal gyrus'), ('NIFGA:birnlex_1292', ':Category:Inferior horn of the lateral ventricle'), ('NIFGA:birnlex_1399', ':Category:Inferior occipital gyrus'), ('NIFGA:birnlex_4020', ':Category:Inferior occipital sulcus'), ('NIFGA:birnlex_1164', ':Category:Inferior olivary complex'), ('NIFGA:birnlex_1194', ':Category:Inferior parietal cortex'), ('NIFGA:birnlex_830', ':Category:Inferior pulvinar nucleus'), ('NIFGA:birnlex_1447', ':Category:Inferior rostral gyrus'), ('NIFGA:birnlex_1577', ':Category:Inferior temporal gyrus'), ('NIFGA:birnlex_1064', ':Category:Inferior transverse frontopolar gyrus'), ('NIFGA:birnlex_1248', ':Category:Infundibular stem'), ('NIFGA:birnlex_1117', ':Category:Insula'), ('NIFGA:birnlex_2683', ':Category:Intercalated amygdaloid nuclei'), ('NIFGA:birnlex_768', ':Category:Intermediate acoustic stria'), ('NIFGA:birnlex_1015', ':Category:Intermediate hypothalamic region'), ('NIFGA:birnlex_803', ':Category:Intermediate oculomotor nucleus'), ('NIFGA:birnlex_1247', ':Category:Intermediate orbital gyrus'), ('NIFGA:birnlex_906', ':Category:Intermediate part of hypophysis'), ('NIFGA:birnlex_1564', ':Category:Intermediate periventricular nucleus'), ('NIFGA:birnlex_1091', ':Category:Internal arcuate fiber bundle'), ('NIFGA:birnlex_1659', ':Category:Internal capsule'), ('NIFGA:birnlex_1621', ':Category:Internal medullary lamina of thalamus'), ('NIFGA:birnlex_1000', ':Category:Interpeduncular nucleus'), ('NIFGA:birnlex_2646', ':Category:Interpolar part of spinal trigeminal nucleus'), ('NIFGA:nlx_anat_20081242', ':Category:Interpositus Nucleus'), ('NIFGA:birnlex_1008', ':Category:Interstitial nucleus of Cajal'), ('NIFGA:birnlex_1530', ':Category:Intralaminar nuclear group'), ('NIFGA:birnlex_4019', ':Category:Intralingual sulcus'), ('NIFGA:nlx_55138', ':Category:Isla magna of Calleja'), ('NIFGA:birnlex_1113', ':Category:Islands of Calleja'), ('NIFGA:nlx_50741', ':Category:Islands of Calleja of olfactory tubercle'), ('NIFGA:birnlex_1541', ':Category:Isthmus of cingulate gyrus'), ('NIFGA:birnlex_1101', ':Category:Juxtarestiform body'), ('NIFGA:birnlex_2641', ':Category:Kolliker-Fuse nucleus'), ('NIFGA:birnlex_1554', ':Category:Lamina of septum pellucidum'), ('NIFGA:birnlex_2689', ':Category:Lateral amygdaloid nucleus, dorsolateral part'), ('NIFGA:birnlex_2690', ':Category:Lateral amygdaloid nucleus, ventrolateral part'), ('NIFGA:birnlex_2691', ':Category:Lateral amygdaloid nucleus, ventromedial part'), ('NIFGA:birnlex_1662', ':Category:Lateral geniculate nucleus'), ('NIFGA:birnlex_1438', ':Category:Lateral habenular nucleus'), ('NIFGA:birnlex_4037', ':Category:Lateral hypothalamic area'), ('NIFGA:birnlex_1199', ':Category:Lateral hypothalamic nucleus'), ('NIFGA:birnlex_976', ':Category:Lateral lemniscus (birnlex 976)'), ('NIFGA:birnlex_1460', ':Category:Lateral mammillary nucleus'), ('NIFGA:birnlex_1634', ':Category:Lateral medullary lamina'), ('NIFGA:birnlex_1537', ':Category:Lateral nuclear group'), ('NIFGA:nlx_54921', ':Category:Lateral nucleus of stria terminalis'), ('NIFGA:birnlex_735', ':Category:Lateral occipital cortex'), ('NIFGA:birnlex_4018', ':Category:Lateral occipital sulcus'), ('NIFGA:birnlex_1244', ':Category:Lateral orbital frontal cortex'), ('NIFGA:birnlex_1036', ':Category:Lateral orbital gyrus'), ('NIFGA:birnlex_897', ':Category:Lateral parabrachial nucleus'), ('NIFGA:nlx_143582', ':Category:Lateral paragigantocellular nucleus'), ('NIFGA:birnlex_2695', ':Category:Lateral part of basal amygdaloid nucleus'), ('NIFGA:birnlex_1314', ':Category:Lateral part of medial mammillary nucleus'), ('NIFGA:birnlex_2647', ':Category:Lateral pericuneate nucleus'), ('NIFGA:birnlex_902', ':Category:Lateral pes lemniscus'), ('NIFGA:birnlex_835', ':Category:Lateral posterior nucleus'), ('NIFGA:birnlex_1722', ':Category:Lateral preoptic nucleus'), ('NIFGA:birnlex_1228', ':Category:Lateral pulvinar nucleus'), ('NIFGA:nlx_anat_20081246', ':Category:Lateral reticular nucleus'), ('NIFGA:birnlex_1321', ':Category:Lateral septal nucleus'), ('NIFGA:birnlex_1675', ':Category:Lateral superior olivary nucleus'), ('NIFGA:birnlex_1206', ':Category:Lateral tuberal nuclear complex'), ('NIFGA:birnlex_1263', ':Category:Lateral ventricle'), ('NIFGA:nlx_144002', ':Category:Lateral vestibular nucleus'), ('NIFGA:birnlex_1795', ':Category:Left cerebral hemisphere'), ('NIFGA:birnlex_1787', ':Category:Left frontal lobe'), ('NIFGA:birnlex_1780', ':Category:Left limbic lobe'), ('NIFGA:birnlex_1782', ':Category:Left occipital lobe'), ('NIFGA:birnlex_1728', ':Category:Left parietal lobe'), ('NIFGA:birnlex_1789', ':Category:Left sub-lobar region'), ('NIFGA:birnlex_1784', ':Category:Left temporal lobe'), ('NIFGA:birnlex_881', ':Category:Lemniscus'), ('NIFGA:birnlex_1128', ':Category:Limbic lobe'), ('NIFGA:birnlex_1493', ':Category:Limen of insula'), ('NIFGA:birnlex_931', ':Category:Limitans nucleus'), ('NIFGA:birnlex_1018', ':Category:Linear nucleus'), ('NIFGA:birnlex_740', ':Category:Lingual gyrus'), ('NIFGA:birnlex_932', ':Category:Lingula'), ('NIFGA:birnlex_1267', ":Category:Lissauer's tract of medulla"), ('NIFGA:birnlex_922', ':Category:Lobe of cerebral cortex'), ('NIFGA:birnlex_1076', ':Category:Lobe parts of the cerebellar cortex'), ('NIFGA:birnlex_1084', ':Category:Lobular parts of the cerebellar cortex'), ('NIFGA:birnlex_905', ':Category:Locus ceruleus'), ('NIFGA:birnlex_1523', ':Category:Longitudinal pontine fibers'), ('NIFGA:birnlex_4017', ':Category:Lunate sulcus'), ('NIFGA:birnlex_1612', ':Category:Magnocellular nucleus of medial geniculate body'), ('NIFGA:birnlex_1262', ':Category:Magnocellular part of medial dorsal nucleus'), ('NIFGA:birnlex_720', ':Category:Magnocellular part of red nucleus'), ('NIFGA:birnlex_716', ':Category:Magnocellular part of ventral anterior nucleus'), ('NIFGA:birnlex_865', ':Category:Mammillary body'), ('NIFGA:birnlex_1486', ':Category:Mammillary peduncle'), ('NIFGA:birnlex_855', ':Category:Mammillothalamic tract of hypothalamus'), ('NIFGA:nlx_anat_20090504', ':Category:Matrix compartment of caudate nucleus'), ('NIFGA:nlx_anat_20090503', ':Category:Matrix compartment of neostriatum'), ('NIFGA:nlx_anat_1010005', ':Category:Matrix part of head of caudate nucleus'), ('NIFGA:nlx_anat_1010006', ':Category:Matrix part of tail of caudate nucleus'), ('NIFGA:nlx_anat_100309', ':Category:Medial accessory olive'), ('NIFGA:birnlex_1543', ':Category:Medial dorsal nucleus'), ('NIFGA:birnlex_908', ':Category:Medial forebrain bundle'), ('NIFGA:birnlex_1670', ':Category:Medial geniculate body'), ('NIFGA:birnlex_1431', ':Category:Medial habenular nucleus'), ('NIFGA:birnlex_1570', ':Category:Medial lemniscus of medulla'), ('NIFGA:birnlex_1296', ':Category:Medial lemniscus of midbrain'), ('NIFGA:birnlex_781', ':Category:Medial lemniscus of pons'), ('NIFGA:birnlex_1574', ':Category:Medial longitudinal fasciculus of medulla'), ('NIFGA:birnlex_1302', ':Category:Medial longitudinal fasciculus of midbrain'), ('NIFGA:birnlex_1708', ':Category:Medial longitudinal fasciculus of pons'), ('NIFGA:birnlex_1299', ':Category:Medial mammillary nucleus'), ('NIFGA:birnlex_1501', ':Category:Medial medullary lamina'), ('NIFGA:nlx_80623', ':Category:Medial nucleus of stria terminalis'), ('NIFGA:birnlex_2595', ':Category:Medial nucleus of trapezoid body'), ('NIFGA:birnlex_813', ':Category:Medial oculomotor nucleus'), ('NIFGA:birnlex_1127', ':Category:Medial olfactory gyrus'), ('NIFGA:birnlex_1249', ':Category:Medial orbital frontal cortex'), ('NIFGA:birnlex_1046', ':Category:Medial orbital gyrus'), ('NIFGA:birnlex_4038', ':Category:Medial parabrachial nucleus'), ('NIFGA:birnlex_2696', ':Category:Medial part of basal amygdaloid nucleus'), ('NIFGA:birnlex_1220', ':Category:Medial part of medial mammillary nucleus'), ('NIFGA:birnlex_1159', ':Category:Medial part of ventral lateral nucleus'), ('NIFGA:birnlex_2648', ':Category:Medial pericuneate nucleus'), ('NIFGA:birnlex_1310', ':Category:Medial pes lemniscus'), ('NIFGA:birnlex_706', ':Category:Medial preoptic nucleus'), ('NIFGA:birnlex_1233', ':Category:Medial pulvinar nucleus'), ('NIFGA:birnlex_1668', ':Category:Medial septal nucleus'), ('NIFGA:birnlex_2662', ':Category:Medial subnucleus of solitary tract'), ('NIFGA:birnlex_1682', ':Category:Medial superior olivary nucleus'), ('NIFGA:birnlex_1074', ':Category:Medial transverse frontopolar gyrus'), ('NIFGA:nlx_22533', ':Category:Medial ventral tegmental area'), ('NIFGA:birnlex_925', ':Category:Median eminence'), ('NIFGA:birnlex_1208', ':Category:Median preoptic nucleus'), ('NIFGA:birnlex_957', ':Category:Medulla oblongata'), ('NIFGA:birnlex_2649', ':Category:Medullary anterior horn'), ('NIFGA:birnlex_1420', ':Category:Medullary raphe nuclear complex'), ('NIFGA:birnlex_1020', ':Category:Medullary reticular formation'), ('NIFGA:birnlex_1414', ':Category:Medullary white matter'), ('NIFGA:birnlex_1010', ':Category:Mesencephalic nucleus of trigeminal nerve'), ('NIFGA:birnlex_1318', ':Category:Mesencephalic tract of trigeminal nerve'), ('NIFGA:birnlex_1461', ':Category:Metathalamus'), ('NIFGA:birnlex_965', ':Category:Metencephalon'), ('NIFGA:birnlex_1667', ':Category:Midbrain'), ('NIFGA:birnlex_1676', ':Category:Midbrain raphe nuclei'), ('NIFGA:birnlex_1235', ':Category:Midbrain reticular formation'), ('NIFGA:birnlex_1032', ':Category:Midbrain tectum'), ('NIFGA:birnlex_1200', ':Category:Midbrain tegmentum'), ('NIFGA:birnlex_1529', ':Category:Middle cerebellar peduncle'), ('NIFGA:birnlex_1451', ':Category:Middle frontal gyrus'), ('NIFGA:nlx_anat_20090308', ':Category:Middle temporal area'), ('NIFGA:birnlex_1653', ':Category:Middle temporal gyrus'), ('NIFGA:birnlex_1462', ':Category:Midline nuclear group'), ('NIFGA:nlx_89', ':Category:Molecular layer of dorsal cochlear nucleus'), ('NIFGA:birnlex_1222', ':Category:Motor nucleus of trigeminal nerve'), ('NIFGA:birnlex_1717', ':Category:Motor root of trigeminal nerve'), ('NIFGA:birnlex_2547', ':Category:Neocortex'), ('NIFGA:birnlex_1567', ':Category:Neodentate part of dentate nucleus'), ('NIFGA:birnlex_1586', ':Category:Neurohypophysis'), ('NIFGA:birnlex_1165', ':Category:Nodulus'), ('NIFGA:birnlex_727', ':Category:Nucleus accumbens'), ('NIFGA:birnlex_2650', ':Category:Nucleus ambiguus'), ('NIFGA:nlx_anat_1005001', ':Category:Nucleus gigantocellularis'), ('NIFGA:birnlex_2654', ':Category:Nucleus intercalatus'), ('NIFGA:nlx_28443', ':Category:Nucleus of CNS'), ('NIFGA:birnlex_896', ':Category:Nucleus of Darkschewitsch'), ('NIFGA:birnlex_712', ':Category:Nucleus of anterior commissure'), ('NIFGA:birnlex_719', ':Category:Nucleus of diagonal band'), ('NIFGA:birnlex_2702', ':Category:Nucleus of lateral olfactory tract'), ('NIFGA:birnlex_870', ':Category:Nucleus of medial eminence'), ('NIFGA:birnlex_868', ':Category:Nucleus of optic tract'), ('NIFGA:birnlex_1470', ':Category:Nucleus of posterior commissure'), ('NIFGA:birnlex_864', ':Category:Nucleus of pretectal area'), ('NIFGA:nlx_143549', ':Category:Nucleus paramedianus dorsalis'), ('NIFGA:birnlex_2652', ':Category:Nucleus prepositus'), ('NIFGA:birnlex_1363', ':Category:Nucleus raphe magnus'), ('NIFGA:birnlex_1369', ':Category:Nucleus raphe obscurus'), ('NIFGA:birnlex_1375', ':Category:Nucleus raphe pallidus'), ('NIFGA:birnlex_1088', ':Category:Nucleus subceruleus'), ('NIFGA:birnlex_747', ':Category:Occipital gyrus'), ('NIFGA:birnlex_1136', ':Category:Occipital lobe'), ('NIFGA:birnlex_4016', ':Category:Occipital pole'), ('NIFGA:birnlex_1323', ':Category:Oculomotor nerve fibers'), ('NIFGA:birnlex_1240', ':Category:Oculomotor nuclear complex'), ('NIFGA:birnlex_1137', ':Category:Olfactory bulb'), ('NIFGA:nlx_53', ':Category:Olfactory bulb accessory nucleus'), ('NIFGA:nlx_anat_1005011', ':Category:Olfactory bulb main glomerular layer'), ('NIFGA:nlx_anat_100201', ':Category:Olfactory bulb main mitral cell body layer'), ('NIFGA:nlx_anat_1005019', ':Category:Olfactory bulb main of rodent'), ('NIFGA:nlx_anat_1005010', ':Category:Olfactory bulb main olfactory nerve layer'), ('NIFGA:birnlex_2707', ':Category:Olfactory cortex'), ('NIFGA:birnlex_2705', ':Category:Olfactory entorhinal cortex'), ('NIFGA:birnlex_4042', ':Category:Olfactory trigone'), ('NIFGA:birnlex_1037', ':Category:Olivary pretectal nucleus'), ('NIFGA:birnlex_823', ':Category:Opercular part of inferior frontal gyrus'), ('NIFGA:birnlex_1416', ':Category:Optic chiasm'), ('NIFGA:nlx_144280', ':Category:Optic recess of third ventricle'), ('NIFGA:birnlex_1100', ':Category:Oral part of spinal trigeminal nucleus'), ('NIFGA:birnlex_817', ':Category:Oral part of ventral lateral nucleus'), ('NIFGA:birnlex_918', ':Category:Oral part of ventral posterolateral nucleus'), ('NIFGA:birnlex_875', ':Category:Oral pontine reticular nucleus'), ('NIFGA:birnlex_1239', ':Category:Oral pulvinar nucleus'), ('NIFGA:birnlex_1049', ':Category:Orbital frontal cortex'), ('NIFGA:birnlex_1223', ':Category:Orbital gyri complex'), ('NIFGA:birnlex_1207', ':Category:Orbital part of inferior frontal gyrus'), ('NIFGA:nlx_anat_100313', ':Category:Organum vasculosum lamina terminalis'), ('NIFGA:nlx_143559', ':Category:Paleocortex'), ('NIFGA:birnlex_1490', ':Category:Paleodentate of dentate nucleus'), ('NIFGA:birnlex_1331', ':Category:Pallidotegmental fasciculus'), ('NIFGA:birnlex_1007', ':Category:Parabigeminal nucleus'), ('NIFGA:nlx_23647', ':Category:Parabrachial nucleus'), ('NIFGA:nlx_144307', ':Category:Parabrachial pigmented nucleus'), ('NIFGA:birnlex_981', ':Category:Paracentral nucleus'), ('NIFGA:birnlex_952', ':Category:Parafascicular nucleus'), ('NIFGA:birnlex_807', ':Category:Parahippocampal gyrus'), ('NIFGA:birnlex_1276', ':Category:Paralaminar part of medial dorsal nucleus'), ('NIFGA:nlx_151902', ':Category:Paramedian reticular nucleus'), ('NIFGA:birnlex_2653', ':Category:Parasolitary nucleus'), ('NIFGA:nlx_anat_091002', ':Category:Parasubiculum'), ('NIFGA:birnlex_860', ':Category:Paratenial nucleus'), ('NIFGA:birnlex_1138', ':Category:Paraterminal gyrus'), ('NIFGA:birnlex_1407', ':Category:Paraventricular nucleus of hypothalamus'), ('NIFGA:birnlex_764', ':Category:Paraventricular nucleus of thalamus'), ('NIFGA:birnlex_1413', ':Category:Paraventricular nucleus of the hypothalamus descending division'), ('NIFGA:birnlex_1374', ':Category:Paraventricular nucleus of the hypothalamus descending division - forniceal part'), ('NIFGA:birnlex_1354', ':Category:Paraventricular nucleus of the hypothalamus descending division - lateral parvicellular part'), ('NIFGA:birnlex_1342', ':Category:Paraventricular nucleus of the hypothalamus descending division - medial parvicellular part, ventral zone'), ('NIFGA:birnlex_1419', ':Category:Paraventricular nucleus of the hypothalamus magnocellular division'), ('NIFGA:birnlex_1384', ':Category:Paraventricular nucleus of the hypothalamus magnocellular division - anterior magnocellular part'), ('NIFGA:birnlex_1388', ':Category:Paraventricular nucleus of the hypothalamus magnocellular division - medial magnocellular part'), ('NIFGA:birnlex_1394', ':Category:Paraventricular nucleus of the hypothalamus magnocellular division - posterior magnocellular part'), ('NIFGA:birnlex_1320', ':Category:Paraventricular nucleus of the hypothalamus magnocellular division - posterior magnocellular part lateral zone'), ('NIFGA:birnlex_1312', ':Category:Paraventricular nucleus of the hypothalamus magnocellular division - posterior magnocellular part medial zone'), ('NIFGA:birnlex_1426', ':Category:Paraventricular nucleus of the hypothalamus parvicellular division'), ('NIFGA:nlx_anat_20081215', ':Category:Paravermic Lobule II'), ('NIFGA:nlx_anat_20081216', ':Category:Paravermic Lobule III'), ('NIFGA:nlx_anat_20081217', ':Category:Paravermic Lobule IV'), ('NIFGA:nlx_anat_20081218', ':Category:Paravermic Lobule IX'), ('NIFGA:nlx_anat_20081219', ':Category:Paravermic Lobule V'), ('NIFGA:nlx_anat_20081220', ':Category:Paravermic Lobule VI'), ('NIFGA:nlx_anat_20081221', ':Category:Paravermic Lobule VII'), ('NIFGA:nlx_anat_20081222', ':Category:Paravermic Lobule VIII'), ('NIFGA:nlx_anat_20081239', ':Category:Paravermis of the anterior lobe of the cerebellum'), ('NIFGA:nlx_anat_20081238', ':Category:Paravermis of the posterior lobe of the cerebellum'), ('NIFGA:nlx_anat_20081237', ':Category:Paravermis parts of the cerebellar cortex'), ('NIFGA:nlx_79282', ':Category:Parietal cortex'), ('NIFGA:birnlex_1148', ':Category:Parietal lobe'), ('NIFGA:birnlex_941', ':Category:Pars nervosa of hypophysis'), ('NIFGA:birnlex_1170', ':Category:Pars postrema of ventral lateral nucleus'), ('NIFGA:birnlex_1283', ':Category:Parvicellular part of medial dorsal nucleus'), ('NIFGA:birnlex_722', ':Category:Parvicellular part of ventral anterior nucleus'), ('NIFGA:birnlex_917', ':Category:Parvicellular part of ventral posteromedial nucleus'), ('NIFGA:birnlex_822', ':Category:Parvocellular oculomotor nucleus'), ('NIFGA:birnlex_725', ':Category:Parvocellular part of red nucleus'), ('NIFGA:birnlex_1437', ':Category:Pedunculopontine tegmental nucleus'), ('NIFGA:birnlex_1291', ':Category:Periamygdaloid area'), ('NIFGA:nlx_144210', ':Category:Periamygdaloid cortex'), ('NIFGA:birnlex_973', ':Category:Periaqueductal gray'), ('NIFGA:birnlex_1059', ':Category:Pericalcarine cortex'), ('NIFGA:birnlex_1056', ':Category:Pericentral nucleus of inferior colliculus'), ('NIFGA:birnlex_804', ':Category:Periolivary nucleus'), ('NIFGA:birnlex_1474', ':Category:Peripeduncular nucleus'), ('NIFGA:nlx_anat_1005006', ':Category:Perirhinal cortex'), ('NIFGA:birnlex_2655', ':Category:Peritrigeminal nucleus'), ('NIFGA:birnlex_1184', ':Category:Pineal body'), ('NIFGA:nlx_anat_091004', ':Category:Piriform cortex layer 1a'), ('NIFGA:nlx_anat_091005', ':Category:Piriform cortex layer 1b'), ('NIFGA:nlx_144291', ':Category:Planum polare'), ('NIFGA:birnlex_733', ':Category:Pons'), ('NIFGA:birnlex_1516', ':Category:Pontine nuclear complex'), ('NIFGA:birnlex_1110', ':Category:Pontine raphe nucleus'), ('NIFGA:birnlex_1050', ':Category:Pontine reticular formation'), ('NIFGA:birnlex_923', ':Category:Pontine tegmentum'), ('NIFGA:birnlex_2656', ':Category:Pontobulbar nucleus'), ('NIFGA:birnlex_1070', ':Category:Postcentral gyrus'), ('NIFGA:birnlex_914', ':Category:Postcommissural fornix'), ('NIFGA:birnlex_4015', ':Category:Posterior calcarine sulcus'), ('NIFGA:birnlex_950', ':Category:Posterior cingulate cortex'), ('NIFGA:birnlex_1546', ':Category:Posterior cingulate gyrus'), ('NIFGA:birnlex_754', ':Category:Posterior column of fornix'), ('NIFGA:birnlex_1297', ':Category:Posterior horn lateral ventricle'), ('NIFGA:birnlex_1651', ':Category:Posterior hypothalamic region'), ('NIFGA:nlx_144258', ':Category:Posterior limb of internal capsule'), ('NIFGA:birnlex_911', ':Category:Posterior lobe of the cerebellum'), ('NIFGA:birnlex_1280', ':Category:Posterior median eminence'), ('NIFGA:birnlex_1467', ':Category:Posterior nuclear complex'), ('NIFGA:birnlex_1463', ':Category:Posterior nucleus of hypothalamus'), ('NIFGA:birnlex_939', ':Category:Posterior nucleus of thalamus'), ('NIFGA:birnlex_1054', ':Category:Posterior orbital gyrus'), ('NIFGA:birnlex_1295', ':Category:Posterior parahippocampal gyrus'), ('NIFGA:birnlex_977', ':Category:Posterior part of anterior commissure'), ('NIFGA:birnlex_1466', ':Category:Posterior periventricular nucleus'), ('NIFGA:birnlex_1661', ':Category:Posterior transverse temporal gyrus'), ('NIFGA:birnlex_1622', ':Category:Posterodorsal nucleus of medial geniculate body'), ('NIFGA:nlx_anat_20081259', ':Category:Posterolateral fissure'), ('NIFGA:birnlex_2573', ':Category:Posteroventral cochlear nucleus'), ('NIFGA:nlx_anat_20081252', ':Category:Precentral fissure'), ('NIFGA:birnlex_1455', ':Category:Precentral gyrus'), ('NIFGA:birnlex_1141', ':Category:Precentral operculum'), ('NIFGA:birnlex_1033', ':Category:Precommissural fornix'), ('NIFGA:birnlex_1446', ':Category:Precuneus cortex'), ('NIFGA:birnlex_1590', ':Category:Predorsal bundle'), ('NIFGA:nlx_anat_090801', ':Category:Prefrontal cortex'), ('NIFGA:birnlex_1473', ':Category:Premammillary nucleus'), ('NIFGA:birnlex_1436', ':Category:Preoccipital notch'), ('NIFGA:birnlex_814', ':Category:Preolivary nucleus'), ('NIFGA:birnlex_1706', ':Category:Preoptic area'), ('NIFGA:birnlex_1201', ':Category:Preoptic periventricular nucleus'), ('NIFGA:nlx_anat_20081257', ':Category:Prepyramidal fissure'), ('NIFGA:birnlex_1097', ':Category:Prepyriform area'), ('NIFGA:birnlex_1108', ':Category:Presubiculum'), ('NIFGA:nlx_59721', ':Category:Pretectum'), ('NIFGA:nlx_143555', ':Category:Primary motor cortex'), ('NIFGA:birnlex_2706', ':Category:Primary olfactory cortex'), ('NIFGA:nlx_143551', ':Category:Primary somatosensory cortex'), ('NIFGA:nlx_144265', ':Category:Primary somatosensory cortex lamina VI'), ('NIFGA:nlx_anat_20081248', ':Category:Principal olivary nucleus'), ('NIFGA:birnlex_927', ':Category:Principal part of ventral posteromedial nucleus'), ('NIFGA:birnlex_1048', ':Category:Principal pretectal nucleus'), ('NIFGA:birnlex_1120', ':Category:Principal sensory nucleus of trigeminal nerve'), ('NIFGA:birnlex_824', ':Category:Pulvinar'), ('NIFGA:birnlex_809', ':Category:Putamen'), ('NIFGA:nlx_anat_20090205', ':Category:Raphe Nuclei'), ('NIFGA:birnlex_1478', ':Category:Red nucleus'), ('NIFGA:nlx_anat_20081201', ':Category:Regional Parts of the Hemisphere Lobules'), ('NIFGA:nlx_anat_20081214', ':Category:Regional Parts of the Paravermal Lobules'), ('NIFGA:nlx_anat_20081223', ':Category:Regional Parts of the Vermal Lobules'), ('NIFGA:birnlex_1094', ':Category:Regional part of a lobe of the cerebellum'), ('NIFGA:birnlex_2678', ':Category:Regional part of amygdala'), ('NIFGA:birnlex_1571', ':Category:Regional part of cerebellar cortex'), ('NIFGA:birnlex_959', ':Category:Regional part of cerebellar white matter'), ('NIFGA:birnlex_748', ':Category:Regional part of cerebellum'), ('NIFGA:nlx_143558', ':Category:Reticular formation'), ('NIFGA:birnlex_882', ':Category:Reticulotegmental nucleus'), ('NIFGA:birnlex_770', ':Category:Reuniens nucleus'), ('NIFGA:birnlex_778', ':Category:Rhomboidal nucleus'), ('NIFGA:birnlex_1797', ':Category:Right cerebral hemisphere'), ('NIFGA:birnlex_1786', ':Category:Right frontal lobe'), ('NIFGA:birnlex_1781', ':Category:Right limbic lobe'), ('NIFGA:birnlex_1783', ':Category:Right occipital lobe'), ('NIFGA:birnlex_1729', ':Category:Right parietal lobe'), ('NIFGA:birnlex_1790', ':Category:Right sub-lobar region'), ('NIFGA:birnlex_1785', ':Category:Right temporal lobe'), ('NIFGA:birnlex_975', ':Category:Rostral anterior cingulate cortex'), ('NIFGA:birnlex_1481', ':Category:Rostral interstitial nucleus of medial longitudinal fasciculus'), ('NIFGA:birnlex_794', ':Category:Rostral intralaminar nuclei'), ('NIFGA:nlx_144319', ':Category:Rostral linear nucleus'), ('NIFGA:birnlex_1090', ':Category:Rostral middle frontal gyrus'), ('NIFGA:birnlex_1702', ':Category:Rostral migratory stream'), ('NIFGA:nlx_anat_20081247', ':Category:Rostral portion of the medial accessory olive'), ('NIFGA:nlx_anat_20081258', ':Category:Secondary fissure'), ('NIFGA:birnlex_2709', ':Category:Secondary olfactory cortex'), ('NIFGA:birnlex_1313', ':Category:Septal nuclear complex'), ('NIFGA:birnlex_1315', ':Category:Septal pellucidum'), ('NIFGA:birnlex_730', ':Category:Septofimbrial nucleus'), ('NIFGA:nlx_60880', ':Category:Septohippocampal nucleus'), ('NIFGA:birnlex_963', ':Category:Septum'), ('NIFGA:nlx_anat_20090307', ':Category:Shell of nucleus accumbens'), ('NIFGA:birnlex_1429', ':Category:Solitary nucleus'), ('NIFGA:nlx_anat_1005009', ":Category:Sommer's sector"), ('NIFGA:birnlex_1477', ':Category:Spinal trigeminal tract of medulla'), ('NIFGA:birnlex_1725', ':Category:Spinal trigeminal tract of pons'), ('NIFGA:birnlex_741', ':Category:Spinothalamic tract of medulla'), ('NIFGA:birnlex_1150', ':Category:Spinothalamic tract of midbrain'), ('NIFGA:birnlex_1719', ':Category:Spinothalamic tract of pons'), ('NIFGA:birnlex_1359', ':Category:Stratum lacunosum moleculare'), ('NIFGA:birnlex_4108', ':Category:Stratum lucidum'), ('NIFGA:birnlex_4113', ':Category:Stratum oriens'), ('NIFGA:birnlex_1444', ':Category:Stratum pyramidale'), ('NIFGA:birnlex_1298', ':Category:Stratum radiatum'), ('NIFGA:birnlex_1727', ':Category:Stratum zonale of thalamus'), ('NIFGA:birnlex_1066', ':Category:Stria medullaris'), ('NIFGA:birnlex_937', ':Category:Stria terminalis'), ('NIFGA:birnlex_1672', ':Category:Striatum'), ('NIFGA:nlx_anat_1010004', ':Category:Striosomal part of body of caudate nucleus'), ('NIFGA:nlx_anat_20090507', ':Category:Striosomal part of caudate nucleus'), ('NIFGA:nlx_anat_20090508', ':Category:Striosomal part of putamen'), ('NIFGA:nlx_anat_20090506', ':Category:Striosome'), ('NIFGA:birnlex_1788', ':Category:Sub-lobar region'), ('NIFGA:nlx_anat_1005003', ':Category:Subbrachial nucleus'), ('NIFGA:birnlex_919', ':Category:Subcallosal area'), ('NIFGA:birnlex_1028', ':Category:Subcommissural organ'), ('NIFGA:birnlex_1441', ':Category:Subcuneiform nucleus'), ('NIFGA:birnlex_783', ':Category:Subfascicular nucleus'), ('NIFGA:nlx_anat_100314', ':Category:Subfornical organ'), ('NIFGA:birnlex_944', ':Category:Subicular complex'), ('NIFGA:birnlex_1305', ':Category:Subiculum'), ('NIFGA:birnlex_1057', ':Category:Sublentiform nucleus'), ('NIFGA:birnlex_2657', ':Category:Sublingual nucleus'), ('NIFGA:birnlex_946', ':Category:Submedial nucleus'), ('NIFGA:birnlex_915', ':Category:Substantia innominata'), ('NIFGA:birnlex_789', ':Category:Substantia nigra'), ('NIFGA:birnlex_990', ':Category:Substantia nigra pars compacta'), ('NIFGA:birnlex_866', ':Category:Substantia nigra pars lateralis'), ('NIFGA:birnlex_968', ':Category:Substantia nigra pars reticulata'), ('NIFGA:nlx_anat_1010002', ':Category:Subthalamic nucleus'), ('NIFGA:birnlex_708', ':Category:Subthalamus'), ('NIFGA:nlx_144262', ':Category:Subventricular Zone'), ('NIFGA:birnlex_4024', ':Category:Superficial feature part of occipital lobe'), ('NIFGA:birnlex_1268', ':Category:Superficial feature part of pons'), ('NIFGA:nlx_anat_20081250', ':Category:Superficial feature part of the cerebellum'), ('NIFGA:birnlex_889', ':Category:Superior central nucleus'), ('NIFGA:birnlex_1711', ':Category:Superior cerebellar peduncle'), ('NIFGA:birnlex_1162', ':Category:Superior cerebellar peduncle of midbrain'), ('NIFGA:birnlex_1726', ':Category:Superior cerebellar peduncle of pons'), ('NIFGA:birnlex_1040', ':Category:Superior colliculus'), ('NIFGA:birnlex_1303', ':Category:Superior frontal gyrus'), ('NIFGA:birnlex_1300', ':Category:Superior medullary velum'), ('NIFGA:birnlex_758', ':Category:Superior occipital gyrus'), ('NIFGA:birnlex_1307', ':Category:Superior olivary complex'), ('NIFGA:birnlex_900', ':Category:Superior olive'), ('NIFGA:birnlex_1450', ':Category:Superior parietal cortex'), ('NIFGA:birnlex_1311', ':Category:Superior rostral gyrus'), ('NIFGA:birnlex_1131', ':Category:Superior salivatory nucleus'), ('NIFGA:birnlex_1648', ':Category:Superior temporal gyrus'), ('NIFGA:birnlex_1082', ':Category:Superior transverse frontopolar gyrus'), ('NIFGA:birnlex_1316', ':Category:Supracallosal gyrus'), ('NIFGA:birnlex_1325', ':Category:Suprachiasmatic nucleus'), ('NIFGA:birnlex_1390', ':Category:Suprachiasmatic nucleus dorsomedial part'), ('NIFGA:birnlex_1393', ':Category:Suprachiasmatic nucleus ventrolateral part'), ('NIFGA:birnlex_953', ':Category:Suprageniculate nucleus'), ('NIFGA:birnlex_1479', ':Category:Supramammillary nucleus'), ('NIFGA:birnlex_1381', ':Category:Supramarginal gyrus'), ('NIFGA:birnlex_1411', ':Category:Supraoptic nucleus'), ('NIFGA:birnlex_2658', ':Category:Supraspinal nucleus'), ('NIFGA:nlx_144479', ':Category:Taenia tecta'), ('NIFGA:birnlex_1215', ':Category:Tail of caudate nucleus'), ('NIFGA:birnlex_750', ':Category:Tectobulbar tract'), ('NIFGA:birnlex_701', ':Category:Tectopontine tract'), ('NIFGA:birnlex_1031', ':Category:Tegmentum'), ('NIFGA:birnlex_1115', ':Category:Telencephalon'), ('NIFGA:nlx_anat_1005012', ':Category:Telencephalon of primate'), ('NIFGA:nlx_anat_1005015', ':Category:Telencephalon of rodent'), ('NIFGA:nlx_94939', ':Category:Temporal cortex'), ('NIFGA:birnlex_1160', ':Category:Temporal lobe'), ('NIFGA:birnlex_1025', ':Category:Temporal operculum'), ('NIFGA:birnlex_1055', ':Category:Temporal pole'), ('NIFGA:nlx_144255', ':Category:Temporoparietal junction'), ('NIFGA:birnlex_1721', ':Category:Thalamic reticular nucleus'), ('NIFGA:birnlex_954', ':Category:Thalamus'), ('NIFGA:birnlex_714', ':Category:Third ventricle'), ('NIFGA:birnlex_1258', ':Category:Transverse frontopolar gyri complex'), ('NIFGA:birnlex_1535', ':Category:Transverse pontine fibers'), ('NIFGA:birnlex_1389', ':Category:Transverse temporal cortex'), ('NIFGA:birnlex_707', ':Category:Trapezoid body'), ('NIFGA:birnlex_745', ':Category:Trapezoid nuclear complex'), ('NIFGA:birnlex_1216', ':Category:Triangular part of inferior frontal gyrus'), ('NIFGA:birnlex_816', ':Category:Triangular septal nucleus'), ('NIFGA:birnlex_974', ':Category:Trigeminal nerve fibers'), ('NIFGA:birnlex_1346', ':Category:Trigeminal nerve root'), ('NIFGA:birnlex_4096', ':Category:Trigeminal nuclear complex'), ('NIFGA:birnlex_1172', ':Category:Trochlear nerve fibers'), ('NIFGA:birnlex_1488', ':Category:Trochlear nucleus'), ('NIFGA:birnlex_1189', ':Category:Tuber cinereum'), ('NIFGA:birnlex_912', ':Category:Tuberal part of hypophysis'), ('NIFGA:birnlex_1271', ':Category:Tuberomammillary nucleus'), ('NIFGA:birnlex_1290', ':Category:Tuberomammillary nucleus dorsal part'), ('NIFGA:birnlex_1294', ':Category:Tuberomammillary nucleus ventral part'), ('NIFGA:birnlex_983', ':Category:Uncinate fasciculus'), ('NIFGA:nlx_98733', ':Category:Uncinate fasciculus of forebrain'), ('NIFGA:birnlex_765', ':Category:Vagal nerve fiber bundle'), ('NIFGA:birnlex_991', ':Category:Ventral acoustic stria'), ('NIFGA:birnlex_1563', ':Category:Ventral amygdalofugal projection'), ('NIFGA:birnlex_1232', ':Category:Ventral anterior nucleus'), ('NIFGA:birnlex_2567', ':Category:Ventral cochlear nucleus'), ('NIFGA:birnlex_1628', ':Category:Ventral external arcuate fiber bundle'), ('NIFGA:birnlex_1237', ':Category:Ventral lateral nucleus'), ('NIFGA:birnlex_1669', ':Category:Ventral nuclear group'), ('NIFGA:birnlex_1597', ':Category:Ventral nucleus of lateral geniculate body'), ('NIFGA:birnlex_1140', ':Category:Ventral nucleus of lateral lemniscus'), ('NIFGA:birnlex_845', ':Category:Ventral nucleus of medial geniculate body'), ('NIFGA:birnlex_2576', ':Category:Ventral nucleus of trapezoid body'), ('NIFGA:birnlex_713', ':Category:Ventral oculomotor nucleus'), ('NIFGA:birnlex_1674', ':Category:Ventral pallidum'), ('NIFGA:birnlex_1116', ':Category:Ventral posterior nucleus'), ('NIFGA:birnlex_728', ':Category:Ventral posteroinferior nucleus'), ('NIFGA:birnlex_737', ':Category:Ventral posterolateral nucleus'), ('NIFGA:birnlex_743', ':Category:Ventral posteromedial nucleus'), ('NIFGA:nlx_57107', ':Category:Ventral striatum'), ('NIFGA:birnlex_1415', ':Category:Ventral tegmental area'), ('NIFGA:birnlex_1421', ':Category:Ventral tegmental nucleus'), ('NIFGA:birnlex_1001', ':Category:Ventral trigeminal tract'), ('NIFGA:birnlex_1572', ':Category:Ventromedial nucleus of hypothalamus'), ('NIFGA:birnlex_1175', ':Category:Vermal parts of the cerebellum'), ('NIFGA:nlx_anat_20081224', ':Category:Vermic Lobule I'), ('NIFGA:nlx_anat_20081225', ':Category:Vermic Lobule II'), ('NIFGA:nlx_anat_20081226', ':Category:Vermic Lobule III'), ('NIFGA:nlx_anat_20081227', ':Category:Vermic Lobule IV'), ('NIFGA:nlx_anat_20081234', ':Category:Vermic Lobule IX'), ('NIFGA:nlx_anat_20081228', ':Category:Vermic Lobule V'), ('NIFGA:nlx_anat_20081229', ':Category:Vermic Lobule VI'), ('NIFGA:nlx_anat_20081230', ':Category:Vermic Lobule VII'), ('NIFGA:nlx_anat_20081231', ':Category:Vermic Lobule VIIA'), ('NIFGA:nlx_anat_20081232', ':Category:Vermic Lobule VIIB'), ('NIFGA:nlx_anat_20081233', ':Category:Vermic Lobule VIII'), ('NIFGA:nlx_anat_20081235', ':Category:Vermic Lobule X'), ('NIFGA:birnlex_1106', ':Category:Vermis'), ('NIFGA:birnlex_1185', ':Category:Vermis of the anterior lobe of the cerebellum'), ('NIFGA:nlx_anat_20081241', ':Category:Vermis of the flocculonodular lobe of the cerebellum'), ('NIFGA:nlx_anat_20081240', ':Category:Vermis of the posterior lobe of the cerebellum'), ('NIFGA:birnlex_1337', ':Category:Vestibular nuclear complex'), ('NIFGA:birnlex_1636', ':Category:Vestibulocochlear nerve fiber bundle'), ('NIFGA:nlx_143553', ':Category:Visual association cortex'), ('NIFGA:nlx_143552', ':Category:Visual cortex primary'), ('NIFGA:birnlex_1105', ':Category:White laminae of cerebellum'), ('NIFGA:nlx_anat_20081249', ':Category:White matter of the cerebellar cortex'), ('OBO:UBERON_0001792', ':Category:Retina ganglion cell layer'), ('NIFCELL:nifext_152', ':Category:Amygdala basolateral nuclear complex pyramidal neuron'), ('NIFCELL:nlx_cell_20090313', ':Category:Aplysia cerebral ganglion metacerebral cell'), ('NIFCELL:nlx_cell_20090203', ':Category:Basalis nucleus cholinergic neuron'), ('NIFCELL:sao1415726815', ':Category:Cerebellum Golgi cell'), ('NIFCELL:nifext_133', ':Category:Cerebellum Lugaro cell'), ('NIFCELL:sao471801888', ':Category:Cerebellum Purkinje cell'), ('NIFCELL:sao666951243', ':Category:Cerebellum basket cell'), ('NIFCELL:nifext_128', ':Category:Cerebellum granule cell'), ('NIFCELL:nifext_130', ':Category:Cerebellum stellate cell'), ('NIFCELL:nifext_132', ':Category:Cerebellum unipolar brush cell'), ('NIFCELL:sao1366775348', ':Category:Ciliary ganglion cell'), ('NIFCELL:sao429277527', ':Category:Cochlea inner hair cell'), ('NIFCELL:sao1582628662', ':Category:Cochlea outer hair cell'), ('NIFCELL:nifext_136', ':Category:Cochlear nucleus (dorsal) Golgi cell'), ('NIFCELL:nifext_76', ':Category:Cochlear nucleus (dorsal) cartwheel cell'), ('NIFCELL:nifext_75', ':Category:Cochlear nucleus (dorsal) giant cell'), ('NIFCELL:nifext_74', ':Category:Cochlear nucleus (dorsal) pyramidal neuron'), ('NIFCELL:nifext_135', ':Category:Cochlear nucleus (dorsal) unipolar brush cell'), ('NIFCELL:nifext_73', ':Category:Cochlear nucleus (dorsal) vertical cell'), ('NIFCELL:nifext_70', ':Category:Cochlear nucleus (ventral) globular bushy cell'), ('NIFCELL:nifext_69', ':Category:Cochlear nucleus (ventral) multipolar D cell'), ('NIFCELL:nifext_68', ':Category:Cochlear nucleus (ventral) multipolar T cell'), ('NIFCELL:nlx_cell_20081202', ':Category:Cochlear nucleus (ventral) multipolar cell'), ('NIFCELL:nifext_72', ':Category:Cochlear nucleus (ventral) octopus cell'), ('NIFCELL:nlx_cell_20081201', ':Category:Cochlear nucleus (ventral) spherical bushy cell'), ('NIFCELL:nifext_83', ':Category:Colliculus inferior intrinsic cell'), ('NIFCELL:nifext_82', ':Category:Colliculus inferior principal cell'), ('NIFCELL:nifext_91', ':Category:DRG IA cell'), ('NIFCELL:nifext_92', ':Category:DRG IB cell'), ('NIFCELL:nifext_93', ':Category:DRG II cell'), ('NIFCELL:nifext_88', ":Category:DRG Meissner's corpuscle cell"), ('NIFCELL:nifext_87', ':Category:DRG Merckel disc cell'), ('NIFCELL:nifext_86', ':Category:DRG Pacinian corpuscle cell'), ('NIFCELL:nifext_85', ':Category:DRG hair follicle cell'), ('NIFCELL:nifext_89', ':Category:DRG pain cell'), ('NIFCELL:nifext_90', ':Category:DRG temperature cell'), ('NIFCELL:nlx_cell_091201', ':Category:Dentate gyrus HIPP cell'), ('NIFCELL:nlx_cell_091203', ':Category:Dentate gyrus IS-I cell'), ('NIFCELL:nlx_cell_091204', ':Category:Dentate gyrus IS-II cell'), ('NIFCELL:nlx_cell_100201', ':Category:Dentate gyrus basket cell'), ('NIFCELL:nifext_153', ':Category:Dentate gyrus granule cell'), ('NIFCELL:nlx_cell_20090727', ':Category:Dentate gyrus hilar cell'), ('NIFCELL:nlx_cell_100204', ':Category:Dentate gyrus trilaminar interneuron'), ('NIFCELL:nifext_84', ':Category:Dorsal root ganglion A alpha-beta non-nociceptive neuron'), ('NIFCELL:nlx_cell_20090403', ':Category:Dorsal tegmental nucleus medium cell'), ('NIFCELL:nlx_cell_20090402', ':Category:Dorsal tegmental nucleus small cell'), ('NIFCELL:nifext_150', ':Category:Globus pallidus intrinsic cell'), ('NIFCELL:nifext_149', ':Category:Globus pallidus principal cell'), ('NIFCELL:nifext_95', ':Category:Gracilis nucleus intrinsic cell'), ('NIFCELL:nifext_94', ':Category:Gracilis nucleus principal cell'), ('NIFCELL:nlx_cell_100209', ':Category:Hippocampus CA1 IS-I neuron'), ('NIFCELL:nlx_cell_1006029', ':Category:Hippocampus CA1 IS-II neuron'), ('NIFCELL:nlx_cell_091205', ':Category:Hippocampus CA1 basket cell'), ('NIFCELL:nlx_cell_1006031', ':Category:Hippocampus CA1 neurogliaform neuron'), ('NIFCELL:nlx_cell_091206', ':Category:Hippocampus CA1 oriens lacunosum moleculare neuron'), ('NIFCELL:sao830368389', ':Category:Hippocampus CA1 pyramidal cell'), ('NIFCELL:nlx_cell_090807', ':Category:Hippocampus CA1 stratum oriens neuron'), ('NIFCELL:nlx_cell_091207', ':Category:Hippocampus CA2 basket cell broad'), ('NIFCELL:nlx_cell_091208', ':Category:Hippocampus CA2 basket cell narrow'), ('NIFCELL:nlx_cell_091209', ':Category:Hippocampus CA2 bistratified cell broad'), ('NIFCELL:nlx_cell_091004', ':Category:Hippocampus CA2 bistratified cell narrow'), ('NIFCELL:nlx_cell_20090311', ':Category:Hippocampus CA2 pyramidal neuron'), ('NIFCELL:nlx_cell_091210', ':Category:Hippocampus CA3 IS-I cell'), ('NIFCELL:nlx_cell_091211', ':Category:Hippocampus CA3 IS-II cell'), ('NIFCELL:nlx_cell_091212', ':Category:Hippocampus CA3 axo-axonic cell'), ('NIFCELL:nlx_cell_091213', ':Category:Hippocampus CA3 basket cell'), ('NIFCELL:nlx_cell_091214', ':Category:Hippocampus CA3 lacunosum moleculare neuron'), ('NIFCELL:nlx_cell_091215', ':Category:Hippocampus CA3 oriens interneuron'), ('NIFCELL:nlx_cell_091216', ':Category:Hippocampus CA3 oriens lacunosum moleculare neuron'), ('NIFCELL:sao383526650', ':Category:Hippocampus CA3 pyramidal cell'), ('NIFCELL:nlx_cell_091217', ':Category:Hippocampus CA3 radiatum neuron'), ('NIFCELL:nlx_cell_091218', ':Category:Hippocampus CA3 spiny CR cell'), ('NIFCELL:nlx_cell_100311', ':Category:Hypoglossal nucleus motor neuron'), ('NIFCELL:nlx_cell_20090202', ':Category:Locus coeruleus NA neuron'), ('NIFCELL:nlx_cell_20081206', ':Category:Neocortex Cajal-Retzius cell'), ('NIFCELL:nifext_55', ':Category:Neocortex Martinotti cell'), ('NIFCELL:nifext_56', ':Category:Neocortex basket cell'), ('NIFCELL:nifext_81', ':Category:Neocortex bipolar cell'), ('NIFCELL:sao910084726', ':Category:Neocortex bouquet double cell'), ('NIFCELL:nifext_134', ':Category:Neocortex candelabrum cell'), ('NIFCELL:nifext_57', ':Category:Neocortex chandelier cell'), ('NIFCELL:nifext_51', ':Category:Neocortex polymorphic cell layer 5-6'), ('NIFCELL:sao2128417084', ':Category:Neocortex pyramidal cell'), ('NIFCELL:nifext_50', ':Category:Neocortex pyramidal cell layer 5-6'), ('NIFCELL:nifext_49', ':Category:Neocortex pyramidal layer 2-3 cell'), ('NIFCELL:nifext_52', ':Category:Neocortex stellate cell'), ('NIFCELL:nifext_53', ':Category:Neocortex stellate layer 4 cell'), ('NIFCELL:sao770302354', ':Category:Neocortex stellate smooth cell'), ('NIFCELL:sao1236796660', ':Category:Neocortex stellate spiny cell'), ('NIFCELL:nifext_144', ':Category:Neostriatum SOM/NOS cell'), ('NIFCELL:sao1866881837', ':Category:Neostriatum cholinergic cell'), ('NIFCELL:nifext_143', ':Category:Neostriatum gaba/parvalbumin interneuron'), ('NIFCELL:nlx_cell_20090501', ':Category:Neuroendocrine motor magnocellular neurosecretory cell'), ('NIFCELL:nifext_122', ':Category:Olfactory bulb (accessory) glomerular layer cell'), ('NIFCELL:nlx_cell_20090401', ':Category:Olfactory bulb (accessory) granule cell'), ('NIFCELL:nlx_cell_20090304', ':Category:Olfactory bulb (accessory) mitral cell'), ('NIFCELL:nifext_124', ':Category:Olfactory bulb (main) Blanes cell'), ('NIFCELL:nlx_144252', ':Category:Olfactory bulb (main) adult-born granule cell'), ('NIFCELL:nifext_123', ':Category:Olfactory bulb (main) granule cell'), ('NIFCELL:nifext_120', ':Category:Olfactory bulb (main) mitral cell'), ('NIFCELL:nlx_cell_091202', ':Category:Olfactory bulb (main) periglomerular cell'), ('NIFCELL:nifext_121', ':Category:Olfactory bulb (main) tufted cell (middle)'), ('NIFCELL:nifext_118', ':Category:Olfactory cortex horizontal cell'), ('NIFCELL:nlx_cell_091001', ':Category:Olfactory cortex multipolar cell'), ('NIFCELL:nlx_cell_091005', ':Category:Olfactory cortex semilunar cell'), ('NIFCELL:nlx_cell_091002', ':Category:Olfactory cortex small globular cell'), ('NIFCELL:nifext_116', ':Category:Olfactory epithelium main sensory cell'), ('NIFCELL:nifext_119', ':Category:Olfactory epithelium main supporting cell'), ('NIFCELL:nifext_155', ':Category:Olfactory tubercle Islets of Calleja DA cell'), ('NIFCELL:nifext_154', ':Category:Olfactory tubercle Islets of Calleja GABA cell'), ('NIFCELL:nifext_36', ':Category:Retina amacrine cell'), ('NIFCELL:nifext_31', ':Category:Retina bipolar cell'), ('NIFCELL:nifext_33', ':Category:Retina bipolar cell off'), ('NIFCELL:nifext_32', ':Category:Retina bipolar cell on'), ('NIFCELL:nifext_39', ':Category:Retina displaced amacrine cell'), ('NIFCELL:nifext_17', ':Category:Retina ganglion cell'), ('NIFCELL:nifext_40', ':Category:Retina horizontal cell'), ('NIFCELL:nifext_38', ':Category:Retina interplexiform cell'), ('NIFCELL:nifext_19', ':Category:Retina medium complex ganglion cell'), ('NIFCELL:nifext_20', ':Category:Retina medium simple ganglion cell'), ('NIFCELL:nifext_34', ':Category:Retina midget bipolar cell'), ('NIFCELL:nifext_35', ':Category:Retina parasol bipolar cell'), ('NIFCELL:nlx_cell_100210', ':Category:Retina photoreceptor L cone cell'), ('NIFCELL:nifext_27', ':Category:Retina photoreceptor M cone cell'), ('NIFCELL:nlx_cell_100211', ':Category:Retina photoreceptor S cone cell'), ('NIFCELL:sao1103104164', ':Category:Retina photoreceptor cone cell'), ('NIFCELL:nlx_cell_100212', ':Category:Retina photoreceptor rod cell'), ('NIFCELL:nifext_21', ':Category:Retina small complex ganglion cell'), ('NIFCELL:nifext_22', ':Category:Retina small simple ganglion cell'), ('NIFCELL:nifext_37', ':Category:Retina starburst amacrine cell'), ('NIFCELL:nifext_101', ':Category:Solitary tract nucleus intrinsic cell'), ('NIFCELL:nifext_100', ':Category:Solitary tract nucleus principal cell'), ('NIFCELL:nifext_109', ':Category:Spinal cord intermediate horn motor neuron sympathetic'), ('NIFCELL:nifext_115', ':Category:Spinal cord proprioception intersegmental cell'), ('NIFCELL:nifext_114', ':Category:Spinal cord ventral horn interneuron FRA'), ('NIFCELL:nifext_110', ':Category:Spinal cord ventral horn interneuron IA'), ('NIFCELL:nifext_111', ':Category:Spinal cord ventral horn interneuron IB'), ('NIFCELL:nifext_112', ':Category:Spinal cord ventral horn interneuron II'), ('NIFCELL:nifext_113', ':Category:Spinal cord ventral horn interneuron Renshaw'), ('NIFCELL:nlx_cell_100205', ':Category:Spinal cord ventral horn interneuron V0'), ('NIFCELL:nlx_cell_1006021', ':Category:Spinal cord ventral horn interneuron V0C'), ('NIFCELL:nlx_cell_1006033', ':Category:Spinal cord ventral horn interneuron V0G'), ('NIFCELL:nlx_cell_100206', ':Category:Spinal cord ventral horn interneuron V1'), ('NIFCELL:nlx_cell_100207', ':Category:Spinal cord ventral horn interneuron V2'), ('NIFCELL:nlx_cell_100208', ':Category:Spinal cord ventral horn interneuron V3'), ('NIFCELL:sao1154704263', ':Category:Spinal cord ventral horn motor neuron alpha'), ('NIFCELL:nifext_106', ':Category:Spinal cord ventral horn motor neuron beta'), ('NIFCELL:sao1438006234', ':Category:Spinal cord ventral horn motor neuron gamma'), ('NIFCELL:nifext_102', ':Category:Spinocerebellar tract cell'), ('NIFCELL:nifext_159', ':Category:Subiculum pyramidal cell'), ('NIFCELL:nifext_145', ':Category:Substantia nigra pars compacta dopaminergic cell'), ('NIFCELL:nifext_147', ':Category:Substantia nigra pars reticulata interneuron GABA'), ('NIFCELL:nifext_148', ':Category:Substantia nigra pars reticulata principal cell'), ('NIFCELL:nifext_98', ':Category:Taste bud type 1 cell'), ('NIFCELL:nifext_99', ':Category:Taste bud type 2 cell'), ('NIFCELL:nifext_46', ':Category:Thalamus geniculate nucleus (lateral) interneuron'), ('NIFCELL:nlx_cell_20081203', ':Category:Thalamus geniculate nucleus (lateral) principal neuron'), ('NIFCELL:nlx_cell_1005001', ':Category:Thalamus geniculate nucleus (medial) principal neuron'), ('NIFCELL:nifext_45', ':Category:Thalamus reticular nucleus cell'), ('NIFCELL:nifext_80', ':Category:Trapezoid body intrinsic cell'), ('NIFCELL:nifext_79', ':Category:Trapezoid body medial nucleus principal cell'), ('NIFCELL:nifext_78', ':Category:Trapezoid body principal cell'), ('NIFCELL:nifext_97', ':Category:Trigeminal nucleus intrinsic cell'), ('NIFCELL:nlx_cell_20090305', ':Category:Ventral tegmental area dopamine neuron'), ('NIFCELL:nifext_66', ':Category:Vestibular ganglion cell'), ('NIFCELL:sao709770772', ':Category:Vestibular type 1 hair cell'), ('NIFNEURCIR:nlx_cell_1003113', ':Category:Intrinsic neuron')]


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
    'abbrev':'TROY:abbrev',
    'Abbrev':'TROY:abbrev_troy',
    'alt_id':'oboInOwl:hasDbXref',
    #'definition':'obo:IAO_0000115',  # FIXME alternate is skos:definition...
    #'Definition':'skos:definition',
    'Definition':'TROY:Definition_troy',
    'Id':'rdf:type',
    'Label':'TROY:Label_troy',
    'old_id':'oboInOwl:hasDbXref',  # old vs alt id?
    'superclass':'rdfs:subClassOf',  # translation required
    'Synonym':'TROY:synonym_troy',
    'SuperCategory':'TROY:SuperCategory',
    'type':'TROY:type',  # bloody type vs superclass :/ ask james
    'Category':'rdfs:Category',
    'categories':'rdfs:categories',
    'Categories':'rdfs:Categories',
    'Species':'rdfs:species',
    'DefiningCriteria':'rdfs:DefiningCriteria',
    'DefiningCitation':'rdfs:DefiningCitation',
    'Has_role':'rdfs:Has_Role',
    'PMID':'TROY:PMID_troy',
    'FBbt_Id':'TROY:FBbt_merge',
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
    'http://www.w3.org/2004/02/skos/core#historyNote':'TROY:historyNote_scigraph',
    'http://www.w3.org/2004/02/skos/core#scopeNote':'TROY:scopeNote_scigraph',
    'types':'TROY:types_scigraph',
    'PREFIX':'TROY:prefixWithID_merge',
    'acronym':'TROY:acronym_scigraph',
    'http://ontology.neuinfo.org/NIF/Backend/OBO_annotation_properties.owl#acronym':'TROY:acronym_scigraph',
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
            #print(columns)
            cheatList.append((js[id_][0][0],PrefixWithID))
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
                mid = label
                if  PrefixWithID == 'NIFGA:birnlex_1249':
                    if "\\\\" in right:
                        #right=right.replace("'''","\\'\\'\\'")
                        print(right)
                if 'nlx_only' == prefix:
                    right = columns
                else:
                    #print(index)
                    #print(columns[index])
                    right = columns[index]
                if not right:
                    continue
                if ' ' in mid:
                    mid=mid.replace(' ','_')
                #if 'http' in mid:
                    #mid = rdflib.URIRef(mid)
                    #print(mid)

                if type(right)==str and ':Category:' in right:
                    if ':Category:' in right and ',' not in right and '.' not in right and '(' not in right:
                        #print(right)
                        right = PrefixWithID
                        node = make_node(PrefixWithID, mid, right)
                        g.add_node(*node)
#FIXME: this is where I change category to prefix + ID
                    elif ':Category:' in right and ',' in right and '.' not in right and '(' not in right:
                        #print(right)
                        e = right.split(',')
                        i = ''
                        #print(e)
                        temp = 'hey'
                        for n,ele in enumerate(e):

                            for items in Cat_to_preID:
                            #print(ele)
                            #for n,ele in enumerate(e):
                                #print(items)
                                if ele == items[1]:
                                    e[n] = items[0]

                        #e = str(','.join(e))
                        #print(e)
                            node = make_node(PrefixWithID, mid, e[n])
                            #print('node', node)
                            g.add_node(*node)


                #if ':Category:' in right and mid == 'Located_in':


                #right can be either a string or list, need to be treated for different occurrences
                elif type(right)==list:
                    right = tuple(right)

                    for e in right:
                        if type(e)==bool:
                            continue
                        if not e:
                            continue
                        e=e.replace('  ',' ').replace("'''","' ''").replace('\\','').replace("\\","")
                        if 'http' in e:
                            if 'http://neurolex.org/wiki/Nlx_anat_1005030' in e:
                                e='http://neurolex.org/wiki/Nlx_anat_1005030'
                            if 'http://www.nature.com/nrn/journal/v6/n4/glossary/nrn1646.html#df1' in e:
                                e='http://www.nature.com/nrn/journal/v6/n4/glossary/nrn1646.html#df1'
                            node = make_node(PrefixWithID, mid, rdflib.term.URIRef(e))
                        else:
                            node = make_node(PrefixWithID, mid, e.strip())


                else: #type(right)==str:
                    right=right.replace('  ',' ').replace("'''","' ''").replace('\\','').replace("\\","")
                    e=right
                    e=e.replace('  ',' ')
                    #typos from previous people
                    if '#' in e:
                        
                        if 'http://neurolex.org/wiki/Nlx_anat_1005030' in e:
                            e='http://neurolex.org/wiki/Nlx_anat_1005030'
                        if 'http://www.nature.com/nrn/journal/v6/n4/glossary/nrn1646.html#df1' in e:
                            e='http://www.nature.com/nrn/journal/v6/n4/glossary/nrn1646.html#df1'

                        node = make_node(PrefixWithID, mid, rdflib.term.URIRef(e))
                    else:
                        node = make_node(PrefixWithID, mid, e.strip())

                #print(node)
                g.add_node(*node)
                continue
    g.write()

if __name__ == '__main__':
    main()
    #embed()
#print(cheatList)