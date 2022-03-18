# kizimkazi has two singer notes

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

class KizimkaziLoss(LossFunction):

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

        n_notes=self.n_notes+1
        if self.add_octave:
            n_notes+=1
        n_note_loss=abs(n_notes-len(notes))*self.weights["n_note_loss"]
        if len(notes)<n_notes:
            return {"loss": 1000000}

        impedances=list(notes.impedance)
        impedances=sorted(impedances, reverse=True)
        notes=notes[notes.impedance>=impedances[n_notes-1]]
        
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
        App.full_init("evolve_kizimkazi")

        losslogger=LossCADLogger()

        fundamental=-31
        fundamental_freq=note_to_freq(fundamental)
        
        length=1168.6795199638118

        wavelength_fundamental=freq_to_wavelength(fundamental_freq)
        wavelength_2nd_harmonic=freq_to_wavelength(fundamental_freq*3)
        wavelength_4nd_harmonic=freq_to_wavelength(fundamental_freq*5)

        max_fundamental=math.sin(length*2*np.pi/wavelength_fundamental)
        max_2nd_harmonic=math.sin(length*2*np.pi/wavelength_2nd_harmonic)
        max_4nd_harmonic=math.sin(length*2*np.pi/wavelength_4nd_harmonic)
        logging.info(f"fundamental\t{max_fundamental}\t{fundamental_freq}")
        logging.info(f"2nd harmonic\t{max_2nd_harmonic}\t{fundamental_freq*3}")
        logging.info(f"4th harmonic\t{max_4nd_harmonic}\t{fundamental_freq*5}")

        # fundamental at 73.42 Hz
        # 2nd harmonic at 220.25 Hz
        # 4th harmonic at 367.08 Hz

        target_peaks=[fundamental_freq*3, fundamental_freq*5]

        length-=25
        weights={
            "octave_loss": 0
        }
        loss=KizimkaziLoss(fundamental=fundamental, target_peaks=target_peaks, add_octave=False, n_notes=2, weights=weights)    
        father=MatemaShape(n_bubbles=1, add_bubble_prob=0.3)

        father.set_minmax("length", length, length)
        father.set_minmax("d_pre_bell", 5,30)
        father.set_minmax("bellsize", 2,5)
        father.set_minmax("d_gerade", 0.9, 1.2)

        initial_pool=MutantPool.create_from_father(father, App.get_config()["n_poolsize"], loss)

        pipeline=Pipeline()

        pipeline.add_step(ExplorePipelineStep(ExploringMutator(), loss, initial_pool, n_generations=300, generation_size=70))
        pipeline.add_step(FinetuningPipelineStep(FinetuningMutator(), loss, n_generations=500, generation_size=30))

        for i in range(10):
            pipeline.add_step(AddPointOptimizerExplore(loss, n_generations=100, generation_size=30))
            pipeline.add_step(AddPointOptimizerFinetune(loss, n_generations=100, generation_size=30))

        ui=EvolutionUI()

        pipeline.run()

    except Exception as e:
        App.log_exception(e)
