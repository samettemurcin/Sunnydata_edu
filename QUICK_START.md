# 🚀 Quick Start Guide

## Your servers are now running!

### ✅ Backend API Server
- **URL:** http://localhost:5001
- **Status:** Running
- **API Docs:** http://localhost:5001/api/status

**Note:** Port 5000 is often used by Apple AirPlay on macOS, so we use port 5001 instead.

### ✅ Frontend Web App
- **URL:** http://localhost:8000
- **Status:** Running
- **Open in browser:** http://localhost:8000

## 🎯 How to Use

1. **Open your browser** and go to: **http://localhost:8000**

2. **Upload your data:**
   - Click on "📤 Upload Data" tab
   - Click "Choose File" and select your CSV/Excel file
   - Click "Upload File"

3. **Clean your data (optional):**
   - Go to "🧹 Clean Data" tab
   - Adjust cleaning options
   - Click "Clean Data"

4. **Train a model:**
   - Go to "🎯 Train Models" tab
   - Select target column
   - Select features
   - Choose model type
   - Click "Train Model"

5. **Compare multiple models:**
   - In "Train Models" tab
   - Select multiple models to compare
   - Click "Train & Compare Models"

6. **Make predictions:**
   - Go to "🔮 Predictions" tab
   - Select a trained model
   - Enter feature values
   - Click "Predict"

7. **View all models:**
   - Go to "📊 Models" tab
   - See all trained models and their performance

## 🛑 To Stop Servers

Press `Ctrl+C` in the terminal where the servers are running, or:

```bash
# Kill backend (port 5000)
lsof -ti:5000 | xargs kill

# Kill frontend (port 8000)
lsof -ti:8000 | xargs kill
```

## 🔄 To Restart

### Backend:
```bash
cd /Users/samettemurcin/Desktop/Sunnydata_edu
source venv/bin/activate
python app.py
```

### Frontend:
```bash
cd /Users/samettemurcin/Desktop/Sunnydata_edu/frontend
python3 -m http.server 8000
```

Or use the start scripts:
```bash
./start.sh          # Backend
./start_frontend.sh  # Frontend
```

## 📝 Notes

- The frontend connects to the backend API automatically
- Make sure both servers are running
- If you see "Disconnected" status, check that the backend is running on port 5000
- All uploaded files are saved in the `uploads/` directory
- All trained models are saved in the `models/` directory

## 🎨 Features

- ✅ File upload (CSV/Excel)
- ✅ Data preview
- ✅ Data cleaning
- ✅ Multiple ML models
- ✅ Model comparison
- ✅ Predictions
- ✅ Model management
- ✅ Beautiful Tailwind CSS UI

Enjoy your ML Model Customization Dashboard! 🎉

