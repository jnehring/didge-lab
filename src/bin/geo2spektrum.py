# create information about the didgeridoo from a .txt geo file. it can create
# * resonant frequency table
# * a nicely formated geo table
# * impedance and ground spektrum as image
# * image of the didgeridoo geometry

from cad.calc.geo import Geo
import argparse
import json
import matplotlib.pyplot as plt
import seaborn as sns
from cad.ui.visualization import DidgeVisualizer
import os
import pandas as pd

if __name__ == "__main__":

    p = argparse.ArgumentParser()
    p.add_argument('-infile', type=str, required=True, help='input file')
    p.add_argument('-create_spektra', action="store_true", help='create additional images of the sound spektra')
    p.add_argument('-create_shape', action="store_true", help='create an image of the shape')
    p.add_argument('-outfolder', type=str, default="", help='Save output in a specific folder instead of in the current folder.')

    args = p.parse_args()

    geo = Geo(infile=args.infile)

    if not os.path.exists(args.outfolder):
        os.mkdir(args.outfolder)

    outfile = os.path.join(args.outfolder, "tuning.txt")
    f = open(outfile, "w")
    df = geo.get_cadsd().get_notes()
    df["rel_imp"] = df["rel_imp"].apply(lambda x : f"{x:.2f}")
    df["cent-diff"] = df["cent-diff"].apply(lambda x : f"{x:.2f}")
    df["impedance"] = df["impedance"].apply(lambda x : f"{x:.2e}")

    f.write(df.to_string(index=False))
    f.close()

    print("wrote " + outfile)

    outfile = os.path.join(args.outfolder, "formated_geo.txt")
    df = []
    for line in geo.geo:
        df.append(line)
    f = open(outfile, "w")
    df=pd.DataFrame(df, columns=["x", "y"])
    df["x"]=df["x"].apply(lambda x : round(x))
    df["y"]=df["y"].apply(lambda x : round(x))
    f.write(df.to_string(index=False))
    f.close()

    print("wrote " + outfile)

    if args.create_spektra:

        spektra = geo.get_cadsd().get_all_spektra_df()
        plt.clf()
        sns.lineplot(data=spektra, x="freq", y="impedance").set(title="impedance spektrum", ylabel="impedance")
        outfile = os.path.join(args.outfolder, "impedance_spektrum.png")
        plt.savefig(outfile)
        print("wrote " + outfile)

        plt.clf()
        sns.lineplot(data=spektra, x="freq", y="ground").set(title="ground sound spektrum", ylabel="volume")
        outfile = os.path.join(args.outfolder, "ground_spektrum.png")
        plt.savefig(outfile)
        print("wrote " + outfile)

    if args.create_shape:
        plt.clf()
        DidgeVisualizer.vis_didge(geo)
        outfile = os.path.join(args.outfolder, "shape.png")
        plt.savefig(outfile)
        print("wrote " + outfile)



