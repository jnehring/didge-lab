from abc import ABC, abstractmethod
import os
import pickle
from cad.calc.loss import Loss
from cad.calc.mutation import Mutator, evolve_generations
from cad.calc.parameters import MutationParameterSet, FinetuningParameters
from cad.common.app import App
import logging

class MutantPool:

    def __init__(self, pool=[]):
        self.pool=pool

    def iterate(self):
        for m in self.mutants:
            yield m[0], m[1]

    def get_pool(self):
        return self.pool

    @classmethod
    def create_from_father(cls, father : MutationParameterSet, n_poolsize : int):
        pool=[[father.copy(), 100000] for i in range(n_poolsize)]
        pool=MutantPool(pool=pool)
        return pool


class PipelineStep(ABC):

    def __init__(self, name):
        self.name=name

    @abstractmethod
    def execute(pool : MutantPool) -> MutantPool:
        pass

class Pipeline:

    def __init__(self, name):
        self.steps=[]
        self.name=name
        self.folder=os.path.join("projects/pipelines/", name)

        if not os.path.exists(self.folder):
            os.makedirs(self.folder)

    def add_step(self, step : PipelineStep):
        self.steps.append(step)

    def run(self):
        
        pool=None

        no_cache=App.get_config().no_cache
        for i in range(len(self.steps)):

            pkl_file=os.path.join(self.folder, str(i) + ".pkl")
            if not no_cache and os.path.exists(pkl_file):
                logging.info(f"loading pipeline step {i} ({self.steps[i].name}) from cache")
                pool=pickle.load(open(pkl_file, "rb"))
            else:
                logging.info(f"executing pipeline step {i} ({self.steps[i].name})")
                pool=self.steps[i].execute(pool)
                pickle.dump(pool, open(pkl_file, "wb"))

class ExplorePipelineStep(PipelineStep):

    def __init__(self, mutator : Mutator, loss : Loss, initial_pool : MutantPool):
        super().__init__("ExplorePipelineStep")
        self.mutator=mutator
        self.loss=loss
        self.initial_pool=initial_pool

    def execute(self,pool : MutantPool) -> MutantPool:
        n_threads=App.get_config().n_threads
        n_generations=App.get_config().n_generations
        n_generation_size=App.get_config().n_generation_size

        pool=evolve_generations(self.initial_pool.pool, self.loss, self.mutator, n_generations=n_generations, n_generation_size=n_generation_size, n_threads=n_threads  )
        pool=MutantPool(pool=pool)
        return pool

class FinetuningPipelineStep(PipelineStep):
    def __init__(self, mutator : Mutator, loss : Loss):
        super().__init__("FinetuningPipelineStep")
        self.mutator=mutator
        self.loss=loss

    def execute(self,pool : MutantPool) -> MutantPool:
        
        parameters=[[FinetuningParameters(x[0].make_geo()), x[1]] for x in pool.pool]

        n_threads=App.get_config().n_threads
        n_generations=App.get_config().n_generations
        n_generation_size=App.get_config(). n_generation_size

        pool=evolve_generations(pool.pool, self.loss, self.mutator, n_generations=n_generations, n_generation_size=n_generation_size, n_threads=n_threads)
        pool=MutantPool(pool=pool)
        return pool
