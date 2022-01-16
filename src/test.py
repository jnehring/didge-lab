from cad.calc.pipeline import Pipeline, ExplorePipelineStep, FinetuningPipelineStep
from cad.common.app import App
from cad.calc.mutation import ExploringMutator, FinetuningMutator, MutantPool
from cad.calc.parameters import ConeMutationParameter, AddBubble, ConeBubble, BasicShapeParameters, IringaShape
from cad.calc.loss import ScaleLoss, AmpLoss, CombinedLoss
import numpy as np
from cad.calc.geo import geotools
from cad.cadsd.cadsd import CADSDResult
from cad.calc.conv import note_to_freq, note_name, freq_to_note_and_cent
import math
import numpy as np
from cad.ui.visualization import DidgeVisualizer
from cad.calc.geo import Geo
import matplotlib.pyplot as plt

father_cone=IringaShape()
father_cone.set_minmax("length", 1500, 2500)
father_cone.set("length", 1500)
#father_cone.set_minmax("bell_width", 70, 105)

App.set_config("pipeline_name", "penta_didge")


father_bubble=AddBubble(None)
m=0.3
for i in range(5):
    father_bubble.set(str(i)+"height", m, max=m)
    father_bubble.set(str(i)+"width", 0.9)
father_bubble.set("n_bubbles", 5)
father=ConeBubble(father_cone, father_bubble)
print(father)
em=ExploringMutator()
mutant=father.copy()
em.mutate(mutant)
mutant.after_mutate()

# geo=mutant.make_geo()

#print(geo.geo)
# for i in range(10):
#     mutant=father.copy()
#     em.mutate(mutant)
#     mutant.after_mutate()

#     print(mutant.make_geo().geo[0])    



geo=father.make_geo()
DidgeVisualizer.vis_didge(geo)
plt.savefig("geo.png")
# #[[0, 32], [375.0, 33.45454545454545], [409.0909090909091, 43.0492653801948], [443.1818181818182, 51.94888045635403], [477.27272727272725, 59.434299640950755], [511.3636363636364, 64.89592367684115], [545.4545454545455, 67.88415629821893], [579.5454545454545, 68.14727318309573], [613.6363636363636, 65.65346364194046], [647.7272727272727, 60.59512580581307], [681.8181818181818, 53.37492815515591], [715.909090909091, 44.574633051146584], [750.0, 34.90909090909091], [750.0, 34.90909090909091], [784.0909090909091, 44.91360364469142], [818.1818181818182, 54.18981255447127], [852.2727272727273, 61.98811720364786], [886.3636363636364, 67.67357021553863], [920.4545454545455, 70.77844203186392], [954.5454545454545, 71.04155891674073], [988.6363636363636, 68.43111018063794], [1022.7272727272727, 63.14894336851017], [1056.8181818181818, 55.61586025327314], [1090.909090909091, 46.43897131564321], [1125.0, 36.36363636363636], [1237.5, 36.8], [1382.142857142857, 45.114285714285714], [1500.0, 51.88888888888889], [1534.090909090909, 69.01935616688547], [1568.1818181818182, 85.98020723678968], [1602.2727272727273, 101.42557389628287], [1636.3636363636365, 114.05711099526536], [1670.4545454545455, 122.74585399562484], [1704.5454545454545, 126.64510005345213], [1738.6363636363635, 125.283432422501], [1772.7272727272727, 118.62837275611753], [1806.8181818181818, 107.11344188431192], [1840.909090909091, 91.62445762390708], [1875.0, 73.44444444444446], [1960.7142857142856, 78.37142857142858], [2105.3571428571427, 86.6857142857143], [2250.0, 95.00000000000001]]
# for i in range(1,len(geo)):
#     print(geo[i-1][0]-geo[i][0])
# geo=Geo(geo=geo)
#cadsd=CADSDResult.from_geo(geo)
#print(cadsd.peaks)

# #    pipeline.run()
# except Exception as e:
#     App.log_exception(e)