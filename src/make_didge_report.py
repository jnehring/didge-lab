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

def visualize_geo(geo, output_dir, index):

    praefix=str(index) + "_"
    spektra=geo.cadsd.get_all_spektra_df()

    plt.clf()
    sns.lineplot(data=spektra, x="freq", y="impedance").set_title("Impedance")
    plt.savefig(os.path.join(output_dir, praefix + "impedance.png"))

    plt.clf()
    sns.lineplot(data=spektra, x="freq", y="ground").set_title("Ground Tone Spektrum")
    plt.savefig(os.path.join(output_dir, praefix + "ground.png"))

    plt.clf()
    sns.lineplot(data=spektra, x="freq", y="overblow").set_title("1st Overblow Spektrum")
    plt.savefig(os.path.join(output_dir, praefix + "overblow.png"))

    plt.clf()
    DidgeVisualizer.vis_didge(geo)
    plt.savefig(os.path.join(output_dir, praefix + "didge.png"))

    f=open(os.path.join(output_dir, praefix + "geo.txt"), "w")
    f.write(json.dumps(geo.geo))
    f.close()

    # heading
    tex = "\\section{Didge Report No " + str(index) + "}\n\n"


    # general info
    tex += "\\subsection{General information}\n"
    tex += "\\begin{centering}\n"
    df=[]
    df.append(["length", geo.length()])
    df.append(["bell size", geo.geo[-1][1]])
    df.append(["number segments", len(geo.geo)])
    df=pd.DataFrame(df)

    # didge picture
    tex += '''
\\begin{figure}[!htb]
\\center{\\includegraphics[width=\\textwidth]
{''' + praefix + '''didge.png}}
\end{figure}
'''

    tex += df.to_latex(index=False, header=False)
    tex += "\\end{centering}\n"
    #tex += "\n\\vspace{2em}"

    # notes table
    tex += "\\subsection{Tuning}\n"
    tex += "\\begin{centering}\n"
    tex += geo.cadsd.get_notes().to_latex(index=False)
    tex += "\\end{centering}\n"
    
    # impedance, ground and overblow images
    tex += "\\begin{centering}\n"
    tex += "\\subsection{Sound Spektra}\n"
    tex += '''
\\begin{figure}[!htb]
\\center{\\includegraphics[width=\\textwidth]
{''' + praefix + '''impedance.png}}
\end{figure}
'''
    tex += '''
\\begin{figure}[!htb]
\\center{\\includegraphics[width=\\textwidth]
{''' + praefix + '''ground.png}}
\end{figure}
'''
    tex += '''
\\begin{figure}[!htb]
\\center{\\includegraphics[width=\\textwidth]
{''' + praefix + '''overblow.png}}
\end{figure}
'''
    tex += "\\end{centering}\n"
    return tex

if __name__ == "__main__":

    p = configargparse.ArgParser()
    p.add('-infile', type=str, required=True, help='input file')
    options = p.parse_args()

    f=open(options.infile, "rb")
    pool=pickle.load(f)
    f.close()

    filename=os.path.basename(options.infile)
    if filename[-4:] == ".pkl":
        filename=filename[0:-4]

    outdir=os.path.join(os.path.dirname(options.infile), "report_" + filename)
    if not os.path.exists(outdir):
        os.mkdir(outdir)

    with tqdm(total=pool.len()) as pbar:
        tex=open(os.path.join(outdir, "report.tex"), "w")
        tex.write('''\\documentclass{article}

\\usepackage{graphicx}
\\usepackage{booktabs} 

\\begin{document}

''')

        for i in range(0, pool.len()):
            mpe=pool.get(i)
            t=visualize_geo(mpe.geo, outdir, i)
            tex.write(t)
            pbar.update(1)

        tex.write("\\end{document}")
        tex.close()

        os.chdir(outdir)
        os.system("pdflatex report")


# from cad.ui.explorer import Explorer
# from cad.calc.parameters import *
# from cad.common.app import App
# from cad.calc.mutation import *


# pipeline="projects/pipelines/penta_didge/"
# App.set_context("pipeline_dir", pipeline)

# explorer=Explorer(pipeline)
# explorer.load("1", 0)
# explorer.start_ui()
