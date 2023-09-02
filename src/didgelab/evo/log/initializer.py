from .checkpoint_writer import CheckPointWriter
from .loss_writer import LossWriter

def initialize_logger():
    cp = CheckPointWriter()
    lw = LossWriter()