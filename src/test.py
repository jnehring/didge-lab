from didgelab.calc.sim.cadsd import CADSD
from didgelab.app import get_app
from didgelab.initializer import init_console_no_output
from didgelab.calc.geo import Geo

init_console_no_output()

geo = [[0,32], [1000, 64]]
cadsd = CADSD(geo)