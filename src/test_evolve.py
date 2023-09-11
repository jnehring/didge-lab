import numpy as np

from didgelab.calc.conv import note_to_freq
from didgelab.evo.loss import LossFunction

from didgelab.evo.evolution import MultiEvolution
from didgelab.initializer import init_console
from didgelab.app import get_config, get_app

from didgelab.calc.sim.sim import compute_impedance_iteratively, get_notes, compute_impedance, create_segments

class ScaleTuningLoss(LossFunction):
        
    def __init__(self, base_note, target_scale):
        LossFunction.__init__(self)

        self.base_note = base_note

        f=note_to_freq(self.base_note)
        i=0
        self.target_freqs = []

        target_notes = []
        while True:
            target_notes.extend(np.array(target_scale) + self.base_note + 12*i)
            i+=1
            if note_to_freq(target_notes[-1])>1000 or i>100:
                break

        self.target_freqs = np.log2(note_to_freq(np.array(target_notes)))

    def get_deviations(self, freq, reference):
        
        deviations = []
        for f in freq:
            d = [np.abs(r-f) for r in reference]
            deviations.append(np.min(d))
        return deviations
        
    def get_loss(self, geo, context=None):
        
        evolution_nr = get_app().get_service(MultiEvolution).evolution_nr
        
        if evolution_nr == 1:
            f = np.arange(1, 1000, 2)
            segments = create_segments(geo)
            i = compute_impedance(segments, f)
        else:
            f, i = compute_impedance_iteratively(geo, n_precision_peaks=5)
        notes = get_notes(f,i)

        freqs = np.log2(list(notes.query("rel_imp>0.15").freqs))
        
        fundamental_loss = self.get_deviations([freqs[0]], [self.target_freqs[0]])[0]
        fundamental_loss *= 10
        
        deviations = self.get_deviations(freqs[1:], self.target_freqs)

        toots_loss = np.sum(deviations) / np.max((1, len(deviations)))
        toots_loss *= 2

        n_toots_loss = 10/len(freqs)

        amp_loss = (1-np.mean(list(notes.rel_imp)[1:])) / len(notes)
        amp_loss *= 2
        
        loss = {
            "loss": fundamental_loss + toots_loss + amp_loss + n_toots_loss,
            "fundamental_loss": fundamental_loss,
            "toots_loss": toots_loss,
            "amp_loss": amp_loss,
            "n_toots_loss": n_toots_loss
        }
        return loss

if __name__ == "__main__":

    init_console()
    evo = MultiEvolution(
        ScaleTuningLoss(base_note=-31, target_scale=[0,4,7,10]),
        n_bubbles=3,
        num_generations_1=100,
        num_generations_2=100,
        num_generations_3=100,
        population_size=10,
        generation_size=100
    )
    evo.evolve()