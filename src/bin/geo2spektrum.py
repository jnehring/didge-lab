# convert a .txt file containing a didgeridoo geometry to a frequency spektrum

from cad.calc.geo import Geo
import argparse
import json

if __name__ == "__main__":

    p = argparse.ArgumentParser()
    p.add_argument('-infile', type=str, required=True, help='input file')
    p.add_argument('-create_spektra', action="store_true", help='create additional images of the sound spektra')

    args = p.parse_args()

    geo = Geo(infile=args.infile)
    print(geo.get_cadsd().get_notes())

