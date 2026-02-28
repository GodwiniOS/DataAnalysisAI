import pandas as pd
import numpy as np

def profile_dataframe(df: pd.DataFrame):
    """
    Performs deep profiling of a pandas DataFrame.
    """
    total_rows = len(df)
    total_cols = len(df.columns)
    
    profile = {
        "overview": {
            "total_rows": total_rows,
            "total_columns": total_cols,
            "missing_cells": int(df.isnull().sum().sum()),
            "missing_percentage": float((df.isnull().sum().sum() / (total_rows * total_cols)) * 100) if total_rows > 0 else 0,
            "duplicate_rows": int(df.duplicated().sum()),
        },
        "columns": {}
    }
    
    for col in df.columns:
        col_data = df[col]
        dtype = str(col_data.dtype)
        unique_count = col_data.nunique()
        missing_count = int(col_data.isnull().sum())
        
        col_profile = {
            "dtype": dtype,
            "unique_values": unique_count,
            "missing_values": missing_count,
            "missing_percentage": float((missing_count / total_rows) * 100) if total_rows > 0 else 0,
        }
        
        if pd.api.types.is_numeric_dtype(col_data.dtype):
            col_profile.update({
                "mean": float(col_data.mean()) if not col_data.empty else 0,
                "median": float(col_data.median()) if not col_data.empty else 0,
                "min": float(col_data.min()) if not col_data.empty else 0,
                "max": float(col_data.max()) if not col_data.empty else 0,
                "std": float(col_data.std()) if not col_data.empty else 0,
            })
            # Histogram data (simple for now)
            try:
                counts, bins = np.histogram(col_data.dropna(), bins=10)
                col_profile["histogram"] = {
                    "counts": counts.tolist(),
                    "bins": bins.tolist()
                }
            except:
                pass
        else:
            # Categorical breakdown (top 10)
            col_profile["top_values"] = col_data.value_counts().head(10).to_dict()
            
        profile["columns"][col] = col_profile
        
    # Correlation Matrix for numeric columns
    numeric_df = df.select_dtypes(include=[np.number])
    if not numeric_df.empty:
        profile["correlation_matrix"] = numeric_df.corr().to_dict()
    
    def clean_floats(obj):
        if isinstance(obj, dict):
            return {k: clean_floats(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [clean_floats(v) for v in obj]
        elif isinstance(obj, (float, np.floating)):
            if pd.isna(obj) or np.isinf(obj):
                return None
            return float(obj)
        elif isinstance(obj, np.integer):
            return int(obj)
        return obj

    return clean_floats(profile)
