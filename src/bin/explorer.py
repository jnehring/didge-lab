from cad.ui.explorer import Explorer
from cad.calc.parameters import *
from cad.common.app import App
from cad.calc.mutation import *

App.init()
App.init_logging()
pipeline="projects/pipelines/penta_didge/"
App.set_context("pipeline_dir", pipeline)

explorer=Explorer(pipeline)
explorer.load("1", 0)
explorer.start_ui()
