# 🎨 ComicCraft - AI Comic Story Creator

ComicCraft is a FastAPI-based AI application that turns your creative story ideas into complete 5-panel comic strips using Google Gemini, Pillow, and FPDF2.

---

## ✨ Features
- **5-Panel Structured Generation**: Powered by Google Gemini (`gemini-3.5-flash`), crafting consistent narrative progression (Beginning, Discovery, Challenge, Climax, Resolution).
- **Stylized Visual Panels**: Generates formatted comic panel images with custom borders, character dialogue bubbles, and art style themes.
- **Instant PDF Export**: Automatically compiles the generated story and visual panels into a downloadable comic book PDF using `fpdf2`.
- **Interactive Web Interface**: Clean UI built with Jinja2 and vanilla CSS/JS.

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.10+
- A Google Gemini API Key from [Google AI Studio](https://aistudio.google.com/)

### 2. Installation
```bash
# Clone the repository
git clone https://github.com/deeparangaiah203-maker/ComicCraft.git
cd ComicCraft

# Create and activate virtual environment
python -m venv env
source env/bin/activate    # On Windows: .\env\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration
Copy `.env.example` to `.env` and fill in your Gemini API key:
```env
GEMINI_API_KEY=your_actual_api_key_here
MOCK_MODE=false
APP_HOST=127.0.0.1
APP_PORT=8000
```

### 4. Run the Application
```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
Open your browser and navigate to:
👉 **http://127.0.0.1:8000**

---

## 📁 Project Structure
```text
comic-craft/
├── app/
│   ├── config.py                  # Settings & environment configuration
│   ├── gemini_flash.py            # Gemini story planner & outline generation
│   ├── main.py                    # FastAPI entrypoint & static mounting
│   ├── routes.py                  # Web & API endpoints
│   ├── models/
│   │   └── schemas.py             # Pydantic schemas (ComicOutline, ComicPanel)
│   └── services/
│       ├── gemini_client.py       # Google GenAI client initialization
│       └── image_generator.py     # Pillow comic rendering & PDF exporter
├── templates/
│   ├── index.html                 # Story creation form
│   ├── comic_preview.html         # 5-panel comic viewer
│   └── export_success.html        # PDF export confirmation
├── requirements.txt               # Dependencies
└── .gitignore                     # Protects environment keys & cache
```
