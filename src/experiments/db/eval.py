from cad.calc.parameters import MbeyaShape
from cad.calc.mutation import ExploringMutator
from tqdm import tqdm
from cad.cadsd.cadsd import CADSD
import pickle
from experiments.db.generate_shapes import dbfile

if __name__=="__main__":

    db = pickle.load(open(dbfile, "rb"))

    for geo, shape, cadsd in db:
        print(cadsd.get_notes())
        break

