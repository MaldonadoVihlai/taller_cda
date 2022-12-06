from joblib import load

class PredictionModel:

    def __init__(self, path="models/log_reg_smote_model.joblib"):
        self.model = load(path)

    def make_predictions(self, data):
        result = self.model.predict(data)
        return result
    def get_model(self):
        return self.model
