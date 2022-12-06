MODEL_NAME = 'model_'
MODELS_PATH = './models/'
ORIGINAL_MODEL = 'best_model.joblib'
CATEGORICAL_FEATURES = ["MultipleLines", 'InternetService',
                        'OnlineSecurity', 'OnlineBackup', 'DeviceProtection', 'TechSupport',
                        'StreamingTV', 'StreamingMovies', 'Contract', 'PaymentMethod']
ORDINAL_COLUMNS = ['gender', 'Partner',
                     'Dependents', 'PhoneService', 'PaperlessBilling']
JOBLIB_EXTENSION = ".joblib"