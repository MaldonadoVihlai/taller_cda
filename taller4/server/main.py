from typing import List
import pandas as pd
from fastapi import FastAPI
from data_model import DataModel
from data_model_predict import DataModelPredict
from prediction_model import PredictionModel
from helper import *
from constants import *

app = FastAPI()


@app.get("/")
def read_root():
   return { "message": "Hello world" }
@app.get("/models")
def read_root():
   return get_all_models()

@app.post("/train")
def train(X: List[DataModel]):
   #original_model = PredictionModel().get_model()
   #print(X)
   df = pd.DataFrame([x.dict() for x in X])
   processing_pipe = get_processing_pipeline()
   processing_pipe.fit(df)
   X_train_processed = processing_pipe.transform(df)
   #print(X_train_processed)
   Y_train = transform_numeric_pipeline_labels(df['Churn'])
   last_model = train_model(processing_pipe, df.drop('Churn', axis=1), Y_train)
   last_model = original_model = PredictionModel(last_model+'.joblib').get_model()
   print(last_model)
   print_confusion_and_roc_auc_metrics(last_model, df, Y_train)
   confusion, roc_auc = get_confusion_and_roc_auc_metrics(last_model, df, Y_train)
   result = {"confusion": confusion, "roc_auc": roc_auc}
   results = get_metrics_all_models(df, Y_train)
   #
   #results = predicion_model.make_predictions(df)
   #return results.tolist()
   return results

@app.post("/predict")
def make_predictions(X: List[DataModelPredict]):
   df = pd.DataFrame([x.dict() for x in X])
   processing_pipe = get_processing_pipeline()
   processing_pipe.fit(df)
   X_train_processed = processing_pipe.transform(df)
   all_model = get_all_models()
   predicion_model = PredictionModel(all_model[-1])

   results = predicion_model.make_predictions(df)
   data_prediction = [x.dict() for x in X]
   i = 0
   for d in data_prediction:
    d["Churn"] = str(results[i])
    i+=1
   return data_prediction

@app.post("/predict_bonus/{model_id}")
async def make_predictions(model_id: str, X: List[DataModelPredict]):
   print(model_id)
   df = pd.DataFrame([x.dict() for x in X])
   processing_pipe = get_processing_pipeline()
   processing_pipe.fit(df)
   predicion_model = PredictionModel(MODELS_PATH + model_id +'.joblib')
   results = predicion_model.make_predictions(df)
   data_prediction = [x.dict() for x in X]
   i = 0
   for d in data_prediction:
    d["Churn"] = str(results[i])
    i+=1
   return data_prediction