import json
from cad.common.app import App
import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import logging

class CADLogger:

    logger=None

    def __init__(self, logfile):

        self.logfile=logfile
        self.f=None

        def pipeline_finished():
            if self.f is not None:
                self.f.close()

        def generation_started(x,y):
            if self.f is not None:
                self.f.flush()

        App.subscribe("pipeline_finished", pipeline_finished)
        App.subscribe("generation_started", generation_started)

    def log(self, entry):

        if self.f is None:
            self.f=open(self.logfile, "w")

        entry["iteration"]=App.get_context("i_iteration")
        entry["generation"]=App.get_context("i_generation")

        self.f.write(json.dumps(entry) + "\n")

    def close(self):
        if self.f is not None:
            self.f.close()

    @classmethod
    def get_logger(cls):
        if CADLogger.logger is None:
            log_dir=App.get_output_folder()
            filename=os.path.join(log_dir, "cadlogger.log")
            CADLogger.logger=CADLogger(filename)
        return CADLogger.logger

class CADLogReader:

    def __init__(self, logfile):
        self.logfile=logfile

    def to_dataframe(self):
        data=None
        for line in open(self.logfile, "r").readlines():
            j=json.loads(line)
            if data is None:
                data={}
                for key in j.keys():
                    data[key]=[]
            for key, value in j.items():
                data[key].append(value)

        #print(data["name"][0:5])
        df=pd.DataFrame(data)
        return df

if __name__ == "__main__":

    infile="output/2022-02-12T17-55-36_default/cadlogger.log"
    df=CADLogReader(infile).to_dataframe()
    sns.lineplot(data=df)
    print(df)
    