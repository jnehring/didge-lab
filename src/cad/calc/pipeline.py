from abc import ABC, abstractmethod
import os
import pickle
from cad.calc.loss import LossFunction
from cad.calc.mutation import Mutator, evolve_generations, FinetuningMutator, MutantPoolEntry, evolve_explore, ExploringMutator
from cad.calc.parameters import MutationParameterSet, FinetuningParameters, AddPointOptimizer
from cad.common.app import App
import logging
from cad.calc.mutation import MutantPool
from cad.ui.evolution_ui import EvolutionUI
import time
import json

class PipelineStep(ABC):

    def __init__(self, name : str, n_generations : int = None, n_generation_size : int = None):
        self.name=name
        self.n_generations=None
        self.generation_size=None
        self.n_generations=n_generations
        self.n_generation_size=n_generation_size

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
        self.log={}
        self.log_file=os.path.join(self.folder, "pipeline.json")
        
        if not os.path.exists(self.folder):
            os.makedirs(self.folder)

    def write_log(self, key, value):
        self.log[key]=value
        f=open(self.log_file, "w")
        f.write(json.dumps(self.log, indent=4))
        f.close()

    def add_step(self, step : PipelineStep):
        self.steps.append(step)

    def run(self):

        try:
            logging.info("starting pipeline " + App.get_config()["pipeline_name"])
            App.set_context("state", "started")
            start_time=time.time()

            self.write_log("pipeline_name", App.get_config()["pipeline_name"])

            pool=None

            no_cache=App.get_config()["no_cache"]
            for i in range(len(self.steps)):

                step_start_time=time.time()

                App.set_context("current_pipeline_step", i)
                App.set_context("pipeline_step_name", self.steps[i].name)
                App.set_context("pipeline_length", len(self.steps))

                n_generation_size=App.get_config()["n_generation_size"]
                if n_generation_size is None:
                    n_generation_size=self.steps[i].n_generation_size
                if n_generation_size is None:
                    n_generation_size=100
                App.set_context("n_generation_size", n_generation_size)

                n_generations=App.get_config()["n_generations"]
                if n_generations is None:
                    n_generations=self.steps[i].n_generations
                if n_generations is None:
                    n_generations=100
                App.set_context("n_generations", n_generations)

                App.publish("start_pipeline_step", (i, type(self.steps).__name__))

                pkl_file=os.path.join(self.folder, str(i) + ".pkl")
                if not no_cache and os.path.exists(pkl_file):
                    logging.info(f"loading pipeline step {i} ({self.steps[i].name}) from cache")
                    pool=pickle.load(open(pkl_file, "rb"))
                else:
                    msg=f"executing pipeline step {i} ({self.steps[i].name})"
                    msg += f", n_generations={n_generations}"
                    msg += f", n_generation_size={n_generation_size}"
                    msg += ", poolsize=" + str(App.get_config()["n_poolsize"])
                    
                    logging.info(msg)
                    pool=self.steps[i].execute(pool)
                    f=open(pkl_file, "wb")
                    pickle.dump(pool, f)
                    f.close()

                duration=time.time()-step_start_time
                self.write_log(f"duration_step_{i}", duration)

            duration=time.time()-start_time
            self.write_log(f"duration_total", duration)

            App.publish("pipeline_finished")
            logging.info("pipeline finished")
            App.set_context("state", "finished")
        except Exception as e:
            App.log_exception(e)

class ExplorePipelineStep(PipelineStep):

    def __init__(self, mutator : Mutator, loss : LossFunction, initial_pool : MutantPool, n_generations=None, generation_size=None):
        super().__init__("ExplorePipelineStep", n_generations, generation_size)
        self.mutator=mutator
        self.loss=loss
        self.initial_pool=initial_pool

    def execute(self,pool : MutantPool) -> MutantPool:
        n_threads=App.get_config()["n_threads"]

        pool=evolve_explore(self.initial_pool, self.loss, self.mutator)
        return pool

class FinetuningPipelineStep(PipelineStep):
    def __init__(self, mutator : Mutator, loss : LossFunction, n_generations=None, generation_size=None):
        super().__init__("FinetuningPipelineStep", n_generations, generation_size)
        self.mutator=mutator
        self.loss=loss

    def execute(self,pool : MutantPool) -> MutantPool:        
        pool=evolve_generations(pool, self.loss, self.mutator)
        return pool

class PipelineStartStep(PipelineStep):
    def __init__(self, pool, n_generations=None, generation_size=None):
        super().__init__("PipelineStart", n_generations, generation_size)
        self.pool=pool

    def execute(self, x):
        return self.pool

class OptimizeGeoStep(PipelineStep):
    def __init__(self, loss : LossFunction, n_generations=None, generation_size=None):
        super().__init__("OptimizeGeoStepgPipelineStep", n_generations, generation_size)
        self.loss=loss

    def execute(self,pool : MutantPool) -> MutantPool:

        mutator=FinetuningMutator()
        new_pool=MutantPool()
        for i in range(0, pool.len()):
            geo=pool.get(i).geo
            param=FinetuningParameters(geo)
            mpe=MutantPoolEntry(param, geo, pool.get(i).loss)
            new_pool.add_entry(mpe)
        pool=evolve_generations(new_pool, self.loss, mutator)
        return pool

class AddPointOptimizerExplore(PipelineStep):

    def __init__(self, loss : LossFunction, n_generations=None, generation_size=None):
        super().__init__("AddPointOptimizerExplore", n_generations, generation_size)
        self.loss=loss

    def execute(self,pool : MutantPool) -> MutantPool:

        mutator=ExploringMutator()
        new_pool=MutantPool()
        for i in range(0, pool.len()):
            geo=pool.get(i).geo
            param=AddPointOptimizer(geo)
            mpe=MutantPoolEntry(param, geo, pool.get(i).loss)
            new_pool.add_entry(mpe)
        pool=evolve_generations(new_pool, self.loss, mutator)
        return pool

class AddPointOptimizerFinetune(PipelineStep):

    def __init__(self, loss : LossFunction, n_generations=None, generation_size=None):
        super().__init__("AddPointOptimizerFinetune", n_generations, generation_size)
        self.loss=loss

    def execute(self,pool : MutantPool) -> MutantPool:

        mutator=FinetuningMutator()
        new_pool=MutantPool()
        for i in range(0, pool.len()):
            geo=pool.get(i).geo
            param=AddPointOptimizer(geo)
            mpe=MutantPoolEntry(param, geo, pool.get(i).loss)
            new_pool.add_entry(mpe)
        pool=evolve_generations(new_pool, self.loss, mutator)
        return pool
