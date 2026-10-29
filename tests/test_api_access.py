import os
import secrets

from fastapi.testclient import TestClient

os.environ.setdefault("OLLAMA_WARMUP_ENABLED", "0")
import webchat


def _new_user(client: TestClient, prefix: str):
    username = f"{prefix}_{secrets.token_hex(4)}"
    response = client.post(
        "/api/auth/register",
        json={"username": username, "password": "strong-pass-123", "display_name": prefix},
    )
    assert response.status_code == 200
    assert "token" not in response.json()
    assert "HttpOnly" in response.headers["set-cookie"]
    return response.json()["user"]


def test_session_idor_and_admin_routes_are_enforced():
    owner_client = TestClient(webchat.app)
    other_client = TestClient(webchat.app)
    admin_client = TestClient(webchat.app)
    owner = _new_user(owner_client, "owner")
    _new_user(other_client, "other")
    admin = _new_user(admin_client, "admin")
    webchat.user_manager.set_role(admin["id"], "admin")

    # Refresh the admin cookie so its verified role reflects the DB update.
    admin_client.post("/api/auth/logout")
    login = admin_client.post(
        "/api/auth/login",
        json={"username": admin["username"], "password": "strong-pass-123"},
    )
    assert login.status_code == 200

    session_id = f"session-{secrets.token_hex(8)}"
    webchat.db.ensure_session(session_id, user_id=owner["id"])
    assert owner_client.get(f"/api/sessions/{session_id}").status_code == 200
    assert other_client.get(f"/api/sessions/{session_id}").status_code == 403

    assert owner_client.get("/api/admin/dashboard").status_code == 403
    assert admin_client.get("/api/admin/dashboard").status_code == 200
    assert admin_client.get("/admin").status_code == 200


def test_application_lifespan_starts_cleanly():
    with TestClient(webchat.app) as client:
        resp = client.get("/api/presets")
        assert resp.status_code == 200
        assert "Content-Security-Policy" in resp.headers
        assert "X-Content-Type-Options" in resp.headers


def test_csp_headers_and_nonce_configuration(monkeypatch):
    # Default mode: supports inline handlers (onclick) without browser blocking
    with TestClient(webchat.app) as client:
        resp = client.get("/")
        assert resp.status_code == 200
        csp = resp.headers.get("Content-Security-Policy", "")
        assert "script-src 'self' 'unsafe-inline'" in csp

    # Opt-in nonce mode:
    monkeypatch.setattr("security.CSP_ENABLE_NONCE", True)
    monkeypatch.setenv("CSP_ENABLE_NONCE", "1")
    with TestClient(webchat.app) as client:
        resp = client.get("/")
        assert resp.status_code == 200
        csp = resp.headers.get("Content-Security-Policy", "")
        assert "'nonce-" in csp
        assert '<script nonce="' in resp.text


def test_zip_bomb_protection():
    import io, zipfile
    from file_processor import _check_zip_bomb, process_docx

    # Create dummy zip with huge uncompressed size
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        # Write large block of zeroes (highly compressible)
        zf.writestr("word/document.xml", b"0" * (100 * 1024 * 1024))
    bomb_bytes = buf.getvalue()

    assert not _check_zip_bomb(bomb_bytes, max_uncompressed_bytes=50 * 1024 * 1024)
    result = process_docx(bomb_bytes)
    assert "File rejected" in result["content"]


def test_chat_sse_stream_response():
    with TestClient(webchat.app) as client:
        resp = client.post(
            "/chat",
            json={"session_id": "test-stream-sess", "message": "/reset", "model": "gemma4:12b"}
        )
        assert resp.status_code == 200
        assert "text/event-stream" in resp.headers.get("content-type", "")
        text = resp.text
        assert 'data: {"token":' in text
        assert 'data: {"done": true' in text
