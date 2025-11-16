// API Configuration
const API_BASE_URL = 'http://localhost:5001/api';

// Global state
let currentFilename = null;
let currentColumns = [];
let currentModels = [];
let connectionCheckInterval = null;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    checkAPIStatus();
    // Check every 5 seconds
    connectionCheckInterval = setInterval(checkAPIStatus, 5000);
    
    // Auto-load models on models tab
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const tabName = this.textContent.toLowerCase().includes('models') ? 'models' : 
                          this.textContent.toLowerCase().includes('predict') ? 'predict' : null;
            if (tabName === 'models') {
                setTimeout(loadModels, 100);
            }
        });
    });
});

// API Status Check with better error handling
async function checkAPIStatus() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`, {
            method: 'GET',
            headers: {
                'Accept': 'application/json',
            },
            // Add timeout
            signal: AbortSignal.timeout(3000)
        });
        
        if (response.ok) {
            const data = await response.json();
            updateStatusUI(true, 'Connected');
        } else {
            updateStatusUI(false, 'Error');
        }
    } catch (error) {
        if (error.name === 'TimeoutError' || error.name === 'TypeError') {
            updateStatusUI(false, 'Disconnected');
        } else {
            updateStatusUI(false, 'Error');
        }
    }
}

// Update Status UI
function updateStatusUI(connected, text) {
    const indicator = document.getElementById('statusIndicator');
    const statusText = document.getElementById('apiStatusText');
    const badge = document.getElementById('apiStatusBadge');
    
    if (!indicator || !statusText || !badge) return; // Safety check
    
    if (connected) {
        indicator.className = 'w-3 h-3 rounded-full bg-green-500';
        statusText.textContent = '✓ ' + text;
        badge.className = 'glass-effect rounded-full px-6 py-3 flex items-center gap-2';
    } else {
        indicator.className = 'w-3 h-3 rounded-full bg-red-500 pulse-animation';
        statusText.textContent = '✗ ' + text;
        badge.className = 'glass-effect rounded-full px-6 py-3 flex items-center gap-2';
    }
}

// Show/Hide Banner
function showBanner(title, text, type = 'info') {
    const banner = document.getElementById('infoBanner');
    const titleEl = document.getElementById('infoBannerTitle');
    const textEl = document.getElementById('infoBannerText');
    
    if (!banner || !titleEl || !textEl) return; // Safety check
    
    const colors = {
        info: 'bg-blue-50 border-blue-200 text-blue-800',
        success: 'bg-green-50 border-green-200 text-green-800',
        error: 'bg-red-50 border-red-200 text-red-800',
        warning: 'bg-yellow-50 border-yellow-200 text-yellow-800'
    };
    
    banner.className = `mb-6 rounded-xl p-4 shadow-lg border-2 ${colors[type]} ${colors[type]}`;
    titleEl.textContent = title;
    textEl.textContent = text;
    banner.classList.remove('hidden');
}

function hideBanner() {
    const banner = document.getElementById('infoBanner');
    if (banner) banner.classList.add('hidden');
}

// Tab Navigation
function showTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.add('hidden');
    });
    
    // Remove active class from all buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('tab-active', 'text-white');
        btn.classList.add('text-gray-600');
    });
    
    // Show selected tab
    document.getElementById(`${tabName}Tab`).classList.remove('hidden');
    
    // Add active class to clicked button
    event.target.classList.remove('text-gray-600');
    event.target.classList.add('tab-active', 'text-white');
    
    // Load data if needed
    if (tabName === 'models') {
        loadModels();
    } else if (tabName === 'predict') {
        loadModels(); // Load models for prediction dropdown
    }
}

// File Selection
function handleFileSelect(event) {
    const file = event.target.files[0];
    if (file) {
        const fileName = file.name;
        const fileNameEl = document.getElementById('fileName');
        const uploadBtn = document.getElementById('uploadBtn');
        
        if (fileNameEl) fileNameEl.innerHTML = `<i class="fas fa-file mr-2"></i>${fileName}`;
        if (uploadBtn) uploadBtn.disabled = false;
        
        // Check file size
        if (file.size > 16 * 1024 * 1024) {
            showMessage('uploadResult', 'File size exceeds 16MB limit', 'error');
            if (uploadBtn) uploadBtn.disabled = true;
        }
    }
}

// Upload File with better error handling
async function uploadFile() {
    const fileInput = document.getElementById('fileInput');
    const file = fileInput.files[0];
    
    if (!file) {
        showMessage('uploadResult', 'Please select a file', 'error');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        showMessage('uploadResult', '<div class="flex items-center gap-2"><div class="loading-spinner"></div> Uploading file...</div>', 'info');
        
        const response = await fetch(`${API_BASE_URL}/upload`, {
            method: 'POST',
            body: formData,
            // Add timeout
            signal: AbortSignal.timeout(60000) // 60 seconds
        });
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ error: 'Server error' }));
            throw new Error(errorData.error || `HTTP ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.success) {
            currentFilename = data.filename;
            currentColumns = data.data_info.columns;
            // Update file info if element exists
            const currentFileEl = document.getElementById('currentFile');
            if (currentFileEl) {
                currentFileEl.textContent = `File: ${data.filename}`;
            }
            showMessage('uploadResult', `
                <div class="bg-green-50 border-2 border-green-200 rounded-lg p-4">
                    <div class="flex items-center gap-2 text-green-800">
                        <i class="fas fa-check-circle text-xl"></i>
                        <span class="font-semibold">File uploaded successfully!</span>
                    </div>
                    <p class="text-sm text-green-700 mt-2">Rows: ${data.data_info.shape.rows}, Columns: ${data.data_info.shape.cols}</p>
                </div>
            `, 'success');
            
            // Load preview
            loadPreview();
            
            // Update train options
            updateTrainOptions();
            
            showBanner('Success', 'File uploaded successfully! You can now clean or train models.', 'success');
        } else {
            showMessage('uploadResult', data.error || 'Upload failed', 'error');
        }
    } catch (error) {
        let errorMsg = 'Upload failed';
        if (error.name === 'TimeoutError') {
            errorMsg = 'Upload timeout. Please try a smaller file or check your connection.';
        } else if (error.message.includes('Failed to fetch')) {
            errorMsg = 'Cannot connect to server. Please make sure the backend is running on port 5000.';
            updateStatusUI(false, 'Disconnected');
        } else {
            errorMsg = `Error: ${error.message}`;
        }
        showMessage('uploadResult', errorMsg, 'error');
        showBanner('Connection Error', 'Cannot connect to the API server. Please check if the backend is running.', 'error');
    }
}

// Load Preview
async function loadPreview() {
    if (!currentFilename) return;
    
    try {
        const response = await fetch(`${API_BASE_URL}/data/preview`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ filename: currentFilename }),
            signal: AbortSignal.timeout(10000)
        });
        
        if (!response.ok) throw new Error('Failed to load preview');
        
        const data = await response.json();
        
        if (data.success) {
            const previewDiv = document.getElementById('dataPreview');
            previewDiv.classList.remove('hidden');
            
            const tableDiv = document.getElementById('previewTable');
            let html = '<table class="min-w-full divide-y divide-gray-200"><thead class="bg-gradient-to-r from-purple-500 to-blue-500"><tr>';
            
            data.columns.forEach(col => {
                html += `<th class="px-4 py-3 text-left text-xs font-semibold text-white uppercase">${col}</th>`;
            });
            
            html += '</tr></thead><tbody class="bg-white divide-y divide-gray-200">';
            
            data.preview.forEach((row, idx) => {
                html += `<tr class="${idx % 2 === 0 ? 'bg-gray-50' : 'bg-white'} hover:bg-purple-50">`;
                data.columns.forEach(col => {
                    html += `<td class="px-4 py-3 text-sm text-gray-900">${row[col] ?? ''}</td>`;
                });
                html += '</tr>';
            });
            
            html += '</tbody></table>';
            tableDiv.innerHTML = html;
        }
    } catch (error) {
        console.error('Preview error:', error);
    }
}

// Update Train Options
function updateTrainOptions() {
    const targetSelect = document.getElementById('targetColumn');
    const featureDiv = document.getElementById('featureSelection');
    
    if (!targetSelect || !featureDiv) return; // Safety check
    
    // Update target column
    targetSelect.innerHTML = '<option value="">Select target column</option>';
    currentColumns.forEach(col => {
        targetSelect.innerHTML += `<option value="${col}">${col}</option>`;
    });
    
    // Update features with better UI
    featureDiv.innerHTML = '';
    currentColumns.forEach(col => {
        const label = document.createElement('label');
        label.className = 'flex items-center p-3 mb-2 bg-white rounded-lg border-2 border-gray-200 hover:border-purple-300 hover:bg-purple-50 cursor-pointer transition';
        label.innerHTML = `
            <input type="checkbox" class="feature-checkbox mr-3 w-5 h-5 text-purple-600 border-gray-300 rounded focus:ring-purple-500" value="${col}">
            <span class="text-sm font-medium text-gray-700">${col}</span>
        `;
        featureDiv.appendChild(label);
    });
}

// Clean Data
async function cleanData() {
    if (!currentFilename) {
        showMessage('cleanResult', 'Please upload a file first', 'error');
        return;
    }
    
    const cleaningOptions = {
        missing_threshold: parseInt(document.getElementById('missingThreshold').value),
        imputation_strategy: document.getElementById('imputationStrategy').value,
        remove_duplicates: document.getElementById('removeDuplicates').checked
    };
    
    try {
        showMessage('cleanResult', '<div class="flex items-center gap-2"><div class="loading-spinner"></div> Cleaning data...</div>', 'info');
        
        const response = await fetch(`${API_BASE_URL}/data/clean`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                filename: currentFilename,
                cleaning_options: cleaningOptions
            }),
            signal: AbortSignal.timeout(30000)
        });
        
        if (!response.ok) {
            let errorMessage = 'Cleaning failed';
            try {
                const errorData = await response.json();
                errorMessage = errorData.error || errorMessage;
            } catch (e) {
                // If response is not JSON, try to get text
                try {
                    const text = await response.text();
                    if (text) errorMessage = text;
                } catch (e2) {
                    errorMessage = `HTTP ${response.status}: ${response.statusText}`;
                }
            }
            throw new Error(errorMessage);
        }
        
        const data = await response.json();
        
        if (data.success) {
            currentFilename = data.cleaned_filename;
            showMessage('cleanResult', `
                <div class="bg-green-50 border-2 border-green-200 rounded-lg p-4">
                    <div class="flex items-center gap-2 text-green-800 mb-3">
                        <i class="fas fa-check-circle text-xl"></i>
                        <span class="font-semibold text-lg">Data cleaned successfully!</span>
                    </div>
                    <div class="grid grid-cols-2 gap-4 text-sm">
                        <div><strong>Rows:</strong> ${data.shape.rows}</div>
                        <div><strong>Columns:</strong> ${data.shape.cols}</div>
                        <div><strong>Rows removed:</strong> ${data.cleaning_report.rows_removed}</div>
                        <div><strong>Columns removed:</strong> ${data.cleaning_report.columns_removed}</div>
                    </div>
                </div>
            `, 'success');
            
            loadPreview();
            updateTrainOptions();
        } else {
            showMessage('cleanResult', `
                <div class="bg-red-50 border-2 border-red-200 rounded-lg p-4">
                    <div class="flex items-center gap-2 text-red-800 mb-2">
                        <i class="fas fa-exclamation-triangle text-xl"></i>
                        <span class="font-semibold">Cleaning Failed</span>
                    </div>
                    <p class="text-red-700">${data.error || 'Unknown error occurred'}</p>
                </div>
            `, 'error');
        }
    } catch (error) {
        showMessage('cleanResult', `
            <div class="bg-red-50 border-2 border-red-200 rounded-lg p-4">
                <div class="flex items-center gap-2 text-red-800 mb-2">
                    <i class="fas fa-exclamation-triangle text-xl"></i>
                    <span class="font-semibold">Error</span>
                </div>
                <p class="text-red-700">${error.message}</p>
                <p class="text-sm text-red-600 mt-2">Please check that the file exists and try again.</p>
            </div>
        `, 'error');
    }
}

// Train Model
async function trainModel() {
    if (!currentFilename) {
        showMessage('trainResult', 'Please upload a file first', 'error');
        return;
    }
    
    const targetColumn = document.getElementById('targetColumn').value;
    const modelType = document.getElementById('modelType').value;
    const selectedFeatures = Array.from(document.querySelectorAll('.feature-checkbox:checked'))
        .map(cb => cb.value);
    
    if (!targetColumn) {
        showMessage('trainResult', 'Please select a target column', 'error');
        return;
    }
    
    if (selectedFeatures.length === 0) {
        showMessage('trainResult', 'Please select at least one feature', 'error');
        return;
    }
    
    const modelConfig = {
        model_type: modelType,
        n_estimators: 100,
        max_depth: 5,
        test_size: 0.2,
        random_state: 42
    };
    
    try {
        showMessage('trainResult', '<div class="flex items-center gap-2"><div class="loading-spinner"></div> Training model... This may take a moment.</div>', 'info');
        
        const response = await fetch(`${API_BASE_URL}/models/train`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                filename: currentFilename,
                target_column: targetColumn,
                feature_selection: selectedFeatures,
                model_config: modelConfig
            }),
            signal: AbortSignal.timeout(120000) // 2 minutes
        });
        
        if (!response.ok) throw new Error('Training failed');
        
        const data = await response.json();
        
        if (data.success) {
            const result = data.result;
            showMessage('trainResult', `
                <div class="bg-gradient-to-r from-green-50 to-emerald-50 border-2 border-green-200 rounded-lg p-6">
                    <div class="flex items-center gap-3 mb-4">
                        <i class="fas fa-check-circle text-3xl text-green-600"></i>
                        <h4 class="font-bold text-2xl text-green-800">Model Trained Successfully!</h4>
                    </div>
                    <div class="grid grid-cols-2 gap-4 text-sm">
                        <div><strong>Model ID:</strong> <code class="bg-gray-100 px-2 py-1 rounded">${result.model_id}</code></div>
                        <div><strong>Model Type:</strong> ${result.model_type}</div>
                        <div class="col-span-2">
                            <div class="grid grid-cols-4 gap-4 mt-4">
                                <div class="text-center p-3 bg-white rounded-lg">
                                    <div class="text-2xl font-bold text-blue-600">${(result.accuracy * 100).toFixed(2)}%</div>
                                    <div class="text-xs text-gray-600">Accuracy</div>
                                </div>
                                <div class="text-center p-3 bg-white rounded-lg">
                                    <div class="text-2xl font-bold text-purple-600">${(result.metrics.precision * 100).toFixed(2)}%</div>
                                    <div class="text-xs text-gray-600">Precision</div>
                                </div>
                                <div class="text-center p-3 bg-white rounded-lg">
                                    <div class="text-2xl font-bold text-green-600">${(result.metrics.recall * 100).toFixed(2)}%</div>
                                    <div class="text-xs text-gray-600">Recall</div>
                                </div>
                                <div class="text-center p-3 bg-white rounded-lg">
                                    <div class="text-2xl font-bold text-orange-600">${(result.metrics.f1_score * 100).toFixed(2)}%</div>
                                    <div class="text-xs text-gray-600">F1 Score</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `, 'success');
            
            loadModels();
        } else {
            showMessage('trainResult', data.error || 'Training failed', 'error');
        }
    } catch (error) {
        showMessage('trainResult', `Error: ${error.message}`, 'error');
    }
}

// Train Multiple Models
async function trainMultipleModels() {
    if (!currentFilename) {
        showMessage('compareResult', 'Please upload a file first', 'error');
        return;
    }
    
    const targetColumn = document.getElementById('targetColumn').value;
    const selectedFeatures = Array.from(document.querySelectorAll('.feature-checkbox:checked'))
        .map(cb => cb.value);
    const selectedModels = Array.from(document.querySelectorAll('.model-checkbox:checked'))
        .map(cb => cb.value);
    
    if (!targetColumn) {
        showMessage('compareResult', 'Please select a target column', 'error');
        return;
    }
    
    if (selectedFeatures.length === 0) {
        showMessage('compareResult', 'Please select at least one feature', 'error');
        return;
    }
    
    if (selectedModels.length === 0) {
        showMessage('compareResult', 'Please select at least one model', 'error');
        return;
    }
    
    try {
        showMessage('compareResult', '<div class="flex items-center gap-2"><div class="loading-spinner"></div> Training multiple models... This may take a moment.</div>', 'info');
        
        const response = await fetch(`${API_BASE_URL}/models/train-multiple`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                filename: currentFilename,
                target_column: targetColumn,
                feature_selection: selectedFeatures,
                models: selectedModels
            }),
            signal: AbortSignal.timeout(300000) // 5 minutes
        });
        
        if (!response.ok) throw new Error('Training failed');
        
        const data = await response.json();
        
        if (data.success) {
            // Handle different response structures
            let results = [];
            let bestModel = null;
            
            if (data.results) {
                // Check if results is an object with a 'results' property or an array
                if (Array.isArray(data.results)) {
                    results = data.results;
                } else if (data.results.results && Array.isArray(data.results.results)) {
                    results = data.results.results;
                    bestModel = data.results.best_model;
                } else if (data.results.best_model) {
                    // If it's an object, extract the results array
                    bestModel = data.results.best_model;
                    // Try to find results array in the object
                    for (let key in data.results) {
                        if (Array.isArray(data.results[key])) {
                            results = data.results[key];
                            break;
                        }
                    }
                }
            }
            
            // Ensure results is an array
            if (!Array.isArray(results)) {
                results = [];
            }
            
            let html = '<div class="space-y-4">';
            html += '<h4 class="font-bold text-xl mb-4 flex items-center gap-2"><i class="fas fa-chart-bar"></i> Model Comparison Results</h4>';
            
            const sortedResults = results
                .filter(r => r && r.accuracy !== undefined && !isNaN(r.accuracy))
                .sort((a, b) => b.accuracy - a.accuracy);
            
            if (sortedResults.length === 0) {
                html += '<div class="text-center py-8 text-gray-500"><p>No successful model training results to display.</p></div>';
            } else {
                sortedResults.forEach((result, idx) => {
                    const isBest = bestModel && (result.model_id === bestModel.model_id || result === bestModel);
                html += `
                    <div class="border-2 rounded-xl p-4 ${isBest ? 'border-green-500 bg-gradient-to-r from-green-50 to-emerald-50' : 'border-gray-200 bg-white'} card-hover">
                        <div class="flex justify-between items-center">
                            <div class="flex items-center gap-3">
                                ${isBest ? '<i class="fas fa-trophy text-yellow-500 text-2xl"></i>' : ''}
                                <div>
                                    <h5 class="font-bold text-lg">${result.model_type} ${isBest ? '<span class="text-green-600">🏆 Best</span>' : ''}</h5>
                                    <p class="text-sm text-gray-600">ID: ${result.model_id}</p>
                                </div>
                            </div>
                            <div class="text-right">
                                <p class="text-3xl font-bold text-purple-600">${(result.accuracy * 100).toFixed(2)}%</p>
                                <p class="text-xs text-gray-500">Accuracy</p>
                            </div>
                        </div>
                    </div>
                `;
                });
            }
            
            html += '</div>';
            showMessage('compareResult', html, 'success');
            
            loadModels();
        } else {
            showMessage('compareResult', data.error || 'Training failed', 'error');
        }
    } catch (error) {
        showMessage('compareResult', `Error: ${error.message}`, 'error');
    }
}

// Load Models
async function loadModels() {
    try {
        const response = await fetch(`${API_BASE_URL}/models/list`, {
            signal: AbortSignal.timeout(10000)
        });
        
        if (!response.ok) throw new Error('Failed to load models');
        
        const data = await response.json();
        
        if (data.success) {
            currentModels = data.models;
            const modelsDiv = document.getElementById('modelsList');
            const predictSelect = document.getElementById('predictModelId');
            
            if (!modelsDiv || !predictSelect) return; // Safety check
            
            if (data.models.length === 0) {
                modelsDiv.innerHTML = '<div class="text-center py-12"><i class="fas fa-database text-6xl text-gray-300 mb-4"></i><p class="text-gray-500 text-lg">No models trained yet.</p></div>';
                predictSelect.innerHTML = '<option value="">No models available</option>';
            } else {
                let html = '<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">';
                predictSelect.innerHTML = '<option value="">Select a model</option>';
                
                data.models.forEach(model => {
                    html += `
                        <div class="border-2 border-gray-200 rounded-xl p-6 bg-white hover:border-purple-300 hover:shadow-lg transition card-hover">
                            <div class="flex items-center gap-3 mb-3">
                                <div class="w-10 h-10 rounded-full bg-gradient-to-r from-purple-500 to-blue-500 flex items-center justify-center">
                                    <i class="fas fa-brain text-white"></i>
                                </div>
                                <h5 class="font-bold text-lg">${model.model_type}</h5>
                            </div>
                            <p class="text-xs text-gray-500 mb-2">ID: ${model.model_id}</p>
                            ${model.accuracy !== 'unknown' ? `
                                <div class="mt-4">
                                    <div class="text-3xl font-bold text-purple-600">${(model.accuracy * 100).toFixed(2)}%</div>
                                    <div class="text-xs text-gray-500">Accuracy</div>
                                </div>
                            ` : ''}
                            <p class="text-xs text-gray-400 mt-4">${new Date(model.created_at).toLocaleString()}</p>
                        </div>
                    `;
                    
                    predictSelect.innerHTML += `<option value="${model.model_id}">${model.model_type} (${(model.accuracy !== 'unknown' ? (model.accuracy * 100).toFixed(2) + '%' : 'N/A')})</option>`;
                });
                
                html += '</div>';
                modelsDiv.innerHTML = html;
            }
            
            predictSelect.addEventListener('change', updatePredictionInputs);
        }
    } catch (error) {
        console.error('Load models error:', error);
        const modelsListEl = document.getElementById('modelsList');
        if (modelsListEl) {
            modelsListEl.innerHTML = '<div class="text-center py-12 text-red-500"><i class="fas fa-exclamation-triangle text-4xl mb-4"></i><p>Failed to load models. Please check your connection.</p></div>';
        }
    }
}

// Update Prediction Inputs
async function updatePredictionInputs() {
    const predictModelSelect = document.getElementById('predictModelId');
    if (!predictModelSelect) return;
    
    const modelId = predictModelSelect.value;
    if (!modelId) return;
    
    try {
        const response = await fetch(`${API_BASE_URL}/models/${modelId}/info`, {
            signal: AbortSignal.timeout(10000)
        });
        
        if (!response.ok) throw new Error('Failed to load model info');
        
        const data = await response.json();
        
        if (data.success) {
            const inputsDiv = document.getElementById('predictionInputs');
            if (!inputsDiv) return; // Safety check
            
            const featureColumns = data.model_info.feature_columns
                .filter(col => !col.endsWith('_encoded'))
                .map(col => col.replace('_encoded', ''));
            
            let html = '';
            featureColumns.forEach(feature => {
                html += `
                    <div>
                        <label class="block text-sm font-semibold text-gray-700 mb-2">
                            <i class="fas fa-sliders-h mr-2 text-indigo-600"></i>${feature}
                        </label>
                        <input type="number" step="any" id="pred_${feature}" class="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200" placeholder="Enter value">
                    </div>
                `;
            });
            
            inputsDiv.innerHTML = html;
        }
    } catch (error) {
        console.error('Update inputs error:', error);
    }
}

// Make Prediction
async function makePrediction() {
    const predictModelSelect = document.getElementById('predictModelId');
    if (!predictModelSelect) {
        showMessage('predictionResult', 'Prediction form not found', 'error');
        return;
    }
    
    const modelId = predictModelSelect.value;
    if (!modelId) {
        showMessage('predictionResult', 'Please select a model', 'error');
        return;
    }
    
    const inputs = document.querySelectorAll('#predictionInputs input');
    const inputData = {};
    
    inputs.forEach(input => {
        const feature = input.id.replace('pred_', '');
        const value = parseFloat(input.value);
        if (!isNaN(value)) {
            inputData[feature] = value;
        }
    });
    
    if (Object.keys(inputData).length === 0) {
        showMessage('predictionResult', 'Please enter at least one feature value', 'error');
        return;
    }
    
    try {
        showMessage('predictionResult', '<div class="flex items-center gap-2"><div class="loading-spinner"></div> Making prediction...</div>', 'info');
        
        const response = await fetch(`${API_BASE_URL}/predict`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                model_id: modelId,
                input_data: inputData
            }),
            signal: AbortSignal.timeout(30000)
        });
        
        if (!response.ok) throw new Error('Prediction failed');
        
        const data = await response.json();
        
        if (data.success) {
            const pred = data.prediction;
            let html = `
                <div class="bg-gradient-to-r from-indigo-50 to-purple-50 border-2 border-indigo-200 rounded-lg p-6">
                    <div class="flex items-center gap-3 mb-4">
                        <i class="fas fa-crystal-ball text-3xl text-indigo-600"></i>
                        <h4 class="font-bold text-2xl text-indigo-800">Prediction Result</h4>
                    </div>
                    <div class="text-center py-6">
                        <p class="text-5xl font-bold text-purple-700 mb-2">${pred.prediction}</p>
                        <p class="text-gray-600">Predicted Class</p>
                    </div>
            `;
            
            if (pred.probabilities) {
                html += '<div class="mt-6"><p class="font-semibold mb-3 text-gray-700">Probabilities:</p><div class="space-y-2">';
                pred.probabilities.forEach((prob, idx) => {
                    const percentage = (prob * 100).toFixed(2);
                    html += `
                        <div class="flex items-center gap-3">
                            <div class="flex-1 bg-gray-200 rounded-full h-4">
                                <div class="bg-gradient-to-r from-purple-500 to-indigo-500 h-4 rounded-full" style="width: ${percentage}%"></div>
                            </div>
                            <span class="text-sm font-medium text-gray-700 w-20">Class ${idx}: ${percentage}%</span>
                        </div>
                    `;
                });
                html += '</div></div>';
            }
            
            html += '</div>';
            showMessage('predictionResult', html, 'success');
        } else {
            showMessage('predictionResult', data.error || 'Prediction failed', 'error');
        }
    } catch (error) {
        showMessage('predictionResult', `Error: ${error.message}`, 'error');
    }
}

// Show Message with better styling
function showMessage(elementId, message, type) {
    const element = document.getElementById(elementId);
    if (!element) {
        console.warn(`Element with id "${elementId}" not found`);
        return; // Safety check
    }
    
    const colors = {
        success: 'bg-green-50 border-green-200 text-green-800',
        error: 'bg-red-50 border-red-200 text-red-800',
        info: 'bg-blue-50 border-blue-200 text-blue-800',
        warning: 'bg-yellow-50 border-yellow-200 text-yellow-800'
    };
    
    element.className = `p-4 rounded-lg border-2 ${colors[type] || colors.info}`;
    element.innerHTML = message;
}
