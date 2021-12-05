from cad.ui.explorer import Explorer
from cad.calc.parameters import *
from cad.common.app import App

App.init()
App.init_logging()
pipeline="projects/pipelines/minisinger/"
App.set_context("pipeline_dir", pipeline)

explorer=Explorer(pipeline)
explorer.load("0", 0)
explorer.start_ui()
