# Multimodal Construction Intelligence Platform

[![Deploy to Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/deploy?repository=Abhay1037/multimodal-construction-ai&branch=main&mainModule=streamlit_app/app.py)

## 🌐 Live Demo

**https://multimodal-construction-ai-ormdkzq6w8tjyhfcjsjjjy.streamlit.app/**

> If the link asks for a Streamlit login, set the app visibility to **Public** (Streamlit Cloud → app menu ⋮ → Settings → Sharing).

AI-powered construction platform that combines multimodal LLaMA vision models, project cost
estimation, and generative AI (Flux / Pollinations) image generation into a single full-stack
dashboard.

## Tech Stack

- **Backend:** Python 3.9+, FastAPI, Uvicorn, Pillow, Requests / httpx, Pydantic, python-dotenv
- **Frontend:** React.js (Vite), Tailwind CSS, Axios, Lucide-react
- **AI Models & APIs:**
  1. **Meta LLaMA** (Vision + Text LLM) via Groq Cloud / Together AI / HuggingFace Inference API — used for
     intelligent site safety monitoring, structural crack detection, and project planning insights.
  2. **Pollinations / Flux** image models — used for AI-based construction visualization and
     architectural concept rendering.

## Project Structure

```
construction-ai-platform/
├── backend/
│   ├── .env.example
│   ├── requirements.txt
│   ├── main.py
│   ├── services/
│   │   ├── llama_service.py
│   │   └── pollination_service.py
│   └── schemas/
│       └── models.py
├── frontend/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   └── src/
│       ├── main.jsx
│       ├── App.jsx
│       ├── index.css
│       └── components/
│           ├── Navbar.jsx
│           ├── SiteInspection.jsx
│           ├── ProjectPlanning.jsx
│           ├── ConstructionVisualization.jsx
│           └── ResultCard.jsx
└── README.md
```

## Backend API Endpoints

| Method | Endpoint | Description |
| ------ | -------- | ----------- |
| GET | `/api/health` | Health check |
| POST | `/api/analyze-site` | Multipart form-data upload of a site photo + `analysis_type` (`safety_monitoring` \| `crack_detection`) |
| POST | `/api/plan-estimate` | JSON body with `plot_size_sqft`, `budget_usd`, `category`, `timeline_weeks` → structured construction plan |
| POST | `/api/generate-visualization` | JSON body with `prompt` → Pollinations / Flux image URL |

### LLaMA Response Contract (`services/llama_service.py`)

```json
{
  "status": "Safe",
  "confidence_score": 87.5,
  "summary": "Site conditions observed are generally compliant.",
  "findings": ["..."],
  "action_items": ["..."]
}
```

## Project 1 Quickstart — Streamlit App (Multimodal Construction Intelligence Platform)

The capstone Streamlit application lives in `streamlit_app/`:

```bash
cd construction-ai-platform/streamlit_app
python -m venv venv
source venv/bin/activate        # Linux / macOS
# venv\Scripts\activate         # Windows

pip install -r requirements.txt

streamlit run app.py
```

The app opens at `http://localhost:8501`.

### Streamlit App Features
1. **Site Safety & PPE Audit** — multimodal photo upload with PPE compliance checklist (OSHA / IS 456), safety score, hazards and downloadable JSON report.
2. **Crack Diagnostics & Structural Integrity** — defect classification (Hairline, Settlement, Structural Shear, Thermal Expansion, Spalling), crack width, root causes and engineering repairs.
3. **Planning & Real Estate Valuation** — budget / CAPEX / market valuation in INR, steel & cement requirements, milestone progress bar, Pollinations/Flux 3D architectural rendering.
4. **Daily Site Assistant & Weather-Aware Advisory** — weather-condition safety alerts and interactive construction chatbot.

### Streamlit Secrets
Create `streamlit_app/.streamlit/secrets.toml` (or set env vars) for:
```toml
GEMINI_API_KEY = "your_gemini_api_key"
```
Without a key, the app runs in graceful **Demonstration Mode**.

### Deploy to Streamlit Community Cloud (1-Click)

Repository: `https://github.com/Abhay1037/multimodal-construction-ai`

1. Go to **https://share.streamlit.io** and sign in with GitHub.
2. Click **Create app** → **Deploy a public app from GitHub**.
3. Fill in:
   - **Repository:** `Abhay1037/multimodal-construction-ai`
   - **Branch:** `main`
   - **Main file path:** `streamlit_app/app.py`
4. Open **Advanced settings**:
   - **Python version:** `3.12` (recommended — `google-generativeai` compatibility)
   - **Secrets** (optional):
     ```toml
     GEMINI_API_KEY = "your_gemini_api_key"
     ```
5. Click **Deploy**. The app will be live at `https://<your-app-name>.streamlit.app`.

The repository root includes `requirements.txt` and `.streamlit/config.toml` so no extra configuration is needed. Without a Gemini key the app still works in Demonstration Mode.

## Local Setup

### 1. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Linux / macOS
# venv\Scripts\activate         # Windows

python -m pip install -r requirements.txt
cp .env.example .env             # then fill in GROQ_API_KEY / POLLINATIONS keys

python -m uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`.

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

The Vite dev server proxies `/api` requests to `http://localhost:8000` (see `vite.config.js`).
The app will be available at `http://localhost:5173`.

## Environment Variables

Copy `backend/.env.example` to `backend/.env` and configure:

- `GROQ_API_KEY` — Groq Cloud API key for LLaMA vision/text models
- `LLAMA_MODEL` — LLaMA model identifier (default: `llama-3.2-11b-vision-preview`)
- `LLAMA_TIMEOUT_SECONDS` — request timeout
- `POLLINATIONS_API_KEY` — Pollinations API key (optional for public Flux access)
- `POLLINATIONS_BASE_URL` — Pollinations base URL (default: `https://image.pollinations.ai/prompt`)
