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

    def mutate(self, father, mutation_rate=1.0, mutation_probability = 1.0):
        mutant = father.copy()

        maxima = np.array([x.maximum for x in mutant.parameters])
        minima = np.array([x.minimum for x in mutant.parameters])
        values = np.array([x.value for x in mutant.parameters])

        diff = mutation_rate * ((np.random.random(len(values))  * (maxima-minima) ) + minima - values)
        
        mutations = np.array([0.0])
        i=0
        while mutations.sum() == 0.0 and i<10:
            mutations = np.random.choice((1,0), size=len(diff), p=(mutation_probability, 1-mutation_probability))
            i+=1

        diff = diff*mutations

        new_values = values + diff

        # make shure the values are within minima and maxima range
        new_values_before = new_values.copy()
        indizes = new_values<minima
        new_values[indizes] = minima[indizes]
        indizes = new_values>maxima
        new_values[indizes] = maxima[indizes]

        for i in range(len(new_values)):
            mutant.parameters[i].value = new_values[i]

        mutant.loss = -1

        return mutant