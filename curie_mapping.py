#!/usr/bin/env python3.5
import csv
import json
import asyncio
from pyontutils.scigraph_client import Vocabulary, Cypher

v = Vocabulary('http://localhost:9000/scigraph')
c = Cypher('http://localhost:9000/scigraph')

prefixes = c.getCuries()

def do_curies(id_):
    output = v.findById(id_)
    if output:
        return id_, output['curie']
    else:
        for prefix in prefixes:
            output = v.findById(prefix + ':' + id_)
            if output:
                return id_, output['curie']
        return id_, 'NLXONLY'

async def check_id(future_, ids):
    loop = asyncio.get_event_loop()
    futures = []
    for id_ in ids:
        future = loop.run_in_executor(None, do_curies, id_)
        futures.append(future)
    output = {}
    for f in futures:
        fragment, curie = await f
        output[fragment] = curie
    future_.set_result(output)

def main():
    with open('neurolex_full.csv', 'rt') as f:
        identifiers = [r[89] for r in csv.reader(f)]

    future = asyncio.Future()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(check_id(future, identifiers))
    fragment_curie_dict = future.result()

    with open('curie_fragment.json', 'wt') as f:
        json.dump(fragment_curie_dict, f)


if __name__ == '__main__':
    main()

