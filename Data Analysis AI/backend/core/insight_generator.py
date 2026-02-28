import pandas as pd
from typing import List, Dict, Any

def generate_suggested_prompts(metadata: Dict[str, Any]) -> List[str]:
    """
    Opportunity Detection Engine:
    Analyzes the dataset profile and generates beginner-friendly, guided 
    action prompts to help the user understand, clean, and analyze their data.
    """
    prompts = []
    cols = metadata.get("columns", {})
    overview = metadata.get("overview", {})
    
    numeric_cols = []
    categorical_cols = []
    date_cols = []
    
    for c, p in cols.items():
        dtype_str = p.get("dtype", "").lower()
        if "datetime" in dtype_str:
            date_cols.append(c)
        elif "numeric" in dtype_str or "int" in dtype_str or "float" in dtype_str:
            numeric_cols.append(c)
        elif "object" in dtype_str or "category" in dtype_str:
            categorical_cols.append(c)
            
    # Always offer structural understanding first
    prompts.append("Understand the structure of this dataset")
    
    # Missing values check -> Clean Data opportunity
    if overview.get("missing_cells", 0) > 0:
        prompts.append("Clean missing values in the data")
        
    # Date column -> Trend analysis opportunity
    if date_cols and numeric_cols:
        prompts.append(f"Analyze the trend of {numeric_cols[0]} over time")
        
    # Categorical + Numeric -> Grouped comparison opportunity
    if categorical_cols and numeric_cols:
        prompts.append(f"Compare {numeric_cols[0]} grouped by {categorical_cols[0]}")
        
    # Multiple Numeric -> Correlation / Relationship opportunity
    if len(numeric_cols) >= 2:
        prompts.append("Explore relationships between numeric columns")
        
    # Just numeric -> Distribution opportunity
    elif len(numeric_cols) == 1:
        prompts.append(f"Show the distribution of {numeric_cols[0]}")
        
    # Always offer an automated insight option
    prompts.append("Find interesting insights automatically")
        
    # Return top 5 most relevant unique prompts to avoid overwhelming the user
    unique_prompts = list(dict.fromkeys(prompts))
    return unique_prompts[:5]
