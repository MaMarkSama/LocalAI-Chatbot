# -*- coding: utf-8 -*-
"""
conversation.py — In-memory + SQLite + Memory Manager hybrid
"""
from typing import List, Dict
import threading
from collections import defaultdict
from database import db


class ConversationManager:
    def __init__(self, max_turns: int = 100):
        self.max_turns = max_turns
        self._cache: Dict[str, List[Dict]] = defaultdict(list)
        self._lock  = threading.Lock()

    def _load_from_db(self, session_id: str):
        with self._lock:
            if session_id not in self._cache:
                limit = self.max_turns if self.max_turns > 0 else 500
                msgs = db.get_messages(session_id, limit=limit)
                self._cache[session_id] = msgs

    def add_message(self, session_id: str, role: str, content: str,
                    source: str = "webchat", user_id: str = None):
        self._load_from_db(session_id)
        with self._lock:
            self._cache[session_id].append({"role": role, "content": content})
            if self.max_turns > 0:
                max_msg = self.max_turns * 2
                if len(self._cache[session_id]) > max_msg:
                    self._cache[session_id] = self._cache[session_id][-max_msg:]
        return db.add_message(session_id, role, content, source, user_id=user_id)

    def get_messages(self, session_id: str) -> List[Dict]:
        self._load_from_db(session_id)
        with self._lock:
            return list(self._cache[session_id])

    def clear(self, session_id: str):
        with self._lock:
            self._cache[session_id] = []
        db.clear_session(session_id)

    def forget(self, session_id: str):
        """Evict a deleted session from memory without issuing another DB write."""
        with self._lock:
            self._cache.pop(session_id, None)
