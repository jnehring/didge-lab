import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from cad.calc.conv import freq_to_note, note_name
from cad.calc.didgmo import didgmo_bridge, didgmo_high_res
import numpy as np

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
        
        fft=fft.copy()
        
        fft=fft.drop(columns=["ground", "overblow", "freq"])
        for column in fft.columns:
            fft[column]=fft[column] / fft[column].max()
        sns.set(rc={'figure.figsize':(15,5)})
        sns.lineplot(data=fft)
        
        if target != None:
            for t in target:
                note_number=freq_to_note(t)
                #print(t, note_number, note_name(note_number))
                plt.axvline(t, 0, 1, color="black", dashes=[5,5])

def visualize_geo_fft(geo, target=None):
    DidgeVisualizer.vis_didge(geo)
    plt.show()
    peak, fft=didgmo_high_res(geo)
    FFTVisualiser.vis_fft_and_target(fft, target)
    plt.show()
    bell_size=geo.geo[-1][1]
    print("size bell end: %.00fmm" % (bell_size))
    return peak.get_impedance_table()

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
