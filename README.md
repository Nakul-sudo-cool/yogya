# 🏛️ Yogya (CivicProver) • Sovereign Civic Eligibility & Prover Engine

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688.svg)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-FF4B4B.svg)](https://streamlit.io)
[![Gemma 4](https://img.shields.io/badge/LLM-Gemma%204%20%7C%20LLaMA%203.2-8E24AA.svg)](https://ai.google.dev/gemma)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **"Zero Hallucinations in Citizen Welfare"** — An open-source, sovereign Civic Prover engine bridging the gap between dense government gazettes and citizen welfare delivery. Built for **IEEE CIS @ MSRIT Hackathon '26**.

---

## 🌟 The Core Innovation: Policy-as-Code

Traditional LLM wrappers suffer from legal hallucinations, often misinforming vulnerable citizens about statutory welfare benefits. 

**Yogya (CivicProver)** solves this with a two-tier sovereign architecture:
1. **Open-Weight Models as Compilers (`gemma4:e4b` / `llama3.2:3b`)**: Used strictly to translate unstructured PDF gazettes, circulars, and income certificates into a formal **Domain Specific Rule DSL**.
2. **Deterministic Mathematical Prover Engine**: Evaluates citizen parameters against strict statutory clauses (`<=`, `>=`, `==`, `in`). Every verdict is mathematically verifiable, producing a transparent audit trail with verbatim clause citations.

---

## 🚀 Key Modules & Architecture

```
                                 ┌────────────────────────────────────────────────────────┐
                                 │                   CITIZEN / KIOSK                      │
                                 └──────────────────────────┬─────────────────────────────┘
                                                            │
                            ┌───────────────────────────────┴───────────────────────────────┐
                            ▼                                                               ▼
           [📄 Revenue Cert / Marksheet]                                   [🏛️ Live Government Gazette / URL]
                            │                                                               │
                            ▼                                                               ▼
       ┌───────────────────────────────────────────┐                   ┌───────────────────────────────────────────┐
       │   Gemma 4 Multimodal Document Ingest     │                   │     Gemma 4 Live Policy URL Compiler      │
       │   (RD Barcode, Income, Domicile, Marks)   │                   │    (Transforms Circular HTML -> Rule DSL) │
       └────────────────────┬──────────────────────┘                   └────────────────────┬──────────────────────┘
                            │                                                               │
                            └───────────────────────────────┬───────────────────────────────┘
                                                            ▼
                                        ┌───────────────────────────────────────┐
                                        │    Pure Deterministic Rules Engine    │
                                        │ (Zero LLM Verdict • Auditable Proofs) │
                                        └───────────────────┬───────────────────┘
                                                            │
                            ┌───────────────────────────────┴───────────────────────────────┐
                            ▼                                                               ▼
               [🟢 ELIGIBLE / 🔴 INELIGIBLE]                                   [🔮 What-If Policy Simulation]
                            │                                                               │
                            ▼                                                               ▼
       ┌───────────────────────────────────────────┐                   ┌───────────────────────────────────────────┐
       │ 🚀 Direct Apply to myScheme.gov.in / Portals│                   │   💡 Shortest-Path Remediation Levers    │
       │ ✍️ Auto-Draft Official Application Letters │                   │ (e.g. +3% marks unlocks ₹25k NSP Merit)   │
       └───────────────────────────────────────────┘                   └───────────────────────────────────────────┘
```

### 1. 📥 Step 1: Upload & Auto-Scan
- Multimodal drag-and-drop document intake for Tahsildar Income Certificates (RD numbers), Caste Certificates, and academic marksheets.
- Extract attributes (income, caste, marks, validity) with instant verification confidence scores and seal detection.

### 2. 👤 Step 2: Citizen Profile Dashboard
- Reactive, type-safe profile manager with persona presets:
  - 👩‍🎓 *Merit Scholar (Post-Matric)*
  - 🌾 *Farmer Child (CM Raita Vidya Nidhi)*
  - 🇮🇳 *National Scholar (Central NSP)*
  - 👩‍💻 *Girl in Tech (AICTE Pragati)*
- Real-time synchronization across the mathematical prover.

### 3. ⚖️ Step 3: Verified Scheme Matches
- Pure mathematical clause evaluation with zero hallucination guarantee.
- Expandable clause-by-clause audit proofs citing statutory guidelines.
- **National Portal Integration**: Direct one-click application via **[myScheme.gov.in](https://www.myscheme.gov.in)** and direct state department systems (SSP Karnataka, MahaDBT, Pudhumai Penn, etc.).

### 4. 🔮 Step 4: What-If Simulation Sandbox
- Dynamic sliders for marks, income, and social levers to simulate eligibility shifts in real-time.
- Unlocks shortest-path remediation levers (e.g., obtaining a FRUITS Farmer ID unlocks CM Raita Vidya with *no* family income cap).

### 5. 📅 Document Validity & Deadline Tracker
- Citizen statutory deadline calendar (2026-2027).
- Real-time countdowns for expiring certificates with one-click **iCalendar (.ics) export** for Google/Apple Calendar.

### 6. 🏛️ Pan-India Registry & Official Letter Generator
- Search across 28 Indian States & Central Portals.
- Paste any live government scheme URL to compile rules on the fly via Gemma 4.
- Official printable letter generator (Application Cover Letter, Tahsildar Expedited Renewal, Institutional Bonafide Request, NPCI Bank Aadhaar Seeding).

### 7. 🟡 🔴 Native Kannada Language Converter
- Floating bottom-left converter button (`🟡 🔴 ಕನ್ನಡಕ್ಕೆ ಬದಲಾಯಿಸಿ`) that immediately transforms the interface, metrics, badges, and audit trails into authentic GovTech Kannada.

### 8. 🗺️ Citizen Service Centers (Kiosks)
- Interactive OpenStreetMap integration pinpointing Grama One and Bangalore One centers with direct contact info and GPS coordinates.

---

## 🛠️ Tech Stack

| Layer | Technologies |
|---|---|
| **Frontend** | Streamlit (Python), Custom CSS (IndiaStack / DigiLocker Motif), Leaflet.js |
| **Backend API** | FastAPI, Uvicorn, Pydantic V2 |
| **AI / Vision** | Gemma 4 (`gemma4:e4b`), LLaMA 3.2 (`llama3.2:3b`), Ollama API |
| **Security** | ZeroTrust Client Encryption (AES-256), SHA-256 Consent Receipts |
| **Integrations** | myScheme.gov.in, Seva Sindhu, SSP Karnataka, NSP National Portal |

---

## 💻 Local Setup & Installation

### Prerequisites
- Python 3.10 or higher
- Git installed on your machine
- *(Optional)* [Ollama](https://ollama.ai) installed with `ollama pull gemma4:e4b` or `llama3.2:3b`

### 1. Clone the Repository
```bash
git clone https://github.com/Nakul-sudo-cool/yogya-civicprover.git
cd yogya-civicprover
```

### 2. Create Virtual Environment & Install Dependencies
```bash
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Start the FastAPI Backend Engine
```bash
cd backend
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```
Backend Swagger API documentation will be available at: `http://127.0.0.1:8000/docs`

### 4. Start the Streamlit Frontend Web App
In a second terminal window:
```bash
# Ensure virtualenv is active
cd frontend
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## 🌐 How to Publish Live

### Option 1: Streamlit Community Cloud (100% Free & 1-Click)
1. Push your repository to GitHub (see instructions below).
2. Go to [share.streamlit.io](https://share.streamlit.io) and log in with your GitHub account.
3. Click **"New App"**.
4. Select your repository: `Nakul-sudo-cool/yogya-civicprover`.
5. Set **Main file path** to: `frontend/app.py`.
6. Click **"Deploy"**! You will receive a free public link (e.g. `https://yogya.streamlit.app`).

### Option 2: Render / Railway / Koyeb (Full-Stack Backend + Frontend)
- Deploy `backend/main.py` as a Python Web Service on [Render](https://render.com) (`uvicorn main:app --host 0.0.0.0 --port $PORT`).
- Update the frontend API URL in `frontend/app.py` or through the in-app sidebar setting.

---

## 📜 License
Distributed under the **MIT License**. See `LICENSE` for more information.

---

## 🤝 Acknowledgements
- **M.S. Ramaiah Institute of Technology (MSRIT)** & **IEEE CIS**
- **IndiaStack**, **myScheme.gov.in**, and **DigiLocker** open standards
- **Google DeepMind** for the open-weight Gemma model series
