# multithreading helper class

import threading
import queue
from tqdm import tqdm
import time
from abc import ABC, abstractmethod
from multiprocessing import Process

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
        self.finished=True

    def is_finished(self):
        return self.finished

def produce_and_iterate(producers, n_total=None, pbar=-1):
    processes=[]
    dataQueue=queue.Queue()
    for producer in producers:
        pt=WorkerProcess(dataQueue, producer)
        processes.append(pt)
        p=Process(target=pt.run, args=())
        p.start()
    stop=False

    has_progressbar=False
    if pbar != -1:
        has_progressbar=True
    elif n_total != None:
        pbar=tqdm(total=n_total)
        has_progressbar=True
    while not stop:
        d=dataQueue.get()
        print(d)
        yield d

        if has_progressbar:
            pbar.update(1)
        count_finished=0
        for t in threads:
            if t.is_finished():
                count_finished+=1
        if count_finished==len(producers):
            stop=True

