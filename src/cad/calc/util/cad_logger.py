import json
from cad.common.app import App
import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import logging
from multiprocessing import Manager, Lock
import argparse

class CADLogger:

    logger=None
    filename="cadlogger.log"
    manager=None
    lock=Lock()

    def __init__(self, logfile):

        self.logfile=logfile
        self.started=False

    def log(self, entry):

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

class LossCADLogger():

    def __init__(self):

        def generation_ended(i_generation, mutant_pool):

            entry={
                "generation": i_generation,
                "pipeline_step": App.context["current_pipeline_step"],
                "pipeline_step_name": App.context["pipeline_step_name"]
            }
            for i in range(mutant_pool.len()):
                mpe=mutant_pool.get(i)
                for key, value in mpe.loss.items():
                    entry[key]=value
                entry["pool_index"]=i

                CADLogger.get_logger().log(entry)
            

        App.subscribe("generation_ended", generation_ended)

def logfile_to_dataframe(infile):
    data=None
    f=open(infile, "r")
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
    #df=df.dropna(subset=["iteration"])
    return df

def loss_report(infile, outfile=None):
    df=logfile_to_dataframe(infile)

    offset=-1
    accumulated_step=[]

    for pi in df.pool_index:
        if pi==0:
            offset+=1
        accumulated_step.append(offset)
    df["accumulated_step"]=accumulated_step

    # steps=df.pipeline_step.unique()

    # for step in steps:
    #     num_steps=df[df.pipeline_step==step].generation.max()+1
    #     generations_per_step[step]=offset
    #     offset += num_steps
    # df["accumulated_step"]=df.pipeline_step.apply(lambda x : generations_per_step[x])
    
    loss_columns=[]
    for c in df.columns:
        if c.find("loss")>=0:
            loss_columns.append(c)

    pool_size=len(df[0:100]["pool_index"].unique())

    losses={}
    for c in loss_columns:
        losses[c]={
            "y_top": [],
            "y_low": [],
            "y_medium": []
        }

    x=[]
    i=0
    offset=0
    while offset<len(df):

        for c in loss_columns:

            l=df[i:i+pool_size][c]
            losses[c]["y_medium"].append(l.mean())

        x.append(i)
        i+=1
        offset=i*pool_size

    charts=[x["y_medium"] for x in losses.values()]
    plt.clf()

    for chart in charts:
        plt.plot(x, chart)

    # add vertical lines
    for step in df.pipeline_step.unique():
        maxx=df[df.pipeline_step==step].accumulated_step.max()

        if maxx < df.accumulated_step.max():
            plt.axvline(x=maxx)

    plt.legend(loss_columns)

    if outfile is not None:
        plt.savefig(outfile)

def loss_report_old(infile, outfile=None):
    df=logfile_to_dataframe(infile)

    # averages loss over all iterations
    df["id"]=df.pipeline_step.astype(str) + "_" + df.generation.astype(str)

    loss_columns=[]
    for c in df.columns:
        if c.find("loss")>=0:
            loss_columns.append(c)

    new_df=[]
    generation_counter=0
    for id in df.id.unique():
        subdf=df[df.id==id] 

        first_row=subdf.iloc[0]

        row=[first_row["generation"],
            generation_counter,
            first_row["pipeline_step"],
            first_row["pipeline_step_name"]]
        for c in loss_columns:
            row.append(subdf[c].mean())
        new_df.append(row)
        generation_counter+=1

    new_columns=["generation", "accumulative_generation", "pipeline_step", "pipeline_step_name"]
    new_columns.extend(loss_columns)
    new_df=pd.DataFrame(new_df, columns=new_columns)
    
    plt.clf()
    plt.plot(new_df.accumulative_generation, new_df[loss_columns])
    plt.legend(loss_columns)
    plt.xlabel("accumulated generation")
    plt.ylabel("loss")

    # add vertical lines
    for step in new_df.pipeline_step.unique():
        maxx=new_df[new_df.pipeline_step==step].accumulative_generation.max()

        if maxx < new_df.accumulative_generation.max():
            plt.axvline(x=maxx)

    if outfile is not None:
        plt.savefig(outfile)
    #plt.show()


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Inspect CAD Logger')
    parser.add_argument('-infile', type=str, required=True, help='input file')
    args = parser.parse_args()

    loss_report(args.infile)
    plt.show()
    #.to_dataframe()
    #sns.lineplot(data=df)
    #plt.show()
    