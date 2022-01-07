from abc import ABC, abstractmethod
import os
import pickle
from cad.calc.loss import Loss
from cad.calc.mutation import Mutator, evolve_generations
from cad.calc.parameters import MutationParameterSet, FinetuningParameters
from cad.common.app import App
import logging
from cad.calc.mutation import MutantPool
from cad.ui.evolution_ui import EvolutionUI

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

        try:
            logging.info("starting pipeline " + self.name)

            pool=None

            no_cache=App.get_config().no_cache
            for i in range(len(self.steps)):

                App.context["current_pipeline_step"]=i
                App.publish("start_pipeline_step", (i, type(self.steps).__name__))

                pkl_file=os.path.join(self.folder, str(i) + ".pkl")
                if not no_cache and os.path.exists(pkl_file):
                    logging.info(f"loading pipeline step {i} ({self.steps[i].name}) from cache")
                    pool=pickle.load(open(pkl_file, "rb"))
                else:
                    logging.info(f"executing pipeline step {i} ({self.steps[i].name})")
                    pool=self.steps[i].execute(pool)
                    pickle.dump(pool, open(pkl_file, "wb"))
        except Exception as e:
            App.log_exception(e)

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

        pool=evolve_generations(self.initial_pool, self.loss, self.mutator, n_generations=n_generations, n_generation_size=n_generation_size, n_threads=n_threads, pipeline_step="explore")
        return pool

class FinetuningPipelineStep(PipelineStep):
    def __init__(self, mutator : Mutator, loss : Loss):
        super().__init__("FinetuningPipelineStep")
        self.mutator=mutator
        self.loss=loss

    def execute(self,pool : MutantPool) -> MutantPool:
        
        n_threads=App.get_config().n_threads
        n_generations=App.get_config().n_generations
        n_generation_size=App.get_config(). n_generation_size

        pool=evolve_generations(pool, self.loss, self.mutator, n_generations=n_generations, n_generation_size=n_generation_size, n_threads=n_threads, pipeline_step="finetune")
        return pool
