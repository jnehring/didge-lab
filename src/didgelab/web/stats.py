import sys
import logging
import numpy as np
import pandas as pd
import os
import threading
import json
import copy

from didgelab.app import get_app, get_config

# service that keeps track of the losses
class EvolutionStats:

    def __init__(self):
        
        # print stats to console
        self.data = {}
        self.lock = threading.Lock()
        def log_loss(i_generation, population):
            losses = [ind.loss for ind in population[0:min(len(population), 20)]]
            new_row = {
                "generation": i_generation,
                "num_individuals_total": len(population)
            }
            for key in losses[0].keys():
                series = [x[key] for x in losses]
                new_row[key + "_min"] = np.min(series)
                new_row[key + "_avg"] = np.mean(series)
                new_row[key + "_max"] = np.max(series)

            # logging.info(new_row)
            with self.lock:
                for key, value in new_row.items():
                    if key not in self.data.keys():
                        self.data[key] = []
                    self.data[key].append(value)
            
        get_app().subscribe("generation_ended", log_loss)

        # write checkpoint on write_results event
        def store_checkpoint(checkpoint_folder):
            df = pd.DataFrame(self.data)
            f = os.path.join(checkpoint_folder, "stats.csv")
            df.to_csv(f, index=False)

        get_app().subscribe("write_results", store_checkpoint)

        get_app().register_service(self)

    def get_latest_logs(self):
        data = self.get_data()
        latest_logs = {key: values[-1] for key, values in data.items()}
        return latest_logs
    
    def get_data(self):
        with self.lock:
            return copy.deepcopy(self.data)
