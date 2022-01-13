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
