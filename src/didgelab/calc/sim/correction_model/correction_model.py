from abc import ABC, abstractmethod
import numpy as np
import pickle
from sklearn import svm
import os
from didgelab.app import App

class FrequencyCorrectionModel(ABC):

    @abstractmethod
    def correct(self, frequencies : np.array) -> np.array:
        pass

class SVMCorrectionModel(FrequencyCorrectionModel):

    def __init__(self):
        infile = os.path.join(os.path.dirname(__file__), "svm_correction_model.bin")
        self.model = pickle.load(open(infile, "rb"))
        App.register_service(self)

    def correct(self, frequencies):
        frequencies = np.array(frequencies)
        X = frequencies.reshape((-1,1))
        corrected = frequencies + self.model.predict(X)
        return np.concatenate(corrected)