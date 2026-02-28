import sqlite3
import json
import os
from typing import List, Dict, Any
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "sessions.sqlite")
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

def init_db():
    os.makedirs(DATA_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Tables for sessions and messages
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY,
            current_index INTEGER DEFAULT -1,
            state_data TEXT DEFAULT '{}',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            role TEXT,
            content TEXT,
            type TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(session_id) REFERENCES sessions(id)
        )
    ''')
    
    conn.commit()
    conn.close()

class PersistenceManager:
    def __init__(self):
        init_db()

    def _get_conn(self):
        return sqlite3.connect(DB_PATH)

    def save_message(self, session_id: str, role: str, content: Any, msg_type: str):
        conn = self._get_conn()
        cursor = conn.cursor()
        
        # Ensure session exists
        cursor.execute("INSERT OR IGNORE INTO sessions (id) VALUES (?)", (session_id,))
        
        # Serialize content if it's not a string
        if not isinstance(content, str):
            content = json.dumps(content)
            
        cursor.execute(
            "INSERT INTO messages (session_id, role, content, type) VALUES (?, ?, ?, ?)",
            (session_id, role, content, msg_type)
        )
        
        cursor.execute("UPDATE sessions SET updated_at = ? WHERE id = ?", (datetime.now(), session_id))
        
        conn.commit()
        conn.close()

    def get_messages(self, session_id: str) -> List[Dict[str, Any]]:
        conn = self._get_conn()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT role, content, type FROM messages WHERE session_id = ? ORDER BY timestamp ASC", (session_id,))
        rows = cursor.fetchall()
        
        messages = []
        for row in rows:
            msg = dict(row)
            # Try to deserialize content
            try:
                msg["content"] = json.loads(msg["content"])
            except:
                pass
            messages.append(msg)
            
        conn.close()
        return messages

    def update_session(self, session_id: str, current_index: int):
        conn = self._get_conn()
        cursor = conn.cursor()
        # Ensure session exists before updating
        cursor.execute("INSERT OR IGNORE INTO sessions (id) VALUES (?)", (session_id,))
        cursor.execute("UPDATE sessions SET current_index = ?, updated_at = ? WHERE id = ?", (current_index, datetime.now(), session_id))
        conn.commit()
        conn.close()

    def get_session(self, session_id: str):
        conn = self._get_conn()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM sessions WHERE id = ?", (session_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            session_dict = dict(row)
            try:
                session_dict['state_data'] = json.loads(session_dict.get('state_data', '{}'))
            except:
                session_dict['state_data'] = {}
            return session_dict
        return None

    def update_session_state(self, session_id: str, state_data: Dict[str, Any]):
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO sessions (id) VALUES (?)", (session_id,))
        
        # Merge with existing state
        current_session = self.get_session(session_id)
        current_state = current_session.get("state_data", {}) if current_session else {}
        current_state.update(state_data)
        
        cursor.execute(
            "UPDATE sessions SET state_data = ?, updated_at = ? WHERE id = ?", 
            (json.dumps(current_state), datetime.now(), session_id)
        )
        conn.commit()
        conn.close()

persistence_manager = PersistenceManager()
