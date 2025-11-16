# How to Use the Train Models Section

## Overview

The "Train Models" section has **two panels** that let you:
1. **Left Panel**: Train a single model at a time
2. **Right Panel**: Train multiple models and compare their performance

---

## 📊 Left Panel: Train Single Model

### Step-by-Step Guide

#### 1. **Select Target Column**
- **What it is**: The column you want to predict (your dependent variable)
- **How to use**: Click the dropdown and choose the column that contains the values you want to predict
- **Example**: If you want to predict student performance, select "performance_category" or "rc_percentile"
- **⚠️ Important**: This column will NOT be used as a feature (it's what you're predicting)

#### 2. **Choose Model Type**
- **What it is**: The machine learning algorithm to use
- **Available options**:
  - 🌲 **Random Forest**: Good for most problems, handles non-linear relationships
  - 🌳 **Decision Tree**: Easy to interpret, good for simple patterns
  - 📊 **Logistic Regression**: Fast, good for binary classification
  - 🔍 **K-Nearest Neighbors (KNN)**: Good for pattern recognition
  - ⚡ **Support Vector Machine (SVM)**: Good for complex boundaries
  - 🚀 **Gradient Boosting**: Often highest accuracy, but slower

#### 3. **Select Features**
- **What they are**: The columns (variables) that will help predict your target
- **How to use**: Check the boxes next to the features you want to use
- **Best practices**:
  - ✅ Select features that are related to your target
  - ✅ Don't select the target column as a feature
  - ✅ Start with 3-5 features, add more if needed
  - ✅ Avoid highly correlated features (e.g., don't use both "rc_score" and "rc_percentile" together)

#### 4. **Train the Model**
- Click the green **"Train Model"** button
- The system will:
  1. Split your data (80% training, 20% testing)
  2. Train the model on the training data
  3. Test it on the test data
  4. Show you the results

#### 5. **View Results**
After training, you'll see:
- ✅ **Model ID**: Unique identifier for this model
- ✅ **Accuracy**: Percentage of correct predictions
- ✅ **Precision**: How many positive predictions were correct
- ✅ **Recall**: How many actual positives were found
- ✅ **F1 Score**: Balance between precision and recall

---

## 📈 Right Panel: Compare Models

### Step-by-Step Guide

#### 1. **Select Models to Compare**
- Check the boxes next to the models you want to train
- **Recommended**: Start with 3-4 models (Random Forest, Decision Tree, Logistic Regression, KNN)
- Each model will be trained with the same data and features

#### 2. **Use Same Settings**
- The comparison uses:
  - Same target column (from left panel)
  - Same features (from left panel)
  - Same train/test split

#### 3. **Train & Compare**
- Click the purple **"Train & Compare Models"** button
- The system will train all selected models
- Results are sorted by accuracy (best first)
- 🏆 The best model is highlighted

#### 4. **Compare Results**
You'll see:
- Side-by-side comparison of all models
- Accuracy for each model
- Best model is marked with a trophy 🏆
- All models are saved for later use

---

## 🎯 Example Workflow

### Scenario: Predict Student Performance

1. **Upload your data** (CSV file with student data)

2. **Clean your data** (optional but recommended)
   - Remove missing values
   - Handle outliers

3. **Train Models**:
   - **Target Column**: Select "performance_category" (what you want to predict)
   - **Features**: Select "MOC", "vocab_score", "rc_score", "composite_percentile"
   - **Model Type**: Start with "Random Forest"

4. **Train Single Model**:
   - Click "Train Model"
   - See the accuracy (e.g., 91.3%)

5. **Compare Multiple Models**:
   - Check: Random Forest, Decision Tree, Logistic Regression, KNN
   - Click "Train & Compare Models"
   - See which model performs best

6. **Use the Best Model**:
   - Go to "Predictions" tab
   - Select the best model
   - Make predictions on new data

---

## 💡 Tips & Best Practices

### Choosing Target Column
- ✅ Use categorical columns for classification (e.g., "High/Medium/Low")
- ✅ Use numerical columns for regression (e.g., "rc_score")
- ❌ Don't use unique IDs (like "student_id")

### Selecting Features
- ✅ Start with 3-5 most relevant features
- ✅ Use features that logically relate to your target
- ❌ Avoid using the target column as a feature
- ❌ Don't use too many features (can cause overfitting)

### Model Selection
- **For beginners**: Start with Random Forest (usually works well)
- **For speed**: Use Logistic Regression or Decision Tree
- **For accuracy**: Try Random Forest or Gradient Boosting
- **For interpretability**: Use Decision Tree

### Understanding Results
- **Accuracy > 80%**: Good model
- **Accuracy 60-80%**: Decent, might need more features
- **Accuracy < 60%**: Poor, check your data and features

---

## ⚠️ Common Mistakes to Avoid

1. **Selecting target as feature**: Don't check the target column in features
2. **Too few features**: Need at least 2-3 relevant features
3. **Too many features**: More isn't always better (can overfit)
4. **Wrong target type**: Make sure target matches model type
5. **Not cleaning data**: Clean your data first for better results

---

## 🔄 What Happens After Training?

1. **Model is saved**: You can use it later in the "Predictions" tab
2. **Results are displayed**: See accuracy and other metrics
3. **Model appears in "Models" tab**: View all your trained models
4. **Ready for predictions**: Use it to predict on new data

---

## 📚 Next Steps

After training:
1. **Go to "Models" tab**: See all your trained models
2. **Go to "Predictions" tab**: Use your best model to make predictions
3. **Try different features**: Experiment to improve accuracy
4. **Compare more models**: Find the best one for your data

---

## 🆘 Troubleshooting

### "Please select a target column"
- Make sure you've selected a target column from the dropdown

### "Please select at least one feature"
- Check at least one feature checkbox

### "Training failed"
- Check that your data is cleaned
- Make sure target column has valid values
- Try with fewer features first

### Low accuracy
- Try different features
- Clean your data better
- Try a different model type
- Check if your target column has enough variety

---

**Ready to train?** Follow the steps above and start with a simple model first!

