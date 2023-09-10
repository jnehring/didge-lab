import numpy as np

from didgelab.calc.conv import note_to_freq
from didgelab.evo.loss import LossFunction

from didgelab.evo.evolution import Evolution
from didgelab.evo.shapes import BasicShape
from didgelab.initializer import init_console

from test_evolve import ScaleTuningLoss
from didgelab.app import get_config

import pickle

if __name__ == "__main__":
    init_console()
    
    loss = ScaleTuningLoss(base_note=-31, target_scale=[0,3,7])
    get_config()["sim.resolution"] = 50
    evo = Evolution(
        loss,
        BasicShape(n_bubbles=1, n_segments=5),
        num_generations=10,
        generation_size=100,
        mutation_probability=1.0,
        mutation_rate_decay_after=0.0,
        population_size=10,
        selection_stratey="global"
    )
    population = evo.evolve()

    #print(population[0].make_geo().get_cadsd().get_notes().iloc[0]["freq"])
    #shape.make_geo().get_cadsd().get_impedance_spektrum()
    #print(shape)

    # evo = MultiEvolution(
    #     TuningLoss(),
    #     num_generations_1=5,
    #     num_generations_2=5,
    #     num_generations_3=5,
    # )
    # evo.evolve()