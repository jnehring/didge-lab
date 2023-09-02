from didgelab.app import App
from didgelab.evo.shapes import Shape

import pickle
import os
import logging
import json

class CheckPointWriter:
    
    def __init__(self, interval=100):

        self.interval = interval

        def write_checkpoint(i_generation, population):
            if self.interval>0 and i_generation>0 and i_generation % self.interval == 0:
                self.write_checkpoint(i_generation, population)

        App.subscribe("generation_ended", write_checkpoint)

        def evolution_ended(population):
            self.write_checkpoint("final", population)

        App.subscribe("evolution_ended", evolution_ended)
        App.register_service(self)

    def write_checkpoint(self, name, population : list[Shape]):
        logging.info("write checkpoint_" + str(name))
        checkpoint_folder = os.path.join(App.get_output_folder(), "checkpoint_" + str(name))
        os.mkdir(checkpoint_folder)
        App.publish("write_results", checkpoint_folder)

        geos = []
        parameters = []
        losses = []
        for to_write in population[0:min(len(population), 50)]:
            geos.append(to_write.make_geo().geo)
            parameters.append(parameters)
            losses.append(to_write.loss)

        f = os.path.join(checkpoint_folder, "parameters.bin")
        pickle.dump(parameters, open(f, "wb"))
        logging.info("wrote " + f)

        f = os.path.join(checkpoint_folder, "geos.json")
        json.dump(geos, open(f, "w"))
        logging.info("wrote " + f)

        f = os.path.join(checkpoint_folder, "losses.json")
        json.dump(losses, open(f, "w"))
        logging.info("wrote " + f)


