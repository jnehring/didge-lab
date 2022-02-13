from cad.calc.didgmo import PeakFile, didgmo_high_res, cleanup
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
import pandas as pd
import shutil
from cad.common.app import App
import json

class Mutator(ABC):

    def mutate(self, parameter):
        self._mutate(parameter)
        parameter.after_mutate()

    @abstractmethod
    def _mutate():
        pass

class ExploringMutator(Mutator):

    def _mutate(self, parameters):
        for i in range(len(parameters.mutable_parameters)):
            p=parameters.mutable_parameters[i]
            if p.immutable:
                continue
            r=random.random()
            p.value = p.minimum + r*(p.maximum-p.minimum)

class FinetuningMutator(Mutator):

    def __init__(self, learning_rate=1):
        self.learning_rate=learning_rate

    def _mutate(self, parameters):
        p=None
        while p == None:
            index=random.randrange(0, len(parameters.mutable_parameters))
            p=parameters.mutable_parameters[index]
            if p.immutable:
                p=None
        
        i_iteration=App.get_context("i_iteration", default=1)
        n_total_iterations=App.get_context("n_total_iterations", default=1)

        if random.random()>0.5:
            p.value += (p.maximum-p.value)*self.learning_rate*random.random()*i_iteration/n_total_iterations
        else:
            p.value -= (p.value-p.minimum)*self.learning_rate*random.random()*i_iteration/n_total_iterations
        
        if p.value>p.maximum:
            p.value=p.maximum
        elif p.value<p.minimum:
            p.value=p.minimum

# this is the multithreaded job that executes one single mutation
class MutationJob:

    def __init__(self, father, mutator, loss, pool_index, i_generation, n_generations):
        self.father=father
        self.pool_index=pool_index
        self.mutator=mutator
        self.loss=loss
        self.i_generation=i_generation
        self.n_generations=n_generations
    
    def mutate(self, result_queue):
        try:
            mutant=self.father.copy()
            self.mutator.mutate(mutant)
            geo=mutant.make_geo()
            mutant_loss=self.loss.get_loss(geo)
            me=MutantPoolEntry(mutant, geo, mutant_loss)
            result_queue.put((me, self.pool_index))
        except Exception as e:
            msg="error in cadsd while processing geo "
            if geo is not None:
                msg += json.dumps(geo.geo)
            App.log_exception(e)
            logging.error(msg)

class MutantPoolEntry:

    def __init__(self, parameterset, geo, loss):
        self.parameterset=parameterset
        self.loss=loss
        self.geo=geo

class MutantPool:

    def __init__(self):
        self.pool=[]

    def iterate(self):
        for m in self.pool:
            yield m

    def add_entry(self, entry):
        self.pool.append(entry)

    def add(self, parameterset, geo, loss):
        e=MutantPoolEntry(parameterset, geo,loss )
        self.add_entry(e)

    @classmethod
    def create_from_father(cls, father : MutationParameterSet, n_poolsize : int, loss, do_cadsd=False):
        pool=MutantPool()
        for x in range(n_poolsize):
            p=father.copy()
            geo=p.make_geo()
            pool.add(p, geo, loss(geo))
        return pool

    def sort(self):
        self.pool = sorted(self.pool, key=lambda x : x.loss["loss"])

    def get_best_loss(self):
        self.sort()
        return self.pool[0].loss["loss"]

    def get_mean_loss(self):
        return np.mean([x.loss["loss"] for x in self.pool])

    def get_best_entry(self):
        self.sort()
        return self.pool[0]

    def len(self):
        return len(self.pool)

    def get(self, i):
        return self.pool[i]

    def remove(self, i):
        del self.pool[i]

# evolve for exploration
def evolve_explore(pool, loss, mutator, store_intermediates=""):

    n_generations=App.get_context("n_generations")
    n_generation_size=App.get_context("n_generation_size")
    n_threads=App.get_config()["n_threads"]

    finish_message="...finished..."

    total=n_generations*pool.len()*n_generation_size

    App.set_context("i_generation", 0)
    App.set_context("i_iteration", 0)
    App.publish("generation_started", (0, pool))

    processing_queue=Queue()
    result_queue=Queue()
    results=MutantPool()
    
    def process_mutator_queue():
        try:
            while True:
                job=processing_queue.get()
                if job == finish_message:
                    result_queue.put(finish_message)
                    break
                job.mutate(result_queue)
        except Exception as e:
            App.log_exception(e)

    # fill processing queue
    for i_generation in range(n_generations):
        for i_pool in range(pool.len()):
            for i_mutation in range(n_generation_size):
                mj=MutationJob(pool.get(i_pool).parameterset, mutator, loss, i_pool, i_generation, n_generations)
                processing_queue.put(mj)
    for i in range(n_threads):
        processing_queue.put(finish_message)

    # start worker threads to process this queue and write results to result_queue
    processes=[]
    for i in range(n_threads):
        p = Process(target=process_mutator_queue, args=())
        processes.append(p)
        p.start()

    i_iteration=0
    i_generation=0

    # collect results to update progress bar
    finished_count=0
    while finished_count<n_threads:
        result=result_queue.get()
        if result!=finish_message:
            App.publish("iteration_finished", (i_iteration,))
            App.set_context("i_iteration", i_iteration)
            
            results.add_entry(result[0])
            results.sort()
            while results.len()>pool.len():
                results.remove(results.len()-1)

            if i_iteration == n_generation_size*pool.len():
                i_iteration=0
                App.publish("generation_ended", (i_generation, results))
                i_generation+=1
                App.publish("generation_started", (i_generation, results))
                App.set_context("i_generation", i_generation)
                App.set_context("i_iteration", 0)

            i_iteration+=1
            App.set_context("i_iteration", i_iteration)
        else:
            finished_count+=1

    return results

# run multithreaded evolution for fine tunning
def evolve_generations(pool, loss, mutator, store_intermediates=""):

    n_generations=App.context["n_generations"]
    n_generation_size=App.context["n_generation_size"]
    n_threads=App.get_config()["n_threads"]

    finish_message="...finished..."

    total=n_generations*pool.len()*n_generation_size

    for i_generation in range(n_generations):

        App.set_context("i_generation", i_generation)
        App.set_context("i_iteration", 0)
        App.publish("generation_started", (i_generation, pool))

        processing_queue=Queue()
        result_queue=Queue()
        results=[]
        def process_mutator_queue():
            try:
                while True:
                    job=processing_queue.get()
                    if job == finish_message:
                        result_queue.put(finish_message)
                        break
                    job.mutate(result_queue)
            except Exception as e:
                App.log_exception(e)

        # fill processing queue
        for i_pool in range(pool.len()):
            for i_mutation in range(n_generation_size):
                mj=MutationJob(pool.get(i_pool).parameterset, mutator, loss, i_pool, i_generation, n_generations)
                processing_queue.put(mj)
        for i in range(n_threads):
            processing_queue.put(finish_message)

        # start worker threads to process this queue and write results to result_queue
        processes=[]
        for i in range(n_threads):
            p = Process(target=process_mutator_queue, args=())
            processes.append(p)
            p.start()

        i_iteration=0

        # collect results in order to update progress bar
        finished_count=0
        while finished_count<n_threads:
            result=result_queue.get()
            if result!=finish_message:
                i_iteration+=1
                App.set_context("i_iteration", i_iteration)
                App.publish("iteration_finished", (i_iteration,))
                results.append(result)
            else:
                finished_count+=1

        # all jobs are processed. now update mutant pool

        # collect all mutants
        result_pool={}
        for i in range(pool.len()):
            result_pool[i]=[]

        for result in results:
            result_pool[result[1]].append(result[0])
        
        # add fathers and create new mutant pool
        pool_size=pool.len()
        new_pool=MutantPool()
        for index in range(pool_size):
            result_pool[index].append(pool.get(index))
            result_pool[index]=sorted(result_pool[index], key=lambda x : x.loss["loss"])
            new_pool.add_entry(result_pool[index][0])

        pool=new_pool
        
        if store_intermediates != "":
            pickle.dump(pool, open(store_intermediates, "wb"))

        App.publish("generation_ended", (i_generation, pool))

    return pool