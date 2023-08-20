from didgelab.calc.geo import Geo
from didgelab.shapes.sintra_shape import EvolveSintra
import random

from deap import base
from deap import creator
from deap import tools
import numpy as np

creator.create("FitnessMin", base.Fitness, weights=(30, 10, 0.000001))
creator.create("Individual", list, fitness=creator.FitnessMin)

toolbox = base.Toolbox()

toolbox.register("attr_float", random.random)

toolbox.register("individual", tools.initRepeat, creator.Individual, 
    toolbox.attr_float, 3)

# define the population to be a list of individuals
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

didgeEvolution = EvolveSintra()

# the goal ('fitness') function to be maximized
def evaluate(individual):
    return didgeEvolution.get_loss(individual)

toolbox.register("evaluate", evaluate)
toolbox.register("mate", tools.cxTwoPoint)
toolbox.register("mate", tools.cxTwoPoint)
toolbox.register("mutate", tools.mutGaussian, mu=0, sigma=1, indpb=0.2)
toolbox.register("select", tools.selTournament, tournsize=3)

def main():
    random.seed(64)

    NGEN=10
    pop = toolbox.population(n=3)
    CXPB, MUTPB = 0.5, 0.2
        
    for g in range(NGEN):
        print("generation " + str(g))
        # Select the next generation individuals
        best_individuals = toolbox.select(pop, 3)
        # Clone the selected individuals
        offspring = list(map(toolbox.clone, best_individuals))

        # Apply mutation on the offspring
        for mutant in offspring:
            toolbox.mutate(mutant)
            del mutant.fitness.values

        # Evaluate the individuals with an invalid fitness
        invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
        fitnesses = list(toolbox.map(toolbox.evaluate, invalid_ind))
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit
            
        # The population is entirely replaced by the offspring
        pop = offspring + best_individuals

if __name__ == "__main__":
    main()