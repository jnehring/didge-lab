import os
import csv

from didgelab.app import App
from didgelab.evo.shapes import Shape

class LossWriter:
    
    def __init__(self, interval=100):

        self.interval = interval
        self.writer = None

        def write_loss(i_generation, population):
            self.write_loss(i_generation, population)

        App.subscribe("generation_ended", write_loss)

        def close(population):
            self.csvfile.close()
            self.writer = None

        App.subscribe("evolution_ended", close)

        App.register_service(self)
        
    def write_loss(self, i_generation, population : list[Shape]):

        if self.writer is None:
            outfile = os.path.join(App.get_output_folder(), "losses.csv")
            self.csvfile = open(outfile, "w")
            self.writer = csv.writer(self.csvfile)
            self.format = None

        if self.format is None:
            self.format = ["i_generation", "i_mutant"]
            for key in population[0].loss.keys():
                self.format.append(key)
            self.writer.writerow(self.format)

        for i in range(len(population)):
            individual = population[i]
            row = [i_generation, i]
            for key in self.format[2:]:
                row.append(individual.loss[key])
            self.writer.writerow(row)
