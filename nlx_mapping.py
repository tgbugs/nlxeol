#!/usr/bin/env python3.5
import asyncio
import csv
import requests
from time import time
from os.path import expanduser
from IPython import embed
from pyontutils.scigraph_client import Vocabulary
from pyontutils.utils import chunk_list

v = Vocabulary()
curies = sorted([c for c in v.getCuriePrefixes() if c])  # 70 currently

async def fragment_getter(future_, fragments):
    loop = asyncio.get_event_loop()
    futures = []
    for fragment in fragments:
        #print(fragment)
        future = loop.run_in_executor(None, run_curies, fragment)
        futures.append((future))
    mapping = []
    for i, f in enumerate(futures):
        out = await f
        print(i, out)
        mapping.append(out)

    future_.set_result(mapping)

def check_response(puta_curie):
    out = v.findById(puta_curie)
    if out:
        return True

def run_curies(fragment):
    if ':' in fragment:
        if check_response(fragment):
            return fragment, fragment
    for curie in curies:
        puta_curie = curie + ':' + fragment
        if check_response(puta_curie):
            return fragment, puta_curie

    return fragment, None

def main():
    with open(expanduser('~/git/nlxeol/neurolex_full.csv'), 'rt') as f:
        rows = [r for r in csv.reader(f) if ':Category:Resource:' not in r[0]]

    id_index = rows[0].index('Id')
    frags = [[r[id_index] for r in rows][1:]]
    #frags = chunk_list([r[id_index] for r in rows][1:], 500)  # 500 * 70 gives 35k  too high, limit seems to be around 28k netstat connections
    #print(len(fragments))
    #embed()

    responses = []
    for i, fragments in enumerate(frags):
        start = time()
        print(len(fragments))
        future = asyncio.Future()
        loop = asyncio.get_event_loop()
        loop.run_until_complete(fragment_getter(future, fragments))  # BLAZING FAST!
        responses.extend(future.result())
        print('done with frags', i)
        stop = time()
        print('elapsed s = ', stop - start)

    with open(expanduser('~/git/nlxeol/neurolex_mapping.csv'), 'wt') as f:
        csv.writer(f).writerows(responses)
    #embed()

if __name__ == '__main__':
    main()
