from pathlib import Path

from user_manager import UserManager


def test_tokens_are_hashed_at_rest_and_login_survives_manager_restart(tmp_path: Path):
    path = tmp_path / "users.db"
    first = UserManager(path)
    result = first.register("tester", "strong-pass-123")
    assert result["ok"] is True
    raw_token = result["token"]

    stored = first._conn().execute("SELECT token, token_hash FROM user_tokens").fetchone()
    assert stored["token"] != raw_token
    assert stored["token"] == stored["token_hash"]

    second = UserManager(path)
    assert second.verify_token(raw_token)["username"] == "tester"

