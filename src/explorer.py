from cad.ui.explorer import Explorer
from cad.calc.parameters import *

pipeline="projects/pipelines/minisinger/"
explorer=Explorer(pipeline)
explorer.load("0", 0)
explorer.start_ui()
