import os, json, re
from google import genai
from .models import CitizenProfile

def _client():
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        return None
    return genai.Client(api_key=key)

def extract_profile(text: str, defaults: dict) -> tuple[CitizenProfile, str]:
    """Extract profile with Gemini when configured; safely fall back to form values."""
    client = _client()
    if client:
        prompt = f"""
Extract only facts explicitly stated by the citizen. Do not guess missing values.
Return ONLY valid JSON matching these fields:
name, age, state, district, annual_income, occupation, education, gender,
category, disability, marital_status, family_size, need.
For unknown values use null. annual_income must be a number in INR per year.
Citizen text: {text}
"""
        try:
            response = client.models.generate_content(
                model=os.getenv("GEMINI_MODEL", "gemini-2.0-flash"),
                contents=prompt
            )
            raw = response.text.strip().replace("```json", "").replace("```", "")
            data = json.loads(raw)
            merged = {**defaults, **{k:v for k,v in data.items() if v is not None}}
            return CitizenProfile.model_validate(merged), "Gemini extraction + Pydantic validation"
        except Exception:
            pass
    # Rule-based fallback: form data remains the source of truth.
    merged = dict(defaults)
    age_match = re.search(r"\b(\d{1,3})\s*(?:year|வயது)", text, re.I)
    income_match = re.search(r"(?:income|வருமானம்)[^\d]{0,20}([\d,]+)", text, re.I)
    if age_match and "age" not in merged:
        merged["age"] = int(age_match.group(1))
    if income_match and not merged.get("annual_income"):
        merged["annual_income"] = float(income_match.group(1).replace(",", ""))
    if text.strip():
        merged["need"] = text.strip()[:300]
    return CitizenProfile.model_validate(merged), "Form-based fallback (Gemini key not configured or unavailable)"

def ask_gemini(question: str, context: str) -> str:
    client = _client()
    if not client:
        return ("Gemini API key is not configured. Use the official source links shown above. "
                "This assistant will not invent scheme rules or deadlines.")
    prompt = f"""
You are BharatScheme AI, a cautious public-benefits information assistant.
Answer using ONLY the supplied retrieved scheme context. If the context does not answer
something, clearly say it needs official verification. Never guarantee approval or invent
deadlines, fees, documents, contacts, or URLs. Keep the answer clear and practical.
Context:
{context[:12000]}
Citizen question: {question}
"""
    try:
        r = client.models.generate_content(
            model=os.getenv("GEMINI_MODEL", "gemini-2.0-flash"),
            contents=prompt
        )
        return r.text or "I could not generate an answer. Please use the official source."
    except Exception as e:
        return f"AI assistant is temporarily unavailable. Please check the official source links. ({type(e).__name__})"
