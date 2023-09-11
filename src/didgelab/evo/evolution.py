import numpy as np
#from multiprocessing import Pool, Manager

from concurrent.futures import ThreadPoolExecutor
import multiprocessing
from tqdm import tqdm
import time
from typing import List
import logging
import os
import pickle
import sys

from didgelab.app import get_app, get_config
from .mutator import MutationRateMutator
from .loss import LossFunction
from .shapes import Shape, BasicShape, DetailShape


class Evolution():

    def __init__(
        self, 
        loss: LossFunction,
        father_shape : Shape = None, 
        initial_population : List[Shape] = None,
        population_size : int = 10, 
        num_generations : int = 100,
        generation_size : int = 200, 
        mutation_rate_decay_after : float = 0.5,
        mutation_probability : float = 1.0,
        generation_offset : int = 0,
        selection_stratey = "pool",
        early_stopping = True,
        early_stopping_generations = 7
        ):

        assert father_shape is not None or initial_population is not None

        self.father_shape = father_shape
        self.loss = loss
        self.population_size = population_size

        if initial_population is not None:
            self.population = initial_population
        else:
            self.population = []

        self.generation_size = generation_size
        self.mutator = MutationRateMutator()
        self.num_generations = num_generations
        self.mutation_rate_decay_after = mutation_rate_decay_after
        self.mutation_probability = mutation_probability

        self.generation_offset = generation_offset
        self.selection_strategy = selection_stratey

        self.early_stopping = early_stopping
        self.early_stopping_generations = early_stopping_generations

    def create_initial_pool(self):
        self.population = [self.father_shape.copy() for i in range(self.population_size)]

    def mutate(self, params):
        father, i_generation, father_index = params
        try:
            decay_generation = self.num_generations * self.mutation_rate_decay_after
            if i_generation < decay_generation:
                mutation_rate = 1
            else:
                mutation_rate = (i_generation-decay_generation) / (self.num_generations-decay_generation)
            mutant = self.mutator.mutate(father, mutation_rate=mutation_rate, mutation_probability=self.mutation_probability)
            geo = mutant.make_geo()
            loss = self.loss.get_loss(geo)
            mutant.loss = loss
            return mutant, father_index
        except Exception as e:
            logging.exception(e)
            
            # report errors
            if get_app().create_output_folder:
                self.write_error(mutant, geo)
            return father, father_index
        
    # write geo and shape to the error directory
    def write_error(self, mutant, geo):
        error_dir = get_app().get_output_folder()
        error_dir = os.path.join(error_dir, "errors")
        if not os.path.exists(error_dir):
            os.mkdir(error_dir)
        i_error = 0
        found=False
        while not found:
            error_file = os.path.join(error_dir, str(i_error) + ".bin")
            found = not os.path.exists(error_file)
        with open(error_file, "wb") as f:
            pickle.dump((mutant, geo), f)

    def evolve(self, pbar=None):

        #  logging.info("start evolution with parameters " + str(self.__dict__))
        if self.father_shape is not None:
            self.father_shape.loss = self.loss.get_loss(self.father_shape.make_geo())
            self.create_initial_pool()

        if pbar is None:
            pbar = tqdm(total=self.num_generations)

        last_losses = None
        last_improved_generation = None
        for i_generation in range(self.generation_offset, self.num_generations + self.generation_offset):
            arguments = [(self.population[i%self.population_size], i_generation, i%self.population_size) for i in range(self.generation_size)]
            with ThreadPoolExecutor(multiprocessing.cpu_count()) as executor:
                results = executor.map(self.mutate, arguments)
                results = list(results)
                if self.selection_strategy == "pool":
                    self.population = self.select_pool(results)
                elif self.selection_strategy == "global":
                    self.population = self.select_global(results)
                else:
                    raise Exception()                                    

            mini = np.argmin([self.population[i].loss["loss"] for i in range(self.population_size)])
            description = {key:f"{value:.2f}" for key, value in self.population[mini].loss.items()}
            description = str(description).replace("'", "")
            pbar.set_description(description)
            pbar.update(1)

            # apply early stopping
            if self.early_stopping:
                current_losses = np.array([i.loss["loss"] for i in self.population])
                if last_losses is None or not np.array_equal(current_losses, last_losses):
                    last_losses = current_losses
                    last_improved_generation = i_generation
                elif i_generation - last_improved_generation >= self.early_stopping_generations:
                    logging.info("stop evolution because of early stopping")
                    while i_generation<self.num_generations:
                        pbar.update(1)
                        i_generation+=1
                    break

            get_app().publish("generation_ended", (i_generation, self.population))
        
        get_app().publish("evolution_ended", (self.population))
        return self.population
    
    # select the best mutant from each pool
    def select_pool(self, results):
        pool = [[self.population[i]] for i in range(self.population_size)]
        losses = [[self.population[i].loss["loss"]] for i in range(self.population_size)]
        for mutant, father_index in results:
            pool[father_index].append(mutant)
            losses[father_index].append(mutant.loss["loss"])

        new_population = []
        for i in range(len(pool)):
            mini = np.argmin(losses[i])
            new_population.append(pool[i][mini])
        return new_population
    
    # select the best mutants across all mutants
    def select_global(self, results):
        pool = [self.population[i] for i in range(self.population_size)]
        losses = [self.population[i].loss["loss"] for i in range(self.population_size)]
        for mutant, father_index in results:
            pool.append(mutant)
            losses.append(mutant.loss["loss"])

        keys = sorted(np.arange(len(pool)), key=lambda i:losses[i])
        pool = [pool[i] for i in keys[0:self.population_size]]
        return pool

class MultiEvolution:

    def __init__(
        self,
        loss: LossFunction,
        # shape parameters
        n_bubbles=1,
        n_bubble_segments=10,
        n_segments_1 = 10,
        n_segments_2 = 30,
        min_length = 1000,
        max_length = 2000,
        d1 = 32,
        min_bellsize = 65,
        max_bellsize = 80,

        # evolution parameters
        population_size : int = 10, 
        num_generations_1 : int = 100,
        num_generations_2 : int = 50,
        num_generations_3 : int = 50,
        generation_size : int = 200, 
        mutation_rate_decay_after : float = 0.5,
    ):
        get_app().register_service(self)
        get_config()["is_multi_evolution"] = True

        self.evolution_nr = -1

        self.loss=loss
        self.n_bubbles=n_bubbles
        self.n_bubble_segments=n_bubble_segments
        self.n_segments_1=n_segments_1
        self.n_segments_2=n_segments_2
        self.min_length=min_length
        self.max_length = max_length
        self.d1=d1
        self.min_bellsize=min_bellsize
        self.max_bellsize=max_bellsize

        self.population_size=population_size
        self.num_generations_1=num_generations_1
        self.num_generations_2=num_generations_2
        self.num_generations_3=num_generations_3
        self.generation_size=generation_size
        self.mutation_rate_decay_after=mutation_rate_decay_after

    def evolve(self):

        basic_shape = BasicShape(
            n_bubbles=self.n_bubbles,
            n_bubble_segments=self.n_bubble_segments,
            n_segments = self.n_segments_1,
            min_length = self.min_length,
            max_length = self.max_length,
            d1 = self.d1,
            min_bellsize = self.min_bellsize,
            max_bellsize = self.max_bellsize
        )

        n=self.num_generations_1+self.num_generations_2+self.num_generations_3
        pbar = tqdm(total=n)

        self.evolution_nr=1

        num_generations = 0
        evo1 = Evolution(
            self.loss, 
            father_shape = basic_shape,
            population_size = self.population_size, 
            num_generations = self.num_generations_1,
            generation_size = self.generation_size, 
            mutation_rate_decay_after = 1.0,
            mutation_probability = 1.0,
            generation_offset=num_generations
        )
        population = evo1.evolve(pbar=pbar)
        num_generations += self.num_generations_1

        self.evolution_nr=2
        evo2 = Evolution(
            self.loss,
            initial_population = population,
            population_size = self.population_size, 
            num_generations = self.num_generations_2,
            generation_size = self.generation_size, 
            mutation_rate_decay_after = 0,
            mutation_probability = 0.3,
            generation_offset=num_generations
        )
        evo2.evolve(pbar=pbar)
        num_generations += self.num_generations_2

        evo3 = Evolution(
            self.loss,
            initial_population = population,
            population_size = self.population_size, 
            num_generations = self.num_generations_3,
            generation_size = self.generation_size, 
            mutation_rate_decay_after = 0,
            mutation_probability = 0.1,
            generation_offset=num_generations
        )
        self.evolution_nr=3
        evo3.evolve(pbar=pbar)
