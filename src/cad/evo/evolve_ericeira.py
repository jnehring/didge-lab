# matema is in d, plays a minor scale and has a singer note at a - 440 Hz

from cad.calc.pipeline import Pipeline, ExplorePipelineStep, OptimizeGeoStep, PipelineStartStep, FinetuningPipelineStep, AddPointOptimizerExplore, AddPointOptimizerFinetune
from cad.common.app import App
from cad.calc.mutation import ExploringMutator, FinetuningMutator, MutantPool
from cad.calc.parameters import MbeyaShape
from cad.evo.evolve_mbeya import MbeyaLoss
from cad.calc.loss import LossFunction, TootTuningHelper, diameter_loss, single_note_loss
import numpy as np
from cad.calc.geo import geotools
from cad.cadsd.cadsd import CADSD, cadsd_octave_tonal_balance
from cad.calc.conv import note_to_freq, note_name, freq_to_note_and_cent, freq_to_wavelength
import math
import numpy as np
from cad.calc.geo import Geo
from cad.ui.evolution_ui import EvolutionUI
from cad.calc.util.losslog import LossLog
from cad.calc.util.cad_logger import LossCADLogger
import logging
import sys
import logging
from cad.calc.parameters import MutationParameterSet

class EriceiraShape(MutationParameterSet):
    
    def __init__(self):
        
        MutationParameterSet.__init__(self)

        self.d1=32
        self.n_bubbles=7
        self.n_bubble_segments=10
        
        self.add_param("length", 2000, 2700)
        self.add_param("bellsize", 65, 100)
        self.add_param("bell_length", 200, 300)
        self.add_param("pre_bell_diameter", 0.7, 0.8)
        
        
        for i in range(self.n_bubbles):
            self.add_param(f"bubble{i}_width", 100, 300)
            self.add_param(f"bubble{i}_height", 5, 30)
            self.add_param(f"bubble{i}_pos", -0.3, 0.3)

    def make_geo(self):
        length = self.get_value("length")
        bellsize = self.get_value("bellsize")
        bell_length = self.get_value("bell_length")
        shape = [
            [0, self.d1],
            [length-bell_length, bellsize * self.get_value("pre_bell_diameter")],
            [length,bellsize]
        ]
        
        bubble_length = length-bell_length
        for i in range(self.n_bubbles):
            
            width = self.get_value(f"bubble{i}_width")
            height = self.get_value(f"bubble{i}_height")
            pos = self.get_value(f"bubble{i}_pos")
                
            x = width * np.arange(self.n_bubble_segments)/self.n_bubble_segments
            y = height * np.sin(np.arange(self.n_bubble_segments)*np.pi/self.n_bubble_segments)
            
            x += bubble_length * i/self.n_bubbles
            x += (0.5+pos)*bubble_length/self.n_bubbles
                        
            if x[0] < 0:
                x += -1*x[0]
                x += 1
            if x[-1] > bubble_length:
                x -= x[-1] - (bubble_length)
            
            geo = Geo(shape)
            y += np.array([geotools.diameter_at_x(geo, _x) for _x in x])
            
            shape = list(filter(lambda a : a[0]<x[0] or a[0]>x[-1], shape))
            shape.extend(zip(x,y))
            shape = sorted(shape, key=lambda x : x[0])
            

        return Geo(shape)
try:
    App.full_init("evolve_ericeira")

    losslogger=LossCADLogger()

    loss=MbeyaLoss(n_notes=8, add_octave=True)    
    father=EriceiraShape()
    initial_pool=MutantPool.create_from_father(father, App.get_config()["n_poolsize"], loss)

    pipeline=Pipeline()

    pipeline.add_step(ExplorePipelineStep(ExploringMutator(), loss, initial_pool, n_generations=200, generation_size=70))
    pipeline.add_step(FinetuningPipelineStep(FinetuningMutator(), loss, n_generations=500, generation_size=30))

    #for i in range(10):
    #    pipeline.add_step(AddPointOptimizerExplore(loss, n_generations=100, generation_size=30))
    #    pipeline.add_step(AddPointOptimizerFinetune(loss, n_generations=100, generation_size=30))

    ui=EvolutionUI()

    pipeline.run()

except Exception as e:
    App.log_exception(e)
