import pandas as pd
import uuid
import os
import json
from typing import Dict, List, Any
from .persistence import persistence_manager

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

class DatasetStore:
    def __init__(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        # We still keep a small cache of the current DataFrames in memory for performance
        self._cache: Dict[str, pd.DataFrame] = {}

    def create_session(self, session_id: str = None) -> str:
        if not session_id:
            session_id = str(uuid.uuid4())
        
        # Check if already exists in DB
        existing = persistence_manager.get_session(session_id)
        if not existing:
            # Create session directory
            os.makedirs(os.path.join(DATA_DIR, session_id), exist_ok=True)
            persistence_manager.update_session(session_id, -1)
            
        return session_id

    def add_version(self, session_id: str, df: pd.DataFrame, metadata: Dict[str, Any]):
        session_info = persistence_manager.get_session(session_id)
        if not session_info:
            # Fallback if creation/insertion was delayed
            persistence_manager.update_session(session_id, -1)
            session_info = persistence_manager.get_session(session_id)
            
        current_index = session_info.get("current_index", -1)
        new_index = current_index + 1
        
        # Save to disk
        session_dir = os.path.join(DATA_DIR, session_id)
        os.makedirs(session_dir, exist_ok=True)
        file_path = os.path.join(session_dir, f"v_{new_index}.parquet")
        
        # Convert all columns to strings if they are objects to avoid parquet issues (common for mixed types)
        # But only if it's necessary. Let's try direct first.
        try:
            df.to_parquet(file_path, engine='pyarrow')
        except Exception as e:
            # Fallback for mixed types or other parquet issues
            df.astype(str).to_parquet(file_path, engine='pyarrow')
            
        # Update DB
        metadata_json = json.dumps(metadata)
        # Note: We need a table for versions if we want to support full undo history 
        # but for now let's just update the current_index.
        persistence_manager.update_session(session_id, new_index)
        
        # Cache current
        self._cache[session_id] = df
        
        return new_index

    def get_current_df(self, session_id: str) -> pd.DataFrame:
        if session_id in self._cache:
            return self._cache[session_id]
            
        session_info = persistence_manager.get_session(session_id)
        if not session_info or session_info["current_index"] == -1:
            return None
            
        current_index = session_info["current_index"]
        file_path = os.path.join(DATA_DIR, session_id, f"v_{current_index}.parquet")
        
        if os.path.exists(file_path):
            df = pd.read_parquet(file_path)
            self._cache[session_id] = df
            return df
            
        return None

    def rollback(self, session_id: str):
        session_info = persistence_manager.get_session(session_id)
        if not session_info or session_info["current_index"] <= 0:
            return False
            
        new_index = session_info["current_index"] - 1
        persistence_manager.update_session(session_id, new_index)
        
        # Clear cache to force reload from disk
        if session_id in self._cache:
            del self._cache[session_id]
            
        return True

    def redo(self, session_id: str):
        # Redo is harder with disk-only index without a versions table
        # Let's just implement basic persistence for now as requested.
        return False

    def get_history(self, session_id: str):
        # For now, just return a simple list based on the current index
        session_info = persistence_manager.get_session(session_id)
        if not session_info:
            return []
            
        return [{"index": i, "metadata": {"status": "Version persisted"}} for i in range(session_info["current_index"] + 1)]

# Global store instance
dataset_store = DatasetStore()
