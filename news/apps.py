from django.apps import AppConfig
import pandas as pd
import joblib
import os

class YourAppConfig(AppConfig):
    name = 'your_app'

    def ready(self):
        global filtered_dataset_df, tfidf_vectorizer, svm_model
        file_path = '/home/ubuntu/filtered_dataset.csv'
        tfidf_vectorizer_path = '/home/ubuntu/tfidf_vectorizer.pkl'
        svm_model_path = '/home/ubuntu/svm_model.joblib'

        if os.path.exists(file_path):
            filtered_dataset_df = pd.read_csv(file_path)
        else:
            filtered_dataset_df = None
        
        if os.path.exists(tfidf_vectorizer_path):
            tfidf_vectorizer = joblib.load(tfidf_vectorizer_path)
        else:
            tfidf_vectorizer = None

        if os.path.exists(svm_model_path):
            svm_model = joblib.load(svm_model_path)
        else:
            svm_model = None

