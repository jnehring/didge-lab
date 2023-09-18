import numpy as np
import math

from didgelab.calc.conv import note_to_freq
from didgelab.evo.loss import LossFunction
from didgelab.evo.loss import diameter_loss, single_note_loss

from didgelab.evo.evolution import MultiEvolution
from didgelab.initializer import init_console
from didgelab.app import get_config, get_app

from didgelab.calc.sim.sim import compute_impedance_iteratively, get_notes, compute_impedance, create_segments

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

        evolution_nr = get_app().get_service(MultiEvolution).evolution_nr

        if evolution_nr <= 2:
            f = np.arange(1, 1000, 2)
            segments = create_segments(geo)
            i = compute_impedance(segments, f)
        else:
            f, i = compute_impedance_iteratively(geo, n_precision_peaks=self.n_notes+1)
        notes = get_notes(f,i)

        fundamental=single_note_loss(-31, notes)*self.weights["fundamental_loss"]
        octave=single_note_loss(-19, notes, i_note=1)*self.weights["octave_loss"]

        #notes=geo.get_cadsd().get_notes()
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
                volume_loss += math.sqrt(1/(note["impedance"]))

        tuning_loss*=self.weights["tuning_loss"]
        volume_loss*=self.weights["volume_loss"]
        
        n_notes=self.n_notes+1
        if self.add_octave:
            n_notes+=1
        n_note_loss=max(n_notes-len(notes), 0)*self.weights["n_note_loss"]

        d_loss = diameter_loss(geo)*self.weights["diameter_loss"]

        loss={
            "tuning_loss": tuning_loss,
            "volume_loss": volume_loss,
            "n_note_loss": n_note_loss,
            "diameter_loss": d_loss,
            "fundamental_loss": fundamental,
            "octave_loss": octave,
        }
        loss["loss"]=sum(loss.values())
        return loss

if __name__ == "__main__":

    init_console()
    evo = MultiEvolution(
        MbeyaLoss(n_notes=5, add_octave=True),    
        n_bubbles=3,
        num_generations_1=100,
        num_generations_2=100,
        num_generations_3=100,
        population_size=10,
        generation_size=100
    )
    evo.evolve()