from cad.calc.parameters import MbeyaShape
from cad.calc.mutation import ExploringMutator
from tqdm import tqdm
from cad.cadsd.cadsd import CADSD
import pickle

dbfile = "experiments/db/db.pkl"

if __name__=="__main__":

    parent = MbeyaShape(n_bubbles=0)

    mutator = ExploringMutator()
    results = []
    for i in tqdm(range(10000)):

        mutant=parent.copy()
        mutator.mutate(mutant)
        geo=mutant.make_geo()
        cadsd = CADSD(geo)
        cadsd.get_impedance_spektrum()

        results.append((geo, mutant, cadsd))

    pickle.dump(results, open(dbfile, "wb"))



