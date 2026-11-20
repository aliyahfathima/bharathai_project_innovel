# BharatScheme AI 🇮🇳
AI-powered government scheme discovery, eligibility comparison and application guidance.

## Features
- Citizen profile form + free-text description
- Gemini-based profile extraction (with safe form-based fallback)
- Pydantic validation for structured citizen profiles
- Tavily live search restricted to government domains
- Conservative eligibility labels:
  - Potential Match
  - Possible Match
  - More Information Required
  - Potential Mismatch
- Source-linked result cards and application guidance
- Gemini follow-up assistant grounded in retrieved search snippets
- SQLite search history
- Attractive Streamlit UI

## 1. Requirements
- Python 3.10 or newer
- Tavily API key: https://tavily.com/
- Gemini API key: https://aistudio.google.com/app/apikey

## 2. Installation (Windows)
Extract the ZIP. Open Command Prompt inside the `BharatScheme_AI` folder.

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## 3. Configure API keys
1. Make a copy of `.env.example`.
2. Rename the copy to `.env`.
3. Add your API keys:

```env
TAVILY_API_KEY=your_real_tavily_key
GEMINI_API_KEY=your_real_gemini_key
GEMINI_MODEL=gemini-2.0-flash
```

Do not share `.env` or upload it to GitHub.

## 4. Run
```bash
streamlit run app.py
```
Streamlit will show a local URL, usually http://localhost:8501.

## 5. Demo / fallback mode
- Without a Gemini key, the form still works using Pydantic-validated form data.
- Without a Tavily key, the app runs but live search is unavailable.
- For actual live scheme discovery, configure Tavily.
- For AI profile extraction and follow-up Q&A, configure Gemini.

## Project structure
```text
BharatScheme_AI/
├── app.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
└── modules/
    ├── __init__.py
    ├── ai.py
    ├── eligibility.py
    ├── models.py
    ├── search.py
    └── storage.py
```

## Important accuracy & safety notes
- Search results are official-domain leads, not proof that a citizen qualifies.
- Eligibility comparison is intentionally conservative and only detects a few simple conditions from snippets.
- Complex rules, category certificates, residency periods, exclusions and special cases must be checked on the official scheme notification.
- Application steps shown are a safe general checklist. Scheme-specific documents, deadlines, contacts and benefit amounts are not fabricated.
- Never enter Aadhaar numbers, OTPs, bank details or other sensitive identifiers.
- This is a prototype, not a government service and not affiliated with any government department.

## Suggested demo flow
1. Select Tamil Nadu, Madurai, age 21, student and annual income ₹2,00,000.
2. Select Scholarship / college fee support.
3. Add a short description of the student's situation.
4. Click **Find My Eligible Schemes**.
5. Open each result's eligibility analysis and official source link.
6. Ask the AI assistant what needs verification before applying.
