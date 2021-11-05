from cad.calc.loss import ScaleLoss, AmpLoss, CombinedLoss, TargetNoteLoss
from cad.calc.parameters import BasicShapeParameters
from cad.calc.mutation import mutate_explore_then_finetune
from cad.calc.visualization import visualize_scales_multiple_shapes
from cad.calc.didgmo import didgmo_bridge
import pickle

pickle_file="projects/temp/mutants.pickle"

def evolve():
    loss=CombinedLoss(
        [ScaleLoss(scale=[0,3], fundamental=-31, n_peaks=2), AmpLoss(n_peaks=2)],
        [3.0, 0.1]
    )
    loss=TargetNoteLoss([-31])
    father=BasicShapeParameters()

    n_explore_iterations=1000
    n_finetune_iterations=200
    n_poolsize=5

    total=n_explore_iterations+n_poolsize*n_finetune_iterations
    #total=n_poolsize*n_finetune_iterations


    mutation_parameters={
        "loss": loss,
        "parameters": BasicShapeParameters(),
        "n_poolsize": n_poolsize,
        "n_explore_iterations": n_explore_iterations,
        "n_finetune_iterations": n_finetune_iterations
    }

    mutants=mutate_explore_then_finetune(**mutation_parameters)
    mutants=[m["mutant"].make_geo() for m in mutants]
    visualize_scales_multiple_shapes(mutants, loss, no_grafic=True)

    pickle.dump(mutants[0], open(pickle_file, "wb"))

def analyze():
    mutant=pickle.load(open(pickle_file, "rb"))
    loss=TargetNoteLoss([-31])
    print(loss.target_freqs)
    
    peak, fft=didgmo_bridge(mutant)
    print(peak.get_impedance_table())

evolve()
analyze()