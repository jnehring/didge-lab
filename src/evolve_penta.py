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
from cad.ui.evolution_ui import EvolutionUI

try:
    App.full_init()

    father_cone=IringaShape()
    father_cone.set_minmax("length", 2000, 2700)
    #father_cone.set_minmax("bell_width", 70, 105)

    father_bubble=AddBubble(None)

    father=ConeBubble(father_cone, father_bubble)

    initial_pool=MutantPool.create_from_father(father, App.get_config().n_poolsize, do_cadsd=True)
    loss=CombinedLoss([ScaleLoss(octave=True, n_peaks=10), AmpLoss(n_peaks=7)], [0.7, 0.3])
    pipeline=Pipeline("penta_didge")
    pipeline.add_step(ExplorePipelineStep(ExploringMutator(), loss, initial_pool))
    pipeline.add_step(FinetuningPipelineStep(FinetuningMutator(), loss))
    
    ui=EvolutionUI()
        
    pipeline.run()
except Exception as e:
    App.log_exception(e)