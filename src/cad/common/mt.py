# multithreading helper class

import threading
from tqdm import tqdm
import time
from abc import ABC, abstractmethod
from multiprocessing import Process, Queue

class Producer(ABC):

    @abstractmethod
    def run(self, producer_thread):
        pass

class WorkerProcess:
    def __init__(self, dataQueue, producer):
        self.dataQueue=dataQueue
        self.producer=producer
        self.finished=False

    def run(self):
        self.producer.run(self.dataQueue)
        self.dataQueue.put("...finished...")
        self.finished=True

    def is_finished(self):
        return self.finished

def produce_and_iterate(producers, n_total=None, pbar=-1):
    processes=[]
    dataQueue=Queue()
    for producer in producers:
        pt=WorkerProcess(dataQueue, producer)
        processes.append(pt)
        p=Process(target=pt.run, args=())
        p.start()

    has_progressbar=False
    if pbar != -1:
        has_progressbar=True
    elif n_total != None:
        pbar=tqdm(total=n_total)
        has_progressbar=True

    finished_processes=0
    while finished_processes != len(processes):
        d=dataQueue.get()

        if d == "...finished...":
            finished_processes+=1
        else:
            yield d

            if has_progressbar:
                pbar.update(1)
