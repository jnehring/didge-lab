from didgelab.app import init_app
from didgelab.web.webserver import start_webwerver_non_blocking
from didgelab.evo.log.checkpoint_writer import CheckPointWriter
from didgelab.evo.log.loss_writer import LossWriter
from didgelab.web.stats import EvolutionStats
from didgelab.web.evolution_state import EvolutionState
from didgelab.calc.sim.correction_model.correction_model import SVMCorrectionModel

def init_web():
    init_app()
    cp = CheckPointWriter()
    lw = LossWriter()
    ss = EvolutionStats()
    es = EvolutionState()
    scm = SVMCorrectionModel()
    start_webwerver_non_blocking()

def init_console():
    init_app()
    cp = CheckPointWriter()
    lw = LossWriter()
    scm = SVMCorrectionModel()

def init_jupyter():
    init_app()
    scm = SVMCorrectionModel()

def init_console_no_output():
    init_app(create_output_folder=False)
    scm = SVMCorrectionModel()

