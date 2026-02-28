import json
from typing import Dict, Any, List
from .base_agent import BaseAgent

class PathwayAgent(BaseAgent):
    """
    Handles the structured Advanced Data Science Pathway Wizard.
    Guides the user through: Target (Y) -> Features (X) -> Algorithm Selection -> Execution.
    """
    async def process(self, session_state: Dict[str, Any], prompt: str, dataset_metadata: Dict[str, Any], provider: str = None, model: str = None) -> Dict[str, Any]:
        
        step = session_state.get("pathway_step", "init")
        
        if step == "init" or "predict" in prompt.lower() or "model" in prompt.lower() or "driver" in prompt.lower():
            # Step 1: Ask for target
            return self._ask_target(dataset_metadata)
            
        elif step == "awaiting_target":
            # Step 2: User provided target, ask for features
            target = prompt # Simplification: assuming they clicked the button
            return self._ask_features(target, dataset_metadata)
            
        elif step == "awaiting_features":
            # Step 3: User provided features, ask for algorithm
            features = prompt
            target = session_state.get("pathway_target", "Unknown")
            return await self._ask_algorithm(target, features, dataset_metadata, provider=provider, model=model)
            
        elif step == "awaiting_algorithm":
            # Step 4: Ready to execute
            algorithm = prompt
            target = session_state.get("pathway_target", "Unknown")
            features = session_state.get("pathway_features", "Unknown")
            
            # Format this as an engineering/analysis prompt to be executed by other agents
            execution_prompt = f"Run a {algorithm} model to predict '{target}' using features: '{features}'. Return the model metrics, and ALSO generate a chart visualising the results to interpret the model."
            return {
                "type": "execute_pathway",
                "execution_prompt": execution_prompt
            }
            
        return {"type": "error", "message": "Unknown pathway state."}

    def _ask_target(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        columns = metadata.get("columns", {})
        # List all columns as potential targets
        options = list(columns.keys())[:10] # limit to 10 for UI constraints
        
        return {
            "type": "clarification", 
            "message": "Let's build a model! First, what column are we trying to **predict** or understand (the Target / Y-variable)?",
            "options": options,
            "next_state": "awaiting_target"
        }
        
    def _ask_features(self, target: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        columns = metadata.get("columns", {})
        options = [col for col in columns.keys() if col != target][:10]
        
        # We add 'All Other Columns' as a quick bypass
        options.insert(0, f"All other columns")
        
        return {
            "type": "clarification",
            "message": f"Great. We are predicting **{target}**. Now, what **inputs** (Features / X-variables) should the model use to learn this?",
            "options": options,
            "next_state": "awaiting_features",
            "state_data": {"pathway_target": target}
        }

    async def _ask_algorithm(self, target: str, features: str, metadata: Dict[str, Any], provider: str = None, model: str = None) -> Dict[str, Any]:
        # Use LLM to dynamically determine appropriate algorithms and explain why
        system_prompt = f"""
        You are an educational Data Science Mentor. The user is building a model.
        Target (Y): {target}
        Features (X): {features}
        Target Data Type: {metadata.get('columns', {}).get(target, 'Unknown')}
        
        Your job is to recommend 2 algorithms to use, and explain WHY.
        
        Format your response EXACTLY as JSON:
        {{
            "message": "Explanation of why certain algorithms work for this data type (e.g. 'Since {target} is a number, we use Regression...'), and what we CANNOT use.",
            "options": ["Algorithm 1 Name", "Algorithm 2 Name"]
        }}
        """
        response = await self.get_completion(system_prompt, "Recommend algorithms", provider=provider, model=model)
        
        import re
        try:
            match = re.search(r"```(?:json)?\s*(.*?)\s*```", response, re.DOTALL | re.IGNORECASE)
            raw = match.group(1).strip() if match else response.strip()
            data = json.loads(raw)
        except Exception:
            data = {
                "message": f"Based on {target}, here are some options:",
                "options": ["Linear Regression", "Random Forest"]
            }
            
        return {
            "type": "clarification",
            "message": data.get("message"),
            "options": data.get("options"),
            "next_state": "awaiting_algorithm",
            "state_data": {"pathway_features": features}
        }
