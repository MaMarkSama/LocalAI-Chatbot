import os
from pathlib import Path

from database import Database


def test_message_search_is_user_isolated_and_delete_cleans_related_rows(tmp_path: Path):
    database = Database(tmp_path / "test.db")
    first_id = database.add_message("session-a", "user", "ค้นหาเอกสารดาวอังคาร", user_id="user-a")
    database.add_message("session-a", "assistant", "คำตอบดาวอังคาร", user_id="user-a")
    database.add_message("session-b", "user", "ข้อมูลดาวอังคารลับ", user_id="user-b")

    assert first_id > 0
    matches = database.search_messages("ดาวอังคาร", user_id="user-a")
    assert matches
    assert {item["session_id"] for item in matches} == {"session-a"}

    database.save_memory("user-a", "session-a", "summary", "memory")
    database.delete_session("session-a")
    assert database.get_session("session-a") is None
    assert database.get_session_messages("session-a") == []
    assert database.get_memories("user-a", "session-a") == []


def test_database_path_is_not_cwd_dependent():
    from gemma_app.config import BASE_DIR, DB_PATH

    assert DB_PATH.is_absolute()
    configured = os.getenv("DB_PATH", "").strip()
    if configured:
        assert DB_PATH == Path(configured).resolve()
    else:
        assert str(DB_PATH).startswith(str(BASE_DIR))
