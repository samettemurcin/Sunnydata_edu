# API Documentation

Complete API reference for the ML Model Customization Web App backend.

## Base URL
```
http://localhost:5001/api
```

**Note:** Port 5000 is often used by Apple AirPlay on macOS, so the backend runs on port 5001 by default.

## Authentication
Currently, the API does not require authentication. For production, implement authentication middleware.

---

## Endpoints

### Health & Status

#### GET `/api/health`
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-12-01T12:00:00"
}
```

#### GET `/api/status`
Get API status and available features.

**Response:**
```json
{
  "status": "running",
  "version": "1.0.0",
  "features": [
    "Data upload and preprocessing",
    "Multiple ML model training",
    "Model comparison",
    "Predictions (single and batch)",
    "Feature importance",
    "Data visualization",
    "Customizable hyperparameters"
  ]
}
```

---

### Data Management

#### POST `/api/upload`
Upload a CSV or Excel file.

**Request:**
- Content-Type: `multipart/form-data`
- Body: `file` (file)

**Response:**
```json
{
  "success": true,
  "message": "File uploaded successfully",
  "filename": "data.csv",
  "data_info": {
    "shape": {"rows": 111, "cols": 12},
    "columns": ["student_id", "MOC", ...],
    "dtypes": {...},
    "missing_values": {...},
    "missing_percentage": {...},
    "numerical_columns": [...],
    "categorical_columns": [...]
  }
}
```

#### POST `/api/data/preview`
Preview uploaded data (first 10 rows).

**Request:**
```json
{
  "filename": "data.csv"
}
```

**Response:**
```json
{
  "success": true,
  "preview": [
    {"student_id": 1024, "MOC": 1.1, ...},
    ...
  ],
  "columns": ["student_id", "MOC", ...],
  "shape": {"rows": 111, "cols": 12}
}
```

#### POST `/api/data/clean`
Clean and preprocess data.

**Request:**
```json
{
  "filename": "data.csv",
  "cleaning_options": {
    "missing_threshold": 50,
    "imputation_strategy": "median",
    "remove_duplicates": true,
    "handle_outliers": false,
    "outlier_method": "iqr",
    "outlier_action": "remove"
  }
}
```

**Cleaning Options:**
- `missing_threshold` (int): Drop columns with >X% missing values (default: 50)
- `imputation_strategy` (string): "median", "mean", "mode", or "drop" (default: "median")
- `remove_duplicates` (boolean): Remove duplicate rows (default: false)
- `handle_outliers` (boolean): Handle outliers (default: false)
- `outlier_method` (string): "iqr" or "zscore" (default: "iqr")
- `outlier_action` (string): "remove" or "cap" (default: "remove")

**Response:**
```json
{
  "success": true,
  "cleaned_filename": "cleaned_data.csv",
  "cleaning_report": {
    "original_shape": [111, 12],
    "cleaned_shape": [111, 12],
    "rows_removed": 0,
    "columns_removed": 1,
    "missing_values_before": 98,
    "missing_values_after": 0,
    "cleaning_steps": [...]
  },
  "shape": {"rows": 111, "cols": 11}
}
```

#### POST `/api/data/analysis`
Get comprehensive data analysis.

**Request:**
```json
{
  "filename": "data.csv"
}
```

**Response:**
```json
{
  "success": true,
  "analysis": {
    "basic_info": {...},
    "statistics": {...},
    "correlations": {...},
    "strong_correlations": [
      {
        "col1": "rc_score",
        "col2": "rc_percentile",
        "correlation": 0.938
      }
    ],
    "outliers": {...},
    "categorical": {...}
  }
}
```

---

### Model Training

#### POST `/api/models/train`
Train a single ML model.

**Request:**
```json
{
  "filename": "cleaned_data.csv",
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

**Available Model Types:**
- `logistic_regression`
- `decision_tree`
- `random_forest`
- `knn`
- `svm`
- `gradient_boosting`
- `naive_bayes`

**Model-Specific Config:**
- **Logistic Regression:**
  - `max_iter` (int, default: 1000)
  - `C` (float, default: 1.0)

- **Decision Tree:**
  - `max_depth` (int, default: 5)
  - `min_samples_split` (int, default: 2)

- **Random Forest:**
  - `n_estimators` (int, default: 100)
  - `max_depth` (int, default: 5)
  - `min_samples_split` (int, default: 2)

- **KNN:**
  - `n_neighbors` (int, default: 5)
  - `weights` (string, default: "uniform")

- **SVM:**
  - `kernel` (string, default: "rbf")
  - `C` (float, default: 1.0)

- **Gradient Boosting:**
  - `n_estimators` (int, default: 100)
  - `max_depth` (int, default: 3)

**Response:**
```json
{
  "success": true,
  "result": {
    "model_id": "random_forest_20241201_120000",
    "model_type": "random_forest",
    "accuracy": 0.9130,
    "metrics": {
      "accuracy": 0.9130,
      "precision": 0.9150,
      "recall": 0.9130,
      "f1_score": 0.9120
    },
    "classification_report": {...},
    "confusion_matrix": [[...], [...]],
    "feature_importance": {
      "rc_score": 0.45,
      "composite_percentile": 0.30,
      ...
    },
    "train_size": 88,
    "test_size": 23
  }
}
```

#### POST `/api/models/train-multiple`
Train multiple models and compare.

**Request:**
```json
{
  "filename": "cleaned_data.csv",
  "target_column": "performance_category",
  "feature_selection": ["MOC", "vocab_score", "rc_score"],
  "models": ["random_forest", "decision_tree", "logistic_regression", "knn"]
}
```

**Response:**
```json
{
  "success": true,
  "results": {
    "results": [
      {
        "model_id": "random_forest_20241201_120000",
        "model_type": "random_forest",
        "accuracy": 0.9130,
        ...
      },
      ...
    ],
    "best_model": {
      "model_id": "random_forest_20241201_120000",
      "model_type": "random_forest",
      "accuracy": 0.9130,
      ...
    },
    "comparison": {
      "models": ["random_forest", "decision_tree", ...],
      "accuracies": [0.9130, 0.7391, ...]
    }
  }
}
```

#### GET `/api/models/list`
List all trained models.

**Response:**
```json
{
  "success": true,
  "models": [
    {
      "model_id": "random_forest_20241201_120000",
      "model_type": "random_forest",
      "accuracy": 0.9130,
      "created_at": "2024-12-01T12:00:00"
    },
    ...
  ]
}
```

#### GET `/api/models/<model_id>/info`
Get information about a trained model.

**Response:**
```json
{
  "success": true,
  "model_info": {
    "model_type": "random_forest",
    "feature_columns": ["MOC", "vocab_score", ...],
    "target_column": "performance_category",
    "created_at": "2024-12-01T12:00:00"
  }
}
```

#### GET `/api/models/<model_id>/feature-importance`
Get feature importance for a model.

**Response:**
```json
{
  "success": true,
  "feature_importance": {
    "rc_score": 0.45,
    "composite_percentile": 0.30,
    "vocab_score": 0.15,
    "MOC": 0.10
  }
}
```

---

### Predictions

#### POST `/api/predict`
Make a single prediction.

**Request:**
```json
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

**Response:**
```json
{
  "success": true,
  "prediction": {
    "prediction": "High",
    "prediction_raw": 2,
    "probabilities": [0.1, 0.2, 0.7]
  }
}
```

#### POST `/api/predict/batch`
Make batch predictions.

**Request:**
```json
{
  "model_id": "random_forest_20241201_120000",
  "filename": "test_data.csv"
}
```

**Response:**
```json
{
  "success": true,
  "predictions": {
    "predictions": ["High", "Medium", "Low", ...],
    "count": 23,
    "probabilities": [[...], [...], ...]
  }
}
```

---

### Visualizations

#### POST `/api/visualize/correlation`
Get correlation matrix.

**Request:**
```json
{
  "filename": "data.csv"
}
```

**Response:**
```json
{
  "success": true,
  "correlation_matrix": {
    "rc_score": {
      "rc_percentile": 0.938,
      "composite_percentile": 0.712,
      ...
    },
    ...
  },
  "columns": ["rc_score", "rc_percentile", ...]
}
```

#### POST `/api/visualize/distribution`
Get distribution statistics.

**Request:**
```json
{
  "filename": "data.csv",
  "columns": ["rc_score", "vocab_score", "MOC"]
}
```

**Response:**
```json
{
  "success": true,
  "distributions": {
    "rc_score": {
      "mean": 0.503,
      "median": 0.500,
      "std": 0.171,
      "min": 0.170,
      "max": 0.880,
      "q25": 0.380,
      "q75": 0.630
    },
    ...
  }
}
```

---

## Error Responses

All endpoints may return error responses in the following format:

```json
{
  "error": "Error message description"
}
```

**Common HTTP Status Codes:**
- `200` - Success
- `400` - Bad Request (missing/invalid parameters)
- `500` - Internal Server Error

---

## Example Frontend Integration (JavaScript/React)

```javascript
// Upload file
const uploadFile = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await fetch('http://localhost:5000/api/upload', {
    method: 'POST',
    body: formData
  });
  
  return await response.json();
};

// Train model
const trainModel = async (filename, targetColumn, features, modelConfig) => {
  const response = await fetch('http://localhost:5000/api/models/train', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      filename,
      target_column: targetColumn,
      feature_selection: features,
      model_config: modelConfig
    })
  });
  
  return await response.json();
};

// Make prediction
const makePrediction = async (modelId, inputData) => {
  const response = await fetch('http://localhost:5000/api/predict', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      model_id: modelId,
      input_data: inputData
    })
  });
  
  return await response.json();
};
```

---

## Notes

- All timestamps are in ISO 8601 format
- File uploads are limited to 16MB
- Models are saved as `.pkl` files in the `models/` directory
- All endpoints support CORS for frontend integration

