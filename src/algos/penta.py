from cad.calc.loss import ScaleLoss, AmpLoss, CombinedLoss
from cad.calc.mutation import mutate_explore_then_finetune, evolve_explore, Reporter, evolve_finetune
from cad.calc.parameters import BasicShapeParameters, MutationParameterSet, MutationParameter
from cad.calc.report import make_html_report, geo_report
import pickle

import math
from cad.calc.geo import Geo
from cad.calc.didgmo import didgmo_bridge
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np


# run it:
# python -m algos.evolve_penta

loss=CombinedLoss(
    [ScaleLoss(scale=[0,3,5,7,10], fundamental=-31, n_peaks=5), AmpLoss(n_peaks=5)],
    [3.0, 0.1]
)
father=BasicShapeParameters()

n_explore_iterations=5000
n_finetune_iterations=300
n_poolsize=3
#total=n_explore_iterations+n_poolsize*n_finetune_iterations
total=n_poolsize*n_finetune_iterations
reporter=Reporter(total)
pickle_file="projects/temp/mutants.pickle"

#mutants=evolve_explore(loss, father, n_poolsize, n_explore_iterations, reporter=reporter)
#pickle.dump(mutants, open(pickle_file, "wb"))

def visualize_scales_multiple_shapes(geos):

    df={}
    note_df={}
    for i in range(len(geos)):
        peak, fft=didgmo_bridge(geos[i])
        key="series_" + str(i)
        df[key]=fft["impedance"]
        note_df[key]=[f"{x['note']} {x['cent-diff']}" for x in peak.impedance_peaks]

    max_len=max([len(x) for x in note_df.values()])
    for key in note_df.keys():
        while len(note_df[key]) < max_len:
            note_df[key].append(np.nan)

    note_df=pd.DataFrame(note_df)
    df=pd.DataFrame(df)
    sns.lineplot(data=df)
    plt.show()

class BubbleParameters(MutationParameterSet):

    def __init__(self, geo):
        self.geo=geo
        super(BubbleParameters, self).__init__()
        
        #self.mutable_parameters.append(MutationParameter("length", 2500, 1800, 3000))
        self.mutable_parameters.append(MutationParameter("pos", 0.5, 0, 1))
        self.mutable_parameters.append(MutationParameter("height", 1.5, 1, 2))
        self.mutable_parameters.append(MutationParameter("width", 200, 50, 400))     
    
    def make_geo(self):
        shape=self.geo.copy().geo


        for index in range(len(shape)):
            if shape[index][0]>geo.length()*self.get_value("pos"):
                break

        x4=shape[index][0]
        y4=shape[index][1]
        x0=shape[index-1][0]
        y0=shape[index-1][1]

        alpha=math.atan(0.5*(y4-y0)/(x4-x0))

        x2=self.geo.length()*self.get_value("pos")
        x1=self.geo.length()*self.get_value("pos")-self.get_value("width")/2
        x3=self.geo.length()*self.get_value("pos")+self.get_value("width")/2
        
        get_y = lambda x : 2*(0.5*y0 + math.tan(alpha)*(x-x0))
        y1=get_y(x1)
        y2=get_y(x2)*self.get_value("height")
        y3=get_y(x3)

        add_point = lambda x,y : new_shape.append([x,y])

        new_shape=shape[0:index]
        add_point(x1, y1)
        add_point(x2, y2)
        add_point(x3, y3)
        new_shape.extend(shape[index:])

        new_shape=sorted(new_shape, key=lambda x : x[0])

        return Geo(geo=new_shape)


mutants=pickle.load(open(pickle_file, "rb"))
geo=mutants[0]["mutant"].make_geo()
print(geo.segments_to_str())
bp=BubbleParameters(geo)
print(bp.make_geo().segments_to_str())
#peak, fft=didgmo_bridge(mutants[0]["mutant"].make_geo())
#print(peak.get_impedance_table())

#print("loss before", loss.get_loss(mutants[0]["mutant"].make_geo()))
#mb=MultiBubble(mutants[0]["mutant"].make_geo(), 5)
#mutants=evolve_finetune(loss, mb, 200, reporter=reporter)
#print("loss after", loss.get_loss(mutants[0]["mutant"].make_geo()))
#print(peak.get_impedance_table())


#geo=mutants[0]["mutant"].make_geo()
#print(geo.segments_to_str())

# geos=[geo]
# num=3
# for i in range(num):
#     abp=MultiBubble(geo, i+1)
#     #abp.set("width", (i+1)*200)
#     print(abp.make_geo().segments_to_str())
#     geos.append(abp.make_geo())

# visualize_scales_multiple_shapes(geos)

#print(abp.make_geo().segments_to_str())

#print("before")
#geo_report(mutants[0]["mutant"].make_geo())
#print()

#mutants=evolve_finetune(loss, mutants, n_finetune_iterations, reporter=reporter)

#print("after")
#geo_report(mutants[0]["mutant"].make_geo())

#mutants=mutate_explore_then_finetune(loss=loss, parameters=BasicShapeParameters(), n_poolsize=3, n_explore_iterations=100, n_finetune_iterations=50)
#mutants=mutate_explore_then_finetune(loss=loss, parameters=BasicShapeParameters(), n_poolsize=3, n_explore_iterations=10, n_finetune_iterations=10)

outdir="projects/penta"

#make_html_report(mutants, outdir)
