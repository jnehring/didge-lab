import numpy as np

from didgelab.calc.conv import note_to_freq
from didgelab.evo.loss import LossFunction

from didgelab.evo.evolution import MultiEvolution
from didgelab.initializer import init_console

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
        
        notes = geo.get_cadsd().get_notes()
        freqs = np.log2(list(notes.freq))
        
        fundamental_loss = self.get_deviations([freqs[0]], [self.target_freqs[0]])[0]
        fundamental_loss *= 10
        
        deviations = self.get_deviations(freqs[1:], self.target_freqs)

        toots_loss = np.sum(deviations[1:])/2
        toots_loss *= 3

        amp_loss = 1-np.mean(list(notes.rel_imp)[1:])
        amp_loss *= 2
        
        loss = {
            "loss": fundamental_loss + toots_loss + amp_loss,
            "fundamental_loss": fundamental_loss,
            "toots_loss": toots_loss,
            "amp_loss": amp_loss
        }
        return loss

if __name__ == "__main__":

    init_console()
    evo = MultiEvolution(
        ScaleTuningLoss(base_note=-31, target_scale=[0,3,5,7,10]),
        n_bubbles=0,
        num_generations_1=100,
        num_generations_2=0,
        num_generations_3=0,
        population_size=5,
        generation_size=100
    )
    evo.evolve()