import json
from cad.common.app import App
import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import logging
from multiprocessing import Manager, Lock

class CADLogger:

    logger=None
    filename="cadlogger.log"
    manager=None
    lock=Lock()

    def __init__(self, logfile):

        self.logfile=logfile
        self.started=False

    def log(self, entry):

        if App.get_context("state") == "initializing":
            return

        entry["iteration"]=i_iterations=App.get_context("i_iteration")
        entry["generation"]=App.context["i_generation"]
        entry["pipeline_step"]=App.context["current_pipeline_step"]
        entry["pipeline_step_name"]=App.context["pipeline_step_name"]

        CADLogger.lock.acquire()
        try:
            f=open(self.logfile, "a")
            f.write(json.dumps(entry) + "\n")
        finally:
            f.close()
            CADLogger.lock.release()

    @classmethod
    def get_logger(cls):
        if CADLogger.logger is None:
            log_dir=App.get_output_folder()
            filename=os.path.join(log_dir, CADLogger.filename)
            CADLogger.manager=Manager()
            CADLogger.logger=CADLogger.manager.dict()
            CADLogger.logger["value"]=CADLogger(filename)
        return CADLogger.logger["value"]

class CADLogReader:

    def __init__(self, logfile=None, latest=False):

        if latest==True:
            fs=os.listdir(App.get_config()["output_folder"])
            sorted(fs)
            self.logfile=os.path.join(App.get_config()["output_folder"], fs[-1], CADLogger.filename)
        else:
            self.logfile=logfile

    def to_dataframe(self):
        data=None
        f=open(self.logfile, "r")
        for line in f.readlines():
            j=json.loads(line)
            if data is None:
                data={}
                for key in j.keys():
                    data[key]=[]
            for key, value in j.items():
                data[key].append(value)
        f.close()

        df=pd.DataFrame(data)
        df=df.dropna(subset=["iteration"])
        return df

if __name__ == "__main__":

    infile="finished_evolutions/mbeya_0/cadlogger.log"
    df=CADLogReader(logfile=infile).to_dataframe()
    sns.lineplot(data=df)
    plt.show()
    