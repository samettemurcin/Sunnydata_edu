import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler
import warnings
warnings.filterwarnings('ignore')

class DataProcessor:
    def __init__(self):
        self.label_encoders = {}
        self.scaler = StandardScaler()
    
    def load_data(self, filepath):
        """Load data from CSV or Excel file"""
        if filepath.endswith('.csv'):
            df = pd.read_csv(filepath)
        elif filepath.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(filepath)
        else:
            raise ValueError("Unsupported file format")
        return df
    
    def get_data_info(self, df):
        """Get basic information about the dataset"""
        return {
            'shape': {'rows': len(df), 'cols': len(df.columns)},
            'columns': list(df.columns),
            'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()},
            'missing_values': df.isnull().sum().to_dict(),
            'missing_percentage': (df.isnull().sum() / len(df) * 100).to_dict(),
            'numerical_columns': list(df.select_dtypes(include=[np.number]).columns),
            'categorical_columns': list(df.select_dtypes(include=['object']).columns)
        }
    
    def clean_data(self, df, options=None):
        """Clean and preprocess data"""
        if options is None:
            options = {}
        
        # Validate input
        if df is None or df.empty:
            raise ValueError("DataFrame is empty or None")
        
        original_shape = df.shape
        cleaning_steps = []
        
        # Create a copy
        try:
            df_cleaned = df.copy()
        except Exception as e:
            raise ValueError(f"Failed to copy dataframe: {str(e)}")
        
        # Step 1: Drop columns with high missing percentage
        threshold = options.get('missing_threshold', 50)
        if threshold > 0 and len(df_cleaned) > 0:
            try:
                missing_percent = (df_cleaned.isnull().sum() / len(df_cleaned) * 100)
                cols_to_drop = missing_percent[missing_percent > threshold].index.tolist()
                if cols_to_drop:
                    df_cleaned = df_cleaned.drop(columns=cols_to_drop)
                    cleaning_steps.append(f"Dropped {len(cols_to_drop)} columns with >{threshold}% missing: {cols_to_drop}")
            except Exception as e:
                raise ValueError(f"Error dropping columns: {str(e)}")
        
        # Step 2: Handle remaining missing values
        imputation_strategy = options.get('imputation_strategy', 'median')  # 'median', 'mean', 'mode', 'drop'
        
        if imputation_strategy == 'drop':
            df_cleaned = df_cleaned.dropna()
            cleaning_steps.append("Dropped rows with missing values")
        else:
            # Impute numerical columns
            numerical_cols = df_cleaned.select_dtypes(include=[np.number]).columns
            for col in numerical_cols:
                if df_cleaned[col].isnull().sum() > 0:
                    try:
                        if imputation_strategy == 'median':
                            value = df_cleaned[col].median()
                        elif imputation_strategy == 'mean':
                            value = df_cleaned[col].mean()
                        else:
                            value = df_cleaned[col].median()
                        
                        # Check if value is NaN (all values are NaN)
                        if pd.isna(value):
                            value = 0  # Default to 0 if all values are NaN
                        
                        missing_count = df_cleaned[col].isnull().sum()
                        df_cleaned[col].fillna(value, inplace=True)
                        cleaning_steps.append(f"Imputed {missing_count} missing values in {col} with {imputation_strategy}: {value:.2f}")
                    except Exception as e:
                        # If imputation fails, fill with 0
                        missing_count = df_cleaned[col].isnull().sum()
                        df_cleaned[col].fillna(0, inplace=True)
                        cleaning_steps.append(f"Imputed {missing_count} missing values in {col} with 0 (fallback)")
            
            # Impute categorical columns with mode
            categorical_cols = df_cleaned.select_dtypes(include=['object']).columns
            for col in categorical_cols:
                if df_cleaned[col].isnull().sum() > 0:
                    try:
                        mode_result = df_cleaned[col].mode()
                        mode_value = mode_result[0] if not mode_result.empty else 'Unknown'
                        missing_count = df_cleaned[col].isnull().sum()
                        df_cleaned[col].fillna(mode_value, inplace=True)
                        cleaning_steps.append(f"Imputed {missing_count} missing values in {col} with mode: {mode_value}")
                    except Exception as e:
                        # If mode fails, fill with 'Unknown'
                        missing_count = df_cleaned[col].isnull().sum()
                        df_cleaned[col].fillna('Unknown', inplace=True)
                        cleaning_steps.append(f"Imputed {missing_count} missing values in {col} with 'Unknown' (fallback)")
        
        # Step 3: Remove duplicates if requested
        if options.get('remove_duplicates', False) and len(df_cleaned) > 0:
            try:
                duplicates_before = len(df_cleaned)
                df_cleaned = df_cleaned.drop_duplicates()
                duplicates_removed = duplicates_before - len(df_cleaned)
                if duplicates_removed > 0:
                    cleaning_steps.append(f"Removed {duplicates_removed} duplicate rows")
            except Exception as e:
                raise ValueError(f"Error removing duplicates: {str(e)}")
        
        # Step 4: Handle outliers if requested
        if options.get('handle_outliers', False):
            method = options.get('outlier_method', 'iqr')  # 'iqr' or 'zscore'
            numerical_cols = df_cleaned.select_dtypes(include=[np.number]).columns
            
            for col in numerical_cols:
                if method == 'iqr':
                    Q1 = df_cleaned[col].quantile(0.25)
                    Q3 = df_cleaned[col].quantile(0.75)
                    IQR = Q3 - Q1
                    lower_bound = Q1 - 1.5 * IQR
                    upper_bound = Q3 + 1.5 * IQR
                    outliers = ((df_cleaned[col] < lower_bound) | (df_cleaned[col] > upper_bound)).sum()
                else:  # zscore
                    z_scores = np.abs((df_cleaned[col] - df_cleaned[col].mean()) / df_cleaned[col].std())
                    outliers = (z_scores > 3).sum()
                
                if outliers > 0 and options.get('outlier_action') == 'remove':
                    if method == 'iqr':
                        df_cleaned = df_cleaned[(df_cleaned[col] >= lower_bound) & (df_cleaned[col] <= upper_bound)]
                    else:
                        df_cleaned = df_cleaned[z_scores <= 3]
                    cleaning_steps.append(f"Removed {outliers} outliers from {col}")
        
        # Check if dataframe became empty after cleaning
        if df_cleaned.empty:
            raise ValueError("After cleaning, the dataset is empty. Please adjust cleaning options (e.g., lower missing threshold, change imputation strategy).")
        
        # Ensure we have valid shapes
        try:
            original_rows, original_cols = original_shape
            cleaned_rows, cleaned_cols = df_cleaned.shape
            
            cleaning_report = {
                'original_shape': [int(original_rows), int(original_cols)],
                'cleaned_shape': [int(cleaned_rows), int(cleaned_cols)],
                'rows_removed': int(original_rows - cleaned_rows),
                'columns_removed': int(original_cols - cleaned_cols),
                'missing_values_before': int(df.isnull().sum().sum()),
                'missing_values_after': int(df_cleaned.isnull().sum().sum()),
                'cleaning_steps': cleaning_steps
            }
        except Exception as e:
            raise ValueError(f"Error creating cleaning report: {str(e)}")
        
        return df_cleaned, cleaning_report
    
    def analyze_data(self, df):
        """Comprehensive data analysis"""
        analysis = {
            'basic_info': self.get_data_info(df),
            'statistics': {},
            'correlations': {},
            'outliers': {}
        }
        
        # Statistical summary
        numerical_cols = df.select_dtypes(include=[np.number]).columns
        if len(numerical_cols) > 0:
            analysis['statistics'] = df[numerical_cols].describe().to_dict()
        
        # Correlation matrix
        if len(numerical_cols) > 1:
            corr_matrix = df[numerical_cols].corr()
            analysis['correlations'] = corr_matrix.to_dict()
            # Find strong correlations
            strong_corrs = []
            for i in range(len(corr_matrix.columns)):
                for j in range(i+1, len(corr_matrix.columns)):
                    corr_val = corr_matrix.iloc[i, j]
                    if abs(corr_val) > 0.7:
                        strong_corrs.append({
                            'col1': corr_matrix.columns[i],
                            'col2': corr_matrix.columns[j],
                            'correlation': float(corr_val)
                        })
            analysis['strong_correlations'] = strong_corrs
        
        # Outlier detection
        for col in numerical_cols:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)]
            
            if len(outliers) > 0:
                analysis['outliers'][col] = {
                    'count': len(outliers),
                    'percentage': len(outliers) / len(df) * 100,
                    'lower_bound': float(lower_bound),
                    'upper_bound': float(upper_bound),
                    'min': float(df[col].min()),
                    'max': float(df[col].max())
                }
        
        # Categorical analysis
        categorical_cols = df.select_dtypes(include=['object']).columns
        analysis['categorical'] = {}
        for col in categorical_cols:
            analysis['categorical'][col] = {
                'unique_count': int(df[col].nunique()),
                'value_counts': df[col].value_counts().head(10).to_dict()
            }
        
        return analysis
    
    def encode_categorical(self, df, columns=None):
        """Encode categorical variables"""
        if columns is None:
            columns = df.select_dtypes(include=['object']).columns
        
        df_encoded = df.copy()
        
        for col in columns:
            if col in df.columns and df[col].dtype == 'object':
                if col not in self.label_encoders:
                    self.label_encoders[col] = LabelEncoder()
                    df_encoded[col + '_encoded'] = self.label_encoders[col].fit_transform(df[col].astype(str))
                else:
                    df_encoded[col + '_encoded'] = self.label_encoders[col].transform(df[col].astype(str))
        
        return df_encoded
    
    def prepare_features(self, df, feature_columns, target_column=None, encode_categorical=True):
        """Prepare features for ML model"""
        df_prepared = df.copy()
        
        # Encode categorical if needed
        if encode_categorical:
            categorical_cols = [col for col in feature_columns if df[col].dtype == 'object']
            if categorical_cols:
                df_prepared = self.encode_categorical(df_prepared, categorical_cols)
                # Update feature columns to use encoded versions
                feature_columns = [col + '_encoded' if col in categorical_cols else col for col in feature_columns]
        
        # Select features
        X = df_prepared[feature_columns]
        
        # Select target if provided
        if target_column:
            if target_column in df_prepared.columns:
                y = df_prepared[target_column]
            else:
                raise ValueError(f"Target column {target_column} not found")
            return X, y
        
        return X

