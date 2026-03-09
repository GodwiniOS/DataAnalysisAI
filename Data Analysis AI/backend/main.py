from fastapi import FastAPI, UploadFile, File, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import io
import json
from typing import Optional, List
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

from core.profiler import profile_dataframe
from core.executor import SafeExecutor
from services.storage import dataset_store
from agents.router import AgentRouter
from agents.engineer import DataEngineeringAgent
from agents.analyst import DataAnalysisAgent
from agents.visualizer import VisualizationAgent
from agents.insight import InsightAgent
from services.persistence import persistence_manager
from core.insight_generator import generate_suggested_prompts

app = FastAPI(title="AI Data Lab API")

# Explicit CORS for local dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from agents.insight import InsightAgent
from agents.clarification import ClarificationAgent
from agents.pathway import PathwayAgent

# Initialize components
executor = SafeExecutor()
router = AgentRouter()
eng_agent = DataEngineeringAgent()
ana_agent = DataAnalysisAgent()
viz_agent = VisualizationAgent()
ins_agent = InsightAgent()
clarify_agent = ClarificationAgent()
pathway_agent = PathwayAgent()

@app.middleware("http")
async def log_requests(request, call_next):
    print(f"DEBUG: {request.method} {request.url}")
    response = await call_next(request)
    print(f"DEBUG: Response status {response.status_code}")
    return response

class ChatRequest(BaseModel):
    session_id: str
    message: str
    provider: str = "openai"
    model: str = "gpt-4o"

@app.get("/")
async def root():
    return {"message": "Welcome to AI Data Lab API"}

@app.post("/upload")
async def upload_csv(file: UploadFile = File(...)):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")
    
    try:
        content = await file.read()
        df = pd.read_csv(io.BytesIO(content), on_bad_lines='skip')
        
        if df.empty:
            raise HTTPException(status_code=400, detail="The uploaded CSV file is empty.")
            
        session_id = dataset_store.create_session()
        profile = profile_dataframe(df)
        preview_data = json.loads(df.head(10).to_json(orient='records'))
        
        # Suggested prompts
        suggested_prompts = generate_suggested_prompts(profile)
        
        # Add initial version
        dataset_store.add_version(session_id, df, {"action": "upload", "filename": file.filename})
        
        # Create initial assistant message
        summary = f"I've analyzed **{file.filename}**. It contains **{profile['overview']['total_rows']}** rows and **{profile['overview']['total_columns']}** columns. "
        if profile['overview']['missing_cells'] > 0:
            summary += f"Note: I found {profile['overview']['missing_cells']} missing values."
        else:
            summary += "The dataset looks clean with no missing values."
        
        persistence_manager.save_message(session_id, "assistant", summary, "insight")
        
        # Get history to return
        history = persistence_manager.get_messages(session_id)
        
        return {
            "session_id": session_id,
            "filename": file.filename,
            "profile": profile,
            "preview": preview_data,
            "suggested_prompts": suggested_prompts,
            "messages": history
        }
    except pd.errors.ParserError as e:
        raise HTTPException(status_code=400, detail=f"Error parsing CSV: {str(e)}")
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

def populate_chart_data(config, df: pd.DataFrame):
    if isinstance(config, dict) and "chartType" in config and "data" in config:
        # Google Charts format detected
        new_data = []
        for row in config["data"]:
            if isinstance(row, list) and any(isinstance(c, str) and c.startswith("$") for c in row):
                cols_data = []
                for cell in row:
                    if isinstance(cell, str) and cell.startswith("$"):
                        col_name = cell[1:]
                        if col_name in df.columns:
                            if pd.api.types.is_numeric_dtype(df[col_name]):
                                cols_data.append(df[col_name].fillna(0).tolist())
                            else:
                                cols_data.append(df[col_name].fillna("").astype(str).tolist())
                        else:
                            cols_data.append([None] * len(df))
                    else:
                        cols_data.append([cell] * len(df))
                        
                # Zip unpacked columns into rows
                zipped_rows = list(map(list, zip(*cols_data)))
                new_data.extend(zipped_rows)
            else:
                new_data.append(row)
                
        config["data"] = new_data
        return config
        
    elif isinstance(config, dict):
        return {k: populate_chart_data(v, df) for k, v in config.items()}
    elif isinstance(config, list):
        return [populate_chart_data(i, df) for i in config]
    elif isinstance(config, str) and config.startswith('$'):
        col_name = config[1:]
        if col_name in df.columns:
            if pd.api.types.is_numeric_dtype(df[col_name]):
                return df[col_name].fillna(0).tolist()
            else:
                return df[col_name].fillna("").astype(str).tolist()
    return config

@app.post("/chat")
async def chat(request: ChatRequest):
    df = dataset_store.get_current_df(request.session_id)
    if df is None:
        raise HTTPException(status_code=404, detail="Session not found or dataset missing.")
    
    # Save user message
    persistence_manager.save_message(request.session_id, "user", request.message, "text")
    
    metadata = profile_dataframe(df)
    
    # 1. Route Intent
    intents = await router.classify_intent(request.message, metadata, provider=request.provider, model=request.model)
    
    response_elements = []
    current_df = df
    
    # Check current session state for Pathway Wizards
    session_data = persistence_manager.get_session(request.session_id)
    session_state = session_data.get("state_data", {}) if session_data else {}
    
    current_step = session_state.get("pathway_step", "init")
    is_pathway_active = current_step != "init"
    
    # Trigger ML pathway if active, OR if prompt specifically asks to predict/model/find drivers
    msg_lower = request.message.lower()
    is_modeling_intent = "predict" in msg_lower or "model" in msg_lower or "driver" in msg_lower or "forecast" in msg_lower
    
    if is_pathway_active or is_modeling_intent:
        pathway_res = await pathway_agent.process(session_state, request.message, metadata, provider=request.provider, model=request.model)
        
        if pathway_res["type"] == "execute_pathway":
            # The Wizard is finished, it generated an execution prompt.
            # We overwrite the user's message with this specific prompt and let the standard Router take over.
            request.message = pathway_res["execution_prompt"]
            intents = await router.classify_intent(request.message, metadata, provider=request.provider, model=request.model)
            # Reset state
            persistence_manager.update_session_state(request.session_id, {"pathway_step": "init"})
        else:
            # We are still in the Wizard (asking questions).
            # Update the DB state so we remember for the next message.
            if "next_state" in pathway_res:
                new_state = {"pathway_step": pathway_res["next_state"]}
                if "state_data" in pathway_res:
                    new_state.update(pathway_res["state_data"])
                persistence_manager.update_session_state(request.session_id, new_state)
            
            response_elements.append({
                "type": pathway_res["type"], 
                "content": pathway_res.get("message", "Continue modeling..."),
                "options": pathway_res.get("options", [])
            })
            
            for element in response_elements:
                persistence_manager.save_message(request.session_id, "assistant", element["content"], element["type"])
                
            return {
                "response": response_elements,
                "preview": json.loads(current_df.head(10).to_json(orient='records')),
                "profile": profile_dataframe(current_df),
                "suggested_prompts": generate_suggested_prompts(metadata)
            }
    
    # 2. Handle Clarification State
    if "clarification" in intents:
        # The user's request was ambiguous. Enter a stateful decision tree.
        clarify_res = await clarify_agent.process(request.message, metadata, provider=request.provider, model=request.model)
        
        response_elements.append({
            "type": clarify_res["type"], 
            "content": clarify_res["message"],
            "options": clarify_res["options"]  # We pass options directly to the frontend
        })
        
        # Save assistant message
        for element in response_elements:
            # We save the full element if it's a rich type (insight/clarify) to preserve options/stats 
            is_rich = element["type"] in ["insight", "clarification"]
            saved_content = element if is_rich else element["content"]
            persistence_manager.save_message(request.session_id, "assistant", saved_content, element["type"])
            
        return {
            "response": response_elements,
            "preview": json.loads(current_df.head(10).to_json(orient='records')),
            "profile": profile_dataframe(current_df),
            "suggested_prompts": generate_suggested_prompts(metadata)
        }
    
    # 3. Execute based on intent
    if "engineering" in intents:
        eng_res = await eng_agent.process(request.message, metadata, provider=request.provider, model=request.model)
        code = eng_res["code"]
        res_text, updated_df, error = executor.execute(code, current_df)
        if error:
            response_elements.append({"type": "error", "content": error})
        else:
            current_df = updated_df
            dataset_store.add_version(request.session_id, current_df, {"action": "engineering", "message": request.message})
            response_elements.append({"type": "code", "content": code})
            response_elements.append({"type": "success", "content": "Data transformed successfully."})

    if "analysis" in intents:
        ana_res = await ana_agent.process(request.message, metadata, provider=request.provider, model=request.model)
        ana_code = ana_res["code"]
        ana_result, updated_df, error = executor.execute(ana_code, current_df)
        if error:
            response_elements.append({"type": "error", "content": error})
        else:
            current_df = updated_df
            # Update dataset metadata for following steps (like visualization)
            metadata = profile_dataframe(current_df)
            response_elements.append({"type": "code", "content": ana_code})
            response_elements.append({"type": "analysis_result", "content": str(ana_result)})



    if "visualization" in intents:
        viz_res = await viz_agent.process(request.message, metadata, provider=request.provider, model=request.model)
        if "error" not in viz_res:
            populated_chart = populate_chart_data(viz_res["chart"], current_df)
            response_elements.append({"type": "chart", "content": populated_chart})
        else:
            response_elements.append({"type": "error", "content": viz_res["error"]})

    # 3. Final Insight
    # Extract only the relevant calculation/error results for the mentor to explain.
    # Exclude raw code or charts as they are visual, the mentor just needs the data outcome.
    action_summaries = []
    for el in response_elements:
        if el["type"] == "error":
            action_summaries.append(f"Error occurred: {el['content']}")
        elif el["type"] == "analysis_result":
            action_summaries.append(f"Calculation result: {el['content']}")
        elif el["type"] == "success":
            action_summaries.append(el['content'])
            
    action_context = " | ".join(action_summaries) if action_summaries else None
    
    insight_res = await ins_agent.process(request.message, metadata, action_context, provider=request.provider, model=request.model)
    response_elements.append({
        "type": "insight", 
        "content": insight_res.get("content", insight_res.get("explanation")),
        "stats": insight_res.get("stats", []),
        "options": insight_res.get("options", [])
    })
    
    # Save assistant messages
    for element in response_elements:
        is_rich = element.get("type") in ["insight", "clarification"]
        saved_content = element if is_rich else element["content"]
        persistence_manager.save_message(request.session_id, "assistant", saved_content, element["type"])
    
    new_profile = profile_dataframe(current_df)
    
    return {
        "response": response_elements,
        "preview": json.loads(current_df.head(10).to_json(orient='records')),
        "profile": new_profile,
        "suggested_prompts": generate_suggested_prompts(new_profile)
    }

@app.get("/sessions/{session_id}")
async def get_session_history(session_id: str):
    history = persistence_manager.get_messages(session_id)
    df = dataset_store.get_current_df(session_id)
    
    preview = None
    profile = None
    
    if df is not None:
        preview = json.loads(df.head(10).to_json(orient='records'))
        profile = profile_dataframe(df)
        
    return {
        "messages": history,
        "preview": preview,
        "profile": profile
    }

from fastapi.responses import JSONResponse
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    import traceback
    with open("/tmp/chat_error.log", "w") as f:
        f.write(traceback.format_exc())
    return JSONResponse(status_code=500, content={"message": "Internal Server Error", "detail": str(exc)})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
