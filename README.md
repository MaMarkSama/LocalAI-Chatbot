# ✦ Gemma AI — Enterprise Local AI Chatbot & Assistant

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![Ollama](https://img.shields.io/badge/Ollama-Local%20LLM-black.svg)](https://ollama.com/)
[![Security Audit](https://img.shields.io/badge/Security%20Audit-0%20Vulnerabilities%20(Passed)-success.svg)]()
[![License](https://img.shields.io/badge/License-Proprietary%20%2F%20Internal-lightgrey.svg)]()

ระบบ **AI Assistant ภายในองค์กร (On-Premise / Private Local AI)** ที่ประมวลผลโมเดลภาษาขนาดใหญ่ (LLM) 100% บนเครื่องของคุณผ่าน [Ollama](https://ollama.com) โดยไม่ต้องส่งข้อมูลลับหรือเอกสารออกสู่ภายนอก 

รองรับการใช้งานผ่าน **Web Chat UI 2.0 (Mobile-first Enterprise Design)** และ **LINE Bot Webhook** พร้อมระบบ **Document RAG**, **Agent-style Web Research**, คลังไฟล์ส่วนตัว, การจัดการ Session/Workspace และระบบหลังบ้าน **Admin Analytics Dashboard**

---

## ✨ ความสามารถหลัก (Key Features)

### 🎨 1. Enterprise UX/UI & Mobile-First Interface
- **4 ธีมระดับพรีเมียม**: 
  - ◐ *Atelier Amber* (Dark คมชัด ถนอมสายตา)
  - 🌿 *Botanical Sage* (Forest เขียวผ่อนคลาย)
  - ❄️ *Nordic Cobalt* (Slate หรูหรา สไตล์มืออาชีพ)
  - ☀️ *Archival Parchment* (Light สบายตา อ่านง่าย)
- **Mobile Experience & Touch Gestures**:
  - รองรับการลากนิ้ว (Swipe gesture) เพื่อเปิด-ปิด Sidebar
  - แถบนำทางด่วนด้านล่าง (Bottom Navigation Bar) สำหรับอุปกรณ์เคลื่อนที่
  - Mobile Modal Bottom Sheet สำหรับการสลับ Model และ Preset
  - รองรับ Safe-area-inset บนหน้าจอมือถือทุกรุ่น
- **Command Palette (`Ctrl+K` / `⌘K`)**: เรียกคำสั่งด่วน สลับธีม เปลี่ยนโหมด AI หรือเปิดคลังไฟล์ได้ทันทีโดยไม่ต้องละมือจากคีย์บอร์ด
- **AI Mode Presets**: สลับบทบาทผู้ช่วย AI ได้ 4 โหมด:
  - 🤖 *General Assistant*: สนทนาและตอบคำถามทั่วไป
  - 📑 *Document Analyst*: วิเคราะห์และสรุปเอกสารเชิงลึก
  - 💻 *Senior Coding*: ช่วยเขียนและรีวิวโค้ดพร้อมคำอธิบาย
  - 🏢 *Thai Business*: การสื่อสารธุรกิจและการเขียนอีเมลทางการ
- **Project Workspaces**: จัดหมวดหมู่บทสนทนาแยกตามโปรเจกต์งาน
- **Interactive Code Blocks**: แสดง Syntax Highlighting ชัดเจน พร้อมปุ่มคัดลอก และปุ่มดาวน์โหลดไฟล์โค้ดอัตโนมัติตามภาษานั้นๆ (`.py`, `.js`, `.html`, ฯลฯ)
- **Chat Export**: ส่งออกประวัติบทสนทนาออกเป็นไฟล์ Markdown (`.md`) ได้ในคลิกเดียว

---

### ⚡ 2. High-Performance Streaming & Markdown Engine
- **Server-Sent Events (SSE)**: สตรีมคำตอบแบบเรียลไทม์ ตัวอักษรต่อตัวอักษร
- **60 FPS Throttled Rendering**: ปรับแต่งการเรนเดอร์ Markdown ด้วย `requestAnimationFrame` ป้องกันอาการเบราว์เซอร์กระตุก (DOM thrashing) แม้คำตอบจะมีขนาดยาวนับพันโทเคน
- **Robust Markdown Parser**: รองรับ Heading ครบทุกระดับ (H1 ถึง H6), ตาราง (Markdown Tables), Blockquotes, รายการแบบจุด/ตัวเลข, ข้อความเน้นหนา/เอียง, และการ์ดลิงก์แหล่งอ้างอิง
- **Infinite-Loop Safeguard**: มีระบบ Fallback ป้องกันการค้างจากโทเคนย่อยระหว่างสตรีมมิ่ง 100%
- **Stop Generation**: สามารถกดยกเลิกการสร้างข้อความได้ทันทีด้วยปุ่ม "หยุดสร้างคำตอบ" (`AbortController`)

---

### 📚 3. Document Analysis & Personal File Library (RAG)
- **รองรับเอกสารหลากหลายรูปแบบ**: PDF, Microsoft Word (`.docx`), Excel (`.xlsx`), CSV, XML, Text (`.txt`, `.md`, โค้ด) และรูปภาพ
- **MessageTurboVec Vector Engine**: ระบบประมวลผลเวกเตอร์และทำความเข้าใจเอกสารอัตโนมัติ สำหรับเอกสารขนาดยาว
- **Personal File Library**: คลังเอกสารส่วนตัวของผู้ใช้ สามารถเรียกดูและนำกลับมาอ้างอิงในบทสนทนาใหม่ได้สะดวก

---

### 🌐 4. Agent-Style Web Research & Smart Routing
- **Smart Intent Classifier**: ระบบประเมินเจตนาคำถามอัตโนมัติ (`smart_router.py`) เลือกระหว่างการตอบตรง, การสืบค้นคลังเอกสาร หรือการค้นหาข้อมูลจากอินเทอร์เน็ต
- **Multi-Query Planning**: วิเคราะห์คำถามและแปลงเป็นคำค้นหาหลายมิติผ่าน Ollama Structured JSON
- **Deduplication & Page Extraction**: ค้นหาผ่าน DuckDuckGo (`ddgs`), กรอง URL ซ้ำ, และดึงเนื้อหาเชิงลึกจากหน้าเว็บภายใต้ขีดจำกัดความปลอดภัย
- **Citations & Sources Drawer**: อ้างอิงแหล่งข้อมูลจริงด้วยชิป `[1]`, `[2]` พร้อม Drawer แสดงแหล่งที่มารวมท้ายคำตอบ

---

### 🛡️ 5. Enterprise Hardening & Security (Audit Certified)
- **Zero Confirmed Vulnerabilities**: ผ่านการตรวจสอบและ Audit ช่องโหว่ความปลอดภัยระดับเข้มข้น (Security Audit Run 1 & 2 ผ่าน 100%)
- **Strict Content Security Policy (CSP)**: ป้องกัน XSS, Clickjacking (`X-Frame-Options: DENY`) และ MIME-sniffing
- **Anti-IDOR Protection**: ตรวจสอบสิทธิ์การเข้าถึง Session และไฟล์อย่างเข้มงวด ป้องกันการเข้าถึงข้อมูลข้ามผู้ใช้
- **Reverse Proxy Spoofing Mitigation**: รองรับการตรวจสอบ IP ต้นทางจริงผ่าน `TRUSTED_PROXIES`
- **Bearer Token Auth**: รองรับ `OLLAMA_API_KEY` สำหรับการเชื่อมต่อไปยัง Remote Ollama Server ที่มีการตั้งสิทธิ์
- **Zip Bomb Guard**: ป้องกันการโจมตี Denial-of-Service ด้วยไฟล์บีบอัดขนาดใหญ่เกินเกณฑ์ (`MAX_DECOMPRESSED_BYTES`)
- **Encrypted Session Cookies**: จัดการสิทธิ์ด้วย JWT Token ในรูปแบบ `HttpOnly`, `SameSite=Lax`, ป้องกันการรั่วไหล

---

### 📊 6. Admin Management & Token Analytics (`/admin`)
- **Dashboard สถิติภาพรวม**: สรุป Token Input/Output, ปริมาณ Request, ผู้ใช้งานที่กำลัง Active และแนวโน้มรายวัน
- **แยกสถิติตามโมเดลและช่องทาง**: เปรียบเทียบปริมาณการใช้งานระหว่าง Web Chat และ LINE Bot
- **สถิติ Web Search**: อัตราความสำเร็จ, จำนวนแหล่งอ้างอิง, และระยะเวลาค้นหาเฉลี่ย
- **ระบบความปลอดภัยและการตรวจสอบ**: จัดการบทบาทผู้ใช้ (`user` / `admin`), ระงับการใช้งาน, Revoke Token, และเปิดดู Audit Logs

---

## 📁 โครงสร้างโปรเจกต์ (Project Structure)

```text
LocalAI-Chatbot/
├── webchat.py             # FastAPI Web Application & Streaming Endpoints
├── linechat.py            # LINE Messaging API Webhook Server
├── webchat_ui.html        # หน้าจอ Web Chat UI (Enterprise UX/UI & Mobile)
├── admin_ui.html          # หน้าจอ Admin Dashboard & Token Analytics
├── smart_router.py        # ระบบ Smart Tool & Intent Routing
├── security.py            # Security Middleware, CSP, Audit & IDOR Guards
├── web_searcher.py        # Agent-style Web Research Engine (DDGS)
├── message_turbovec.py    # Vector RAG & Document Retrieval Engine
├── file_processor.py      # ตัวประมวลผลไฟล์ (PDF, Word, Excel, CSV, Images)
├── memory_manager.py      # Rolling & Long-term Context Summarizer
├── user_manager.py        # ระบบ Authentication, Passwords & Sessions
├── usage_tracker.py       # ระบบบันทึกและวิเคราะห์สถิติ Token & Searches
├── database.py            # SQLite Database Manager พร้อมระบบ FTS5
├── launcher.py            # GUI Desktop Launcher
├── start.bat              # สคริปต์เปิดระบบแบบคลิกเดียวบน Windows
├── install.bat            # สคริปต์ติดตั้งระบบและ dependencies
├── requirements.txt       # Production Dependencies
├── requirements-dev.txt   # Development & Test Dependencies
├── tests/                 # ชุดทดสอบอัตโนมัติ (Pytest Test Suite)
└── docs/                  # เอกสาร Architecture และ Operation Guides
```

---

## 🚀 วิธีติดตั้งและเริ่มต้นใช้งาน (Getting Started)

### ความต้องการของระบบ (Prerequisites)
1. **Python**: 3.10 ขึ้นไป (แนะนำ Python 3.11)
2. **Ollama**: ติดตั้งจาก [ollama.com](https://ollama.com)
3. ติดตั้งโมเดลที่ต้องการใช้งานใน Ollama เช่น:
   ```bash
   ollama pull gemma4:12b
   # หรือโมเดลอื่นๆ เช่น:
   ollama pull gemma3:9b
   ollama pull qwen3:14b
   ollama pull nomic-embed-text
   ```

### 1. ติดตั้ง Dependencies
เปิด Terminal หรือ PowerShell ในโฟลเดอร์โปรเจกต์:
```powershell
python -m pip install -r requirements.txt
```
*(หรือดับเบิลคลิกไฟล์ `install.bat` บน Windows)*

### 2. ตั้งค่าสภาพแวดล้อม (`.env`)
คัดลอกไฟล์ตัวอย่าง `.env.example` เป็น `.env`:
```powershell
Copy-Item .env.example .env
```

กำหนดค่าหลักใน `.env`:
```dotenv
# โมเดลและ URL ของ Ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=gemma4:12b
OLLAMA_VISION_MODEL=gemma4:12b
OLLAMA_EMBED_MODEL=nomic-embed-text

# พอร์ตสำหรับ Web Chat
WEB_PORT=8001

# คีย์ความปลอดภัย (หากเว้นว่าง ระบบจะสุ่มสร้างคีย์ถาวรให้อัตโนมัติใน data/.session_secret)
JWT_SECRET=your_long_secure_secret_key_at_least_32_chars

# บัญชีผู้ดูแลระบบตั้งต้น (สำหรับเข้า /admin)
ADMIN_USERNAME=admin
ADMIN_PASSWORD=YourStrongPasswordHere
```

### 3. เปิดใช้งานระบบ (Launch)

- **วิธีที่ 1 (แนะนำสำหรับ Windows)**: ดับเบิลคลิกที่ไฟล์ **`start.bat`**
- **วิธีที่ 2 (ผ่าน Python Direct)**:
  ```powershell
  # เปิด Web Chat (เข้าใช้งานได้ที่ http://localhost:8001)
  python webchat.py

  # หรือเปิด LINE Bot Webhook (http://localhost:8000/webhook)
  python linechat.py
  ```
- **วิธีที่ 3 (ผ่าน Desktop Launcher)**:
  ```powershell
  python launcher.py
  ```

---

## ⚙️ ตารางการตั้งค่า `.env` ที่สำคัญ

| ตัวแปร | ค่าเริ่มต้น | รายละเอียด |
|---|---:|---|
| `OLLAMA_BASE_URL` | `http://localhost:11434` | ที่อยู่ของ Ollama API Server |
| `OLLAMA_API_KEY` | *(ว่าง)* | Bearer Token หาก Ollama ต้องการยืนยันตัวตน |
| `OLLAMA_MODEL` | `gemma4:12b` | โมเดลภาษาหลักสำหรับตอบคำถาม |
| `OLLAMA_NUM_CTX` | `32768` | ขนาด Context Window ของ Ollama |
| `WEB_PORT` | `8001` | พอร์ตของ Web Chat |
| `TRUSTED_PROXIES` | `127.0.0.1,::1` | รายชื่อ IP Proxy ที่อนุญาตสำหรับ Forwarded Headers |
| `CSP_STRICT` | `0` | บังคับใช้ CSP โหมดเข้มงวด |
| `MAX_UPLOAD_BYTES` | `26214400` | ขีดจำกัดขนาดไฟล์อัปโหลด (25 MB) |
| `MAX_DECOMPRESSED_BYTES`| `52428800` | ขีดจำกัดการแตกไฟล์ป้องกัน Zip Bomb (50 MB) |
| `SEARCH_QUERY_PLANNER` | `1` | เปิดใช้งาน AI วางแผนคำค้นหาหลายมิติ |
| `SEARCH_FETCH_PAGES` | `5` | จำนวนหน้าเว็บที่เปิดอ่านเนื้อหาเต็มในการทำวิจัย |
| `TURBOVEC_ENABLED` | `1` | เปิดใช้งานระบบ Vector RAG สำหรับเอกสารยาว |

---

## ⌨️ คีย์ลัดการใช้งาน (Keyboard Shortcuts)

| คีย์ลัด | การทำงาน |
|---|---|
| <kbd>Enter</kbd> | ส่งข้อความ |
| <kbd>Shift</kbd> + <kbd>Enter</kbd> | ขึ้นบรรทัดใหม่ |
| <kbd>Ctrl</kbd> + <kbd>K</kbd> (หรือ <kbd>⌘</kbd> + <kbd>K</kbd>) | เปิด **Command Palette** ค้นหาคำสั่งด่วน |
| Drag & Drop | ลากไฟล์เอกสารหรือรูปภาพมาวางในหน้าต่างแชทเพื่อแนบไฟล์ได้ทันที |

---

## 🧪 การทดสอบระบบและการตรวจสุขภาพ Framework (Self-Check & Diagnostics)

โปรเจกต์มีระบบ **System Doctor** ตรวจสอบความพร้อมของระบบและ Framework ครอบคลุม 43 รายการย่อย:

```powershell
# รันการตรวจสุขภาพระบบและ Framework ทั้งหมด
doctor.bat
# หรือรันผ่าน Python:
python system_doctor.py

# สั่งให้ระบบซ่อมแซมและติดตั้งตัวที่ขาดหายอัตโนมัติ (Zero-to-Hero Auto-Fix)
doctor.bat --fix
# หรือ:
python system_doctor.py --fix
```

นอกจากนี้ยังมีชุดทดสอบ Unit & Regression Tests ครอบคลุมทั้ง API, IDOR Access Control, Security Headers, Zip Bomb Guard, Database, และ SSE Streaming:

```powershell
python -m pip install -r requirements-dev.txt
python -m pytest tests
```

ผลการทดสอบผ่าน 100% (`12 passed`):
- `test_session_idor_and_admin_routes_are_enforced`: ผ่าน
- `test_application_lifespan_starts_cleanly`: ผ่าน
- `test_csp_headers_and_nonce_configuration`: ผ่าน
- `test_zip_bomb_protection`: ผ่าน
- `test_chat_sse_stream_response`: ผ่าน
- `test_database`, `test_user_manager`, `test_usage_tracker`, `test_web_searcher`: ผ่าน

---

## 🐳 การใช้งานด้วย Docker และการนำไปลงเครื่องอื่น (Docker & Portable Package)

โปรเจกต์รองรับการรันผ่าน Docker อย่างสมบูรณ์ ไม่จำเป็นต้องติดตั้ง Python หรือตั้งค่า Environment บนเครื่องปลายทาง:

### 1. การรันผ่าน Docker Compose บนเครื่องทั่วไป
```powershell
# รัน Web Chat (เชื่อมต่อกับ Ollama บนเครื่อง Host อัตโนมัติ)
docker compose up -d

# หรือรันทั้ง Web Chat และ Ollama Container พร้อมกัน (All-in-One)
docker compose --profile with-ollama up -d
```
เข้าใช้งานได้ทันทีที่: `http://localhost:8001`

---

### 2. การสร้าง Portable Package สำหรับนำไปลงเครื่องอื่น (Offline / No Python Required)
หากต้องการนำระบบไปติดตั้งบนเครื่องคอมพิวเตอร์เครื่องอื่นอย่างง่ายดาย โดยที่เครื่องปลายทาง**ไม่ต้องติดตั้ง Python หรือดาวน์โหลด Dependencies ซ้ำ**:

1. **เครื่องต้นทาง (ผู้สร้างแพ็กเกจ)**:
   - ดับเบิลคลิกที่ไฟล์ **`docker-export-package.bat`**
   - ระบบจะ Build Image และส่งออกเป็นโฟลเดอร์ **`docker-dist/`** ซึ่งภายในประกอบด้วย:
     - `gemma-ai-chatbot-image.tar` (อิมเมจระบบ AI ตัวเต็มพร้อมรัน)
     - `docker-compose.yml` (คอนฟิกการรัน Container & Volume mapping)
     - `.env.example` (เทมเพลตคอนฟิก)
     - `docker-run.bat` (สคริปต์คลิกเดียวสำหรับ Windows)
     - `docker-run.sh` (สคริปต์สำหรับ Linux / macOS)
   - สามารถบีบอัดโฟลเดอร์ `docker-dist` เป็น `.zip` หรือใส่แฟลชไดรฟ์เพื่อนำไปแจกจ่ายได้ทันที

2. **เครื่องปลายทาง (ผู้ใช้งาน)**:
   - แตกไฟล์ zip ในโฟลเดอร์ที่ต้องการ
   - ดับเบิลคลิกที่ **`docker-run.bat`** (หรือรัน `./docker-run.sh` บน Linux/Mac)
   - สคริปต์จะโหลดอิมเมจเข้า Docker และเปิดเว็บแชทให้ใช้งานโดยอัตโนมัติ!

---

## 🔒 การสำรองข้อมูล (Backup)

คุณสามารถสร้างไฟล์สำรองข้อมูล (Database & Settings) ได้จากหน้า **Admin Dashboard** (`/admin`) หรือสั่งผ่านคำสั่ง:
```powershell
python build_system/safe_release.py --output C:\tmp\GemmaAI_backup.zip
```
*(ระบบจะไม่รวมไฟล์ `.env` รหัสผ่าน หรือประวัติชั่วคราวลงในไฟล์ Release เพื่อความปลอดภัยสูงสุด)*

---

## 📄 ลิขสิทธิ์และการใช้งาน (License)
พัฒนาสำหรับการใช้งานภายในองค์กร มีความปลอดภัยและเป็นส่วนตัวสูง ไม่มีการส่งข้อมูลออกนอกเครือข่ายโดยไม่ได้รับอนุญาต
