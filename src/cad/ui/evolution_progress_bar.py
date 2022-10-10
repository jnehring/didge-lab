from cad.common.app import App
from tqdm import tqdm

class EvolutionProgressBar:

    def __init__(self, num_generations):
        self.num_generations = num_generations

        def pipeline_started():
            self.pbar = tqdm(total=num_generations)

        def generation_started(i_generation, mutant_pool):
            self.pbar.update(1)

        def pipeline_finished():
            self.pbar.close()

        App.subscribe("pipeline_started", pipeline_started)
        App.subscribe("generation_started", generation_started)
        App.subscribe("pipeline_finished", pipeline_finished)
