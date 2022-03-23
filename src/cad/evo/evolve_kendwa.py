# kendwa is tuned in d and has toots in the minor scale
# it is very long

from cad.calc.pipeline import Pipeline, ExplorePipelineStep, OptimizeGeoStep, PipelineStartStep, FinetuningPipelineStep, AddPointOptimizerExplore, AddPointOptimizerFinetune
from cad.common.app import App
from cad.calc.mutation import ExploringMutator, FinetuningMutator, MutantPool
from cad.calc.parameters import MatemaShape
from cad.calc.loss import LossFunction, TootTuningHelper, diameter_loss, single_note_loss
import numpy as np
from cad.calc.geo import geotools
from cad.cadsd.cadsd import CADSD, cadsd_octave_tonal_balance
from cad.calc.conv import note_to_freq, note_name, freq_to_note_and_cent
import math
import numpy as np
from cad.calc.geo import Geo
from cad.ui.evolution_ui import EvolutionUI
from cad.calc.util.losslog import LossLog
from cad.calc.util.cad_logger import LossCADLogger
import logging

class MbeyaLoss(LossFunction):

    # fundamental: note number of the fundamental
    # add_octave: the first toot is one octave above the fundamental
    # scale: define the scale of the toots of the didgeridoo as semitones relative from the fundamental
    # target_peaks: define the target peaks as list of math.log(frequency, 2). overrides scale 
    # n_notes: set > 0 to determine the number of impedance peaks (above fundamental and add_octave)
    # weights: override the default weights
    # {
    #     "tuning_loss": 8,
    #     "volume_loss": 0.5,
    #     "octave_loss": 4,
    #     "n_note_loss": 5,
    #     "diameter_loss": 0.1,
    #     "fundamental_loss": 8,
    # }
    def __init__(self, fundamental=-31, add_octave=True, n_notes=-1, scale=[0,2,3,5,7,9,10], target_peaks=None, weights={}):
        LossFunction.__init__(self)

        self.weights={
            "tuning_loss": 8,
            "volume_loss": 0.5,
            "octave_loss": 4,
            "n_note_loss": 5,
            "diameter_loss": 0.1,
            "fundamental_loss": 8,
        }
        for key, value in weights.items():
            if key not in self.weights:
                raise Exception(f"Unknown weight {key}")
            self.weights[key]=value


        self.scale=scale
        self.fundamental=fundamental
        self.add_octave=add_octave
        self.n_notes=n_notes

        if target_peaks is not None:
            self.target_peaks=target_peaks
        else:
            self.scale_note_numbers=[]
            for i in range(len(self.scale)):
                self.scale_note_numbers.append(self.scale[i]+self.fundamental)

            n_octaves=10
            self.target_peaks=[]
            for note_number in self.scale_note_numbers:
                for i in range(0, n_octaves):
                    transposed_note=note_number+12*i
                    freq=note_to_freq(transposed_note)
                    freq=math.log(freq, 2)
                    self.target_peaks.append(freq)

    def get_loss(self, geo, context=None):

        fundamental=single_note_loss(-31, geo)*self.weights["fundamental_loss"]
        octave=single_note_loss(-19, geo, i_note=1)*self.weights["octave_loss"]

        notes=geo.get_cadsd().get_notes()
        tuning_loss=0
        volume_loss=0

        start_index=1
        if self.add_octave:
            start_index+=1
        if len(notes)>start_index:
            for ix, note in notes[start_index:].iterrows():
                f1=math.log(note["freq"],2)
                closest_target_index=np.argmin([abs(x-f1) for x in self.target_peaks])
                f2=self.target_peaks[closest_target_index]
                tuning_loss += math.sqrt(abs(f1-f2))
                volume_loss += math.sqrt(1/(note["impedance"]/1e6))

        tuning_loss*=self.weights["tuning_loss"]
        volume_loss*=self.weights["volume_loss"]
        
        n_notes=self.n_notes+1
        if self.add_octave:
            n_notes+=1
        n_note_loss=max(n_notes-len(notes), 0)*self.weights["n_note_loss"]

        d_loss = diameter_loss(geo)*self.weights["diameter_loss"]

        loss={
            # "tuning_loss": tuning_loss,
            "tuning_loss": tuning_loss,
            "volume_loss": volume_loss,
            "n_note_loss": n_note_loss,
            "diameter_loss": d_loss,
            "fundamental_loss": fundamental,
            "octave_loss": octave,
        }
        loss["loss"]=sum(loss.values())
        return loss

if __name__=="__main__":
    try:
        App.full_init("evolve_penta")

        losslogger=LossCADLogger()

        loss=MbeyaLoss(n_notes=3)    
        father=MatemaShape()
        father.set_minmax("length", 2100, 3000)
        initial_pool=MutantPool.create_from_father(father, App.get_config()["n_poolsize"], loss)

        pipeline=Pipeline()

        pipeline.add_step(ExplorePipelineStep(ExploringMutator(), loss, initial_pool, n_generations=500, generation_size=70))
        pipeline.add_step(FinetuningPipelineStep(FinetuningMutator(), loss, n_generations=500, generation_size=30))

        for i in range(15):
            pipeline.add_step(AddPointOptimizerExplore(loss, n_generations=100, generation_size=30))
            pipeline.add_step(AddPointOptimizerFinetune(loss, n_generations=100, generation_size=30))

        ui=EvolutionUI()

        pipeline.run()

    except Exception as e:
        App.log_exception(e)
