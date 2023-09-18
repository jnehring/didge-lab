import configargparse
import logging
import pickle
import os
#from cad.ui.visualization import visualize_geo_to_files, DidgeVisualizer
from didgelab.util.didge_visualizer import DidgeVisualizer
from tqdm import tqdm
import seaborn as sns
import matplotlib.pyplot as plt
import json
import pandas as pd
#from cad.calc.util.cad_logger import loss_report
from pathlib import Path
import sys
from didgelab.calc.geo import Geo
from didgelab.calc.sim.sim import quick_analysis

def to_latex(df):
    s=df.style.hide(axis="index").to_latex()
    lines = s.split("\n")
    header = lines[1].split("&")
    header[-1] = header[-1].replace("\\\\", "")
    header = ["\\textbf{" + h.strip() + "}" for h in header]
    lines[1] = " & ".join(header) + "\\\\"
    return "\n".join(lines)

#from cad.calc.parameters import *
# possible values for contents: all,impedance,spektra,parameters,notes,general
def visualize_geo(geo, output_dir, index, parameters=None, losses=None, contents="all", notes=None):
    geo = Geo(geo)
    praefix=str(index) + "_"
    spektra = quick_analysis(geo)

    def in_contents(what):
        return contents == "all" or contents.find(what)>=0
    
    plt.clf()
    plt.plot(spektra["freqs"], spektra["impedance"], label="Impedance")
    plt.plot(spektra["ground_freqs"], spektra["ground_spectrum"], label="Ground Spectrum")
    plt.legend()
    plt.savefig(os.path.join(output_dir, praefix + "spectra.png"))

    if in_contents("geo"):
        plt.clf()
        DidgeVisualizer.vis_didge(geo)
        plt.savefig(os.path.join(output_dir, praefix + "didge.png"))

    f=open(os.path.join(output_dir, praefix + "geo.txt"), "w")
    f.write(json.dumps(geo.geo))
    f.close()

    # heading
    tex = "\\section{Didge Report No " + str(index) + "}\n\n"

    # general info
    if in_contents("general"):
        tex += "\\subsection{Shape}\n"
        tex += "\\begin{centering}\n"
        df=[]
        df.append(["length", f"{geo.length():.2f} mm"])
        df.append(["bell size", f"{geo.geo[-1][1]:.2f} mm"])
        df.append(["number segments", len(geo.geo)])
        df.append(["volume", f"{geo.compute_volume()/100:.2f} cm2"])

        # if losses is not None:
        #     for key, value in losses.items():
        #         df.append([key, f"{value:.2f}"])
        df=pd.DataFrame(df, columns=["Property", "Value"])
        #df.Value = df.Value.apply(lambda x:f"{x:.2f}")
        tex += to_latex(df)

        if losses is not None:
            tex += "\\hfill"
            l = [[k.replace("_", "\\_"),f"{v:.2f}"] for k,v in losses.items()]
            l = pd.DataFrame(l, columns=["loss type", "value"])
            tex += to_latex(l)

        tex += "\\end{centering}\n\n"
        # didge picture
    if in_contents("geo"):
        tex += '''
\\begin{centering}
\\begin{figure}[!h]
{\\includegraphics[width=\\textwidth]
{''' + praefix + '''didge.png}}
\\caption{Didge ''' + str(index+1) + '''}
\\end{figure}
\\end{centering}\n
'''

    if in_contents("notes"):
        notes = spektra["notes"]
        for c in ["cent_diff", "freq", "impedance", "rel_imp"]:
            notes[c] = notes[c].apply(lambda x:f"{x:.2f}")
        
        notes.note_name = notes.note_name.apply(lambda x:x.replace("#", "\\#"))
        notes = notes.rename(columns={c: c.replace("_", "-") for c in notes.columns})
        tex += "\\subsection{Tuning}\n"
        tex += "\\begin{centering}\n"
        tex += to_latex(notes)
        tex += "\\end{centering}\n"

    if in_contents("parameters") and parameters is not None:
        # parameter
        tex += "\\subsection{Evolution Parameters}\n"
        t=type(parameters)
        tex += "\n" + t.__module__ + "." + t.__name__ + "\n\n"
        tex += "\\begin{centering}\n"
        tex += to_latex(parameters.to_pandas())
        tex += "\\end{centering}\n"

    # impedance, ground and overblow Iimages
    tex += "\\subsection{Sound Spektra}\n"
    tex += '''
\\begin{figure}[!h]
{\\includegraphics[width=100mm]
{''' + str(index) + '''_spectra.png}
\\caption{Sound Spectra ''' + str(index+1) + '''}}
\\end{figure}'''

    return tex

def loss_report(loss_file, outdir):
    plt.clf()

    df = pd.read_csv(loss_file)
    steps = []
    df = df.query("i_generation<i_generation.max()")
    df

    x = df.i_generation.unique()

    columns=list(df.columns)
    columns=columns[4:]
    colors = ['#8a3ffc', '#33b1ff', '#007d79', '#ff7eb6', '#fa4d56', '#fff1f1', '#6fdc8c', '#4589ff', '#d12771', '#d2a106', '#08bdba', '#bae6ff', '#ba4e00', '#d4bbff']
    for i in range(len(columns)):
        c = columns[i]
        ymin=df.groupby("i_generation")[c].min()
        plt.plot(x, ymin, label=c, color=colors[i])
        ymin=df.groupby("i_generation")[c].max()
        plt.plot(x, ymin, label="_" + c, color=colors[i])
        
    for step in df.step.unique()[0:-1]:
        f=df.query("step==@step").i_generation.max()
        plt.axvline(f)

    plt.legend()
    plt.savefig(os.path.join(outdir, "loss_report.png"))
    tex = '''
    \\section{Evolution Overview}
    \\begin{centering}\n
    \\begin{figure}[!ht]
    {\\includegraphics[width=100mm]{loss_report.png}}
    \\caption{Loss Report}
    \\end{figure}
    \\end{centering}\n
    '''

    _df = df.query("i_generation==i_generation.max()")
    columns = _df.columns[4:]
    dfl = {"loss": columns}
    for c in ["min", "max", "mean"]:
        dfl[c] = []
        
    for c in columns:
        dfl["min"].append(_df[c].min())
        dfl["max"].append(_df[c].max())
        dfl["mean"].append(_df[c].mean())

    dfl = pd.DataFrame(dfl)
    for c in ["min", "max", "mean"]:
        dfl[c] = dfl[c].apply(lambda x:f"{x:.2f}")
    dfl.loss = dfl.loss.apply(lambda x : x.replace("_", "\\_"))

    tex += to_latex(dfl)
    
    return tex

def didge_report(geos, outdir, overview_report=None, loss_file=None, parameters=None, losses=None, contents="all", notes=None):

    if parameters is not None:
        assert(len(geos) == len(parameters))

    # open tex file
    tex=open(os.path.join(outdir, "report.tex"), "w")
    tex.write('''\\documentclass{article}

\\usepackage{graphicx}
\\usepackage{booktabs} 
\\usepackage[section]{placeins}

\\begin{document}

''')

    if loss_file is not None:
        tex.write(loss_report(loss_file, outdir))

    with tqdm(total=len(geos)) as pbar:

        for i in range(0, len(geos)):
            p = parameters[i] if parameters is not None else None
            l = losses[i] if losses is not None else None
            t=visualize_geo(geos[i], outdir, i, parameters=p, losses=l, contents=contents, notes=notes)
            tex.write(t)
            pbar.update(1)

        tex.write("\\end{document}")
        tex.close()

    # create pdf
    current_dir=os.path.abspath(".")
    os.chdir(outdir)

    os.system("pdflatex report")
    os.chdir(current_dir)

    # cleanup
    files=os.listdir(outdir)
    print("wrote output to " + outdir)
    for f in files:
        if f=="report.pdf" or f[-7:] == "geo.txt":
            continue
        
        os.remove(os.path.join(outdir, f))

if __name__ == "__main__":

    p = configargparse.ArgParser()
    p.add('-infile', type=str, default=None, help='input file')
    p.add('-limit', type=int, default=-1, help='limit to first n shapes')
    p.add('-single', type=int, default=-1, help='create a report for a single shape.')
    options = p.parse_args()

    if options.infile is None:
        infile = "../evolutions/"
        f = sorted(os.listdir(infile))[-1]
        infile = os.path.join(infile, f)
        n = "checkpoint_final_"
        f = sorted(list(filter(lambda x : x[0:len(n)]==n, os.listdir(infile))))[-1]
        infile = os.path.join(infile, f, "geos.json")
    else:
        infile = options.infile

    if not os.path.exists(infile):
        raise Exception(f"cannot find file {infile}")

    indir = os.path.dirname(infile)
    print("reading from " + indir)
    outdir=os.path.join(indir, "report")
    if not os.path.exists(outdir):
        os.mkdir(outdir)

    loss_file=os.path.join(indir, "..", "losses.csv")
    if not os.path.exists(loss_file):
        loss_file = None

    losses=os.path.join(indir, "losses.json")
    if not os.path.exists(losses):
        losses = None
    else:
        losses = json.load(open(losses, "r"))
    geos = json.load(open(infile, "r"))

    indizes = list(range(len(losses)))
    indizes = sorted(indizes, key=lambda i:losses[i]["loss"])
    geos = [geos[i] for i in indizes]
    losses = [losses[i] for i in indizes]

    didge_report(geos, outdir, overview_report=True, parameters=None, loss_file=loss_file, losses=losses)