from typing import Dict, Any
from .base_agent import BaseAgent

import re

class DataAnalysisAgent(BaseAgent):
    """
    Generates code for statistical analysis and calculations.
    """
    async def process(self, prompt: str, dataset_metadata: Dict[str, Any], provider: str = None, model: str = None) -> Dict[str, Any]:
        system_prompt = f"""
        You are a Data Scientist / Analyst. 
        Generate Python code using pandas to calculate metrics or perform analysis based on the user request.
        
        Rules:
        1. Access the dataset as `df`.
        2. Save the final result to a variable named `result`.
        3. If the result is a number, string, or small dictionary, just assign it.
        4. If the result is a table, assign the relevant DataFrame/Series to `result`.
        5. Do NOT import libraries.
        6. Return ONLY the code block.
        7. **Robust Date Parsing**: If converting strings to dates, ALWAYS use `pd.to_datetime(..., errors='coerce', dayfirst=True)` or `pd.to_datetime(..., format='mixed')` to avoid common parsing errors like "day out of range".
        
        Dataset Metadata:
        {dataset_metadata.get('columns', {})}
        """
        
        user_prompt = f"User Request: {prompt}"
        code = await self.get_completion(system_prompt, user_prompt, provider=provider, model=model)
        
        match = re.search(r"```(?:python)?\s*(.*?)\s*```", code, re.DOTALL | re.IGNORECASE)
        if match:
            code = match.group(1).strip()
        else:
            code = code.strip()
        
        return {"type": "analysis", "code": code}
