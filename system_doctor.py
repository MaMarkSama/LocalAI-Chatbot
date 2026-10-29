# -*- coding: utf-8 -*-
"""
system_doctor.py — Enterprise System Diagnostics, Self-Check & Auto-Installer
สำหรับ Gemma AI / LocalAI-Chatbot

ความสามารถ:
1. Self-Check ตรวจสอบความสมบูรณ์ของไฟล์และโค้ดของตัวเอง (File Integrity & Codebase)
2. Framework Check ตรวจสอบ Python, Pip, และ Packages สำคัญทั้งหมด (FastAPI, Uvicorn, ฯลฯ)
3. Ollama & Model Check ตรวจสอบการทำงานของ Ollama Service, พอร์ต, และรายชื่อโมเดล
4. Storage & DB Check ตรวจสอบการอ่านเขียน SQLite, WAL mode, และสิทธิ์ไดเรกทอรี
5. Hardware Check ตรวจสอบ RAM, CPU Cores, GPU (NVIDIA CUDA / Driver / VRAM)
6. Zero-to-Hero Auto-Installer (--fix): ติดตั้งทุกสิ่งที่ขาดหายให้อัตโนมัติ (Python packages, Ollama, .env)
"""

from __future__ import annotations

import ctypes
import json
import os
import platform
import shutil
import socket
import sqlite3
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

if sys.platform == "win32" and sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

BASE_DIR = Path(__file__).resolve().parent

# ANSI Colors for terminal output
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"


def _safe_print(msg: str):
    try:
        print(msg)
    except UnicodeEncodeError:
        print(msg.encode("ascii", errors="replace").decode("ascii"))


class DiagnosticResult:
    def __init__(self, category: str, name: str, status: str, details: str, fixable: bool = False, fix_hint: str = ""):
        self.category = category
        self.name = name
        self.status = status  # 'PASS', 'WARN', 'FAIL'
        self.details = details
        self.fixable = fixable
        self.fix_hint = fix_hint

    def to_dict(self) -> Dict[str, Any]:
        return {
            "category": self.category,
            "name": self.name,
            "status": self.status,
            "details": self.details,
            "fixable": self.fixable,
            "fix_hint": self.fix_hint,
        }


class SystemDoctor:
    def __init__(self, base_dir: Optional[Path] = None):
        self.base_dir = base_dir or BASE_DIR
        self.results: List[DiagnosticResult] = []

    def log_result(self, category: str, name: str, status: str, details: str, fixable: bool = False, fix_hint: str = ""):
        r = DiagnosticResult(category, name, status, details, fixable, fix_hint)
        self.results.append(r)
        return r

    # ── 1. Hardware & System Diagnostics ──────────────────────────────────────
    def check_hardware(self):
        category = "1. ระบบและฮาร์ดแวร์ (Hardware)"

        # OS info
        os_info = f"{platform.system()} {platform.release()} ({platform.architecture()[0]})"
        self.log_result(category, "ระบบปฏิบัติการ (OS)", "PASS", os_info)

        # CPU info
        cpu_count = os.cpu_count() or 1
        self.log_result(category, "หน่วยประมวลผล (CPU)", "PASS", f"{cpu_count} Logical Cores")

        # RAM info
        ram_gb = 0.0
        try:
            if sys.platform == "win32":
                class MEMORYSTATUSEX(ctypes.Structure):
                    _fields_ = [
                        ("dwLength", ctypes.c_ulong),
                        ("dwMemoryLoad", ctypes.c_ulong),
                        ("ullTotalPhys", ctypes.c_ulonglong),
                        ("ullAvailPhys", ctypes.c_ulonglong),
                        ("ullTotalPageFile", ctypes.c_ulonglong),
                        ("ullAvailPageFile", ctypes.c_ulonglong),
                        ("ullTotalVirtual", ctypes.c_ulonglong),
                        ("ullAvailVirtual", ctypes.c_ulonglong),
                        ("sullAvailExtendedVirtual", ctypes.c_ulonglong),
                    ]
                stat = MEMORYSTATUSEX()
                stat.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
                ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat))
                ram_gb = stat.ullTotalPhys / (1024 ** 3)
                avail_gb = stat.ullAvailPhys / (1024 ** 3)
                details = f"รวม {ram_gb:.1f} GB (ว่าง {avail_gb:.1f} GB)"
            else:
                pages = os.sysconf("SC_PHYS_PAGES")
                page_size = os.sysconf("SC_PAGE_SIZE")
                ram_gb = (pages * page_size) / (1024 ** 3)
                details = f"รวม {ram_gb:.1f} GB"

            if ram_gb >= 15.0:
                self.log_result(category, "หน่วยความจำ (RAM)", "PASS", f"{details} — ยอดเยี่ยมสำหรับโมเดล 12B/14B")
            elif ram_gb >= 7.5:
                self.log_result(category, "หน่วยความจำ (RAM)", "PASS", f"{details} — เหมาะกับโมเดล 7B/9B")
            else:
                self.log_result(category, "หน่วยความจำ (RAM)", "WARN", f"{details} — แนะนำโมเดลขนาดเล็ก เช่น 4B หรือ 3B")
        except Exception as e:
            self.log_result(category, "หน่วยความจำ (RAM)", "WARN", f"ไม่สามารถคำนวณ RAM: {e}")

        # GPU / CUDA detection
        gpu_detected = False
        gpu_name = ""
        vram_info = ""

        # Check nvidia-smi
        if shutil.which("nvidia-smi"):
            try:
                proc = subprocess.run(
                    ["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader"],
                    capture_output=True, text=True, timeout=3
                )
                if proc.returncode == 0 and proc.stdout.strip():
                    gpu_name = proc.stdout.strip().split("\n")[0]
                    gpu_detected = True
                    self.log_result(category, "กราฟิกการ์ด (GPU / CUDA)", "PASS", f"พบ {gpu_name} (รองรับ GPU Acceleration)")
            except Exception:
                pass

        if not gpu_detected and sys.platform == "win32":
            try:
                proc = subprocess.run(
                    ["powershell", "-NoProfile", "-Command", "Get-CimInstance Win32_VideoController | Select-Object -ExpandProperty Name"],
                    capture_output=True, text=True, timeout=5
                )
                names = [line.strip() for line in proc.stdout.splitlines() if line.strip()]
                if names:
                    gpu_name = ", ".join(names)
                    self.log_result(category, "กราฟิกการ์ด (Display Device)", "PASS", f"พบ {gpu_name} (ทำงานได้ทั้ง CPU/GPU)")
                    gpu_detected = True
            except Exception:
                pass

        if not gpu_detected:
            self.log_result(category, "กราฟิกการ์ด (GPU)", "PASS", "รันด้วยโหมด CPU Inference (Ollama รองรับ AVX2)")

    # ── 2. Framework & Python Runtime Diagnostics ─────────────────────────────
    def check_framework(self):
        category = "2. Framework & Python สภาพแวดล้อม"

        # Python Version
        py_ver = sys.version_info
        ver_str = f"{py_ver.major}.{py_ver.minor}.{py_ver.micro}"
        if py_ver >= (3, 10):
            self.log_result(category, "Python Runtime", "PASS", f"Python {ver_str} ({sys.executable})")
        else:
            self.log_result(
                category, "Python Runtime", "FAIL",
                f"Python {ver_str} เก่าเกินไป (ต้องการ 3.10+)",
                fixable=True, fix_hint="ติดตั้ง Python 3.11 หรือใหม่กว่า"
            )

        # Pip check
        pip_ok = False
        try:
            r = subprocess.run([sys.executable, "-m", "pip", "--version"], capture_output=True, text=True)
            if r.returncode == 0:
                pip_ok = True
                self.log_result(category, "Pip Package Manager", "PASS", r.stdout.strip().split("\n")[0])
        except Exception:
            pass

        if not pip_ok:
            self.log_result(
                category, "Pip Package Manager", "FAIL", "ไม่พบ pip",
                fixable=True, fix_hint="python -m ensurepip --default-pip"
            )

        # Required dependencies
        required_pkgs = [
            ("fastapi", "FastAPI Web Framework"),
            ("uvicorn", "Uvicorn ASGI Server"),
            ("httpx", "HTTPX Async Client"),
            ("pypdf", "PyPDF Document Extractor"),
            ("docx", "Python-Docx (Word Parser)"),
            ("openpyxl", "OpenPyXL (Excel Parser)"),
            ("multipart", "Python-Multipart Form Parser"),
            ("dotenv", "Python-Dotenv Config Loader"),
            ("ddgs", "DDGS Web Research Searcher"),
            ("sqlite3", "SQLite3 Built-in Database"),
        ]

        missing_pkgs = []
        for mod_name, label in required_pkgs:
            try:
                __import__(mod_name)
                self.log_result(category, f"Library: {label}", "PASS", f"ติดตั้งแล้ว ({mod_name})")
            except ImportError:
                missing_pkgs.append(mod_name)
                self.log_result(
                    category, f"Library: {label}", "FAIL", f"ยังไม่ได้ติดตั้ง ({mod_name})",
                    fixable=True, fix_hint=f"pip install -r requirements.txt"
                )

        return len(missing_pkgs) == 0

    # ── 3. Application Self-Check & File Integrity ─────────────────────────────
    def check_self_integrity(self):
        category = "3. ความสมบูรณ์ของระบบ (Self-Check & Files)"

        core_files = [
            ("webchat.py", "Web Chat Server & SSE Pipeline"),
            ("linechat.py", "LINE Messaging API Webhook"),
            ("smart_router.py", "Smart Tool & Intent Router"),
            ("security.py", "Security Guard, CSP & Audit"),
            ("database.py", "Database Schema & History Manager"),
            ("user_manager.py", "Auth, JWT Cookies & Passwords"),
            ("usage_tracker.py", "Token & Search Analytics"),
            ("file_processor.py", "Document & Image Parsers"),
            ("message_turbovec.py", "MessageTurboVec Vector RAG"),
            ("memory_manager.py", "Rolling Context & Long-term Memory"),
            ("webchat_ui.html", "WebChat UI 2.0 (Enterprise Frontend)"),
            ("admin_ui.html", "Admin Analytics Dashboard"),
            (".env.example", "Environment Variables Template"),
        ]

        all_files_ok = True
        for rel_path, desc in core_files:
            p = self.base_dir / rel_path
            if p.exists() and p.stat().st_size > 0:
                self.log_result(category, f"ไฟล์: {rel_path}", "PASS", f"{desc} ({p.stat().st_size // 1024} KB)")
            else:
                all_files_ok = False
                self.log_result(
                    category, f"ไฟล์: {rel_path}", "FAIL", f"ไม่พบไฟล์หรือไฟล์ว่างเปล่า ({desc})",
                    fixable=True, fix_hint="ตรวจสอบไฟล์ต้นฉบับใน Repository"
                )

        # Directories
        core_dirs = [
            ("gemma_app", "Shared Process/Config Package"),
            ("skill", "Enterprise UX/UI Master Skills"),
            ("tokens", "Design Token Definitions"),
        ]
        for rel_dir, desc in core_dirs:
            p = self.base_dir / rel_dir
            if p.is_dir() and any(p.iterdir()):
                self.log_result(category, f"โฟลเดอร์: {rel_dir}/", "PASS", f"{desc}")
            else:
                self.log_result(category, f"โฟลเดอร์: {rel_dir}/", "WARN", f"ไม่พบโฟลเดอร์ {desc}")

        # Check .env
        env_file = self.base_dir / ".env"
        if env_file.exists():
            self.log_result(category, "การตั้งค่า: .env", "PASS", "พบไฟล์การตั้งค่า .env พร้อมใช้งาน")
        else:
            self.log_result(
                category, "การตั้งค่า: .env", "WARN", "ยังไม่มีไฟล์ .env (จะสร้างจาก .env.example อัตโนมัติ)",
                fixable=True, fix_hint="คัดลอก .env.example ไปเป็น .env"
            )

        return all_files_ok

    # ── 4. Storage & Database Permissions ─────────────────────────────────────
    def check_storage_and_database(self):
        category = "4. ฐานข้อมูลและสิทธิ์บันทึกข้อมูล (Storage & DB)"

        # Check & create directories
        for dname in ("data", "logs", "backups"):
            dpath = self.base_dir / dname
            try:
                dpath.mkdir(parents=True, exist_ok=True)
                test_file = dpath / ".write_test"
                test_file.write_text("ok", encoding="utf-8")
                test_file.unlink()
                self.log_result(category, f"ไดเรกทอรี {dname}/", "PASS", "สิทธิ์อ่าน/เขียนสมบูรณ์")
            except Exception as e:
                self.log_result(
                    category, f"ไดเรกทอรี {dname}/", "FAIL", f"ไม่มีสิทธิ์เขียน: {e}",
                    fixable=True, fix_hint=f"ตั้งค่า permission ให้โฟลเดอร์ {dname}/"
                )

        # Disk Free Space
        try:
            total, used, free = shutil.disk_usage(self.base_dir)
            free_gb = free / (1024 ** 3)
            if free_gb >= 10.0:
                self.log_result(category, "พื้นที่ว่างบนไดรฟ์ (Disk Space)", "PASS", f"ว่าง {free_gb:.1f} GB (เพียงพอสำหรับโมเดล AI)")
            elif free_gb >= 3.0:
                self.log_result(category, "พื้นที่ว่างบนไดรฟ์ (Disk Space)", "WARN", f"ว่าง {free_gb:.1f} GB (อาจเหลือน้อยสำหรับโมเดลใหญ่)")
            else:
                self.log_result(category, "พื้นที่ว่างบนไดรฟ์ (Disk Space)", "FAIL", f"ว่างเพียง {free_gb:.1f} GB (พื้นที่ไม่พอ)")
        except Exception:
            pass

        # SQLite Connection and WAL mode check
        db_path = self.base_dir / "data" / "chat_history.db"
        try:
            conn = sqlite3.connect(str(db_path), timeout=5.0)
            conn.execute("PRAGMA journal_mode=WAL;")
            cur = conn.cursor()
            cur.execute("CREATE TABLE IF NOT EXISTS _doctor_test (id INTEGER PRIMARY KEY, ts TEXT);")
            cur.execute("INSERT INTO _doctor_test (ts) VALUES (datetime('now'));")
            conn.commit()
            cur.execute("DROP TABLE _doctor_test;")
            conn.commit()
            conn.close()
            self.log_result(category, "ฐานข้อมูล SQLite (WAL Mode)", "PASS", "เชื่อมต่อและทดสอบอ่าน/เขียนผ่านฉลุย")
        except Exception as e:
            self.log_result(category, "ฐานข้อมูล SQLite", "FAIL", f"เกิดข้อผิดพลาดในการเชื่อมต่อฐานข้อมูล: {e}")

    # ── 5. Ollama & Port Diagnostics ──────────────────────────────────────────
    def check_ollama_and_ports(self):
        category = "5. ระบบ AI Engine (Ollama & Ports)"

        # Check port 8001
        web_port = int(os.getenv("WEB_PORT", "8001"))
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1.0)
        try:
            res = sock.connect_ex(("127.0.0.1", web_port))
            if res == 0:
                self.log_result(category, f"พอร์ต Web Chat (:{web_port})", "WARN", f"พอร์ต {web_port} มีโปรแกรมกำลังเปิดใช้งานอยู่แล้ว (อาจเป็น Gemma AI ที่กำลังรัน)")
            else:
                self.log_result(category, f"พอร์ต Web Chat (:{web_port})", "PASS", f"พอร์ต {web_port} ว่าง พร้อมเปิดบริการ")
        finally:
            sock.close()

        # Check Ollama installation
        ollama_bin = shutil.which("ollama")
        if ollama_bin:
            try:
                proc = subprocess.run(["ollama", "--version"], capture_output=True, text=True, timeout=3)
                ver_str = proc.stdout.strip() or proc.stderr.strip() or "ติดตั้งแล้ว"
                self.log_result(category, "Ollama CLI Binary", "PASS", f"พบ {ollama_bin} ({ver_str})")
            except Exception:
                self.log_result(category, "Ollama CLI Binary", "PASS", f"พบ {ollama_bin}")
        else:
            self.log_result(
                category, "Ollama CLI Binary", "FAIL", "ยังไม่ได้ติดตั้ง Ollama บนเครื่องนี้",
                fixable=True, fix_hint="ติดตั้ง Ollama จาก https://ollama.com หรือผ่าน winget install Ollama.Ollama"
            )

        # Check Ollama Daemon HTTP connection
        ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
        ollama_online = False
        models_list = []
        try:
            req = urllib.request.Request(f"{ollama_url}/api/tags", headers={"User-Agent": "GemmaAI-Doctor/1.0"})
            with urllib.request.urlopen(req, timeout=3.0) as resp:
                if resp.status == 200:
                    ollama_online = True
                    data = json.loads(resp.read().decode("utf-8"))
                    models_list = [m.get("name", "") for m in data.get("models", [])]
                    self.log_result(category, "Ollama Service Daemon", "PASS", f"เชื่อมต่อ {ollama_url} สำเร็จ (Online)")
        except Exception as e:
            self.log_result(
                category, "Ollama Service Daemon", "WARN", f"ไม่สามารถเชื่อมต่อ Ollama ได้ที่ {ollama_url} (อาจยังไม่ได้เปิด Service)",
                fixable=True, fix_hint="สั่งเปิด Ollama Desktop หรือรัน 'ollama serve'"
            )

        # Check if configured model is installed
        target_model = os.getenv("OLLAMA_MODEL", "gemma4:12b")
        if ollama_online:
            has_target = any(target_model in m or target_model.split(":")[0] in m for m in models_list)
            if has_target:
                self.log_result(category, f"AI Model: {target_model}", "PASS", f"โมเดล {target_model} พร้อมใช้งาน")
            else:
                installed_str = ", ".join(models_list[:3]) or "ยังไม่มีโมเดล"
                self.log_result(
                    category, f"AI Model: {target_model}", "WARN", f"ยังไม่พบโมเดล {target_model} (โมเดลที่มีในเครื่อง: {installed_str})",
                    fixable=True, fix_hint=f"รันคำสั่ง: ollama pull {target_model}"
                )

        # Check Internet Connectivity for Web Research
        try:
            req = urllib.request.Request("https://duckduckgo.com", headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=3.0) as resp:
                if resp.status in (200, 301, 302):
                    self.log_result(category, "การเชื่อมต่ออินเทอร์เน็ต (Web Search)", "PASS", "เชื่อมต่ออินเทอร์เน็ตสำเร็จ รองรับ Agent Web Research")
        except Exception:
            self.log_result(category, "การเชื่อมต่ออินเทอร์เน็ต (Web Search)", "WARN", "ไม่สามารถเชื่อมต่ออินเทอร์เน็ตได้ (ระบบจะทำงานในโหมด Offline RAG)")

    # ── Run All Checks ────────────────────────────────────────────────────────
    def run_all(self) -> Dict[str, Any]:
        self.results.clear()
        self.check_hardware()
        self.check_framework()
        self.check_self_integrity()
        self.check_storage_and_database()
        self.check_ollama_and_ports()

        passes = sum(1 for r in self.results if r.status == "PASS")
        warns = sum(1 for r in self.results if r.status == "WARN")
        fails = sum(1 for r in self.results if r.status == "FAIL")

        return {
            "ok": fails == 0,
            "passes": passes,
            "warns": warns,
            "fails": fails,
            "total": len(self.results),
            "results": [r.to_dict() for r in self.results]
        }

    # ── 6. Auto-Fix / Zero-to-Hero Installer ──────────────────────────────────
    def auto_fix(self, on_progress=None):
        def notify(msg: str):
            if on_progress:
                on_progress(msg)
            else:
                _safe_print(f"  {CYAN}▸ {msg}{RESET}")

        notify("กำลังเริ่มขั้นตอนตรวจสอบและซ่อมแซม/ติดตั้งอัตโนมัติ...")

        # 1. Create missing directories
        for dname in ("data", "logs", "backups"):
            p = self.base_dir / dname
            if not p.exists():
                p.mkdir(parents=True, exist_ok=True)
                notify(f"สร้างไดเรกทอรี {dname}/ เรียบร้อย")

        # 2. Create .env if missing
        env_file = self.base_dir / ".env"
        example_env = self.base_dir / ".env.example"
        if not env_file.exists() and example_env.exists():
            import secrets
            content = example_env.read_text(encoding="utf-8")
            # Replace JWT_SECRET placeholder with a secure random key
            new_jwt = secrets.token_urlsafe(32)
            content = content.replace("your_random_secret_here", new_jwt)
            env_file.write_text(content, encoding="utf-8")
            notify("สร้างไฟล์ .env จาก .env.example พร้อมสุ่มรหัสความปลอดภัย JWT_SECRET ให้แล้ว")

        # 3. Install missing Python dependencies
        req_file = self.base_dir / "requirements.txt"
        if req_file.exists():
            notify("กำลังติดตั้ง/อัปเดต Python Packages ที่จำเป็นจาก requirements.txt...")
            flags = {"creationflags": subprocess.CREATE_NO_WINDOW} if sys.platform == "win32" else {}
            try:
                proc = subprocess.run(
                    [sys.executable, "-m", "pip", "install", "-r", str(req_file), "-q", "--no-warn-script-location"],
                    capture_output=True, text=True, **flags
                )
                if proc.returncode == 0:
                    notify("ติดตั้ง Python Packages สำเร็จครบถ้วน")
                else:
                    notify(f"คำเตือน: pip ติดตั้งบางส่วนไม่สำเร็จ: {proc.stderr[:100]}")
            except Exception as e:
                notify(f"เกิดข้อผิดพลาดในการรัน pip: {e}")

        # 4. Check & Install Ollama on Windows if missing
        if not shutil.which("ollama") and sys.platform == "win32":
            notify("ไม่พบ Ollama ในเครื่อง กำลังลองติดตั้งผ่าน winget...")
            try:
                proc = subprocess.run(
                    ["winget", "install", "Ollama.Ollama", "--accept-source-agreements", "--accept-package-agreements", "-h"],
                    capture_output=True, text=True, timeout=120
                )
                if proc.returncode == 0:
                    notify("ติดตั้ง Ollama สำเร็จเรียบร้อย!")
                else:
                    notify("ไม่สามารถติดตั้งผ่าน winget อัตโนมัติได้ กรุณาดาวน์โหลดที่ https://ollama.com")
            except Exception:
                notify("กรุณาดาวน์โหลดและติดตั้ง Ollama จาก https://ollama.com")

        # 5. Pull default model if Ollama is running
        target_model = os.getenv("OLLAMA_MODEL", "gemma4:12b")
        try:
            req = urllib.request.Request("http://localhost:11434/api/tags")
            with urllib.request.urlopen(req, timeout=2.0) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode("utf-8"))
                    models = [m.get("name", "") for m in data.get("models", [])]
                    if not any(target_model.split(":")[0] in m for m in models):
                        notify(f"Ollama กำลังรันอยู่ แต่ยังไม่มีโมเดล {target_model} กำลังเริ่ม Pull โมเดล...")
                        p_pull = subprocess.run(["ollama", "pull", target_model], capture_output=True, text=True)
                        if p_pull.returncode == 0:
                            notify(f"Pull โมเดล {target_model} สำเร็จ!")
                        else:
                            notify(f"ไม่สามารถ pull โมเดลอัตโนมัติ: {p_pull.stderr[:80]}")
        except Exception:
            pass

        notify("ขั้นตอนซ่อมแซมและติดตั้งเสร็จสมบูรณ์!")


# ── Terminal CLI Formatter ────────────────────────────────────────────────────
def print_cli_report(summary: Dict[str, Any]):
    _safe_print(f"\n{BOLD}{CYAN}======================================================================{RESET}")
    _safe_print(f"{BOLD}{CYAN}   🩺  Gemma AI — System & Framework Diagnostic Report {RESET}")
    _safe_print(f"{BOLD}{CYAN}======================================================================{RESET}\n")

    current_cat = ""
    for r in summary["results"]:
        if r["category"] != current_cat:
            current_cat = r["category"]
            _safe_print(f"\n{BOLD}── {current_cat} ──{RESET}")

        if r["status"] == "PASS":
            tag = f"{GREEN}[ PASS ]{RESET}"
        elif r["status"] == "WARN":
            tag = f"{YELLOW}[ WARN ]{RESET}"
        else:
            tag = f"{RED}[ FAIL ]{RESET}"

        _safe_print(f"  {tag} {BOLD}{r['name']}{RESET}")
        _safe_print(f"         {r['details']}")
        if r["status"] != "PASS" and r["fix_hint"]:
            _safe_print(f"         {CYAN}↳ ข้อแนะนำ: {r['fix_hint']}{RESET}")

    _safe_print(f"\n{BOLD}{CYAN}======================================================================{RESET}")
    status_color = GREEN if summary["ok"] else RED
    _safe_print(f"  สรุปผล: ผ่าน {GREEN}{summary['passes']}{RESET} รายการ | เตือน {YELLOW}{summary['warns']}{RESET} รายการ | ไม่ผ่าน {RED}{summary['fails']}{RESET} รายการ")

    if summary["ok"]:
        _safe_print(f"  สถานะ: {GREEN}{BOLD}✓ ระบบและ Framework พร้อมใช้งาน 100%!{RESET}")
    else:
        _safe_print(f"  สถานะ: {RED}{BOLD}✗ มีบางรายการไม่ผ่าน กรุณารัน 'python system_doctor.py --fix' เพื่อซ่อมแซม{RESET}")
    _safe_print(f"{BOLD}{CYAN}======================================================================{RESET}\n")


if __name__ == "__main__":
    doctor = SystemDoctor()
    if "--fix" in sys.argv or "--install-all" in sys.argv:
        _safe_print(f"{BOLD}{CYAN}🛠️  เริ่มโหมด Auto-Fix & Install All Missing Components...{RESET}")
        doctor.auto_fix()
        _safe_print(f"\n{BOLD}ตรวจเช็กผลการทำงานอีกครั้ง:{RESET}")

    report = doctor.run_all()
    print_cli_report(report)
    sys.exit(0 if report["ok"] else 1)
