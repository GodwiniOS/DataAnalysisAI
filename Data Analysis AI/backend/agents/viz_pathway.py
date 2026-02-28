import json
from typing import Dict, Any, List
from .base_agent import BaseAgent

class VizPathwayAgent(BaseAgent):
    """
    Handles the structured Visualization Pathway Wizard.
    Guides the user through: Chart Goal -> X-Axis -> Y-Axis -> Execution.
    """
    async def process(self, session_state: Dict[str, Any], prompt: str, dataset_metadata: Dict[str, Any]) -> Dict[str, Any]:
        
        step = session_state.get("viz_step", "init")
        
        if step == "init" or any(w in prompt.lower() for w in ["visualize", "chart", "plot", "graph"]):
            # Step 1: Ask for chart goal
            return self._ask_chart_goal()
            
        elif step == "awaiting_goal":
            # Step 2: User provided chart goal, ask for X-Axis
            goal = prompt 
            return self._ask_x_axis(goal, dataset_metadata)
            
        elif step == "awaiting_x_axis":
            # Step 3: User provided X-Axis, ask for Y-Axis
            x_axis = prompt
            goal = session_state.get("viz_goal", "Unknown")
            return self._ask_y_axis(goal, x_axis, dataset_metadata)
            
        elif step == "awaiting_y_axis":
            # Step 4: Ready to execute
            y_axis = prompt
            goal = session_state.get("viz_goal", "Unknown")
            x_axis = session_state.get("viz_x_axis", "Unknown")
            
            # Format this as a visualization prompt to be executed by the VisualizationAgent
            execution_prompt = f"Create a chart to {goal}. Put '{x_axis}' on the X-axis and '{y_axis}' on the Y-axis."
            return {
                "type": "execute_viz_pathway",
                "execution_prompt": execution_prompt
            }
            
        return {"type": "error", "message": "Unknown viz pathway state."}

    def _ask_chart_goal(self) -> Dict[str, Any]:
        options = [
            "Compare Categories (Bar/Column)",
            "See Trends over Time (Line)",
            "Find Correlations (Scatter)",
            "See Distribution (Histogram)"
        ]
        
        return {
            "type": "clarification", 
            "message": "Let's build a chart! What kind of relationship do you want to safely explore?",
            "options": options,
            "next_state": "awaiting_goal"
        }
        
    def _ask_x_axis(self, goal: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        columns = metadata.get("columns", {})
        
        # Keep options relevant to the goal if possible, or just list top columns
        options = list(columns.keys())[:10]
        
        return {
            "type": "clarification",
            "message": f"Got it, you want to **{goal}**. What should go on the **bottom (X-axis)**?",
            "options": options,
            "next_state": "awaiting_x_axis",
            "state_data": {"viz_goal": goal}
        }

    def _ask_y_axis(self, goal: str, x_axis: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        columns = metadata.get("columns", {})
        
        # Usually Y-axis needs to be numeric
        numeric_cols = [c for c, dtype in columns.items() if any(num_type in str(dtype).lower() for num_type in ['int', 'float', 'numeric'])]
        
        options = numeric_cols[:10] if numeric_cols else list(columns.keys())[:10]
        if x_axis in options:
            options.remove(x_axis)
            
        # Add a frequency option if it makes sense (e.g. for categorical comparisons)
        if "Compare Categories" in goal or "Distribution" in goal:
            options.insert(0, "Count / Frequency")
            
        return {
            "type": "clarification",
            "message": f"Perfect, '{x_axis}' is on the X-axis. What numerical value are we measuring on the **vertical (Y-axis)**?",
            "options": options,
            "next_state": "awaiting_y_axis",
            "state_data": {"viz_x_axis": x_axis}
        }
