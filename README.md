# MedNova AI

> **AI-Assisted Early Identification of Rare Diseases Using Generative Medical Data and Clinical Information**

MedNova AI is a translational medical informatics research and educational prototype designed to accelerate the early identification of rare, atypical, and complex medical conditions. By combining patient-reported symptoms, structured clinical indicators, and verified medical registries with bounded generative artificial intelligence (via Google Gemini), MedNova AI generates structured differential discussion summaries for licensed clinical specialists.

---

## ⚠️ Important Medical Safety & Research Disclaimer

- **Educational & Research Prototype Only:** MedNova AI is **NOT** a certified medical diagnostic device or Software as a Medical Device (SaMD).
- **Non-Diagnostic:** The application never declares a confirmed diagnosis or excludes conditions.
- **Segregated Information Layers:** User-reported symptoms, AI-generated differential possibilities, and verified medical registry facts are strictly separated.
- **No Treatment Guidance:** MedNova AI will never recommend starting, modifying, or discontinuing pharmacotherapy or treatment protocols.
- **Synthetic Data Requirement:** Users must utilize de-identified, synthetic, or academic educational case vignettes.

---

## Core Features

- **Generative AI Clinical Triangulation:** Powered by Google's official `google-genai` SDK with strict clinical prompt bounding and structured JSON output normalization.
- **Curated Rare Disease Knowledge Base:** Verified entries cross-referenced against authoritative registries (**Orphanet**, **NORD**, **NIH GARD**, **MedlinePlus**).
- **Clinical Intake & Server-Side Validation:** Validates patient age, sex/gender, symptom progression, medical history, and consent with length and character safety limits.
- **Secure Medical Report Vault:** Upload and inspect laboratory reports (PDF and TXT up to 10MB) stored privately outside the public web root with cryptographic UUID naming.
- **Session-Bound History & Isolation:** Multi-case history tracked through isolated SQLite sessions, featuring single-click session clearing.
- **Healthcare-Inspired Responsive UI:** Modern, accessible interface featuring loading overlays to prevent duplicate submissions, status indicators, and print-optimized clinical exports.

---

## Technology Stack

- **Backend:** Python 3.11+ / 3.15, Flask 3.1, Flask-SQLAlchemy, Flask-WTF, python-dotenv
- **Generative AI:** Google GenAI Python SDK (`google-genai`)
- **Database:** SQLite with SQLAlchemy ORM
- **Testing:** Pytest 9.x
- **Frontend:** Semantic HTML5, CSS3, Vanilla JavaScript, Jinja2 Templates

---

## Project Structure

```text
meda nova ai/
├── app.py                     # Application entry point
├── config.py                  # Environment-driven configuration (Dev & Test)
├── wsgi.py                    # WSGI server entry point
├── requirements.txt           # Python package dependencies
├── pytest.ini                 # Pytest configuration
├── .env.example               # Environment variables template
├── .env                       # Local environment file (git-ignored)
├── .gitignore                 # Git ignore rules
├── README.md                  # Comprehensive documentation
├── app/
│   ├── __init__.py            # Application factory and error handlers
│   ├── extensions.py          # SQLAlchemy and CSRFProtect instances
│   ├── models.py              # PatientCase and UploadedReport ORM models
│   ├── forms.py               # WTForms with strict server validation
│   ├── routes/
│   │   ├── __init__.py        # Blueprint exports
│   │   ├── main.py            # Home, Dashboard, KB, and About routes
│   │   ├── analysis.py        # Patient intake and differential evaluation
│   │   ├── reports.py         # Secure document upload and deletion
│   │   └── history.py         # Session history and records management
│   ├── services/
│   │   ├── __init__.py        # Service exports
│   │   ├── gemini_service.py  # Google Gemini SDK integration with safe fallbacks
│   │   ├── disease_service.py # Curated rare disease registry search & matching
│   │   └── report_service.py  # File validation, UUID storage, and extraction
│   ├── knowledge_base/
│   │   └── rare_diseases.json # Verified rare disease database
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css      # Clinical stylesheet with responsive layouts
│   │   └── js/
│   │       └── main.js        # Mobile toggle, form locking, loading overlays
│   └── templates/
│       ├── base.html          # Base layout with disclaimers and navigation
│       ├── index.html         # Portal homepage and module highlights
│       ├── dashboard.html     # Clinical metrics and active session feed
│       ├── analysis.html      # Patient symptom intake form
│       ├── results.html       # Differential findings and disease matches
│       ├── reports.html       # Document vault and upload interface
│       ├── history.html       # Active session history
│       ├── knowledge_base.html# Rare disease registry directory and search
│       ├── knowledge_base_detail.html # Comprehensive disease monograph
│       ├── about.html         # Clinical ethics and project mission
│       └── errors/
│           ├── 400.html       # Bad Request handler
│           ├── 404.html       # Resource Not Found handler
│           ├── 413.html       # Payload Too Large handler
│           └── 500.html       # Internal Server Error handler
├── tests/
│   ├── conftest.py            # Pytest test fixtures with memory database
│   ├── test_routes.py         # HTTP route and navigation tests
│   ├── test_forms.py          # Server-side validation and boundary tests
│   └── test_services.py       # Services and mocked Gemini evaluation tests
└── uploads/                   # Private file storage (outside web root)
```

---

## Setup & Installation

### Prerequisites

- Python 3.11, 3.12, 3.13, 3.14, or 3.15 installed on your machine.
- Git (optional, for version management).

---

### macOS & Linux Setup

1. **Clone or open the project folder in terminal:**
   ```bash
   cd "meda nova ai"
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Set up the environment configuration:**
   ```bash
   cp .env.example .env
   ```

---

### Windows Setup (PowerShell or Command Prompt)

1. **Open PowerShell in the project directory:**
   ```powershell
   cd "meda nova ai"
   ```

2. **Create and activate a virtual environment:**
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```
   *(If script execution is disabled, run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`)*

3. **Install dependencies:**
   ```powershell
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Copy `.env.example` to `.env`:**
   ```powershell
   Copy-Item .env.example .env
   ```

---

## Gemini API Configuration

MedNova AI uses the official `google-genai` SDK.

1. Obtain a Google Gemini API key at **[Google AI Studio](https://aistudio.google.com/app/apikey)**.
2. Open your `.env` file and set the key:
   ```env
   GEMINI_API_KEY=your_actual_gemini_api_key_here
   GEMINI_MODEL=gemini-2.5-flash
   ```
3. **Graceful Demo Mode:** If `GEMINI_API_KEY` is left blank, the application operates smoothly in **Demonstration Mode**. Basic routing, curated registry matching, and report vaulting will function normally without errors.

---

## Running the Application

Ensure your virtual environment is active:

```bash
# macOS / Linux
source venv/bin/activate

# Windows
.\venv\Scripts\Activate.ps1
```

Start the Flask development server:

```bash
python app.py
```

Access the portal in your browser at:
👉 **`http://127.0.0.1:5000`**

---

## Running Automated Tests

MedNova AI includes an automated test suite verifying route integrity, server validation rules, CSRF tokens, file security, and mocked Gemini API behaviors.

Execute pytest with:

```bash
pytest -v
```

All 29 tests execute against an in-memory SQLite database and isolated mock fixtures.

---

## Security & Privacy Protections

1. **Strict File Upload Vault:** Uploads are restricted to `.pdf` and `.txt` up to 10MB, stored in `uploads/` with random UUID filenames.
2. **Path Traversal Prevention:** Upload file names and paths are sanitized and resolved against parent boundaries.
3. **Session-Bound Storage:** Historical patient records and documents are partitioned by the user's active session.
4. **CSRF Enforcement:** All HTML forms enforce cryptographic CSRF token validation via Flask-WTF.
5. **No Secret Leakage:** API keys and sensitive environment variables are never transmitted to frontend templates or logged.

---

## Troubleshooting

- **ModuleNotFoundError:** Ensure your virtual environment is activated (`source venv/bin/activate` or `.\venv\Scripts\Activate.ps1`) before executing commands.
- **Port 5000 in use on macOS:** macOS AirPlay receiver may occupy port 5000. You can disable AirPlay Receiver in System Settings &gt; General &gt; AirDrop &amp; Handoff, or specify an alternative port: `PORT=5001 python app.py`.
- **Gemini API Error:** Check that your API key is active and that your region supports Gemini 2.5 Flash via Google AI Studio.

---

## License & Attribution

Developed for academic research and medical informatics education. 
Curated disease profiles reference verified public resources including **Orphanet** (orphadata), **NORD** (National Organization for Rare Disorders), and the **NIH Genetic and Rare Diseases Information Center (GARD)**.
