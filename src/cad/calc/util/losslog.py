from cad.common.app import App
import os
import csv

# log loss after each generation to loss_log.txt
class LossLog:

    def __init__(self):

        logdir=os.path.join(App.get_config()["pipelines_dir"], App.get_config()["pipeline_name"])
        if not os.path.exists(logdir):
            os.mkdir(logdir)
        self.logfile=os.path.join(logdir, "loss_log.txt")
        self.f=open(self.logfile, "w")
        self.writer=csv.writer(self.f)

        def generation_started(i_generation, mutant_pool):
            log=[i_generation]
            [log.append(x.loss) for x in mutant_pool.pool]
            self.writer.writerow(log)
        App.subscribe("generation_started", generation_started)

        def pipeline_finished():
            self.f.close()
        App.subscribe("pipeline_finished", pipeline_finished)

if __name__ == "__main__":

    # make a chart of number of improvements per 100 generations
    # call: 
    # python -m cad.calc.util.losslog

    import pandas as pd
    import seaborn as sns
    import matplotlib.pyplot as plt
    import numpy as np

    infile="projects/finished_evolutions/penta_didge/loss_log.txt"
    df=pd.read_csv(infile)
    n_poolsize=len(df.columns)-1
    df=np.array(df)
    
    n_batchsize=100
    i_iteration=0
    losses=[100000]*n_poolsize
    df_improvements=[]
    while i_iteration < len(df):

        i_iteration+=n_batchsize
        batch=df[i_iteration:i_iteration+n_batchsize]

        improvements=[0]*n_poolsize
        for i_batch in range(0, n_batchsize):

            if i_batch>=len(batch):
                break

            for i_series in range(n_poolsize):

                series_loss=batch[i_batch][i_series]
                if series_loss<losses[i_series]:
                    losses[i_series]=series_loss
                    improvements[i_series]+=1

        for i in range(len(improvements)):
            df_improvements.append([i_iteration, improvements[i], i])

    df_improvements=pd.DataFrame(df_improvements, columns=["iteration", "n_improvements", "series"])
    #print(df_improvements)
    sns.barplot(data=df_improvements, x="iteration", y="n_improvements", hue="series")
    plt.show()


    # columns=["iteration"]

    # n_poolsize=len(df.columns)-1
    # [columns.append(str(i)) for i in range(n_poolsize)]

    # df.columns=columns

    # # improvements per 100 generations
    # improvements=[]
    # for iteration in df.iteration:
    # print(df)


    # df_new=[]
    # for i in range(n_poolsize):
    #     series=df[str(i)]
    #     df_series={
    #         "iteration": df.iteration,
    #         "loss": df[str(i)],
    #         "series": i
    #     }
    #     df_new.append(pd.DataFrame(df_series))

    # df_new=pd.concat(df_new)

    #df_new=df_new[df_new.series==0]
    # sns.lineplot(data=df_new, x="iteration", y="loss")
    # plt.show()