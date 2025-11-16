import os
import pickle
import json
import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import (
    accuracy_score, classification_report, confusion_matrix,
    precision_score, recall_score, f1_score, roc_auc_score
)
import warnings
warnings.filterwarnings('ignore')

class ModelTrainer:
    def __init__(self, models_folder='models'):
        self.models_folder = models_folder
        os.makedirs(models_folder, exist_ok=True)
        self.models = {}
        self.scalers = {}
        self.label_encoders = {}
        self.model_metadata = {}
    
    def train_model(self, df, target_column, feature_selection=None, model_config=None):
        """Train a single ML model"""
        if model_config is None:
            model_config = {}
        
        model_type = model_config.get('model_type', 'random_forest')
        
        # Prepare data
        if feature_selection is None or len(feature_selection) == 0:
            # Auto-select features (exclude target and non-numeric)
            feature_cols = [col for col in df.columns 
                          if col != target_column and df[col].dtype in ['int64', 'float64']]
        else:
            feature_cols = feature_selection
        
        # Encode categorical features
        df_encoded = df.copy()
        categorical_features = [col for col in feature_cols if df[col].dtype == 'object']
        
        for col in categorical_features:
            if col not in self.label_encoders:
                le = LabelEncoder()
                df_encoded[col + '_encoded'] = le.fit_transform(df[col].astype(str))
                self.label_encoders[col] = le
            else:
                df_encoded[col + '_encoded'] = self.label_encoders[col].transform(df[col].astype(str))
            
            # Replace original with encoded in feature_cols
            feature_cols = [c + '_encoded' if c == col else c for c in feature_cols]
        
        X = df_encoded[feature_cols]
        y = df_encoded[target_column]
        
        # Encode target if categorical
        if y.dtype == 'object':
            if target_column not in self.label_encoders:
                le_target = LabelEncoder()
                y_encoded = le_target.fit_transform(y)
                self.label_encoders[target_column] = le_target
            else:
                y_encoded = self.label_encoders[target_column].transform(y)
            y = pd.Series(y_encoded)
        
        # Split data
        test_size = model_config.get('test_size', 0.2)
        random_state = model_config.get('random_state', 42)
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state, stratify=y if len(y.unique()) > 1 else None
        )
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        self.scalers[model_type] = scaler
        
        # Create and train model
        model = self._create_model(model_type, model_config)
        
        # Train
        if model_type in ['logistic_regression', 'knn', 'svm']:
            model.fit(X_train_scaled, y_train)
            y_pred = model.predict(X_test_scaled)
        else:
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
        
        # Evaluate
        accuracy = accuracy_score(y_test, y_pred)
        
        # Additional metrics
        metrics = {
            'accuracy': float(accuracy),
            'precision': float(precision_score(y_test, y_pred, average='weighted', zero_division=0)),
            'recall': float(recall_score(y_test, y_pred, average='weighted', zero_division=0)),
            'f1_score': float(f1_score(y_test, y_pred, average='weighted', zero_division=0))
        }
        
        # Classification report
        try:
            report = classification_report(y_test, y_pred, output_dict=True, zero_division=0)
        except:
            report = {}
        
        # Confusion matrix
        cm = confusion_matrix(y_test, y_pred).tolist()
        
        # Save model
        model_id = f"{model_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        model_path = os.path.join(self.models_folder, f"{model_id}.pkl")
        
        with open(model_path, 'wb') as f:
            pickle.dump({
                'model': model,
                'scaler': scaler if model_type in ['logistic_regression', 'knn', 'svm'] else None,
                'feature_columns': feature_cols,
                'target_column': target_column,
                'label_encoders': self.label_encoders,
                'model_type': model_type
            }, f)
        
        # Store metadata
        self.model_metadata[model_id] = {
            'model_type': model_type,
            'accuracy': accuracy,
            'metrics': metrics,
            'feature_columns': feature_cols,
            'target_column': target_column,
            'train_size': len(X_train),
            'test_size': len(X_test),
            'created_at': datetime.now().isoformat()
        }
        
        # Feature importance if available
        feature_importance = None
        if hasattr(model, 'feature_importances_'):
            feature_importance = dict(zip(feature_cols, model.feature_importances_.tolist()))
        
        return {
            'model_id': model_id,
            'model_type': model_type,
            'accuracy': accuracy,
            'metrics': metrics,
            'classification_report': report,
            'confusion_matrix': cm,
            'feature_importance': feature_importance,
            'train_size': len(X_train),
            'test_size': len(X_test)
        }
    
    def train_multiple_models(self, df, target_column, feature_selection=None, models_to_train=None):
        """Train multiple models and compare"""
        if models_to_train is None or models_to_train == ['all']:
            models_to_train = ['logistic_regression', 'decision_tree', 'random_forest', 
                             'knn', 'svm', 'gradient_boosting', 'naive_bayes']
        
        results = []
        
        for model_type in models_to_train:
            try:
                result = self.train_model(
                    df=df,
                    target_column=target_column,
                    feature_selection=feature_selection,
                    model_config={'model_type': model_type}
                )
                results.append(result)
            except Exception as e:
                results.append({
                    'model_type': model_type,
                    'error': str(e)
                })
        
        # Sort by accuracy
        successful_results = [r for r in results if 'accuracy' in r]
        if successful_results:
            successful_results.sort(key=lambda x: x['accuracy'], reverse=True)
            best_model = successful_results[0]
        else:
            best_model = None
        
        return {
            'results': results,
            'best_model': best_model,
            'comparison': {
                'models': [r.get('model_type', 'unknown') for r in results],
                'accuracies': [r.get('accuracy', 0) for r in results if 'accuracy' in r]
            }
        }
    
    def _create_model(self, model_type, config):
        """Create model instance based on type"""
        if model_type == 'logistic_regression':
            return LogisticRegression(
                max_iter=config.get('max_iter', 1000),
                random_state=config.get('random_state', 42),
                C=config.get('C', 1.0)
            )
        elif model_type == 'decision_tree':
            return DecisionTreeClassifier(
                max_depth=config.get('max_depth', 5),
                random_state=config.get('random_state', 42),
                min_samples_split=config.get('min_samples_split', 2)
            )
        elif model_type == 'random_forest':
            return RandomForestClassifier(
                n_estimators=config.get('n_estimators', 100),
                max_depth=config.get('max_depth', 5),
                random_state=config.get('random_state', 42),
                min_samples_split=config.get('min_samples_split', 2)
            )
        elif model_type == 'knn':
            return KNeighborsClassifier(
                n_neighbors=config.get('n_neighbors', 5),
                weights=config.get('weights', 'uniform')
            )
        elif model_type == 'svm':
            return SVC(
                kernel=config.get('kernel', 'rbf'),
                C=config.get('C', 1.0),
                random_state=config.get('random_state', 42)
            )
        elif model_type == 'gradient_boosting':
            return GradientBoostingClassifier(
                n_estimators=config.get('n_estimators', 100),
                max_depth=config.get('max_depth', 3),
                random_state=config.get('random_state', 42)
            )
        elif model_type == 'naive_bayes':
            return GaussianNB()
        else:
            raise ValueError(f"Unknown model type: {model_type}")
    
    def get_model_info(self, model_id):
        """Get information about a trained model"""
        if model_id in self.model_metadata:
            return self.model_metadata[model_id]
        
        # Try to load from file
        model_path = os.path.join(self.models_folder, f"{model_id}.pkl")
        if os.path.exists(model_path):
            with open(model_path, 'rb') as f:
                model_data = pickle.load(f)
            
            return {
                'model_type': model_data.get('model_type', 'unknown'),
                'feature_columns': model_data.get('feature_columns', []),
                'target_column': model_data.get('target_column', 'unknown'),
                'created_at': 'unknown'
            }
        
        raise ValueError(f"Model {model_id} not found")
    
    def get_feature_importance(self, model_id):
        """Get feature importance for a model"""
        model_path = os.path.join(self.models_folder, f"{model_id}.pkl")
        if not os.path.exists(model_path):
            raise ValueError(f"Model {model_id} not found")
        
        with open(model_path, 'rb') as f:
            model_data = pickle.load(f)
        
        model = model_data['model']
        feature_columns = model_data.get('feature_columns', [])
        
        if hasattr(model, 'feature_importances_'):
            importance = dict(zip(feature_columns, model.feature_importances_.tolist()))
            # Sort by importance
            importance = dict(sorted(importance.items(), key=lambda x: x[1], reverse=True))
            return importance
        else:
            return {"message": "Feature importance not available for this model type"}
    
    def list_models(self):
        """List all trained models"""
        models = []
        
        # From metadata
        for model_id, metadata in self.model_metadata.items():
            models.append({
                'model_id': model_id,
                'model_type': metadata.get('model_type', 'unknown'),
                'accuracy': metadata.get('accuracy', 0),
                'created_at': metadata.get('created_at', 'unknown')
            })
        
        # From files
        if os.path.exists(self.models_folder):
            for filename in os.listdir(self.models_folder):
                if filename.endswith('.pkl'):
                    model_id = filename[:-4]  # Remove .pkl
                    if model_id not in [m['model_id'] for m in models]:
                        try:
                            info = self.get_model_info(model_id)
                            models.append({
                                'model_id': model_id,
                                'model_type': info.get('model_type', 'unknown'),
                                'accuracy': 'unknown',
                                'created_at': info.get('created_at', 'unknown')
                            })
                        except:
                            pass
        
        return models

