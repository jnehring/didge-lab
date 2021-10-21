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
from threading import Thread, Lock

from abc import ABC, abstractmethod
import time

class Mutator(Thread):
    
    def __init__(self, father, loss, n_iterations, learning_rate=1, n_poolsize=10, decrease_lr=True, thread_num=0, reporter=None):
        Thread.__init__(self)
        self.father=father
        self.loss=loss
        self.n_iterations=n_iterations
        self.learning_rate=learning_rate
        self.n_poolsize=n_poolsize
        self.pool=[]
        self.decrease_lr=decrease_lr
        self.thread_num=thread_num
        self.reporter=reporter
        
    def run(self):
        
        total_loss=0.0

        for i_iteration in range(self.n_iterations):

            lr=self.learning_rate
            if self.decrease_lr:
                lr=lr-(i_iteration*lr/self.n_iterations)

            mutant=self.father.copy()
            mutant.mutate(lr)
            mutant_loss=self.loss.get_loss(mutant.make_geo(), thread_num=self.thread_num)
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



class PoolMutator:
    
    def __init__(self, pool, loss, n_iterations, learning_rate=1):
        self.pool=pool
        self.losses=[]
        self.n_iterations=n_iterations
        self.learning_rate=learning_rate
        self.loss=loss
        
    def mutate(self):
                
        for i_pool in range(len(self.pool)):
            father=self.pool[i_pool]
            mutator=Mutator(self.pool[i_pool], self.loss, self.n_iterations, self.learning_rate, 1)
            mutant, mutant_loss=mutator.mutate()
            self.pool[i_pool] = mutant
            self.losses.append(mutant_loss)

        # sort pool and losses

        self.pool=pool_sorted
        self.losses=losses_sorted
        
        return self.pool, self.losses

    def sort_pool(self, pool, losses):
        loss_indizes={}
        for i in range(len(losses)):
            loss_indizes[i]=losses[i]

        keys=sorted(list(loss_indizes.keys()), key=lambda x : losses[x])

        pool_sorted=[]
        losses_sorted=[]
        for key in keys:
            pool_sorted.append(pool[key])
            losses_sorted.append(losses[key])

        return pool_sorted, losses_sorted

# mutate first in an exploratory and then in a fine tuning fashion
def mutate_explore_then_finetune(loss=None, parameters=BasicShapeParameters(), n_poolsize=10, n_explore_iterations=3000, n_finetune_iterations=300, n_threads=4):
    assert(loss != None)

    # explore
    print("exploring...")
    n_explore_iterations_thread=int(n_explore_iterations/n_threads)
    reporter=Reporter(n_explore_iterations)

    mutators=[]
    start=time.time()
    for i in range(n_threads):
        mutator=Mutator(copy.deepcopy(parameters), copy.deepcopy(loss), n_explore_iterations_thread, n_poolsize=n_poolsize, decrease_lr=False, thread_num=i, reporter=reporter)
        mutators.append(mutator)
        mutators[i].start()

    for i in range(n_threads):
        mutators[i].join()

    print(f"done in {time.time()-start:.2f}s")

    

    # pool_mutator=PoolMutator(mutator.get_pool(), loss, n_finetune_iterations, 0.1)
    # pool, losses=pool_mutator.mutate()
    # return pool, losses