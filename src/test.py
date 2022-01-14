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
from cad.calc.geo import Geo

father_cone=IringaShape()
father_cone.set_minmax("length", 1500, 2500)
#father_cone.set_minmax("bell_width", 70, 105)

App.set_config("pipeline_name", "penta_didge")

father_bubble=AddBubble(None)

father=ConeBubble(father_cone, father_bubble)

father.make_geo()

em=ExploringMutator()

# for i in range(10):
#     mutant=father.copy()
#     em.mutate(mutant)
#     mutant.after_mutate()

#     print(mutant.make_geo().geo[0])    

# geo=Geo(geo=geo)
# CADSDResult.from_geo(geo)
    

# #    pipeline.run()
# except Exception as e:
#     App.log_exception(e)