from joblib import load
from constants import *


class PredictionModel:

    def __init__(self, path=MODELS_PATH + ORIGINAL_MODEL):
        self.model = load(path)

    def make_predictions(self, data):
        result = self.model.predict(data)
        return result

    def make_probability_predictions(self, data):
        result = self.model.predict_proba(data)
        return result

    def get_model(self):
        return self.model
