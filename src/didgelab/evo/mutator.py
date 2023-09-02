from abc import ABC, abstractmethod
from .shapes import Shape
import numpy as np

class Mutator(ABC):

    @abstractmethod
    def mutate(self, shape:Shape)->Shape:
        pass

class MutationRateMutator(Mutator):

    def __init__(self):
        pass

    def mutate(self, father, mutation_rate=1.0):
        mutant = father.copy()

        maxima = np.array([x.maximum for x in mutant.parameters])
        minima = np.array([x.minimum for x in mutant.parameters])
        values = np.array([x.value for x in mutant.parameters])

        diff = mutation_rate * ((np.random.random(len(values))  * (maxima-minima) ) + minima - values)

        new_values = values + diff

        for i in range(len(new_values)):
            mutant.parameters[i].value = new_values[i]

        mutant.loss = -1

        return mutant