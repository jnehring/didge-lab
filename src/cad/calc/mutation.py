from cad.calc.didgmo import PeakFile, didgmo_bridge
from cad.calc.visualization import DidgeVisualizer, FFTVisualiser
import matplotlib.pyplot as plt
from cad.calc.conv import note_to_freq, note_name, freq_to_note
from cad.calc.geo import Geo
from cad.calc.parameters import BasicShapeParameters
from IPython.display import clear_output
import math
import random
import copy
from tqdm import tqdm
from threading import Lock, Thread
from multiprocessing import Pool
import concurrent.futures

from abc import ABC, abstractmethod
import time

class Mutator:

    def __init__(self, father, loss, n_iterations, learning_rate=1, n_poolsize=10, decrease_lr=True, reporter=None):
        self.father=father
        self.loss=loss
        self.n_iterations=n_iterations
        self.learning_rate=learning_rate
        self.n_poolsize=n_poolsize
        self.pool=[]
        self.decrease_lr=decrease_lr
        self.reporter=reporter
        
    def run(self):
        
        total_loss=0.0

        for i_iteration in range(self.n_iterations):

            lr=self.learning_rate
            if self.decrease_lr:
                lr=lr-(i_iteration*lr/self.n_iterations)

            mutant=self.father.copy()
            mutant.mutate(lr)
            mutant_loss=self.loss.get_loss(mutant.make_geo())
            total_loss += mutant_loss

            if len(self.pool)<self.n_poolsize or mutant_loss < self.pool[-1]["loss"]:
                self.pool.append({
                    "loss": mutant_loss,
                    "mutant": mutant 
                })
                self.pool.sort(key=lambda x : x["loss"])
                if len(self.pool) > self.n_poolsize:
                    self.pool=self.pool[0:self.n_poolsize]

            if self.reporter != None:
                self.reporter.update()

            average_loss=total_loss / (1+i_iteration)
            best_loss=self.pool[0]["loss"]
                    
        return self.pool[0]["mutant"], self.pool[0]["loss"]

    def x(self):
        return 3
    
    def get_pool(self):
        return [x["mutant"] for x in self.pool]

class Reporter(Thread):

    def __init__(self, total, description=None):
        self.lock = Lock()
        self.pbar=tqdm(total=total)

    def set_description(self, description):
        self.pbar.set_description(description)

    def update(self, n=1):
        self.lock.acquire()
        self.pbar.update(n)
        self.lock.release()


def get_n_best_results(pool, n):
    pool.sort(key=lambda x : x["loss"])
    return pool[0:n]

def run_mutator(mutator):
    mutator.run()

# mutate first in an exploratory and then in a fine tuning fashion
def mutate_explore_then_finetune(loss=None, parameters=BasicShapeParameters(), n_poolsize=10, n_explore_iterations=3000, n_finetune_iterations=300, n_threads=4):
    assert(loss != None)

    start=time.time()
    # explore
    n_explore_iterations_thread=int(n_explore_iterations/n_threads)
    reporter=Reporter(n_explore_iterations + n_poolsize*n_finetune_iterations)
    reporter.set_description("exploring")

    mutators=[]
    for i in range(n_threads):
        mutator=Mutator(copy.deepcopy(parameters), copy.deepcopy(loss), n_explore_iterations_thread, n_poolsize=n_poolsize, decrease_lr=False, reporter=reporter)
        mutators.append(mutator)

    with concurrent.futures.ThreadPoolExecutor(max_workers=n_threads) as executor:
        executor.map(run_mutator, mutators)

    mutant_pool=[]
    [mutant_pool.extend(m.pool) for m in mutators]
    mutant_pool=get_n_best_results(mutant_pool, n_poolsize)

    # finetune
    reporter.set_description("finetuning")
    mutators=[]
    for mutant in mutant_pool:
        mutator=Mutator(copy.deepcopy(mutant["mutant"]), copy.deepcopy(loss), n_finetune_iterations, n_poolsize=1, decrease_lr=True, reporter=reporter)
        mutators.append(mutator)

    with concurrent.futures.ThreadPoolExecutor(max_workers=n_threads) as executor:
        executor.map(run_mutator, mutators)
    mutant_pool=[]
    [mutant_pool.extend(m.pool) for m in mutators]
    mutant_pool=get_n_best_results(mutant_pool, n_poolsize)


    print(f"done in {time.time()-start:.2f}s")

    return mutant_pool

