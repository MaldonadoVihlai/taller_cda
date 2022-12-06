from typing import List
import pandas as pd
from fastapi import FastAPI
from data_model import DataModel
from data_model_predict import DataModelPredict
from prediction_model import PredictionModel
from helper import *
from constants import *
import __main__

app = FastAPI()


class CleanTransformer(BaseEstimator, TransformerMixin):
    def __init__(self, feature_name):
        self.feature_name = feature_name

    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        X_ = X.copy()
        X_[self.feature_name] = X_[self.feature_name].replace('', 0)
        return X_


__main__.CleanTransformer = CleanTransformer


@app.get("/")
def read_root():
    return {"message": "Hello world"}


@app.get("/models")
def read_root():
    return list(map(lambda x: x.replace(MODELS_PATH, '').replace(
        JOBLIB_EXTENSION, ''), get_all_models()))


@app.post("/train")
def train(X: List[DataModel]):
    original_model = PredictionModel().get_model()
    df = pd.DataFrame([x.dict() for x in X])
    processing_pipe = get_processing_pipeline()
    processing_pipe.fit(df)
    X_train_processed = processing_pipe.transform(df)
    # print(X_train_processed)
    Y_train = transform_numeric_pipeline_labels(df['Churn'])
    last_model = train_model(
        processing_pipe, df.drop('Churn', axis=1), Y_train)
    last_model = original_model = PredictionModel(
        last_model+JOBLIB_EXTENSION).get_model()
    confusion, roc_auc = get_confusion_and_roc_auc_metrics(
        last_model, df, Y_train)
    result = {"confusion": confusion, "roc_auc": roc_auc}
    results = get_metrics_all_models(df, Y_train)
    return results


@app.post("/predict")
def make_predictions(X: List[DataModelPredict]):
    df = pd.DataFrame([x.dict() for x in X])
    processing_pipe = get_processing_pipeline()
    processing_pipe.fit(df)
    all_model = get_all_models()
    predicion_model = PredictionModel(all_model[-1])  # Predict with last model
    results = build_prediction_result(df, predicion_model)
    return results


@app.post("/predict_bonus")
async def make_predictions(X: List[DataModelPredict], model_id: str = None):
    print("query param: ", model_id)
    if model_id == None:
      model_id = ORIGINAL_MODEL.replace('.joblib', '')
    df = pd.DataFrame([x.dict() for x in X])
    processing_pipe = get_processing_pipeline()
    processing_pipe.fit(df)
    # Predict with model passed by query param
    predicion_model = PredictionModel(
        MODELS_PATH + model_id + JOBLIB_EXTENSION)
    results = build_prediction_result(df, predicion_model)
    return results
