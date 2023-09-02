import os
import csv

from didgelab.app import App
from didgelab.evo.shapes import Shape

class LossWriter:
    
    def __init__(self, interval=100):

        self.interval = interval

        def write_loss(i_generation, population):
            self.write_loss(i_generation, population)

        App.subscribe("generation_ended", write_loss)

        def close():
            self.writer.close()

        App.subscribe("evolution_ended", close)
        
        App.register_service(self)
        
        outfile = os.path.join(App.get_output_folder(), "losses.csv")

        csvfile = open(outfile, "w")
        self.writer = csv.writer(csvfile)
        self.format = None

    def write_loss(self, i_generation, population : list[Shape]):
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
