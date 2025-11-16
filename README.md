# ML Model Customization Web App - Backend API

A comprehensive Flask-based REST API for customizing and training machine learning models with interactive features.

## Features

- 📊 **Data Upload & Preprocessing**
  - Upload CSV/Excel files
  - Automatic data cleaning
  - Missing value handling (imputation/dropping)
  - Outlier detection and handling
  - Duplicate removal

- 🤖 **Multiple ML Models**
  - Logistic Regression
  - Decision Tree
  - Random Forest
  - K-Nearest Neighbors (KNN)
  - Support Vector Machine (SVM)
  - Gradient Boosting
  - Naive Bayes

- ⚙️ **Customizable Parameters**
  - Hyperparameter tuning
  - Feature selection
  - Train/test split ratio
  - Model-specific configurations

- 📈 **Model Comparison**
  - Train multiple models simultaneously
  - Compare performance metrics
  - Feature importance analysis

- 🔮 **Predictions**
  - Single prediction
  - Batch predictions
  - Probability scores

- 📊 **Data Visualization**
  - Correlation matrices
  - Distribution analysis
  - Statistical summaries

## Installation

1. **Clone or navigate to the project directory:**
```bash
cd /Users/samettemurcin/Desktop/Sunnydata_edu
```

2. **Create a virtual environment (recommended):**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

## Running the API

Start the Flask server:
```bash
python app.py
```

The API will be available at `http://localhost:5001`

**Note:** Port 5000 is often used by Apple AirPlay on macOS. If you encounter connection issues, the backend uses port 5001 by default.

## API Endpoints

### Health & Status
- `GET /api/health` - Health check
- `GET /api/status` - API status and features

### Data Management
- `POST /api/upload` - Upload CSV/Excel file
- `POST /api/data/preview` - Preview uploaded data
- `POST /api/data/clean` - Clean and preprocess data
- `POST /api/data/analysis` - Get comprehensive data analysis

### Model Training
- `POST /api/models/train` - Train a single model
- `POST /api/models/train-multiple` - Train multiple models and compare
- `GET /api/models/list` - List all trained models
- `GET /api/models/<model_id>/info` - Get model information
- `GET /api/models/<model_id>/feature-importance` - Get feature importance

### Predictions
- `POST /api/predict` - Make single prediction
- `POST /api/predict/batch` - Make batch predictions

### Visualizations
- `POST /api/visualize/correlation` - Get correlation matrix
- `POST /api/visualize/distribution` - Get distribution statistics

## Example API Usage

### 1. Upload Data
```bash
curl -X POST http://localhost:5000/api/upload \
  -F "file=@your_data.csv"
```

### 2. Clean Data
```json
POST /api/data/clean
{
  "filename": "your_data.csv",
  "cleaning_options": {
    "missing_threshold": 50,
    "imputation_strategy": "median",
    "remove_duplicates": true,
    "handle_outliers": false
  }
}
```

### 3. Train Model
```json
POST /api/models/train
{
  "filename": "cleaned_your_data.csv",
  "target_column": "performance_category",
  "feature_selection": ["MOC", "vocab_score", "rc_score", "composite_percentile"],
  "model_config": {
    "model_type": "random_forest",
    "n_estimators": 100,
    "max_depth": 5,
    "test_size": 0.2,
    "random_state": 42
  }
}
```

### 4. Train Multiple Models
```json
POST /api/models/train-multiple
{
  "filename": "cleaned_your_data.csv",
  "target_column": "performance_category",
  "feature_selection": ["MOC", "vocab_score", "rc_score"],
  "models": ["random_forest", "decision_tree", "logistic_regression", "knn"]
}
```

### 5. Make Prediction
```json
POST /api/predict
{
  "model_id": "random_forest_20241201_120000",
  "input_data": {
    "MOC": 2.1,
    "vocab_score": 45.0,
    "rc_score": 0.65,
    "composite_percentile": 70.0
  }
}
```

## Frontend Integration

This backend is designed to work with a Tailwind CSS frontend. The API returns JSON responses that can be easily consumed by your frontend application.

### Response Format
All endpoints return JSON in the following format:
```json
{
  "success": true,
  "data": {...},
  "message": "Optional message"
}
```

### Error Format
```json
{
  "error": "Error message description"
}
```

## Project Structure

```
Sunnydata_edu/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md              # This file
├── utils/
│   └── data_processor.py  # Data preprocessing utilities
├── ml/
│   ├── models.py          # Model training logic
│   └── predictor.py       # Prediction logic
├── uploads/               # Uploaded data files (created automatically)
└── models/                # Trained models (created automatically)
```

## Model Configuration Options

### Logistic Regression
- `max_iter`: Maximum iterations (default: 1000)
- `C`: Regularization strength (default: 1.0)

### Decision Tree
- `max_depth`: Maximum tree depth (default: 5)
- `min_samples_split`: Minimum samples to split (default: 2)

### Random Forest
- `n_estimators`: Number of trees (default: 100)
- `max_depth`: Maximum tree depth (default: 5)
- `min_samples_split`: Minimum samples to split (default: 2)

### KNN
- `n_neighbors`: Number of neighbors (default: 5)
- `weights`: Weight function (default: 'uniform')

### SVM
- `kernel`: Kernel type (default: 'rbf')
- `C`: Regularization parameter (default: 1.0)

### Gradient Boosting
- `n_estimators`: Number of boosting stages (default: 100)
- `max_depth`: Maximum tree depth (default: 3)

## Notes

- All uploaded files are stored in the `uploads/` directory
- Trained models are saved in the `models/` directory
- The API supports CORS for frontend integration
- Maximum file upload size is 16MB

## License

See LICENSE file for details.

