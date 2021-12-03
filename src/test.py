from cad.calc.mutation import MutantPool, MutantPoolEntry
from cad.calc.parameters import BasicShapeParameters, AddBubble
from cad.ui.evolution_display import EvolutionDisplay
from cad.cadsd.cadsd import CADSDResult
import pickle

pool=pickle.load(open("projects/pipelines/evolve_penta/0.pkl", "rb"))
geo=pool.pool[0][0].geo
cadsd_result=CADSDResult.from_geo(geo)

mpe=MutantPoolEntry(None, geo, 1.2, cadsd_result)
pool=MutantPool()
pool.add_entry(mpe)

ed=EvolutionDisplay(3,3,1,1, "test")
try:
    ed.update_generation(1, pool)
finally:
    ed.end()