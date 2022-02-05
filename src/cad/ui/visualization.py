import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from cad.calc.conv import freq_to_note, note_name
from cad.calc.didgmo import didgmo_bridge, didgmo_high_res
import numpy as np
import os
from cad.cadsd.cadsd import CADSD
from cad.calc.geo import geotools
import json

class DidgeVisualizer:
    
    @classmethod
    def create_didge_shape(cls, geo):

        margin_y=10
        margin_x=10

        max_y=max([x[1] for x in geo.geo])
        center_y = max_y/2 + margin_y

        df={"x":[], "y": [], "series": []}
        for i in range(0, len(geo.geo)):
            p=geo.geo[i]

            p_oben=center_y + p[1]/2 
            p_unten=center_y - p[1]/2

            df["x"].append(p[0])
            df["y"].append(p_oben)
            df["series"].append("oben")
            df["x"].append(p[0])
            df["y"].append(p_unten)
            df["series"].append("unten")
            df["x"].append(p[0])
            df["y"].append(p_unten)
            df["series"].append("seg" + str(i))
            df["x"].append(p[0])
            df["y"].append(p_oben)
            df["series"].append("seg" + str(i))

        return pd.DataFrame(df)
    
    @classmethod
    def vis_didge(cls, geo):

        df=DidgeVisualizer.create_didge_shape(geo)
        n_series=len(df["series"].unique())
        palette = ["#000000"]*n_series
        sns.set(rc={'figure.figsize':(15,3)})
        g=sns.lineplot(data=df, x="x", y="y", hue="series", palette=palette)
        g.set(ylim=(0, df["y"].max()))
        g.set(xlim=(0, df["x"].max()))
        g.get_legend().remove()
        g.set_yticks([])
        g.xaxis.set_ticks_position("top")
        plt.axis('equal')
        return g

        
class FFTVisualiser:
    
    @classmethod
    def vis_fft_and_target(cls, fft, target=None):
        
        #fft=fft.copy().drop(columns=["ground", "overblow"])
        fft=fft.copy()
        fft.reset_index(drop=True, inplace=True) 
        # for column in fft.columns:
        #     fft[column]=fft[column] / fft[column].max()

        sns.set(rc={'figure.figsize':(15,5)})
        sns.lineplot(data=fft, x="freq", y="impedance")
        
        if target != None:
            for t in target:
                note_number=freq_to_note(t)
                #print(t, note_number, note_name(note_number))
                plt.axvline(t, 0, 1, color="black", dashes=[5,5])

def visualize_mutant_to_files(mutant, output_dir, filename):
    plt.clf()
    DidgeVisualizer.vis_didge(mutant.geo)
    geofile=os.path.join(output_dir, filename + "geo.png")
    plt.savefig(geofile)
    plt.clf()
    FFTVisualiser.vis_fft_and_target(mutant.cadsd_result.fft)
    fftfile=os.path.join(output_dir, filename + "fft.png")
    plt.savefig(fftfile)
    return geofile, fftfile

def visualize_geo_to_files(geo, output_dir, filename, skip_cadsd=False, cadsd_result=None):

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    plt.clf()
    DidgeVisualizer.vis_didge(geo)
    geofile=os.path.join(output_dir, filename + "geo.png")
    plt.savefig(geofile, dpi=500)
    plt.clf()

    if not skip_cadsd:

        if cadsd_result==None:
            cadsd_result=CADSDResult.from_geo(geo)
        FFTVisualiser.vis_fft_and_target(cadsd_result.fft)
        fftfile=os.path.join(output_dir, filename + "fft.png")
        plt.savefig(fftfile, dpi=500)

        report=geotools.print_geo_summary(geo, peak=cadsd_result.peaks)

        f=open(os.path.join(output_dir, filename + "report.txt"), "w")
        f.write(report)
        f.write("\n\n")
        f.write(json.dumps(geo.geo))
        f.close()

def visualize_geo_fft(geo, target=None):
    DidgeVisualizer.vis_didge(geo)
    plt.show()
    fft=didgmo_high_res(geo)
    FFTVisualiser.vis_fft_and_target(fft, target)
    plt.show()
    bell_size=geo.geo[-1][1]
    print("size bell end: %.00fmm" % (bell_size))

def print_geo(geo):
    print(geo.segments_to_str())
    fft=didgmo_high_res(geo)
    print(fft.peaks)

def visualize_scales_multiple_shapes(geos, loss, no_grafic=False):

    losses={"geo": [], "loss": [] }
    for i in range(len(geos)):
        losses["geo"].append(i)
        losses["loss"].append(loss.get_loss(geos[i]))

    print(pd.DataFrame(losses))
    df={}
    note_df={}
    for i in range(len(geos)):
        peak, fft=didgmo_bridge(geos[i])
        key="geo " + str(i)
        df[key]=fft["impedance"]
        note_df[key]=[f"{x['note']} {x['cent-diff']} {x['freq']}" for x in peak.impedance_peaks]

    max_len=max([len(x) for x in note_df.values()])
    for key in note_df.keys():
        while len(note_df[key]) < max_len:
            note_df[key].append(np.nan)

    note_df=pd.DataFrame(note_df)
    print(note_df)

    if not no_grafic:
        df=pd.DataFrame(df)
        sns.lineplot(data=df)
        plt.show()

#def draw_impedance_spektrum(cadsd):


#def joint_spektra(cadsd):

    # ground_spectrum=cadsd.get_ground_spektrum()
    # impedance_spectrum=cadsd.get_impedance_spektrum().copy()

    # df=[]
    # for freq, imp in ground_spectrum.items():
    #     df.append([freq, imp, "ground"])

    # df=pd.DataFrame(df, columns=["freq", "impedance", "series"])
    # impedance_spectrum["series"]="impedance"
    # df=pd.concat([df, impedance_spectrum], ignore_index=True)

    # sns.set(rc={'figure.figsize':(15,5)})
    # sns.lineplot(data=df, x="freq", y="impedance", hue="series")


def make_didge_report(geos, cadsds, output_dir):
 
    assert cadsds==None or len(geos) == len(cadsds)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for i in range(len(geos)):

        filename=str(i)
        geo=geos[i]

        cadsd=cadsds[i] if cadsds != None else CADSD(geo)

        plt.clf()
        DidgeVisualizer.vis_didge(geo)
        geofile=os.path.join(output_dir, filename + "geo.png")
        plt.savefig(geofile, dpi=500)
        plt.clf()

        # FFTVisualiser.vis_fft_and_target(cadsd.get_impedance_spektrum())
        #joint_spektra(cadsd)
        plt.clf()
        impedance_spectrum=cadsd.get_impedance_spektrum()
        sns.set(rc={'figure.figsize':(15,5)})
        sns.lineplot(data=impedance_spectrum, x="freq", y="impedance")
        fftfile=os.path.join(output_dir, filename + "impedance_spektrum.png")
        plt.savefig(fftfile, dpi=500)

        plt.clf()
        ground_spectrum=cadsd.get_ground_spektrum()
        sns.set(rc={'figure.figsize':(15,5)})
        sns.lineplot(data=ground_spectrum, x="freq", y="impedance")
        fftfile=os.path.join(output_dir, filename + "ground_spectrum.png")
        plt.savefig(fftfile, dpi=500)

        report=geotools.print_geo_summary(geo, peak=cadsd.get_overblow_notes())

        f=open(os.path.join(output_dir, filename + "report.txt"), "w")
        f.write(report)
        f.write("\n\n")
        f.write(json.dumps(geo.geo))
        f.close()
