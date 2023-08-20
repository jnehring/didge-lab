import configargparse
import logging
from cad.calc.mutation import MutantPool
import pickle
import os
from cad.ui.visualization import visualize_geo_to_files, DidgeVisualizer
from tqdm import tqdm
import seaborn as sns
import matplotlib.pyplot as plt
import json
import pandas as pd
from cad.calc.util.cad_logger import loss_report
from pathlib import Path
import sys
from cad.calc.geo import Geo

from cad.calc.parameters import *
# possible values for contents: all,impedance,spektra,parameters,notes,general
def visualize_geo(geo, output_dir, index, parameters=None, losses=None, contents="all", notes=None):

    praefix=str(index) + "_"
    spektra=geo.cadsd.get_all_spektra_df()

    def in_contents(what):
        return contents == "all" or contents.find(what)>=0

    if in_contents("impedance"):
        plt.clf()
        sns.lineplot(data=spektra, x="freq", y="impedance").set_title("Impedance")
        plt.savefig(os.path.join(output_dir, praefix + "impedance.png"))

    if in_contents("spektra"):
        plt.clf()
        sns.lineplot(data=spektra, x="freq", y="ground").set_title("Ground Tone Spektrum")
        plt.savefig(os.path.join(output_dir, praefix + "ground.png"))

        plt.clf()
        sns.lineplot(data=spektra, x="freq", y="overblow").set_title("1st Overblow Spektrum")
        plt.savefig(os.path.join(output_dir, praefix + "overblow.png"))

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
        df.append(["length", geo.length()])
        df.append(["bell size", geo.geo[-1][1]])
        df.append(["number segments", len(geo.geo)])

        if losses is not None:
            for key, value in losses.items():
                df.append([key, f"{value:.2f}"])
        df=pd.DataFrame(df)
        tex += df.to_latex(index=False, header=False)
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
        # notes table
        tex += "\\subsection{Tuning}\n"
        tex += "\\begin{centering}\n"
        tex += geo.cadsd.get_notes().to_latex(index=False)
        tex += "\\end{centering}\n"

    if in_contents("parameters") and parameters is not None:
        # parameter
        tex += "\\subsection{Evolution Parameters}\n"
        t=type(parameters)
        tex += "\n" + t.__module__ + "." + t.__name__ + "\n\n"
        tex += "\\begin{centering}\n"
        tex += parameters.to_pandas().to_latex(index=False)
        tex += "\\end{centering}\n"

    if in_contents("impedance"):
        # impedance, ground and overblow images
        tex += "\\subsection{Sound Spektra}\n"
        tex += '''
    \\begin{figure}[!h]
    {\\includegraphics[width=100mm]
    {''' + str(index) + '''_impedance.png}
    \\caption{Impedance Spektrum ''' + str(index+1) + '''}}
    \\end{figure}'''

    if in_contents("spektra"):

        tex += '''
    \\begin{figure}[!h]
        \\begin{tabular}{cc}
                \\includegraphics[width=75mm]{''' + str(index) + '''_ground.png} &  
                \\includegraphics[width=75mm]{''' + str(index) + '''_overblow} \\\\
        \\end{tabular}
    \\caption{Spektra ''' + str(index+1) + '''}
    \\end{figure}
    '''

    return tex

def didge_report(geos, outdir, overview_report=None, parameters=None, losses=None, contents="all", notes=None):

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

    if overview_report is not None:
        overview_report.render(tex)


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

class OverviewReport():

    def __init__(self, outdir, cad_report_file=None, pipeline_json_file=None):
        self.cad_report_file=cad_report_file
        self.outdir=outdir
        self.pipeline_json_file=pipeline_json_file
    
    def render(self, tex):

        tex.write("\\section{Evolution Summary}")

        if self.cad_report_file is not None and os.path.exists(self.cad_report_file):
            self.cad_report(tex)

        if self.pipeline_json_file is not None and os.path.exists(self.pipeline_json_file):
            self.pipeline_json(tex)

    def pipeline_json(self, tex):
        f=open(self.pipeline_json_file)
        data=json.load(f)
        f.close()

        # convert all durations to min
        needle="duration_"
        for key, value in data.items():
            if key[0:len(needle)]==needle:
                value/=60
                value=f"{value:.2f} min"
                data[key]=value

        # write table
        tex.write("\\subsection{Evolution Parameters}")

        df=[]
        for key, value in data.items():
            df.append([key, value])
        df=pd.DataFrame(df, columns=["parameter", "value"])

        tex.write(df.to_latex(index=False, header=False))

    def cad_report(self, tex):
            cad_report_outfile=os.path.join(self.outdir, "loss_report.png")
            loss_report(self.cad_report_file, cad_report_outfile)

            tex.write('''
\\subsection{Loss Report}
\\begin{centering}\n
\\begin{figure}[!ht]
{\\includegraphics[width=100mm]{loss_report.png}}
\\caption{Loss Report}
\\end{figure}
\\end{centering}\n
''')


def didge_report_from_pkl(options):

    f=open(options.infile, "rb")
    pool=pickle.load(f)
    f.close()
    
    filename=os.path.basename(options.infile)
    if filename[-4:] == ".pkl":
        filename=filename[0:-4]

    outdir=os.path.join(os.path.dirname(options.infile), "report_" + filename)

    if options.single >= 0:
        outdir += "_single_" + str(options.single)
    if not os.path.exists(outdir):
        os.mkdir(outdir)

    geos=[]
    parameters=[]
    losses=[]

    if options.single>=0:
        mpe=pool.get(options.single)
        geos.append(mpe.geo)
        losses.append(mpe.loss)
        parameters.append(mpe.parameterset)

        didge_report(geos, outdir, overview_report=None, parameters=parameters, losses=losses)
    else:
        cad_report=os.path.join(Path(options.infile).parent.parent.absolute(), "cadlogger.log")
        pipeline_json=os.path.join(Path(options.infile).parent.absolute(), "pipeline.json")
        overview_report=OverviewReport(outdir, cad_report_file=cad_report, pipeline_json_file=pipeline_json)

        total=pool.len()
        if options.limit>0 and options.limit < pool.len():
            total=options.limit

        for i in range(total):
            mpe=pool.get(i)
            geos.append(mpe.geo)
            losses.append(mpe.loss)
            parameters.append(mpe.parameterset)

        didge_report(geos, outdir, overview_report=overview_report, parameters=parameters, losses=losses)

def didge_report_from_txt(options):

    outdir=os.path.join(os.path.dirname(options.infile), "report_" + options.infile[0:-4])
    
    if not os.path.exists(outdir):
        os.mkdir(outdir)

    f=open(options.infile, "r")
    geo=json.load(f)
    f.close()
    geo=Geo(geo)

    geos=[geo]
    print(outdir)
    didge_report(geos, outdir, overview_report=None, parameters=None, losses=None)


if __name__ == "__main__":

    p = configargparse.ArgParser()
    p.add('-infile', type=str, required=True, help='input file')
    p.add('-limit', type=int, default=-1, help='limit to first n shapes')
    p.add('-single', type=int, default=-1, help='create a report for a single shape.')
    options = p.parse_args()

    if not os.path.exists(options.infile):
        print("cannot find infile " + options.infile)
    elif options.infile[-4:] == ".pkl":
        didge_report_from_pkl(options)
    elif options.infile[-4:] == ".txt":
        didge_report_from_txt(options)
    else:
        print("-infile must point to a .pkl or a .txt file.")