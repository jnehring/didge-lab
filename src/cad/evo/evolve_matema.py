# matema is in d, plays a minor scale and has a singer note at a - 440 Hz

from cad.calc.pipeline import Pipeline, ExplorePipelineStep, OptimizeGeoStep, PipelineStartStep, FinetuningPipelineStep, AddPointOptimizerExplore, AddPointOptimizerFinetune
from cad.common.app import App
from cad.calc.mutation import ExploringMutator, FinetuningMutator, MutantPool
from cad.calc.parameters import MatemaShape
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

class MatemaLoss(LossFunction):

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
    def __init__(self, fundamental=-31, add_octave=True, n_notes=-1, scale=[0,2,3,5,7,9,10], singer_peaks=None, weights={}):
        LossFunction.__init__(self)

        self.weights={
            "other_tuning_loss": 5,
            "other_volume_loss": 0.3,
            "singer_tuning_loss": 16,
            "singer_volume_loss": 1.8,
            "octave_loss": 0,
            "n_note_loss": 5,
            "diameter_loss": 0.1,
            "fundamental_loss": 8,
        }
        for key, value in weights.items():
            if key not in self.weights:
                raise Exception(f"Unknown weight {key}")
            self.weights[key]=value

        self.singer_peaks=[math.log(freq, 2) for freq in singer_peaks]

        self.scale=scale
        self.fundamental=fundamental
        self.add_octave=add_octave
        self.n_notes=n_notes

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

        notes=geo.get_cadsd().get_notes().copy()
        tuning_loss=0
        volume_loss=0

        n_notes=self.n_notes

        notes=notes[notes.rel_imp>0.1]
        n_note_loss=abs(n_notes-len(notes))*self.weights["n_note_loss"]
        if len(notes)<n_notes:
            return {"loss": 1000000}
        
        start_index=1
        if self.add_octave:
            start_index+=1

        notes["log_freq"]=notes.freq.apply(lambda x : math.log(x, 2))

        # singer tuning loss
        singer_indizes=[]
        singer_tuning_loss=0
        singer_volume_loss=0
        for freq in self.singer_peaks:
            closest_note=np.argmin([abs(x-freq) for x in notes.log_freq])
            f2=list(notes.log_freq)[closest_note]
            singer_indizes.append(singer_indizes)
            singer_tuning_loss += math.sqrt(abs(freq-f2))
            singer_volume_loss += math.sqrt(1/(list(notes.impedance)[closest_note]/1e6))
        singer_tuning_loss*=self.weights["singer_tuning_loss"]
        singer_volume_loss*=self.weights["singer_volume_loss"]

        # other toots loss
        other_tuning_loss=0
        other_volume_loss=0
        for i in range(start_index, len(notes)):
            if i in singer_indizes:
                continue
            f1=list(notes.log_freq)[i]
            closest_note=np.argmin([abs(f1-f2) for f2 in self.target_peaks])
            f2=self.target_peaks[closest_note]
            other_tuning_loss += math.sqrt(abs(f1-f2))
            other_volume_loss += math.sqrt(1/(list(notes.impedance)[i]/1e6))

        num_other_toots=len(notes) - (start_index + len(self.singer_peaks))
        other_tuning_loss/=num_other_toots
        other_volume_loss/=num_other_toots
        other_tuning_loss*=self.weights["other_tuning_loss"]
        other_volume_loss*=self.weights["other_volume_loss"]
        
        d_loss = diameter_loss(geo)*self.weights["diameter_loss"]

        loss={
            # "tuning_loss": tuning_loss,
            "singer_tuning_loss": singer_tuning_loss,
            "singer_volume_loss": singer_volume_loss,
            "other_tuning_loss": other_tuning_loss,
            "other_volume_loss": other_volume_loss,
            "n_note_loss": n_note_loss,
            "diameter_loss": d_loss,
            "fundamental_loss": fundamental,
            "octave_loss": octave,
        }
        loss["loss"]=sum(loss.values())
        return loss

if __name__=="__main__":
    try:
        App.full_init("evolve_kizimkazi")

        losslogger=LossCADLogger()

        fundamental=-31
        fundamental_freq=note_to_freq(fundamental)
        
        length=1755.0-25

        wavelength_fundamental=freq_to_wavelength(fundamental_freq)
        # fundamental at 73.42 Hz
        # 2nd harmonic at 220.25 Hz
        # 4th harmonic at 367.08 Hz

        target_peaks=[440]

        length-=25
        loss=MatemaLoss(fundamental=fundamental, singer_peaks=target_peaks, add_octave=False, n_notes=5)    
        father=MatemaShape(n_bubbles=1, add_bubble_prob=0.3)

        father.set_minmax("length", length, length)
        father.set_minmax("d_pre_bell", 5,30)
        father.set_minmax("bellsize", 2,5)
        father.set_minmax("d_gerade", 0.9, 1.2)

        initial_pool=MutantPool.create_from_father(father, App.get_config()["n_poolsize"], loss)

        pipeline=Pipeline()

        pipeline.add_step(ExplorePipelineStep(ExploringMutator(), loss, initial_pool, n_generations=500, generation_size=70))
        pipeline.add_step(FinetuningPipelineStep(FinetuningMutator(), loss, n_generations=500, generation_size=30))

        for i in range(10):
            pipeline.add_step(AddPointOptimizerExplore(loss, n_generations=100, generation_size=30))
            pipeline.add_step(AddPointOptimizerFinetune(loss, n_generations=100, generation_size=30))

        ui=EvolutionUI()

        pipeline.run()

    except Exception as e:
        App.log_exception(e)
