import numpy as np

from didgelab.calc.conv import note_to_freq
from didgelab.evo.loss import LossFunction

from didgelab.evo.evolution import MultiEvolution
from didgelab.initializer import init_console

import pickle
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

    error_file = "../evolutions/2023-09-05T19-56-35_test_evolve/errors/0.bin"
    shape, geo = pickle.load(open(error_file, "rb"))

    geo = shape.make_geo().geo
    for i in range(1, len(geo)):
        print(geo[i][0]-geo[i-1][0])

    #shape.make_geo().get_cadsd().get_impedance_spektrum()
    #print(shape)

    # evo = MultiEvolution(
    #     TuningLoss(),
    #     num_generations_1=5,
    #     num_generations_2=5,
    #     num_generations_3=5,
    # )
    # evo.evolve()