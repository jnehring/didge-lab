from didgelab.calc.geo import Geo
from didgelab.evo.nevolution import Genome, LossFunction, Nevolution
from didgelab.util.didge_visualizer import vis_didge
from didgelab.calc.sim.sim import compute_impedance_iteratively, get_notes, compute_impedance, create_segments, get_log_simulation_frequencies, quick_analysis
from didgelab.calc.conv import note_to_freq, freq_to_note_and_cent, note_name

import numpy as np


def gene2geo(genome : Genome) -> Geo:

    d0 = 32
    x = [0]
    y = [d0]
    min_l = 1000
    max_l = 2000

    d_factor = 75
    min_d = 25

    l = genome.genome[0] * (max_l-min_l) + min_l 
    i=1
    while i < len(genome.genome):
        x.append(genome.genome[i] + x[-1])
        y.append(genome.genome[i+1])
        i += 2

    x = np.array(x)
    x /= x[-1]

    x = x * l
    x[0] = 0
    y = np.array(y) * d_factor + min_d
    y[0] = d0

    geo = list(zip(x,y))

    return Geo(geo)

def get_fundamental_freq(geo):
    segments = create_segments(geo)
    freqs = get_log_simulation_frequencies(50, 120, 2)
    impedance = compute_impedance(segments, freqs)
    fundamental = np.argmax(impedance)
    return freqs[fundamental]

class Loss(LossFunction):
    
    def __init__(self):
        self.target_f = note_to_freq(-31)
        self.target_f = np.log2(self.target_f)

    def loss(self, genome : Genome):
        geo = gene2geo(genome)
        fundamental = get_fundamental_freq(geo)
        loss = np.abs(np.log2(fundamental) - self.target_f)
        return loss

def evolve():

    loss = Loss()

    n_segments = 10
    genome_length = n_segments+1

    def generation_end(evo):

        print(evo.i_generation, np.round(evo.population[0].loss, 3))

    evo = Nevolution(
        loss, 
        genome_length,
        generation_size = 50,
        num_generations = 20,
        population_size = 100,
        mutation_prob = 0.9,
        crossover_prob = 0.9,
        generation_end_callback=generation_end)
    evo.evolve()       
    #genome = Genome(n_genes=n_segments+1)
    #geo = gene2geo(genome)

    #vis_didge(geo)


if __name__ == "__main__":
    evolve()