from cad.calc.didgmo import PeakFile, didgmo_high_res, cleanup
from cad.calc.visualization import DidgeVisualizer, FFTVisualiser
import matplotlib.pyplot as plt
from cad.calc.conv import note_to_freq, note_name, freq_to_note
from cad.calc.geo import Geo
from cad.calc.parameters import BasicShapeParameters, MutationParameterSet
from IPython.display import clear_output
import math
import random
import copy
from tqdm import tqdm
from threading import Lock, Thread
from multiprocessing import Pool, Queue, Process
import concurrent.futures
import traceback
from abc import ABC, abstractmethod
import time
import logging
from cad.common.mt import Producer, produce_and_iterate
import pickle
import numpy as np
import curses

class Mutator(ABC):

    @abstractmethod
    def mutate(self, parameter, i_iteration=1, n_total_iterations=1):
        pass

class ExploringMutator(Mutator):

    def mutate(self, parameters, i_iteration=1, n_total_iterations=1):
        for i in range(len(parameters.mutable_parameters)):
            p=parameters.mutable_parameters[i]
            if p.immutable:
                continue
            p.value = p.minimum + random.random()*(p.maximum-p.minimum)

class FinetuningMutator(Mutator):

    def __init__(self, learning_rate=1):
        #Mutator.__init__(self)
        self.learning_rate=learning_rate

    def mutate(self, parameters, i_iteration=1, n_total_iterations=1):
        p=None
        while p == None:
            index=random.randrange(0, len(parameters.mutable_parameters))
            p=parameters.mutable_parameters[index]
            if p.immutable:
                p=None
        
        if random.random()>0.5:
            p.value += (p.maximum-p.value)*self.learning_rate*random.random()*i_iteration/n_total_iterations
        else:
            p.value -= (p.value-p.minimum)*self.learning_rate*random.random()*i_iteration/n_total_iterations
        
        if p.value>p.maximum:
            p.value=p.maximum
        elif p.value<p.minimum:
            p.value=p.minimum

class Evolver:

    def __init__(self, father, loss, mutator, n_iterations, n_poolsize=10, reporter=None, pbar=None, show_progress=False, log_loss=False, local_rank=0):
        self.father=father
        self.loss=loss
        self.n_iterations=n_iterations
        self.n_poolsize=n_poolsize
        self.pool=[]
        self.reporter=reporter
        self.is_log_loss=log_loss
        self.show_progress=show_progress
        self.mutator=mutator
        self.local_rank=local_rank
        self.pbar=pbar

    def run(self):
        total_loss=0.0

        if self.is_log_loss:
            self.log_loss=[]

        if self.show_progress and self.pbar is None:
            self.pbar=tqdm(total=self.n_iterations)

        self.pool.append({
            "mutant": self.father,
            "loss": self.loss.get_loss(self.father.make_geo())
        })

        for i_iteration in range(self.n_iterations):
            self.current_iteration=i_iteration
            mutant=self.father.copy()
            
            mutant.before_mutate()
            self.mutator.mutate(mutant, i_iteration=i_iteration, n_total_iterations=self.n_iterations)
            mutant.after_mutate()
            
            mutant_loss=self.loss.get_loss(mutant.make_geo())
            if self.is_log_loss:
                self.log_loss.append(mutant_loss)
            total_loss += mutant_loss

            self.pool.append({
                "loss": mutant_loss,
                "mutant": mutant 
            })

            self.pool.sort(key=lambda x : x["loss"])
            if len(self.pool) > self.n_poolsize:
                self.pool=self.pool[0:self.n_poolsize]

            if self.reporter != None:
                self.reporter.update(self)

            average_loss=total_loss / (1+i_iteration)
            best_loss=self.pool[0]["loss"]

            if self.show_progress:
                self.pbar.update(1)
        return self.pool[0]["mutant"], self.pool[0]["loss"]

    def get_pool(self):
        return [x["mutant"] for x in self.pool]

class ReporterCallback(ABC):

    @abstractmethod
    def call(self, evolver, reporter):
        pass

class ScaleLoggingCallback(ReporterCallback):

    def call(self, evolver, reporter):
        geo=evolver.pool[0]["mutant"].make_geo()
        fft=didgmo_high_res(geo)
        print("-"*50)
        print("iteration " + str(reporter.pbar.n))
        print("-"*50)
        print(geo.segments_to_str())
        print("-"*50)
        print(fft.peaks)
        print("-"*50)

class Reporter(Thread):

    def __init__(self, total, description=None):
        self.lock = Lock()
        self.pbar=tqdm(total=total)
        self.callbacks=[]
        self.evolvers={}

    def register_evolvers(self, evolvers):
        for evolver in self.evolvers:
            self.evolvers[evolver.local_rank]=evolver

    def set_description(self, description):
        self.pbar.set_description(description)

    def register_callback(self, intervall, callback):
        self.callbacks.append({
            "intervall": intervall,
            "callback": callback
        })

    def update(self, evolver):
        self.lock.acquire()
        self.pbar.update(1)
        
        for i in range(len(self.callbacks)):
            if self.pbar.n % self.callbacks[i]["intervall"] == 0:
                self.callbacks[i]["callback"].call(evolver, self)
        self.lock.release()

def get_n_best_results(pool, n):
    pool.sort(key=lambda x : x["loss"])
    return pool[0:n]

def run_evolver(evolver):
    try:
        evolver.run()
    except Exception as e:
        print(traceback.format_exc())

def evolve_explore(loss, parameters, n_poolsize, n_explore_iterations, n_threads=4, reporter=None):
    try:
        n_explore_iterations_thread=int(n_explore_iterations/n_threads)

        if reporter == None:
            reporter=Reporter(n_explore_iterations)
        reporter.set_description("exploring")

        evolvers=[]
        for i in range(n_threads):
            evolver=Evolver(copy.deepcopy(parameters), copy.deepcopy(loss), ExploringMutator(), n_explore_iterations_thread, n_poolsize=n_poolsize, reporter=reporter, local_rank=i)
            evolvers.append(evolver)

        reporter.register_evolvers(evolvers)

        with concurrent.futures.ThreadPoolExecutor(max_workers=n_threads) as executor:
            executor.map(run_evolver, evolvers)

        mutant_pool=[]
        [mutant_pool.extend(m.pool) for m in evolvers]
        mutant_pool=get_n_best_results(mutant_pool, n_poolsize)
        return mutant_pool
    except Exception as e:
        print(traceback.format_exc())
    finally:
        cleanup()

def evolve_finetune(loss, mutant_pool, n_finetune_iterations, n_threads=4, reporter=None):

    if isinstance(mutant_pool, MutationParameterSet):
        mutant_pool=[{"loss": 0, "mutant": mutant_pool}]

    if len(mutant_pool)<n_threads:
        n_threads=len(mutant_pool)

    try:

        if reporter == None:
            reporter=Reporter(n_finetune_iterations)
        reporter.set_description("finetuning")
        evolvers=[]
        lr=0.5
        n_iterations_thread=int(n_finetune_iterations/len(mutant_pool))
        for mutant in mutant_pool:
            evolver=Evolver(copy.deepcopy(mutant), copy.deepcopy(loss), FinetuningMutator(learning_rate=lr), n_iterations_thread, n_poolsize=1, reporter=reporter)
            evolvers.append(evolver)

        with concurrent.futures.ThreadPoolExecutor(max_workers=n_threads) as executor:
            executor.map(run_evolver, evolvers)

        mutant_pool=[]
        [mutant_pool.extend(m.pool) for m in evolvers]
        mutant_pool=get_n_best_results(mutant_pool, len(mutant_pool))

        return mutant_pool
    except Exception as e:
        print(traceback.format_exc())
    finally:
        cleanup()


# mutate first in an exploratory and then in a fine tuning fashion
def mutate_explore_then_finetune(loss=None, parameters=BasicShapeParameters(), n_poolsize=10, n_explore_iterations=3000, n_finetune_iterations=300, n_threads=4):
    assert(loss != None)

    try:
        start=time.time()
        # explore
        n_explore_iterations_thread=int(n_explore_iterations/n_threads)
        reporter=Reporter(n_explore_iterations + n_poolsize*n_finetune_iterations)
        reporter.set_description("exploring")

        evolvers=[]
        for i in range(n_threads):
            evolver=Evolver(copy.deepcopy(parameters), copy.deepcopy(loss), ExploringMutator(), n_explore_iterations_thread, n_poolsize=n_poolsize, reporter=reporter)
            evolvers.append(evolver)

        with concurrent.futures.ThreadPoolExecutor(max_workers=n_threads) as executor:
            executor.map(run_evolver, evolvers)

        mutant_pool=[]
        [mutant_pool.extend(m.pool) for m in evolvers]
        mutant_pool=get_n_best_results(mutant_pool, n_poolsize)

        # finetune
        reporter.set_description("finetuning")
        evolvers=[]
        lr=0.5
        for mutant in mutant_pool:
            evolver=Evolver(copy.deepcopy(mutant["mutant"]), copy.deepcopy(loss), FinetuningMutator(learning_rate=lr), n_finetune_iterations, n_poolsize=1, reporter=reporter)
            evolvers.append(evolver)

        with concurrent.futures.ThreadPoolExecutor(max_workers=n_threads) as executor:
            executor.map(run_evolver, evolvers)
        mutant_pool=[]
        [mutant_pool.extend(m.pool) for m in evolvers]
        mutant_pool=get_n_best_results(mutant_pool, n_poolsize)

        print(f"done in {time.time()-start:.2f}s")

        return mutant_pool
    except Exception as e:
        print(traceback.format_exc())
    finally:
        cleanup()

class MutationJob:

    def __init__(self, father, mutator, loss, pool_index, i_generation, n_generations):
        self.father=father
        self.pool_index=pool_index
        self.mutator=mutator
        self.loss=loss
        self.i_generation=i_generation
        self.n_generations=n_generations
    
    def mutate(self, result_queue):
        mutant=self.father.copy()
        self.mutator.mutate(mutant, i_iteration=self.i_generation, n_total_iterations=self.n_generations)
        mutant.after_mutate()
        mutant_loss, cadsd_result=self.loss.get_loss(mutant.make_geo())
        result_queue.put((mutant, mutant_loss, cadsd_result, self.pool_index))

class EvolutionDisplay:

    def __init__(self, n_generations, n_generation_size):
        self.n_generations=n_generations
        self.n_generation_size=n_generation_size
        self.cache=""
        self.disabled=False
        self.is_initialized=False

    def update_iteration(self):
        self.i_iteration+=1
        self.visualize()

    def update_generation(self, i_generation, best_geo, cadsd_result, best_loss, mean_loss):

        self.i_generation=i_generation
        self.i_iteration=1
        self.best_geo=best_geo
        self.cadsd_result=cadsd_result
        self.best_loss=best_loss
        self.mean_loss=mean_loss
        self.cache=f"generation: {self.i_generation}\n"
        self.visualize()

    def visualize(self):
        if self.disabled:
            return
        if not self.is_initialized:
            self.stdscr = curses.initscr()

        self.stdscr.erase()
        #self.stdscr.addstr(f"best loss: {best_loss:.2f}")
        #self.stdscr.addstr(f"generation: {i_generation}")
        self.stdscr.addstr(f"iteration: {self.i_iteration}\n")
        self.stdscr.addstr(self.cache)
        self.stdscr.refresh()

    def end(self):
        if self.is_initialized:
            curses.endwin()

def evolve_generations(pool, loss, mutator, n_generations=100, n_generation_size=100, n_threads=20, store_intermediates=""):

    finish_message="...finished..."

    total=n_generations*len(pool)*n_generation_size
    pbar=tqdm(total=total)

    best_loss=min([x[1] for x in pool])
    mean_loss=np.mean([x[1] for x in pool])
    best_geo=np.mean([x[1] for x in pool])

    display=EvolutionDisplay(n_generations, n_generation_size)
    display.disabled=True
    try:
        display.update_generation(1, None, None, best_loss, mean_loss)
        #pbar.set_description(f"best_loss={best_loss:.2f}, mean_loss={mean_loss:.2f}, gen={1}/{n_generations}, pool_size={len(pool)}")
        for i_generation in range(n_generations):

            processing_queue=Queue()
            result_queue=Queue()
            results=[]
            
            def process_mutator_queue():
                while True:
                    job=processing_queue.get()
                    if job == finish_message:
                        result_queue.put(finish_message)
                        break
                    job.mutate(result_queue)

            # fill processing queue
            for i_pool in range(len(pool)):
                for i_mutation in range(n_generation_size):
                    mj=MutationJob(pool[i_pool][0], mutator, loss, i_pool, i_generation, n_generations)
                    processing_queue.put(mj)
            for i in range(n_threads):
                processing_queue.put(finish_message)

            # start worker threads to process this queue and write results to result_queue
            processes=[]
            for i in range(n_threads):
                p = Process(target=process_mutator_queue, args=())
                processes.append(p)
                p.start()

            # collect results in order to update progress bar
            finished_count=0
            while finished_count<n_threads:
                result=result_queue.get()
                if result!=finish_message:
                    display.update_iteration()
                    results.append(result)
                else:
                    finished_count+=1

            # all jobs are processed. now update mutant pool

            # collect all mutants
            result_pool={}
            for i in range(len(pool)):
                result_pool[i]=[]

            for result in results:
                result_pool[result[3]].append((result[0], result[1], result[2]))
            
            # add fathers and get fitest
            for index in range(len(pool)):
                result_pool[index].append(pool[index])
                result_pool[index]=sorted(result_pool[index], key=lambda x : x[1])
                pool[index]=result_pool[index][0]

            print("-"*20)
            print(pool[0])
            print(len(pool[0]))
            print("-"*20)

            # get best mutant
            best_mutant_index=np.argmax([x[1] for x in pool])
            best_loss=pool[best_mutant_index][1]
            best_geo=pool[best_mutant_index][0].make_geo()
            best_cadsd_result=result_pool[best_mutant_index][2]
            mean_loss=np.mean([x[1] for x in pool])

            display.update_generation(i_generation, best_geo, best_cadsd_result, best_loss, mean_loss)

            # pbar.set_description(f"best_loss={best_loss:.2f}, mean_loss={mean_loss:.2f}, gen={i_generation+1}/{n_generations}, pool_size={len(pool)}")

            if store_intermediates != "":
                pickle.dump(pool, open(store_intermediates, "wb"))
    finally:
        display.end()
    return pool