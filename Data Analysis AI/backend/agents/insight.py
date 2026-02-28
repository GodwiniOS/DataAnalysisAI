import json
import re
from typing import Dict, Any
from .base_agent import BaseAgent

class InsightAgent(BaseAgent):
    """
    Acts as a Data Mentor, explaining findings and guiding the user.
    """
    async def process(self, prompt: str, dataset_metadata: Dict[str, Any], result: Any = None, provider: str = None, model: str = None) -> Dict[str, Any]:
        # Handle cases where the user just asked a general question (no action taken)
        action_context = f"Results of the action we just took: {result}" if result else "No specific action was taken. The user is asking a general question about the dataset."
        
        system_prompt = f"""
        You are an expert Data Scientist acting as a friendly, encouraging Data Mentor for a beginner user.
        Your goal is to guide the user step-by-step through exploring, cleaning, and understanding their data.
        
        Context:
        User's prompt: "{prompt}"
        {action_context}
        
        Dataset Overview:
        - Columns: {dataset_metadata.get('columns', {})}
        - Summary Stats: {dataset_metadata.get('overview', {})}
        
        You MUST respond in VALID JSON format with the following keys:
        1. "explanation": A conversational text response explaining the data or results.
           - CRITICAL: Wrap ALL column names in backticks like `column_name`.
           - CRITICAL: Wrap key metrics, numbers, or percentages in double asterisks like **11,123 rows** or **3.93**.
           - Use Markdown for structure (bullet points, bolding).
        2. "stats": A list of 2-3 key stats to highlight (e.g., total rows, columns, or missing values). 
           Format: [ {{"label": "Rows", "value": "1,000", "icon": "rows"}}, ... ]
           Valid icons: "rows", "columns", "missing", "duplicates".
        3. "next_steps": A list of 2-3 logical next step strings (interactive buttons).
           - **MANDATORY**: At least ONE of these MUST be a visualization request (e.g., "Visualize the trend of `column_name`", "Show a distribution of `column_name`").
        
        Rules for your response:
        1. **Teach, don't just tell**: Explain concepts in simple terms.
        2. **Use Structure**: Use bullet points and paragraphs to make information readable.
        3. **Highlight Key Columns**: Always wrap column names in backticks.
        4. **Highlight Metrics**: Always bold important numbers.
        5. **Always Include Visualization**: Ensure one suggestion is always about creating a chart or plot.
        6. **Be concise but warm**.
        """
        
        user_prompt = "Provide your insight in the specified JSON format. Ensure all column names use backticks and all key metrics are bolded. Use bullet points for any lists in the explanation."
        raw_res = await self.get_completion(system_prompt, user_prompt, provider=provider, model=model)
        
        try:
            # Robust extraction of content between { and }
            json_match = re.search(r'(\{.*\})', raw_res, re.DOTALL)
            if json_match:
                clean_res = json_match.group(1).strip()
                data = json.loads(clean_res)
                return {
                    "type": "insight",
                    "content": data["explanation"],
                    "stats": data.get("stats", []),
                    "options": data.get("next_steps", [])
                }
            raise ValueError("No JSON found")
        except Exception:
            # Fallback if AI fails JSON
            return {"type": "insight", "content": raw_res}
