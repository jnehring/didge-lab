import threading
import queue
from tqdm import tqdm
import time

class ProducerThread(threading.Thread):
    def __init__(self, dataQueue, lambda_produce, args):
        threading.Thread.__init__(self)
        self.dataQueue=dataQueue
        self.lambda_produce=lambda_produce
        self.args=args
        self.finished=False

    def run(self):
        self.lambda_produce(self, self.args)

    def is_finished(self):
        return self.finished

def produce_and_iterate(lambda_produce, n_threads=4):
    threads=[]

    dataQueue=queue.Queue()
    for i in range(n_threads):
        pt=ProducerThread(dataQueue, lambda_produce, [i])
        threads.append(pt)
        pt.start()

    stop=False
    while not stop:
        d=dataQueue.get()
        yield d
        count_finished=0
        for t in threads:
            if t.is_finished():
                count_finished+=1
        if count_finished==n_threads:
            stop=True


