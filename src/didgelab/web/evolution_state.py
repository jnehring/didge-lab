from ..app import get_app, get_config
import threading
import copy
import logging

class EvolutionState:

    def __init__(self):
        self.population = None
        self.i_generation = None
        self.lock = threading.Lock()

        get_app().register_service(self)

        def on_generation_ended(i_generation, population):
            with self.lock:
                self.i_generation = i_generation
                self.population = population
        get_app().subscribe("generation_ended", on_generation_ended)

    def get_geo(self, i_mutant):
        with self.lock:
            return copy.deepcopy(self.population[i_mutant].make_geo())

    def get_loss(self, i_mutant):
        with self.lock:
            return copy.deepcopy(self.population[i_mutant].loss)
        
    def get_population_size(self):
        with self.lock:
            return len(self.population)