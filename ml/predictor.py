import os
import pickle
import pandas as pd
import numpy as np

class ModelPredictor:
    def __init__(self, models_folder='models'):
        self.models_folder = models_folder
    
    def predict(self, model_id, input_data):
        """Make prediction for a single input"""
        model_path = os.path.join(self.models_folder, f"{model_id}.pkl")
        if not os.path.exists(model_path):
            raise ValueError(f"Model {model_id} not found")
        
        with open(model_path, 'rb') as f:
            model_data = pickle.load(f)
        
        model = model_data['model']
        scaler = model_data.get('scaler')
        feature_columns = model_data.get('feature_columns', [])
        label_encoders = model_data.get('label_encoders', {})
        model_type = model_data.get('model_type', 'unknown')
        
        # Prepare input data
        if isinstance(input_data, dict):
            # Convert dict to DataFrame
            input_df = pd.DataFrame([input_data])
        elif isinstance(input_data, list):
            input_df = pd.DataFrame(input_data)
        else:
            raise ValueError("Input data must be dict or list of dicts")
        
        # Encode categorical features
        for col in feature_columns:
            if col.endswith('_encoded'):
                original_col = col.replace('_encoded', '')
                if original_col in input_df.columns and original_col in label_encoders:
                    input_df[col] = label_encoders[original_col].transform(input_df[original_col].astype(str))
                elif original_col not in input_df.columns:
                    raise ValueError(f"Missing feature: {original_col}")
        
        # Select features
        X = input_df[feature_columns]
        
        # Scale if needed
        if scaler is not None:
            X = scaler.transform(X)
        
        # Predict
        prediction = model.predict(X)
        prediction_proba = None
        
        if hasattr(model, 'predict_proba'):
            prediction_proba = model.predict_proba(X).tolist()
        
        # Decode prediction if needed
        target_column = model_data.get('target_column', '')
        if target_column in label_encoders:
            le = label_encoders[target_column]
            prediction_labels = le.inverse_transform(prediction)
        else:
            prediction_labels = prediction.tolist()
        
        result = {
            'prediction': prediction_labels[0] if len(prediction_labels) == 1 else prediction_labels,
            'prediction_raw': int(prediction[0]) if len(prediction) == 1 else prediction.tolist()
        }
        
        if prediction_proba:
            result['probabilities'] = prediction_proba[0] if len(prediction_proba) == 1 else prediction_proba
        
        return result
    
    def predict_batch(self, model_id, df):
        """Make batch predictions"""
        model_path = os.path.join(self.models_folder, f"{model_id}.pkl")
        if not os.path.exists(model_path):
            raise ValueError(f"Model {model_id} not found")
        
        with open(model_path, 'rb') as f:
            model_data = pickle.load(f)
        
        model = model_data['model']
        scaler = model_data.get('scaler')
        feature_columns = model_data.get('feature_columns', [])
        label_encoders = model_data.get('label_encoders', {})
        
        # Encode categorical features
        df_encoded = df.copy()
        for col in feature_columns:
            if col.endswith('_encoded'):
                original_col = col.replace('_encoded', '')
                if original_col in df_encoded.columns and original_col in label_encoders:
                    df_encoded[col] = label_encoders[original_col].transform(df_encoded[original_col].astype(str))
        
        # Select features
        X = df_encoded[feature_columns]
        
        # Scale if needed
        if scaler is not None:
            X = scaler.transform(X)
        
        # Predict
        predictions = model.predict(X)
        prediction_proba = None
        
        if hasattr(model, 'predict_proba'):
            prediction_proba = model.predict_proba(X)
        
        # Decode predictions if needed
        target_column = model_data.get('target_column', '')
        if target_column in label_encoders:
            le = label_encoders[target_column]
            prediction_labels = le.inverse_transform(predictions)
        else:
            prediction_labels = predictions.tolist()
        
        result = {
            'predictions': prediction_labels.tolist() if hasattr(prediction_labels, 'tolist') else list(prediction_labels),
            'count': len(predictions)
        }
        
        if prediction_proba is not None:
            result['probabilities'] = prediction_proba.tolist()
        
        return result

