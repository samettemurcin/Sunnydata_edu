# Frontend Integration Guide

This guide helps you integrate the ML Model Customization API with your Tailwind CSS frontend.

## Setup

### 1. API Base URL
```javascript
const API_BASE_URL = 'http://localhost:5000/api';
```

### 2. API Service Class

Create an API service to handle all API calls:

```javascript
// apiService.js
class APIService {
  constructor(baseURL = 'http://localhost:5000/api') {
    this.baseURL = baseURL;
  }

  async uploadFile(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await fetch(`${this.baseURL}/upload`, {
      method: 'POST',
      body: formData
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Upload failed');
    }
    
    return await response.json();
  }

  async previewData(filename) {
    const response = await fetch(`${this.baseURL}/data/preview`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ filename })
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Preview failed');
    }
    
    return await response.json();
  }

  async cleanData(filename, cleaningOptions = {}) {
    const response = await fetch(`${this.baseURL}/data/clean`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ filename, cleaning_options: cleaningOptions })
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Cleaning failed');
    }
    
    return await response.json();
  }

  async analyzeData(filename) {
    const response = await fetch(`${this.baseURL}/data/analysis`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ filename })
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Analysis failed');
    }
    
    return await response.json();
  }

  async trainModel(filename, targetColumn, featureSelection, modelConfig) {
    const response = await fetch(`${this.baseURL}/models/train`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        filename,
        target_column: targetColumn,
        feature_selection: featureSelection,
        model_config: modelConfig
      })
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Training failed');
    }
    
    return await response.json();
  }

  async trainMultipleModels(filename, targetColumn, featureSelection, models = ['all']) {
    const response = await fetch(`${this.baseURL}/models/train-multiple`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        filename,
        target_column: targetColumn,
        feature_selection: featureSelection,
        models
      })
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Training failed');
    }
    
    return await response.json();
  }

  async listModels() {
    const response = await fetch(`${this.baseURL}/models/list`);
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Failed to list models');
    }
    
    return await response.json();
  }

  async getModelInfo(modelId) {
    const response = await fetch(`${this.baseURL}/models/${modelId}/info`);
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Failed to get model info');
    }
    
    return await response.json();
  }

  async getFeatureImportance(modelId) {
    const response = await fetch(`${this.baseURL}/models/${modelId}/feature-importance`);
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Failed to get feature importance');
    }
    
    return await response.json();
  }

  async predict(modelId, inputData) {
    const response = await fetch(`${this.baseURL}/predict`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ model_id: modelId, input_data: inputData })
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Prediction failed');
    }
    
    return await response.json();
  }

  async predictBatch(modelId, filename) {
    const response = await fetch(`${this.baseURL}/predict/batch`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ model_id: modelId, filename })
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Batch prediction failed');
    }
    
    return await response.json();
  }

  async getCorrelationMatrix(filename) {
    const response = await fetch(`${this.baseURL}/visualize/correlation`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ filename })
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Failed to get correlation');
    }
    
    return await response.json();
  }

  async getDistribution(filename, columns) {
    const response = await fetch(`${this.baseURL}/visualize/distribution`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ filename, columns })
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Failed to get distribution');
    }
    
    return await response.json();
  }
}

export default new APIService();
```

## React Component Examples

### File Upload Component

```jsx
import { useState } from 'react';
import apiService from './apiService';

function FileUpload({ onUploadSuccess }) {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setError(null);
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file');
      return;
    }

    setUploading(true);
    setError(null);

    try {
      const result = await apiService.uploadFile(file);
      onUploadSuccess(result);
    } catch (err) {
      setError(err.message);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="p-6 bg-white rounded-lg shadow-md">
      <h2 className="text-2xl font-bold mb-4">Upload Data</h2>
      
      <div className="mb-4">
        <input
          type="file"
          accept=".csv,.xlsx,.xls"
          onChange={handleFileChange}
          className="block w-full text-sm text-gray-500
            file:mr-4 file:py-2 file:px-4
            file:rounded-full file:border-0
            file:text-sm file:font-semibold
            file:bg-blue-50 file:text-blue-700
            hover:file:bg-blue-100"
        />
      </div>

      {error && (
        <div className="mb-4 p-3 bg-red-100 text-red-700 rounded">
          {error}
        </div>
      )}

      <button
        onClick={handleUpload}
        disabled={uploading || !file}
        className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {uploading ? 'Uploading...' : 'Upload'}
      </button>
    </div>
  );
}

export default FileUpload;
```

### Model Training Component

```jsx
import { useState } from 'react';
import apiService from './apiService';

function ModelTraining({ filename, columns }) {
  const [targetColumn, setTargetColumn] = useState('');
  const [selectedFeatures, setSelectedFeatures] = useState([]);
  const [modelType, setModelType] = useState('random_forest');
  const [training, setTraining] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleFeatureToggle = (feature) => {
    setSelectedFeatures(prev =>
      prev.includes(feature)
        ? prev.filter(f => f !== feature)
        : [...prev, feature]
    );
  };

  const handleTrain = async () => {
    if (!targetColumn || selectedFeatures.length === 0) {
      setError('Please select target column and features');
      return;
    }

    setTraining(true);
    setError(null);

    try {
      const modelConfig = {
        model_type: modelType,
        n_estimators: 100,
        max_depth: 5,
        test_size: 0.2
      };

      const response = await apiService.trainModel(
        filename,
        targetColumn,
        selectedFeatures,
        modelConfig
      );

      setResult(response.result);
    } catch (err) {
      setError(err.message);
    } finally {
      setTraining(false);
    }
  };

  return (
    <div className="p-6 bg-white rounded-lg shadow-md">
      <h2 className="text-2xl font-bold mb-4">Train Model</h2>

      {/* Target Column Selection */}
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Target Column
        </label>
        <select
          value={targetColumn}
          onChange={(e) => setTargetColumn(e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-md"
        >
          <option value="">Select target column</option>
          {columns.map(col => (
            <option key={col} value={col}>{col}</option>
          ))}
        </select>
      </div>

      {/* Feature Selection */}
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Features
        </label>
        <div className="space-y-2">
          {columns.filter(col => col !== targetColumn).map(col => (
            <label key={col} className="flex items-center">
              <input
                type="checkbox"
                checked={selectedFeatures.includes(col)}
                onChange={() => handleFeatureToggle(col)}
                className="mr-2"
              />
              {col}
            </label>
          ))}
        </div>
      </div>

      {/* Model Type Selection */}
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Model Type
        </label>
        <select
          value={modelType}
          onChange={(e) => setModelType(e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-md"
        >
          <option value="random_forest">Random Forest</option>
          <option value="decision_tree">Decision Tree</option>
          <option value="logistic_regression">Logistic Regression</option>
          <option value="knn">K-Nearest Neighbors</option>
          <option value="svm">Support Vector Machine</option>
          <option value="gradient_boosting">Gradient Boosting</option>
        </select>
      </div>

      {error && (
        <div className="mb-4 p-3 bg-red-100 text-red-700 rounded">
          {error}
        </div>
      )}

      <button
        onClick={handleTrain}
        disabled={training}
        className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50"
      >
        {training ? 'Training...' : 'Train Model'}
      </button>

      {result && (
        <div className="mt-4 p-4 bg-green-50 rounded">
          <h3 className="font-bold text-lg mb-2">Training Results</h3>
          <p>Model ID: {result.model_id}</p>
          <p>Accuracy: {(result.accuracy * 100).toFixed(2)}%</p>
          <p>Precision: {(result.metrics.precision * 100).toFixed(2)}%</p>
          <p>Recall: {(result.metrics.recall * 100).toFixed(2)}%</p>
          <p>F1 Score: {(result.metrics.f1_score * 100).toFixed(2)}%</p>
        </div>
      )}
    </div>
  );
}

export default ModelTraining;
```

### Prediction Component

```jsx
import { useState } from 'react';
import apiService from './apiService';

function Prediction({ modelId, featureColumns }) {
  const [inputData, setInputData] = useState({});
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleInputChange = (feature, value) => {
    setInputData(prev => ({
      ...prev,
      [feature]: parseFloat(value) || value
    }));
  };

  const handlePredict = async () => {
    if (Object.keys(inputData).length !== featureColumns.length) {
      setError('Please fill all feature values');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await apiService.predict(modelId, inputData);
      setPrediction(response.prediction);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 bg-white rounded-lg shadow-md">
      <h2 className="text-2xl font-bold mb-4">Make Prediction</h2>

      <div className="space-y-4 mb-4">
        {featureColumns.map(feature => (
          <div key={feature}>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {feature}
            </label>
            <input
              type="number"
              step="any"
              value={inputData[feature] || ''}
              onChange={(e) => handleInputChange(feature, e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
            />
          </div>
        ))}
      </div>

      {error && (
        <div className="mb-4 p-3 bg-red-100 text-red-700 rounded">
          {error}
        </div>
      )}

      <button
        onClick={handlePredict}
        disabled={loading}
        className="px-4 py-2 bg-purple-600 text-white rounded hover:bg-purple-700 disabled:opacity-50"
      >
        {loading ? 'Predicting...' : 'Predict'}
      </button>

      {prediction && (
        <div className="mt-4 p-4 bg-purple-50 rounded">
          <h3 className="font-bold text-lg mb-2">Prediction</h3>
          <p className="text-2xl font-bold text-purple-700">
            {prediction.prediction}
          </p>
          {prediction.probabilities && (
            <div className="mt-2">
              <p className="text-sm text-gray-600">Probabilities:</p>
              <ul className="list-disc list-inside">
                {prediction.probabilities.map((prob, idx) => (
                  <li key={idx}>Class {idx}: {(prob * 100).toFixed(2)}%</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default Prediction;
```

## Tailwind CSS Styling Tips

1. **Use Tailwind's utility classes** for consistent styling
2. **Create reusable components** for common UI patterns
3. **Use Tailwind's color palette** for status indicators (green for success, red for errors, blue for info)
4. **Implement loading states** with Tailwind's opacity and cursor utilities
5. **Use Tailwind's spacing scale** for consistent margins and padding

## Error Handling

Always wrap API calls in try-catch blocks and display user-friendly error messages:

```javascript
try {
  const result = await apiService.someMethod();
  // Handle success
} catch (error) {
  // Display error to user
  console.error('API Error:', error.message);
  // Show error notification
}
```

## Loading States

Implement loading states for better UX:

```jsx
const [loading, setLoading] = useState(false);

// In your component
{loading && (
  <div className="flex items-center justify-center">
    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
  </div>
)}
```

This guide provides a solid foundation for building your frontend. Customize the components and styling to match your design requirements!

