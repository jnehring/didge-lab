import numpy as np

from didgelab.calc.conv import note_to_freq
from didgelab.evo.loss import LossFunction

from didgelab.evo.evolution import MultiEvolution
from didgelab.initializer import init_console

class TuningLoss(LossFunction):
        
    def __init__(self):
        LossFunction.__init__(self)
        
        self.base_note = -31

        self.target_notes = np.array([0, 12,24]) + self.base_note
        self.target_freqs = np.log2(note_to_freq(self.target_notes))

    def get_deviations(self, freq, reference):
        
        deviations = []
        for f in freq:
            d = [np.abs(r-f) for r in reference]
            deviations.append(np.min(d))
        return deviations
        
    def get_loss(self, geo, context=None):
        
        notes = geo.get_cadsd().get_notes()
        freqs = np.log2(list(notes.freq))
        
        deviations = self.get_deviations(freqs, self.target_freqs)
        fundamental_loss = deviations[0]
        fundamental_loss *= 30

        toots_loss = np.sum(deviations[1:])/2
        toots_loss *= 10

        amp_loss = 1-np.mean(list(notes.rel_imp)[1:])
        amp_loss *= 10
        
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
        TuningLoss(),
        n_bubbles=0,
        num_generations_1=50,
        num_generations_2=50,
        num_generations_3=50,
        population_size=10,
        generation_size=200
    )
    evo.evolve()