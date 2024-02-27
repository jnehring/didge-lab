"""
python -m didgelab.evo.neolution
"""

import numpy as np
from abc import ABC, abstractmethod
from typing import List
import multiprocessing

class Genome(ABC):

    def __init__(self, n_genes=3, genome=None):
        assert n_genes is not None or genome is not None

        if n_genes is not None:
            self.genome = np.random.sample(size=n_genes)
        elif genome is not None:
            self.genome = genome
        self.loss = None

class LossFunction(ABC):

    @abstractmethod
    def loss(self, shape : Genome):
        pass

class MutationOperator(ABC):

    @abstractmethod
    def apply(self, genome : Genome) -> Genome:
        pass

class CrossoverOperator(ABC):

    @abstractmethod
    def apply(self, genome1 : Genome, genome2 : Genome) -> Genome:
        pass

class SimpleMutation(MutationOperator):

    def __init__(self):

        self.mutation_prob=0.1
        self.mutation_rate=0.1

    def apply(self, genome : Genome):
        mutation = np.random.uniform(low=-self.mutation_rate, high=self.mutation_rate, size=len(genome.genome))
        mutation *= (np.random.sample(size=len(mutation))<self.mutation_prob).astype(int)
        mutation = genome.genome + mutation
        mutation[mutation<0] = 0
        mutation[mutation>0] = 1
        return Genome(genome=mutation)
    
class RandomMutation(MutationOperator):

    def apply(self, genome : Genome):
        return Genome(n_genes=len(genome.genome))
    
class RandomCrossover(CrossoverOperator):

    def apply(self, parent1 : Genome, parent2 : Genome) -> Genome:
        new_genome = list(zip(parent1.genome, parent2.genome))
        new_genome = [np.random.choice(x) for x in new_genome]
        return Genome(genome=new_genome)
    
class AverageCrossover(CrossoverOperator):

    def apply(self, parent1 : Genome, parent2 : Genome) -> Genome:
        new_genome = (parent1.genome + parent2.genome) / 2
        return Genome(genome=new_genome)

class Evolution():

    def __init__( self,
        loss : LossFunction,
        generation_size = 5,
        num_generations = 10,
        population_size = 10,
        mutation_prob = 0.5,
        crossover_prob = 0.5,
        crossover_operators = [RandomCrossover(), AverageCrossover()],
        mutation_operators = [SimpleMutation(), RandomMutation()],
        generation_end_callback = None):

        self.loss = loss
        self.generation_size = generation_size
        self.num_generations = num_generations
        self.population_size = population_size
        self.mutation_prob = mutation_prob
        self.crossover_prob = crossover_prob
        self.crossover_operators = crossover_operators
        self.mutation_operators = mutation_operators
        self.generation_end_callback = generation_end_callback

        self.i_generation = -1
        self.population = None

    def evolve(self):

        # initialize
        pool = multiprocessing.Pool()

        self.population = []
        for i in range(self.population_size):
            self.population.append(Genome())

        losses = pool.map(self.loss.loss, self.population)
        for i in range(len(losses)):
            self.population[i].loss = losses[i]

        self.population = sorted(self.population, key=lambda x:x.loss)

        # compute probabilities that an individual will be selected
        probs = np.arange(0, 1, 1/len(self.population))
        probs = np.exp(probs)
        probs = np.exp(probs)
        probs = np.flip(probs)
        probs /= probs.sum()

        def mutate(genome : Genome, mutation_prob=0.1, mutation_rate=0.1):
            mutation = np.random.uniform(low=-mutation_rate, high=mutation_rate, size=len(genome.genome))
            mutation *= (np.random.sample(size=len(mutation))<mutation_prob).astype(int)
            mutation = genome.genome + mutation
            mutation[mutation<0] = 0
            mutation[mutation>0] = 1
            return Genome(genome=mutation)
        
        def crossover(parent1 : Genome, parent2 : Genome):
            new_genome = list(zip(parent1.genome, parent2.genome))
            new_genome = [np.random.choice(x) for x in new_genome]
            return Genome(genome=new_genome)

        # evolve
        for i_generation in range(self.num_generations):
            
            self.i_generation = i_generation

            losses = np.array([p.loss for p in self.population])
            indizes = np.random.choice(np.arange(len(self.population)), size=self.generation_size, replace=False, p=probs)
            generation = [self.population[i] for i in indizes]
            
            # mutate
            i_mutants = np.arange(self.generation_size)[np.random.sample(self.generation_size)<self.mutation_prob]
            for i in i_mutants:
                operator = np.random.choice(self.mutation_operators)
                generation[i] = operator.apply(generation[i])

            # crossover
            i_crossover = np.arange(self.generation_size)[np.random.sample(self.generation_size)<self.crossover_prob]
            for parent1 in i_crossover:
                parent2 = parent1
                while parent1 == parent2:
                    parent2 = np.random.choice(np.arange(len(self.population)), p=probs)

                operator = np.random.choice(self.crossover_operators)
                generation[parent1] = operator.apply(self.population[parent1], self.population[parent2])
                
            # add only changed genes to population
            i_changed = np.arange(self.generation_size)
            i_changed = i_changed[[i in i_mutants or i in i_crossover for i in i_changed]]
            generation = [generation[i] for i in i_changed]

            # compute loss
            losses = pool.map(self.loss.loss, generation)
            for i in range(len(losses)):
                generation[i].loss = losses[i]

            self.population = self.population + generation
            self.population = sorted(self.population, key=lambda x:x.loss)
            self.population = self.population[0:self.population_size]

            if self.generation_end_callback is not None:
                self.generation_end_callback(self)

        return self.population

class TestLossFunction(LossFunction):

    def loss(self, genome : Genome):
        l = int(len(genome.genome)/2)
        return np.sum(genome.genome[0:l]) / np.sum(genome.genome[l:])

# test method
if __name__ == "__main__":

    def generation_end(evo):

        print(evo.i_generation)
        for i in range(5):
            print(evo.population[i].genome.round(2), evo.population[i].loss.round(2))

    evo = Evolution(TestLossFunction(), generation_end_callback=generation_end)
        
    evo.evolve()
