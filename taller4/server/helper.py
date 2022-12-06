from datetime import datetime
import imblearn
from imblearn.pipeline import Pipeline
from imblearn.over_sampling import SMOTE
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import StandardScaler, OneHotEncoder, OrdinalEncoder
from sklearn.compose import ColumnTransformer
from sklearn.metrics import ConfusionMatrixDisplay, precision_score, recall_score, f1_score, classification_report, roc_auc_score
import joblib
from os import listdir
from os.path import isfile, join
import glob
from prediction_model import PredictionModel
from constants import *
#Best Model
from sklearn.linear_model import LogisticRegression

class CleanTransformer(BaseEstimator, TransformerMixin):
  # add another additional parameter, just for fun, while we are at it
  def __init__(self, feature_name):
    self.feature_name = feature_name

  def fit(self, X, y = None):
    return self

  def transform(self, X, y = None):
    X_ = X.copy() # creating a copy to avoid changes to original dataset
    X_[self.feature_name] = X_[self.feature_name].replace('', 0)
    return X_

class TransformNumericTransformer(BaseEstimator, TransformerMixin):
  def fit(self, X, y = None):
    return self

  def transform(self, X, y = None):
    X_ = X.copy()
    X_ = X_.replace({'Yes':1, 'No':0})
    return X_

categorical_features = ["MultipleLines", 'InternetService',
       'OnlineSecurity', 'OnlineBackup', 'DeviceProtection', 'TechSupport',
       'StreamingTV', 'StreamingMovies', 'Contract', 'PaymentMethod']
categorical_transformer = OneHotEncoder(handle_unknown="ignore")

x_columns_ordinal = ['gender', 'Partner', 'Dependents', 'PhoneService', 'PaperlessBilling']
preprocessor = ColumnTransformer(
    transformers=[
        ("cat", categorical_transformer, categorical_features),
        ('ord_encoder', OrdinalEncoder(), x_columns_ordinal),
    ], remainder = 'passthrough'
)
def get_processing_pipeline():
    processing_pipe = Pipeline([
        ('cleaning_column', CleanTransformer('TotalCharges')),
        ('columnsTransformer', preprocessor),
        ("selector", ColumnTransformer([("selector", "passthrough", list(range(1,21,1)))], remainder="drop")),
        ("scaler", StandardScaler()),
        # ("classifier", LogisticRegression())
        ])
    return processing_pipe

def transform_numeric_pipeline_labels(Y_train):
    transform_numeric_pipe = Pipeline([
    ('cleaning_column', TransformNumericTransformer())
    ])
    Y_train = transform_numeric_pipe.transform(Y_train)
    return Y_train

def get_timestamp():
    dt = datetime.now()
    ts = datetime.timestamp(dt)
    return str(int(ts))

def train_model(processing_pipe, X_train, Y_train):
    best_hyperparameters = {'C': 10000.0, 'max_iter': 5000, 'penalty': 'l2'}
    processing_pipe.steps.append(['sampling', SMOTE()])
    processing_pipe.steps.append(["classifier",  LogisticRegression(**best_hyperparameters)])
    processing_pipe.fit(X_train, Y_train)
    joblib.dump(processing_pipe, MODELS_PATH + MODEL_NAME + get_timestamp() + '.joblib', compress = 1)
    return MODELS_PATH + MODEL_NAME + get_timestamp()

def print_confusion_and_roc_auc_metrics(model, X_df, y_df):
    predictions = model.predict(X_df)
    print("Matriz de confusión:")
    print(classification_report(y_df, predictions))
    print("ROC AUC:")
    print(roc_auc_score(y_df, predictions))

def get_all_models():
    #onlyfiles = [f for f in listdir(MODELS_PATH) if isfile(join(MODELS_PATH, f))]
    onlyfiles = glob.glob(MODELS_PATH + "*.joblib")
    return onlyfiles

def get_metrics_all_models(df, Y_train):
    results = []
    for model in get_all_models():
        print(model)
        mode_joblib = PredictionModel(model).get_model()
        confusion, roc_auc = get_confusion_and_roc_auc_metrics(mode_joblib, df, Y_train)
        result = {"confusion": confusion, "roc_auc": roc_auc}
        results.append(result)
    return results

def get_confusion_and_roc_auc_metrics(model, X_df, y_df):
    predictions = model.predict(X_df)
    return classification_report(y_df, predictions), roc_auc_score(y_df, predictions)