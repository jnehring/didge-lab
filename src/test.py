from cad.calc.mutation import MutantPool, MutantPoolEntry
from cad.calc.parameters import BasicShapeParameters, AddBubble
from cad.cadsd.cadsd import CADSDResult
import pickle
from cad.ui.ui import UserInterface, PeakWindow, StaticTextWindow
from cad.ui.fft_window import FFTWindow
from cad.ui.explorer import Explorer

pipeline="projects/pipelines/minisinger/"
explorer=Explorer(pipeline)
explorer.start_ui()


# generate_pickle=False
# f="projects/temp/temp.pkl"

# if generate_pickle:
#     pool=pickle.load(open("projects/pipelines/evolve_penta/0.pkl", "rb"))
#     mp=MutantPool()
#     for i in range(len(pool.pool)):
#         print(i)
#         geo=pool.pool[i][0].geo
#         cadsd_result=CADSDResult.from_geo(geo)
#         me=MutantPoolEntry(None, geo, 5, cadsd_result)
#         mp.add_entry(me)
#     pickle.dump(mp, open(f, "wb"))

# mp=pickle.load(open(f, "rb"))

# ui=UserInterface()

# peak=mp.get(0).cadsd_result.peaks
# peak_window=PeakWindow(peak)
# ui.add_window(peak_window)

# ui.add_separator()

# fft=mp.get(0).cadsd_result.fft
# ui.add_window(FFTWindow(fft))



# print(ui.render())
#ui.add_window(PeakWindow(peak))

# try:
#     ui.start()
#     ui.render()
#     ui.wait_for_key()
# finally:
#     ui.end()


# ed=EvolutionDisplay(3,3,1,1, "test")
# #ed.disabled=True
# try:
#     ed.update_generation(1, mp)
#     #char = ed.stdscr.getch()
# finally:
#     ed.end()
