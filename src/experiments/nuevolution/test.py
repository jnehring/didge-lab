import numpy as np

from experiments.nuevolution.evolve import MbeyaGemome
from didgelab.calc.sim.sim import compute_impedance_iteratively, get_notes, compute_impedance, create_segments, get_log_simulation_frequencies, quick_analysis
from didgelab.evo.nuevolution import Genome, LossFunction, Nuevolution, GeoGenomeA, GeoGenome
from didgelab.calc.conv import note_to_freq, freq_to_note_and_cent, note_name


class MultiplierLoss(LossFunction):
    
    def __init__(self):
        self.target_f = np.arange(1,15) * note_to_freq(-31)
        self.target_f = np.log2(self.target_f)

    def loss(self, genome : GeoGenome):
        geo = genome.genome2geo()
        freqs = get_log_simulation_frequencies(1, 1000, 10)
        segments = create_segments(geo)
        impedance = compute_impedance(segments, freqs)
        notes = get_notes(freqs, impedance)
        notes = notes[notes.impedance>3]

        logfreq = np.log2(notes.freq)
        deltas = []
        for freq in logfreq:
            closest_target_i = np.argmin(np.abs(self.target_f - freq))
            deltas.append(np.abs(self.target_f[closest_target_i]-freq))

        fundamental_loss = 5*deltas[0]
        if len(deltas) == 1:
            harmonic_loss = 10
        else:
            harmonic_loss = np.mean(deltas[1:])
        n_notes_loss = (10-len(notes))/10

        return {
            "total": fundamental_loss + harmonic_loss + n_notes_loss,
            "fundamental_loss": fundamental_loss,
            "harmonic_loss": harmonic_loss,
            "n_notes_loss": n_notes_loss
        }

def get_fundamental_freq(geo):
    segments = create_segments(geo)
    freqs = get_log_simulation_frequencies(50, 120, 2)
    impedance = compute_impedance(segments, freqs)
    fundamental = np.argmax(impedance)
    return freqs[fundamental]

loss = MultiplierLoss()
np.random.seed(0)
for i in range(34):
    geo = MbeyaGemome()
    if i == 32:
        loss.loss(geo)
