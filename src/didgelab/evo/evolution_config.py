from abc import ABC, abstractmethod
import numpy as np

from didgelab.evo.shapes import Cone, Cylinder, MultiSegmentShape, WideningShape
from didgelab.evo.operators import MutateOperator

class EvolutionBoundaries:

    def __init__(self,
        min_length=1000,
        max_length=2000,
        max_bell_diameter=150,
        d1=32
    ):
        self.min_length = min_length
        self.max_length = max_length
        self.max_bell_diameter = max_bell_diameter
        self.d1 = d1

class EvolutionConfig(ABC):

    def __init__(self,
        n_generations=10,
        n_max_population=100,
        n_mutate_population=100,
        n_start_population=10,
        n_threads=8,
        mutation_prob = 0.8,
        mutation_rate = 1.0,
        checkpoint_interval=-1
    ):
        self.n_generations = n_generations
        self.n_max_population = n_max_population
        self.n_mutate_population = n_mutate_population
        self.n_start_population = n_start_population
        self.n_threads = n_threads
        self.mutation_prob = mutation_prob
        self.checkpoint_interval = -1

    @abstractmethod
    def create_basic_shape(self):
        p = np.random.random()
        n_shapes = 4
        if p<1/n_shapes:
            return Cone()
        elif p<2/n_shapes:
            return Cylinder()
        elif p<3/n_shapes:
            return MultiSegmentShape()
        else:
            return WideningShape()

    @abstractmethod
    def get_mutation_operator(self):
        pass

    @abstractmethod
    def get_boundaries(self):
        pass

class StandardEvolutionConfig(EvolutionConfig):

    def __init__(self,
        n_generations = 100,
        n_max_population = 1000,
        n_mutate_population = 100,
        n_start_population = 8,
        n_threads = 8,
        mutation_prob = 0.8,
        mutation_rate = 1.0,
        checkpoint_interval = 20
    ):
        EvolutionConfig.__init__(
            n_generations = n_generations,
            n_max_population = n_max_population,
            n_mutate_population = n_mutate_population,
            n_start_population = n_start_population,
            n_threads = n_threads,
            mutation_prob = mutation_prob,
            mutation_rate = mutation_rate,
            checkpoint_interval = checkpoint_interval
        )

        self.evolution_boundaries = EvolutionBoundaries(
            min_length=1000,
            max_length=2000,
            max_bell_diameter=150,
            d1=32
        )

        self.mutate_operator = MutateOperator(self.mutation_prob, self.mutation_rate)

    def create_basic_shape(self):
        p = np.random.random()
        n_shapes = 4
        if p<1/n_shapes:
            return Cone()
        elif p<2/n_shapes:
            return Cylinder()
        elif p<3/n_shapes:
            return MultiSegmentShape()
        else:
            return WideningShape()

    def get_mutation_operator(self):
        return self.mutate_operator
    
    def get_boundaries(self):
        return self.evolution_boundaries
