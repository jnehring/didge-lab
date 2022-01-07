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

try:
    App.full_init()

    father_cone=IringaShape()
    #father_cone.set_minmax("length", 1700, 2700)
    #father_cone.set_minmax("bell_width", 70, 105)

    father_bubble=AddBubble(None)

    father=ConeBubble(father_cone, father_bubble)

    initial_pool=MutantPool.create_from_father(father, App.get_config().n_poolsize, do_cadsd=True)
    loss=CombinedLoss([ScaleLoss(octave=True, n_peaks=7), AmpLoss(n_peaks=7)], [0.9, 0.1])
    pipeline=Pipeline("penta_didge")
    pipeline.add_step(ExplorePipelineStep(ExploringMutator(), loss, initial_pool))
    pipeline.add_step(FinetuningPipelineStep(FinetuningMutator(), loss))

    geo=[[444.73581406535266, 32.374713861050935], [485.16634261674835, 41.53938686097165], [525.596871168144, 49.9827691676354], [566.0273997195397, 57.021318363756954], [606.4579282709354, 62.083995094297826], [646.8884568223311, 64.75881512242862], [687.3189853737268, 64.82659818381853], [727.7495139251225, 62.279149342888466], [768.1800424765181, 57.320365501050055], [808.6105710279139, 50.35014155712723], [849.0410995793095, 41.93234564250608], [889.4716281307052, 32.74942772210188], [929.9021566821009, 42.0196698161804], [970.3326852334966, 50.56006863683687], [1010.7632137848923, 57.679222065801774], [1051.1937423362879, 62.799560672463514], [1091.6242708876837, 65.50442879771776], [1132.0547994390793, 65.5722118591077], [1172.485327990475, 62.99471492105416], [1212.9158565418707, 57.978269203094875], [1253.3463850932665, 50.9274410263287], [1293.776913644662, 42.41262859771483], [1778.9432562614104, 33.498855444203755], [1819.373784812806, 45.042019678727875], [1859.8043133642018, 57.1503313761795], [1900.2348419155974, 68.55995984209326], [1940.6653704669932, 76.55571306549686], [1981.0958990183888, 80.32441660329829], [2021.5264275697846, 80.87838543090886], [2061.95695612118, 78.15064501572381], [2102.3874846725757, 72.34189401701954], [2142.818013223972, 63.9077156022617], [2183.2485417753674, 54.089076130900686], [2223.679070326763, 43.11773333780769], [2284.1052545367643, 44.48939248360618], [2432.013589505864, 50.10375253947186], [2502.6094450830524, 56.08727979141405], [2606.918323025966, 64.58016484216358], [2668.4148843921157, 71.30328805150347]]

    geo=Geo(geo=geo)
    a,b=loss.get_loss(geo)

#    pipeline.run()
except Exception as e:
    App.log_exception(e)