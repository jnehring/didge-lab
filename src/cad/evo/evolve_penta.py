from cad.calc.pipeline import Pipeline, ExplorePipelineStep, FinetuningPipelineStep, OptimizeGeoStep
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
from cad.calc.util.losslog import LossLog
try:
    App.full_init()

    father_cone=IringaShape()
    father_cone.set_minmax("length", 1500, 2500)
    father_cone.set_minmax("bell_width", 70, 105)

    App.set_config("pipeline_name", "penta_didge")

    father_bubble=AddBubble(None)

    father=ConeBubble(father_cone, father_bubble)

    initial_pool=MutantPool.create_from_father(father, App.get_config()["n_poolsize"], do_cadsd=True)
    loss=ScaleLoss(octave=True, n_peaks=7)
    pipeline=Pipeline()
    pipeline.add_step(ExplorePipelineStep(ExploringMutator(), loss, initial_pool))
    pipeline.add_step(FinetuningPipelineStep(FinetuningMutator(), loss))
    pipeline.add_step(OptimizeGeoStep(loss))
    ui=EvolutionUI()

    losslog=LossLog()
        
    pipeline.run()
except Exception as e:
    App.log_exception(e)