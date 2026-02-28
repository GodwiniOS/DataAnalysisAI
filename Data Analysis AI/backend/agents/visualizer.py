from typing import Dict, Any
from .base_agent import BaseAgent
import json

class VisualizationAgent(BaseAgent):
    """
    Decides on the correct chart and returns Plotly JSON config.
    """
    async def process(self, prompt: str, dataset_metadata: Dict[str, Any], provider: str = None, model: str = None) -> Dict[str, Any]:
        system_prompt = f"""
        You are a Data Visualization expert. 
        Your task is to return a `react-google-charts` JSON configuration for a chart that answers the user's request.
        
        Rules:
        1. Choose the best chartType (e.g., "ScatterChart", "BarChart", "LineChart", "PieChart", "Histogram", "ColumnChart").
        2. Reference column names from the metadata.
        3. The `data` array MUST be an array of arrays. The first array must be the header row with column names (strings). The second array must contain placeholders like "$COL_NAME" corresponding to the columns we need to extract from the dataframe.
        4. Return ONLY a valid JSON object with 'chartType', 'data', and 'options' keys.
        
        Example Output Format:
        {{
            "chartType": "ScatterChart",
            "data": [
                ["Age", "Weight"],
                ["$Age_Column", "$Weight_Column"]
            ],
            "options": {{
                "title": "Age vs. Weight",
                "hAxis": {{ "title": "Age" }},
                "vAxis": {{ "title": "Weight" }}
            }}
        }}

        Dataset Metadata:
        {dataset_metadata.get('columns', {})}
        """
        
        user_prompt = f"User Request: {prompt}"
        response = await self.get_completion(system_prompt, user_prompt, provider=provider, model=model)
        
        import re
        try:
            # Try to parse as JSON
            match = re.search(r"```(?:json)?\s*(.*?)\s*```", response, re.DOTALL | re.IGNORECASE)
            if match:
                response = match.group(1).strip()
            else:
                response = response.strip()
            chart_config = json.loads(response)
        except:
            chart_config = {"error": "Failed to generate chart config", "raw": response}
            
        return {"type": "visualization", "chart": chart_config}
