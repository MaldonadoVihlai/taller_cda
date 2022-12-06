from datetime import datetime
from imblearn.pipeline import Pipeline
from imblearn.over_sampling import SMOTE
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import StandardScaler, OneHotEncoder, OrdinalEncoder
from sklearn.compose import ColumnTransformer
from sklearn.metrics import classification_report, roc_auc_score
import joblib
import glob
from prediction_model import PredictionModel
from constants import *
# Best Model
from sklearn.linear_model import LogisticRegression


class CleanTransformer(BaseEstimator, TransformerMixin):
    def __init__(self, feature_name):
        self.feature_name = feature_name

    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        X_ = X.copy()
        X_[self.feature_name] = X_[self.feature_name].replace('', 0)
        return X_


class TransformNumericTransformer(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        X_ = X.copy()
        X_ = X_.replace({'Yes': 1, 'No': 0})
        return X_


categorical_transformer = OneHotEncoder(handle_unknown="ignore")

preprocessor = ColumnTransformer(
    transformers=[
        ("cat", categorical_transformer, CATEGORICAL_FEATURES),
        ('ord_encoder', OrdinalEncoder(), ORDINAL_COLUMNS),
    ], remainder='passthrough'
)


def get_processing_pipeline():
    processing_pipe = Pipeline([
        ('cleaning_column', CleanTransformer('TotalCharges')),
        ('columnsTransformer', preprocessor),
        ("selector", ColumnTransformer(
            [("selector", "passthrough", list(range(1, 21, 1)))], remainder="drop")),
        ("scaler", StandardScaler())
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
    processing_pipe.steps.append(
        ["classifier",  LogisticRegression(**best_hyperparameters)])
    processing_pipe.fit(X_train, Y_train)
    joblib.dump(processing_pipe, MODELS_PATH + MODEL_NAME +
                get_timestamp() + JOBLIB_EXTENSION, compress=1)
    return MODELS_PATH + MODEL_NAME + get_timestamp()


def print_confusion_and_roc_auc_metrics(model, X_df, y_df):
    predictions = model.predict(X_df)
    print("Matriz de confusión:")
    print(classification_report(y_df, predictions))
    print("ROC AUC:")
    print(roc_auc_score(y_df, predictions))


def get_all_models():
    files = glob.glob(MODELS_PATH + "*" + JOBLIB_EXTENSION)
    return files


def get_metrics_all_models(df, Y_train):
    results = []
    for model in get_all_models():
        mode_joblib = PredictionModel(model).get_model()
        confusion, roc_auc = get_confusion_and_roc_auc_metrics(
            mode_joblib, df, Y_train)
        result = {"model": model.replace(MODELS_PATH, '').replace(
            JOBLIB_EXTENSION, ''), "roc_auc": roc_auc}
        results.append(result)
    return results


def get_confusion_and_roc_auc_metrics(model, X_df, y_df):
    predictions = model.predict(X_df)
    return classification_report(y_df, predictions), roc_auc_score(y_df, predictions)


def build_prediction_result(df, predicion_model):
    labels = predicion_model.make_predictions(df).tolist()
    probabilities = predicion_model.make_probability_predictions(df).tolist()
    ind = 0
    results = []
    for ind in range(len(labels)):
        prediction_dict = {"label": labels[ind],
                           "probabilidad": max(probabilities[ind])}
        results.append(prediction_dict)
    return results
