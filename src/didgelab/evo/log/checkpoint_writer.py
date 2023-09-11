from didgelab.app import get_app, get_config
from didgelab.evo.shapes import Shape
from didgelab.evo.evolution import MultiEvolution

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

        get_app().subscribe("generation_ended", write_checkpoint)

        def evolution_ended(population):
            suffix = ""
            if "is_multi_evolution" in get_config() and get_config()["is_multi_evolution"] is True:
                suffix = get_app().get_service(MultiEvolution).evolution_nr
                suffix = "_" + str(suffix)
            self.write_checkpoint("final" + suffix, population)

        get_app().subscribe("evolution_ended", evolution_ended)
        get_app().register_service(self)

    def write_checkpoint(self, name, population : list[Shape]):
        logging.info("write checkpoint_" + str(name))
        checkpoint_folder = os.path.join(get_app().get_output_folder(), "checkpoint_" + str(name))
        os.mkdir(checkpoint_folder)
        get_app().publish("write_results", checkpoint_folder)

        geos = []
        shapes = []
        losses = []
        for to_write in population[0:min(len(population), 50)]:
            geos.append(to_write.make_geo().geo)
            shapes.append(to_write)
            losses.append(to_write.loss)

        f = os.path.join(checkpoint_folder, "shapes.bin")
        pickle.dump(shapes, open(f, "wb"))
        logging.info("wrote " + f)

        f = os.path.join(checkpoint_folder, "geos.json")
        json.dump(geos, open(f, "w"))
        logging.info("wrote " + f)

        f = os.path.join(checkpoint_folder, "losses.json")
        json.dump(losses, open(f, "w"))
        logging.info("wrote " + f)


