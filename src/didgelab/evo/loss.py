from abc import ABC, abstractmethod
from didgelab.app import App

class LossFunction(ABC):

    def __init__(self):
        App.register_service(self)

    @abstractmethod
    def get_loss(self, geo):
        raise Exception("this is abstract so we should never reach this code")

    def __call__(self, geo, context=None):
        return self.get_loss(geo)

