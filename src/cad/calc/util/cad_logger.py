import json
from cad.common.app import App
import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import logging

class CADLogger:

    logger=None
    filename="cadlogger.log"

    def __init__(self, logfile):

        self.logfile=logfile
        self.f=None
        self.started=False

        def pipeline_finished():
            if self.f is not None:
                self.f.close()

        def generation_started(x,y):
            self.started=True
            if self.f is not None:
                self.f.flush()

        App.subscribe("pipeline_finished", pipeline_finished)
        App.subscribe("generation_started", generation_started)

    def log(self, entry):

        if not self.started:
            return
    
        if self.f is None:
            self.f=open(self.logfile, "w")

        entry["iteration"]=App.context["i_iteration"]
        entry["generation"]=App.context["i_generation"]

        self.f.write(json.dumps(entry) + "\n")

    def close(self):
        if self.f is not None:
            self.f.close()

    @classmethod
    def get_logger(cls):
        if CADLogger.logger is None:
            log_dir=App.get_output_folder()
            filename=os.path.join(log_dir, CADLogger.filename)
            CADLogger.logger=CADLogger(filename)
        return CADLogger.logger

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

    df=CADLogReader(latest=True).to_dataframe()
    sns.lineplot(data=df)
    plt.show()
    