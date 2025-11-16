from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import json
import pandas as pd
import numpy as np
from werkzeug.utils import secure_filename
import base64
import io
from datetime import datetime

from utils.data_processor import DataProcessor
from ml.models import ModelTrainer
from ml.predictor import ModelPredictor

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

# Configuration
UPLOAD_FOLDER = 'uploads'
MODELS_FOLDER = 'models'
ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MODELS_FOLDER'] = MODELS_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create necessary directories
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(MODELS_FOLDER, exist_ok=True)

# Initialize processors
data_processor = DataProcessor()
model_trainer = ModelTrainer()
model_predictor = ModelPredictor()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ==================== DATA UPLOAD & PREPROCESSING ====================

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Upload and process CSV/Excel file"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Load and process data
            df = data_processor.load_data(filepath)
            data_info = data_processor.get_data_info(df)
            
            return jsonify({
                'success': True,
                'message': 'File uploaded successfully',
                'filename': filename,
                'data_info': data_info
            }), 200
        else:
            return jsonify({'error': 'Invalid file type'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/data/preview', methods=['POST'])
def preview_data():
    """Preview uploaded data"""
    try:
        data = request.json
        filename = data.get('filename')
        
        if not filename:
            return jsonify({'error': 'Filename required'}), 400
        
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        df = data_processor.load_data(filepath)
        
        # Return preview (first 10 rows)
        preview = df.head(10).to_dict('records')
        columns = list(df.columns)
        
        return jsonify({
            'success': True,
            'preview': preview,
            'columns': columns,
            'shape': {'rows': len(df), 'cols': len(columns)}
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/data/clean', methods=['POST'])
def clean_data():
    """Clean and preprocess data"""
    try:
        data = request.json
        filename = data.get('filename')
        cleaning_options = data.get('cleaning_options', {})
        
        if not filename:
            return jsonify({'error': 'Filename required'}), 400
        
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Check if file exists
        if not os.path.exists(filepath):
            return jsonify({'error': f'File not found: {filename}. Please upload the file first.'}), 404
        
        try:
            df = data_processor.load_data(filepath)
        except Exception as e:
            return jsonify({'error': f'Error loading file: {str(e)}'}), 400
        
        # Check if dataframe is empty
        if df.empty:
            return jsonify({'error': 'The uploaded file is empty'}), 400
        
        # Apply cleaning
        try:
            cleaned_df, cleaning_report = data_processor.clean_data(df, cleaning_options)
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            print(f"Cleaning error details: {error_trace}")  # Log full traceback
            error_msg = str(e)
            # Make error message more user-friendly
            if 'division by zero' in error_msg.lower():
                error_msg = 'Cannot calculate statistics: dataset may be too small or have invalid values'
            elif 'nan' in error_msg.lower():
                error_msg = 'Invalid data values detected. Please check your dataset.'
            return jsonify({'error': f'Error during cleaning: {error_msg}'}), 500
        
        # Check if cleaned dataframe is empty
        if cleaned_df.empty:
            return jsonify({'error': 'After cleaning, the dataset is empty. Please adjust cleaning options.'}), 400
        
        # Save cleaned data
        cleaned_filename = f"cleaned_{filename}"
        cleaned_filepath = os.path.join(app.config['UPLOAD_FOLDER'], cleaned_filename)
        
        try:
            cleaned_df.to_csv(cleaned_filepath, index=False)
        except Exception as e:
            return jsonify({'error': f'Error saving cleaned file: {str(e)}'}), 500
        
        return jsonify({
            'success': True,
            'cleaned_filename': cleaned_filename,
            'cleaning_report': cleaning_report,
            'shape': {'rows': len(cleaned_df), 'cols': len(cleaned_df.columns)}
        }), 200
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Cleaning error: {error_details}")  # Log for debugging
        return jsonify({'error': f'Cleaning failed: {str(e)}'}), 500

@app.route('/api/data/analysis', methods=['POST'])
def analyze_data():
    """Get comprehensive data analysis"""
    try:
        data = request.json
        filename = data.get('filename')
        
        if not filename:
            return jsonify({'error': 'Filename required'}), 400
        
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        df = data_processor.load_data(filepath)
        
        analysis = data_processor.analyze_data(df)
        
        return jsonify({
            'success': True,
            'analysis': analysis
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== MODEL TRAINING ====================

@app.route('/api/models/train', methods=['POST'])
def train_model():
    """Train ML model with customizable parameters"""
    try:
        data = request.json
        filename = data.get('filename')
        model_config = data.get('model_config', {})
        feature_selection = data.get('feature_selection', [])
        target_column = data.get('target_column')
        
        if not filename or not target_column:
            return jsonify({'error': 'Filename and target_column required'}), 400
        
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        df = data_processor.load_data(filepath)
        
        # Train model
        result = model_trainer.train_model(
            df=df,
            target_column=target_column,
            feature_selection=feature_selection,
            model_config=model_config
        )
        
        return jsonify({
            'success': True,
            'result': result
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/models/train-multiple', methods=['POST'])
def train_multiple_models():
    """Train multiple models and compare"""
    try:
        data = request.json
        filename = data.get('filename')
        target_column = data.get('target_column')
        feature_selection = data.get('feature_selection', [])
        models_to_train = data.get('models', ['all'])
        
        if not filename or not target_column:
            return jsonify({'error': 'Filename and target_column required'}), 400
        
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        df = data_processor.load_data(filepath)
        
        # Train multiple models
        results = model_trainer.train_multiple_models(
            df=df,
            target_column=target_column,
            feature_selection=feature_selection,
            models_to_train=models_to_train
        )
        
        # Ensure results is properly structured
        if isinstance(results, dict) and 'results' in results:
            # Results already has the correct structure
            return jsonify({
                'success': True,
                'results': results
            }), 200
        else:
            # Wrap results in expected structure
            return jsonify({
                'success': True,
                'results': {
                    'results': results.get('results', []) if isinstance(results, dict) else [],
                    'best_model': results.get('best_model') if isinstance(results, dict) else None,
                    'comparison': results.get('comparison', {}) if isinstance(results, dict) else {}
                }
            }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/models/<model_id>/info', methods=['GET'])
def get_model_info(model_id):
    """Get information about a trained model"""
    try:
        info = model_trainer.get_model_info(model_id)
        return jsonify({
            'success': True,
            'model_info': info
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/models/list', methods=['GET'])
def list_models():
    """List all trained models"""
    try:
        models = model_trainer.list_models()
        return jsonify({
            'success': True,
            'models': models
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== PREDICTIONS ====================

@app.route('/api/predict', methods=['POST'])
def predict():
    """Make predictions using a trained model"""
    try:
        data = request.json
        model_id = data.get('model_id')
        input_data = data.get('input_data')
        
        if not model_id or not input_data:
            return jsonify({'error': 'model_id and input_data required'}), 400
        
        prediction = model_predictor.predict(model_id, input_data)
        
        return jsonify({
            'success': True,
            'prediction': prediction
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/predict/batch', methods=['POST'])
def predict_batch():
    """Make batch predictions"""
    try:
        data = request.json
        model_id = data.get('model_id')
        filename = data.get('filename')
        
        if not model_id or not filename:
            return jsonify({'error': 'model_id and filename required'}), 400
        
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        df = data_processor.load_data(filepath)
        
        predictions = model_predictor.predict_batch(model_id, df)
        
        return jsonify({
            'success': True,
            'predictions': predictions
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== FEATURE IMPORTANCE ====================

@app.route('/api/models/<model_id>/feature-importance', methods=['GET'])
def get_feature_importance(model_id):
    """Get feature importance for a model"""
    try:
        importance = model_trainer.get_feature_importance(model_id)
        return jsonify({
            'success': True,
            'feature_importance': importance
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== VISUALIZATIONS ====================

@app.route('/api/visualize/correlation', methods=['POST'])
def visualize_correlation():
    """Generate correlation matrix visualization"""
    try:
        data = request.json
        filename = data.get('filename')
        
        if not filename:
            return jsonify({'error': 'Filename required'}), 400
        
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        df = data_processor.load_data(filepath)
        
        # Generate correlation matrix
        numerical_cols = df.select_dtypes(include=[np.number]).columns
        if len(numerical_cols) < 2:
            return jsonify({'error': 'Need at least 2 numerical columns'}), 400
        
        corr_matrix = df[numerical_cols].corr().to_dict()
        
        return jsonify({
            'success': True,
            'correlation_matrix': corr_matrix,
            'columns': list(numerical_cols)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/visualize/distribution', methods=['POST'])
def visualize_distribution():
    """Get distribution statistics for columns"""
    try:
        data = request.json
        filename = data.get('filename')
        columns = data.get('columns', [])
        
        if not filename:
            return jsonify({'error': 'Filename required'}), 400
        
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        df = data_processor.load_data(filepath)
        
        distributions = {}
        for col in columns:
            if col in df.columns:
                if df[col].dtype in ['int64', 'float64']:
                    distributions[col] = {
                        'mean': float(df[col].mean()),
                        'median': float(df[col].median()),
                        'std': float(df[col].std()),
                        'min': float(df[col].min()),
                        'max': float(df[col].max()),
                        'q25': float(df[col].quantile(0.25)),
                        'q75': float(df[col].quantile(0.75))
                    }
                else:
                    distributions[col] = {
                        'value_counts': df[col].value_counts().to_dict()
                    }
        
        return jsonify({
            'success': True,
            'distributions': distributions
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== HEALTH CHECK ====================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    }), 200

@app.route('/api/status', methods=['GET'])
def status():
    """Get API status and available features"""
    return jsonify({
        'status': 'running',
        'version': '1.0.0',
        'features': [
            'Data upload and preprocessing',
            'Multiple ML model training',
            'Model comparison',
            'Predictions (single and batch)',
            'Feature importance',
            'Data visualization',
            'Customizable hyperparameters'
        ]
    }), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)

