import pickle
#from cad.calc.geo import geotools, geo
from cad.cadsd.cadsd import CADSD
import argparse
import os

if __name__ == "__main__":

    p = argparse.ArgumentParser()
    p.add_argument('-infile', type=str, help='input file. if infile is not specified it will load the latest file')
    p.add_argument('-limit', type=int, default=1, help='limit to first n shapes')
    args = p.parse_args()

    infile=args.infile
    if infile is None:
        # load latest file
        infile="output"
        folder=sorted(os.listdir(infile))[-1]
        infile=os.path.join(infile, folder, "results")
        pkl=sorted(os.listdir(infile))[-1]
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
        print("-"*20)
        print("shape")
        geo=mutant_pool.get(i).geo
        print(geo.geo)
        print()
        print("notes")
        print(geo.get_cadsd().get_notes())