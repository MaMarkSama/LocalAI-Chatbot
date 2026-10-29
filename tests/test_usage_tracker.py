from pathlib import Path

import usage_tracker as usage_module
from database import Database


def test_usage_events_do_not_double_count_message_tokens(tmp_path: Path, monkeypatch):
    database = Database(tmp_path / "usage.db")
    monkeypatch.setattr(usage_module, "db", database)
    tracker = usage_module.UsageTracker()

    database.add_message("s1", "user", "hello", user_id="u1")
    message_id = database.add_message("s1", "assistant", "answer", user_id="u1")
    tracker.record_usage(
        "s1", 11, 7, message_id=message_id, user_id="u1", model="test-model"
    )
    tracker.record_usage(
        "s1", 3, 2, user_id="u1", model="test-model", operation="search_planner"
    )

    stats = tracker.get_user_stats("u1")
    assert stats["input_tokens"] == 14
    assert stats["output_tokens"] == 9
    assert stats["total_tokens"] == 23
    assert stats["requests"] == 2


def test_legacy_message_tokens_are_included(tmp_path: Path, monkeypatch):
    database = Database(tmp_path / "legacy.db")
    monkeypatch.setattr(usage_module, "db", database)
    tracker = usage_module.UsageTracker()
    message_id = database.add_message("legacy", "assistant", "old", user_id="u1")
    database._conn().execute(
        "UPDATE messages SET prompt_tokens = 5, completion_tokens = 4 WHERE id = ?", (message_id,)
    )
    database._conn().commit()

    stats = tracker.get_user_stats("u1")
    assert stats["total_tokens"] == 9
    assert stats["requests"] == 1

