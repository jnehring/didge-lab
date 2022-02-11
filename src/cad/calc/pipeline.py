from abc import ABC, abstractmethod
import os
import pickle
from cad.calc.loss import LossFunction
from cad.calc.mutation import Mutator, evolve_generations, FinetuningMutator, MutantPoolEntry, evolve_explore
from cad.calc.parameters import MutationParameterSet, FinetuningParameters
from cad.common.app import App
import logging
from cad.calc.mutation import MutantPool
from cad.ui.evolution_ui import EvolutionUI

class PipelineStep(ABC):

    def __init__(self, name):
        self.name=name
        self.n_generations=None
        self.generation_size=None

    def get_n_generations(self):
        if self.n_generations is not None:
            return self.n_generations
        else:
            return App.get_config()["n_generations"]

    def get_generation_size(self):
        if self.generation_size is not None:
            return self.generation_size
        else:
            return App.get_config()["n_generation_size"]

    @abstractmethod
    def execute(pool : MutantPool) -> MutantPool:
        pass

class Pipeline:

    def __init__(self):
        self.steps=[]
        self.folder=os.path.join(App.get_output_folder(), "results")
        
        if not os.path.exists(self.folder):
            os.makedirs(self.folder)

    def add_step(self, step : PipelineStep):
        self.steps.append(step)

    def run(self):

        try:
            logging.info("starting pipeline " + App.get_config()["pipeline_name"])

            pool=None

            no_cache=App.get_config()["no_cache"]
            for i in range(len(self.steps)):

                App.context["current_pipeline_step"]=i
                App.context["pipeline_step_name"]=self.steps[i].name
                App.publish("start_pipeline_step", (i, type(self.steps).__name__))

                pkl_file=os.path.join(self.folder, str(i) + ".pkl")
                if not no_cache and os.path.exists(pkl_file):
                    logging.info(f"loading pipeline step {i} ({self.steps[i].name}) from cache")
                    pool=pickle.load(open(pkl_file, "rb"))
                else:
                    logging.info(f"executing pipeline step {i} ({self.steps[i].name})")
                    pool=self.steps[i].execute(pool)
                    pickle.dump(pool, open(pkl_file, "wb"))

            App.publish("pipeline_finished")
        except Exception as e:
            App.log_exception(e)

class ExplorePipelineStep(PipelineStep):

    def __init__(self, mutator : Mutator, loss : LossFunction, initial_pool : MutantPool, n_generations=None, generation_size=None):
        super().__init__("ExplorePipelineStep")
        self.mutator=mutator
        self.loss=loss
        self.initial_pool=initial_pool
        self.n_generations=n_generations
        self.generation_size=generation_size

    def execute(self,pool : MutantPool) -> MutantPool:
        n_threads=App.get_config()["n_threads"]
        n_generations=self.get_n_generations()
        n_generation_size=self.get_generation_size()

        pool=evolve_explore(self.initial_pool, self.loss, self.mutator, n_generations=n_generations, n_generation_size=n_generation_size, n_threads=n_threads, pipeline_step="explore")
        return pool

class FinetuningPipelineStep(PipelineStep):
    def __init__(self, mutator : Mutator, loss : LossFunction, n_generations=None, generation_size=None):
        super().__init__("FinetuningPipelineStep")
        self.mutator=mutator
        self.loss=loss
        self.n_generations=n_generations
        self.generation_size=generation_size

    def execute(self,pool : MutantPool) -> MutantPool:
        
        n_threads=App.get_config()["n_threads"]
        n_generations=self.get_n_generations()
        n_generation_size=self.get_generation_size()

        pool=evolve_generations(pool, self.loss, self.mutator, n_generations=n_generations, n_generation_size=n_generation_size, n_threads=n_threads, pipeline_step="finetune")
        return pool

class PipelineStartStep(PipelineStep):
    def __init__(self, pool):
        super().__init__("PipelineStart")
        self.pool=pool

    def execute(self, x):
        return self.pool

class OptimizeGeoStep(PipelineStep):
    def __init__(self, loss : LossFunction, n_generations=None, generation_size=None):
        super().__init__("OptimizeGeoStepgPipelineStep")
        self.loss=loss
        self.n_generations=n_generations
        self.generation_size=generation_size

    def execute(self,pool : MutantPool) -> MutantPool:

        mutator=FinetuningMutator()
        n_threads=App.get_config()["n_threads"]
        n_generations=self.get_n_generations()
        n_generation_size=self.get_generation_size()

        new_pool=MutantPool()
        for i in range(0, pool.len()):
            geo=pool.get(i).geo
            param=FinetuningParameters(geo)
            mpe=MutantPoolEntry(param, geo, pool.get(i).loss)
            new_pool.add_entry(mpe)
        pool=evolve_generations(new_pool, self.loss, mutator, n_generations=n_generations, n_generation_size=n_generation_size, n_threads=n_threads, pipeline_step=self.name)
        return pool
