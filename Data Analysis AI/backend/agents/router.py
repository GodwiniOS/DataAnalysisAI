from typing import Dict, Any, List
from .base_agent import BaseAgent

class AgentRouter(BaseAgent):
    """
    Routes user prompts to the correct agent(s).
    """
    
    INTENT_MAP = {
        "engineering": "Data cleaning, transformation, renaming, filtering, columns creation, merging, etc.",
        "analysis": "Calculations, counting specific rows or values, statistics, trends, correlations, outliers, regressions, specific questions requiring data manipulation to answer, etc.",
        "visualization": "Creating charts, plots, graphs, etc.",
        "insight": "High-level explanations of data, summarizing findings from previous steps, or explaining existing results without needing to write code."
    }

    async def classify_intent(self, prompt: str, metadata: Dict[str, Any], provider: str = None, model: str = None) -> List[str]:
        """
        Classifies the user intent using the LLM.
        """
        system_prompt = f"""
        You are a Data Lab Orchestrator. Your job is to classify the user's request into one or more categories:
        - engineering: Data transformation, cleaning, or modification.
        - analysis: Statistical analysis or calculations.
        - visualization: Generating charts or plots.
        - insight: Specific questions about dataset structure or explaining *existing* results.
        - clarification: The user asks open-ended questions like "what can I do", "how do I start", or gives a vague prompt where you must narrow down their intent using multiple choice.
        
        Available Categories:
        {self.INTENT_MAP}
        
        Return a comma-separated list of categories. Only return the list, nothing else.
        Example: "engineering, visualization"
        """
        
        user_prompt = f"User Request: {prompt}\nDataset Overview: {metadata.get('overview', {})}"
        
        result = await self.get_completion(system_prompt, user_prompt, provider=provider, model=model)
        # Simple parsing
        intents = [i.strip().lower() for i in result.split(',') if i.strip().lower() in self.INTENT_MAP]
        
        # Default to insight if nothing is found
        return intents if intents else ["insight"]

    async def process(self, prompt: str, dataset_metadata: Dict[str, Any], provider: str = None, model: str = None) -> Dict[str, Any]:
        intents = await self.classify_intent(prompt, dataset_metadata, provider=provider, model=model)
        return {"intents": intents}
