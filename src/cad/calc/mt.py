# multithreading helper class

import threading
import queue
from tqdm import tqdm
import time
from abc import ABC, abstractmethod

class Producer(ABC):

    @abstractmethod
    def run(self, producer_thread):
        pass

class WorkerThread(threading.Thread):
    def __init__(self, dataQueue, producer):
        threading.Thread.__init__(self)
        self.dataQueue=dataQueue
        self.producer=producer
        self.finished=False

    def run(self):
        self.producer.run(self.dataQueue)
        self.finished=True

    def is_finished(self):
        return self.finished

def produce_and_iterate(producers, n_total=None):
    threads=[]
    dataQueue=queue.Queue()
    for producer in producers:
        pt=WorkerThread(dataQueue, producer)
        threads.append(pt)
        pt.start()

    stop=False

    has_progressbar=False
    if n_total != None:
        pbar=tqdm(total=n_total)
        has_progressbar=True
    while not stop:
        d=dataQueue.get()
        yield d

        if has_progressbar:
            pbar.update(1)
        count_finished=0
        for t in threads:
            if t.is_finished():
                count_finished+=1
        if count_finished==len(producers):
            stop=True

