# iringa is tuned in a major pentatonic

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

try:
    App.full_init("evolve_iringa")

    losslogger=LossCADLogger()

    class IringaLoss(LossFunction):

        def __init__(self):
            LossFunction.__init__(self)

            self.base_note=-31
            scale=[0,4,5,7,10]
            freq=note_to_freq(self.base_note)
            self.scale_peaks=[freq]
            i=0
            while freq<1000:
                oct=np.floor(i/len(scale))
                note=self.base_note + oct*12 + scale[i%len(scale)]
                freq=note_to_freq(note)
                #print(i, oct*12, scale[i%len(scale), note)
                i+=1
                self.scale_peaks.append(math.log(freq, 2))

        def get_loss(self, geo, context=None):

            fundamental=single_note_loss(self.base_note, geo)*8
            octave=single_note_loss(self.base_note+12, geo, i_note=1)*4

            toot_tuning_loss=0
            toot_volume_loss=0
            notes=geo.get_cadsd().get_notes()
            notes=notes[notes.rel_imp>0.10]

            num_toots_loss=abs(6-len(notes))

            i=0
            for ix, note in notes.iterrows():
                f1=math.log(note["freq"], 2)
                f2=min(self.scale_peaks, key=lambda x:abs(x-f1))
                weight=2*(len(notes)-i)/len(notes)
                i+=1
                toot_tuning_loss += math.sqrt(abs(f1-f2)) * weight
                toot_volume_loss += math.sqrt(1/(note["impedance"]/1e6)) * weight

            toot_tuning_loss/=len(notes)
            toot_volume_loss/=len(notes)
            toot_tuning_loss*=15
            toot_volume_loss*=3

            d_loss = diameter_loss(geo)*0.1

            # make sure the bell does not get smaller 
            shape=geo.geo
            x=geo.geo[-1][0]-200
            y=geotools.diameter_at_x(geo, x)
            shape.append([x,y])
            shape=Geo(shape)
            shape.sort_segments()
            shape=shape.geo
            for i in range(len(shape)):
                if shape[i][0]==x:
                    if shape[i+1]==x:
                        i+=1
                    break
            shape=shape[i:]
            bell_d_loss=diameter_loss(shape)*5

            losses={
                "toot_tuning_loss": toot_tuning_loss,
                "toot_volume_loss": toot_volume_loss,
                "diameter_loss": d_loss,
                "fundamental_loss": fundamental,
                "octave_loss": octave,
                "num_toots_loss": num_toots_loss,
                "bell_d_loss": bell_d_loss
            }
            final_loss=sum(losses.values())
            losses["loss"]=final_loss
            return losses

    loss=IringaLoss()
    father=MatemaShape(n_bubbles=5, add_bubble_prob=0.15)

    father.set_minmax("length", 1500, 3000)
    initial_pool=MutantPool.create_from_father(father, App.get_config()["n_poolsize"], loss)

    pipeline=Pipeline()

    pipeline.add_step(ExplorePipelineStep(ExploringMutator(), loss, initial_pool, n_generations=500, generation_size=70))
    pipeline.add_step(FinetuningPipelineStep(FinetuningMutator(), loss, n_generations=800, generation_size=30))

    for i in range(15):
        pipeline.add_step(AddPointOptimizerExplore(loss, n_generations=100, generation_size=30))
        pipeline.add_step(AddPointOptimizerFinetune(loss, n_generations=100, generation_size=30))

    ui=EvolutionUI()

    pipeline.run()

except Exception as e:
    App.log_exception(e)
