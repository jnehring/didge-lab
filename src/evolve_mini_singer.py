from cad.calc.pipeline import Pipeline, ExplorePipelineStep, FinetuningPipelineStep
from cad.common.app import App
from cad.calc.mutation import ExploringMutator, FinetuningMutator, MutantPool
from cad.calc.didgedb import DidgeMongoDb, DatabaseObject
from cad.calc.parameters import RandomDidgeParameters
from cad.calc.loss import SingerLoss, ScaleLoss
import numpy as np
from cad.calc.geo import geotools
from cad.cadsd.cadsd import CADSDResult
from cad.calc.conv import note_to_freq, note_name, freq_to_note_and_cent
import math
import numpy as np
from cad.calc.geo import Geo

App.init()
App.init_logging()

father=RandomDidgeParameters()
father.set_minmax("length", 1300, 1700)
father.set_minmax("bell_width", 50, 100)
initial_pool=MutantPool.create_from_father(father, App.get_config().n_poolsize)

loss=SingerLoss()
pipeline=Pipeline("minisinger")
pipeline.add_step(ExplorePipelineStep(ExploringMutator(), loss, initial_pool))
pipeline.add_step(FinetuningPipelineStep(FinetuningMutator(), loss))
loss.weight_singer_loss=0.3
pipeline.add_step(FinetuningPipelineStep(FinetuningMutator(), loss))

pipeline.run()
