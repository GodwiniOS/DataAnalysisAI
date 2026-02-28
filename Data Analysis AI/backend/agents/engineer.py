from typing import Dict, Any
from .base_agent import BaseAgent

import re

class DataEngineeringAgent(BaseAgent):
    """
    Generates Pandas code for data engineering tasks.
    """
    async def process(self, prompt: str, dataset_metadata: Dict[str, Any], provider: str = None, model: str = None) -> Dict[str, Any]:
        system_prompt = f"""
        You are a Data Engineering expert. 
        Your task is to generate Python code using the pandas library to fulfill the user's data transformation request.
        
        Rules:
        1. Access the dataset using the variable `df`.
        2. Assign the modified dataset back to `df`.
        3. Do NOT import libraries (pandas as pd and numpy as np are pre-imported).
        4. Focus ONLY on data transformation (cleaning, renaming, filtering, new columns, etc.).
        5. Return ONLY the code block, no markdown formatting or extra text.
        6. **Robust Date Parsing**: If converting strings to dates, ALWAYS use `pd.to_datetime(..., errors='coerce', dayfirst=True)` or `pd.to_datetime(..., format='mixed')` to avoid parsing errors.
        7. If the task is impossible, return "Error: <reason>".
        
        Dataset Metadata:
        {dataset_metadata.get('columns', {})}
        """
        
        user_prompt = f"User Request: {prompt}"
        code = await self.get_completion(system_prompt, user_prompt, provider=provider, model=model)
        
        # Clean the response if it contains markdown code blocks
        match = re.search(r"```(?:python)?\s*(.*?)\s*```", code, re.DOTALL | re.IGNORECASE)
        if match:
            code = match.group(1).strip()
        else:
            code = code.strip()
            
        return {"type": "engineering", "code": code}
