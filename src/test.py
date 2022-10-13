from cad.calc.geo import Geo
from cad.cadsd.cadsd import CADSD

# first we define the open didgeridoo geometry
geo = [[0, 32], [800, 32], [900, 38], [970, 42], [1050, 40], [1180, 48], [1350, 60], [1390, 68], [1500, 72]]
geo = Geo(geo)

# then we compute the resonant peaks
cadsd = CADSD(geo)
cadsd.get_notes()

from cad.calc.loss import LossFunction, TootTuningHelper, diameter_loss, single_note_loss
from cad.calc.conv import note_to_freq
import tqdm as tqdm
from cad.calc.parameters import FinetuningParameters


# first we define the loss function
class OptimizeOpenDidgeridooLoss(LossFunction):

    def __init__(self):

        self.target_notes = [-31, -15, -7]
        self.target_freqs = [note_to_freq(note) for note in self.target_notes]
        self.min_impedance = 4e+6

    # Every loss function implements the get_loss method that computes the loss
    # for a geometry. Do not mind the context here, we do not need it.
    def get_loss(self, geo, context=None):

        # we do compute the cadsd directly, but we get it from the geometry.
        # in case we need it again, we do not need to compute it a 2nd time
        # but can use it from the cache in the geo object
        cadsd = geo.get_cadsd()
        notes = cadsd.get_notes()

        # if we have less than 3 resonant peaks then return a super high loss
        if len(notes) < 3:
            return 1000

        tuning_loss = 0
        for i in range(3):
            # we compute the squared error for deviations from the target frequency
            diff = notes.freq.iloc[i] - self.target_freqs[i]
            tuning_loss += diff * diff

        volume_loss = 0
        for i in range(3):
            imp = notes.impedance.iloc[i]
            if imp < self.min_impedance:
                diff = 1 + (
                            self.min_impedance - imp) / self.min_impedance  # this is a number between 1 and 2, with 1 meaning no deviation and 2 meaning super high deviation from our goal
                diff *= 20  # we want to put a high penalty to this
                volume_loss += diff

        # we return multiple loss values as a dictionary. the evolution considers only the "loss" key. the other keys can
        # give an insight in how the different parts of the loss influence the evolution.
        loss = {
            "loss": tuning_loss + volume_loss,
            "tuning_loss": tuning_loss,
            "volume_loss": volume_loss,
        }
        return loss


loss = OptimizeOpenDidgeridooLoss()

# evolution does not improve geometries, but it improves parameter sets. the FinetuningParameters define one parameter for each part
# of a geometry.
parameters = FinetuningParameters(geo)
parameters

from cad.calc.pipeline import Pipeline, FinetuningPipelineStep
from cad.calc.mutation import MutantPool, FinetuningMutator
from cad.ui.evolution_ui import EvolutionUI

# our mutant pool contains only a single mutant. we do not want to mutate several mutants
mutant_pool=MutantPool.create_from_father(parameters, 1, loss)

# here we define a processing pipeline that consists of fine tuning only
pipeline=Pipeline()
pipeline.add_step(FinetuningPipelineStep(FinetuningMutator(), loss, n_generations=20, generation_size=30, initial_pool=mutant_pool))

ui=EvolutionUI()
pipeline.run()
