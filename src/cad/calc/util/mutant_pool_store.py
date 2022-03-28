# save and load mutant pools

from cad.calc.mutation import MutantPool, MutantPoolEntry
import pickle

def save_mutant_pool(pool : MutantPool, outfile : str):
    new_mutant_pool=MutantPool()
    for i in range(pool.len()):
        mpe=pool.get(i)
        geo=mpe.geo.copy()
        geo.reset_cadsd()
        mpe.parameterset.release_memory()
        new_mpe=MutantPoolEntry(mpe.parameterset, geo, mpe.loss)
        new_mutant_pool.add_entry(new_mpe)

    f=open(outfile, "wb")
    pickle.dump(new_mutant_pool, f)
    f.close()

def load_mutant_pool(infile):
    return pickle.load(open(infile, "rb"))
    
