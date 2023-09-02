import numpy as np
from multiprocessing import Pool
import multiprocessing
from tqdm import tqdm
import time

from didgelab.evo.mutator import MutationRateMutator
from didgelab.evo.loss import LossFunction
from didgelab.evo.shapes import Shape

class Evolution():

    def __init__(
        self, 
        father_shape : Shape, 
        loss: LossFunction,
        population_size : int = 10, 
        num_generations : int = 100,
        generation_size : int = 20, 
        mutation_rate_decay_after : float = 0.5,
        ):
        self.father_shape = father_shape
        self.loss = loss
        self.population_size = population_size
        self.population = []
        self.generation_size = generation_size
        self.mutator = MutationRateMutator()
        self.num_generations = num_generations
        self.mutation_rate_decay_after = mutation_rate_decay_after

    def create_initial_pool(self):
        self.population = [self.father_shape.copy() for i in range(self.population_size)]

    def mutate(self, father : Shape, i_generation : int, father_index : int):
        decay_generation = self.num_generations * self.mutation_rate_decay_after
        if i_generation < decay_generation:
            mutation_rate = 1
        else:
            mutation_rate = (i_generation-decay_generation) / (self.num_generations-decay_generation)
        mutant = self.mutator.mutate(father, mutation_rate)
        geo = mutant.make_geo()
        loss = self.loss.get_loss(geo)
        mutant.loss = loss
        return mutant, father_index
        
    def evolve(self):
        self.father_shape.loss = self.loss.get_loss(self.father_shape.make_geo())
        self.create_initial_pool()
        pbar = tqdm(total=self.num_generations)
        for i_generation in range(self.num_generations):
            arguments = [(self.population[i%self.population_size], i_generation, i%self.population_size) for i in range(self.generation_size)]
            with Pool(2*multiprocessing.cpu_count()) as p:
                results = p.starmap(self.mutate, arguments)
                pool = [[self.population[i]] for i in range(self.population_size)]
                losses = [[self.population[i].loss["loss"]] for i in range(self.population_size)]
                for mutant, father_index in results:
                    pool[father_index].append(mutant)
                    losses[father_index].append(mutant.loss["loss"])
                for i in range(len(pool)):
                    mini = np.argmin(losses[i])
                    self.population[i] = pool[i][mini]

            mini = np.argmin([self.population[i].loss["loss"] for i in range(self.population_size)])
            description = {key:f"{value:.2f}" for key, value in self.population[mini].loss.items()}
            description = str(description).replace("'", "")
            pbar.set_description(description)
            pbar.update(1)
