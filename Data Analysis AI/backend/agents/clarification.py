import json
from typing import Dict, Any, List
from .base_agent import BaseAgent

class ClarificationAgent(BaseAgent):
    """
    Handles ambiguous user requests by generating a multiple-choice clarifying question.
    """
    async def process(self, prompt: str, dataset_metadata: Dict[str, Any], provider: str = None, model: str = None) -> Dict[str, Any]:
        system_prompt = f"""
        You are an expert Data Mentor. The user asked a vague or very broad question.
        Instead of guessing what they want to do or writing complex code, you need to guide them down a decision tree.
        
        Rules:
        1. Keep the explanation short, warm, and helpful.
        2. Provide exactly 2 or 3 distinct options/paths they can take.
        3. Make the options **VERY concise** (maximum 4-5 words) so they fit nicely on UI buttons.
        4. ALWAYS include at least one concrete action like "Build a predictive model", "Create a Chart", "Visualize Data", or "Clean missing data" so the user can immediately enter a workflow.
        5. Format your response STRICTLY as valid JSON with two keys:
           - "message": A warm string explaining that you need to narrow down the focus.
           - "options": An array of 2-3 short string options (e.g., ["Build Predictive Model", "Visualize the Data"]).
           - **MANDATORY**: At least ONE option MUST be visualization-related (e.g., "Visualize distribution of column_name", "Show trend chart").
        
        Dataset Metadata:
        - Columns: {dataset_metadata.get('columns', {})}
        - Overview: {dataset_metadata.get('overview', {})}
        """
        
        user_prompt = f"User Request: {prompt}"
        response = await self.get_completion(system_prompt, user_prompt, provider=provider, model=model)
        
        import re
        try:
            # Extract JSON block
            match = re.search(r"```(?:json)?\s*(.*?)\s*```", response, re.DOTALL | re.IGNORECASE)
            if match:
                response = match.group(1).strip()
            else:
                response = response.strip()
            
            clarification = json.loads(response)
        except Exception as e:
            # Fallback if LLM fails to return JSON
            clarification = {
                "message": "It looks like we have a few ways to approach this. Could you be a bit more specific?",
                "options": ["Analyze numeric trends", "Find anomalies", "Clean missing data"]
            }
            
        return {
            "type": "clarification",
            "message": clarification.get("message", "Let's narrow this down!"),
            "options": clarification.get("options", [])
        }
