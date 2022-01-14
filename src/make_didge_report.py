import configargparse
import logging
from cad.calc.mutation import MutantPool
import pickle
import os
from cad.ui.visualization import visualize_geo_to_files
from tqdm import tqdm

p = configargparse.ArgParser()
p.add('-infile', type=str, required=True, help='input file')
options = p.parse_args()

pool=pickle.load(open(options.infile, "rb"))

outdir=os.path.join(os.path.dirname(options.infile), "report")
if not os.path.exists(outdir):
    os.mkdir(outdir)

with tqdm(total=pool.len()) as pbar:
    for i in range(0, pool.len()):
        mpe=pool.get(i)
        visualize_geo_to_files(mpe.geo, outdir, str(i), cadsd_result=mpe.cadsd_result)
        pbar.update(1)



# from cad.ui.explorer import Explorer
# from cad.calc.parameters import *
# from cad.common.app import App
# from cad.calc.mutation import *


# pipeline="projects/pipelines/penta_didge/"
# App.set_context("pipeline_dir", pipeline)

# explorer=Explorer(pipeline)
# explorer.load("1", 0)
# explorer.start_ui()
