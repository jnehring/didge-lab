import pickle
#from cad.calc.geo import geotools, geo
from cad.cadsd.cadsd import CADSD
import argparse
import os
import sys
import re

if __name__ == "__main__":

    p = argparse.ArgumentParser()
    p.add_argument('-infile', type=str, help='input file. if infile is not specified it will load the latest file')
    p.add_argument('-limit', type=int, default=-1, help='limit to first n shapes')
    p.add_argument('-full_shape', action="store_true", help='output the full shape')
    args = p.parse_args()

    infile=args.infile
    if infile is None:
        # load latest file
        infile="output"
        folder=sorted(os.listdir(infile))[-1]
        infile=os.path.join(infile, folder, "results")
        
        candidates=[]
        for x in os.listdir(infile):
            if re.match("[0-9]*\.pkl", x) is None:
                continue
            x=int(x[0:x.find(".")])
            candidates.append(x)
        
        candidates=sorted(candidates)
        pkl=str(candidates[-1]) + ".pkl"
        infile=os.path.join(infile, pkl)

    print("loading from infile " + infile)

    mutant_pool=pickle.load(open(infile, "rb"))

    if args.limit <0:
        limit=mutant_pool.len()
    else:
        limit = min(mutant_pool.len(), args.limit)

    for i in range(limit):
        print("-"*20)
        print(f"mutant {i}")
        geo=mutant_pool.get(i).geo

        if args.full_shape:
            print("shape", str(geo.geo))
        else:
            print("shape", str(geo.geo[-1]))
        print(geo.get_cadsd().get_notes())