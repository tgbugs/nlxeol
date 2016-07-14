#!/usr/bin/env python3

from pyontutils.utils import makeGraph, rowParse
from IPython import embed

class convertCurated(rowParse):
    def __init__(self, graph, rows, header):
        pass

    # TODO look at pyontutils/parcellation.py line 128 for reference

def main():
    filename = 'hello world'
    PREFIXES = {'to':'do'}
    new_graph = makeGraph(filename, PREFIXES)
    rows = None  #TODO look at line 15 of nlxeol/mysqlinsert.py for this
    header = None  #TODO
    # convert the header names so that ' ' is replaced with '_'
    convertCurated(new_graph, rows, header)
    embed()

if __name__ == '__main__':
    main()

