import random
import numpy as np
from abc import ABC

from didgelab.evo.shapes import Shape, MutationParameter, MultiSegmentShape

class MutationOperator(ABC):

    def __init__(self, name):
        self.name = name

class MutateOperator(MutationOperator):

    def __init__(self, mutate_gene_prob : float, mutation_rate : float, force_mutation : bool):
        """_summary_

        Args:
            mutate_gene_prob (float): Probability to mutate a single gene (between 0 and 1).
            mutation_rate (float): Strength of mutation (betweeen 0 and 1)
            force_mutation (bool): If no parameter was mutated due to mutate_gene_prob, force_mutation=True will force the mutation of a single, random parameter.
        """

        MutationOperator.init("mutate")

        assert mutate_gene_prob >=0 and mutation_rate<=1
        assert mutation_rate >=0 and mutation_rate<=1

        self.mutate_gene_prob = mutate_gene_prob
        self.mutation_rate = mutation_rate
        self.force_mutation = force_mutation

    def mutate_single_parameter(self, p : MutationParameter):
        if random.random()>0.5:
            p.value += (p.maximum-p.value)*self.mutation_rate*random.random()
        else:
            p.value -= (p.value-p.minimum)*self.mutation_rate*random.random()
        
        if p.value>p.maximum:
            p.value=p.maximum
        elif p.value<p.minimum:
            p.value=p.minimum

    def mutate(self, parameters : MutationParameterSet):

        has_mutated = False
        for i in range(len(parameters.parameters)):
            if random.random()>self.mutate_gene_prob:
                continue
            has_mutated = True
            p = parameters.parameters[i]
            self.mutate_single_parameter(p)

        if not has_mutated and self.force_mutation:
            # mutate a single parameter
            p = np.random.choice(parameters.parameters)
            self.mutate_single_parameter(p)
            parameters.loss = None
        else:
            parameters.loss = None


class CrossOver(MutationOperator):
    
    def crossover(self, shape1, shape2):
        crossx = np.random.random()
        geo1 = shape1.make_geo()
        geo2 = shape2.make_geo()
        crossx1 = crossx*geo1.geo[-1][0]
        crossx2 = crossx*geo2.geo[-1][0]
        
        geo1.geo.append([crossx1, geo1.diameter_at_x(crossx1)])
        geo2.geo.append([crossx1, geo2.diameter_at_x(crossx2)])

        geo1 = list(filter(lambda x : x[0] <= crossx1, geo1.geo))
        geo2 = list(filter(lambda x : x[0] >= crossx2, geo2.geo))
        
        geo2 = sorted(geo2, key=lambda x : x[0])
        geo2 = [[x[0]-geo1[-1][0], x[1] - (geo2[0][1] - geo1[-1][1])] for x in geo2[1:]] 
        
        new_geo = geo1
        new_geo.extend(geo2)

        return MultiSegmentShape(new_geo)
