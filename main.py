from fastapi import FastAPI
from pydantic import BaseModel
import requests
import os

app = FastAPI()

# =========================
# 🔐 CONFIG
# =========================
API_KEY = os.getenv("OPENROUTER_API_KEY")
URL = "https://openrouter.ai/api/v1/chat/completions"

# =========================
# 📦 MODELS
# =========================

class DebateInput(BaseModel):
    topic: str
    side: str
    user_text: str

class DebateAnalysisInput(BaseModel):
    user_text: str

class StoryInput(BaseModel):
    words: list
    story: str

class RapidFireInput(BaseModel):
    topic: str
    speech: str
    constraint_words: list
    forbidden_words: list

# =========================
# 🔥 COMMON AI FUNCTION
# =========================

def ask_ai(prompt):
    try:
        response = requests.post(
            URL,
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "HTTP-Referer": "https://debate-backend-9azm.onrender.com",
                "X-Title": "Speech Arena",
                "Content-Type": "application/json"
            },
            json={
                "model": "meta-llama/llama-3-8b-instruct",
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "You are a STRICT professional evaluator.\n"
                            "You MUST follow output format EXACTLY.\n"
                            "You are NOT allowed to:\n"
                            "- Skip any field\n"
                            "- Add extra explanation\n"
                            "- Change format\n"
                            "- Give fake feedback\n\n"
                            "All scores must be REAL and based on input.\n"
                            "All mistakes must be from actual text.\n"
                            "If no mistakes → write 'None'.\n"
                            "If no improvements → write 'Good job'.\n\n"
                            "Output must be COMPLETE and VALID always."
                        )
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": 300,
                "temperature": 0.2
            },
            timeout=30
        )

        if response.status_code != 200:
            return None

        data = response.json()

        if "choices" in data:
            return data["choices"][0]["message"]["content"].strip()

        return None

    except Exception:
        return None


# =========================
# 🔥 DEBATE API
# =========================

@app.post("/debate")
def debate(data: DebateInput):

    prompt = f"""
Topic: {data.topic}
User side: {data.side}

User argument:
{data.user_text}

OUTPUT FORMAT:
Line 1: Attack user's argument
Line 2: Show benefit of your side
Line 3: Ask one question

RULES:
- EXACTLY 3 lines
- No explanation
- Simple sentences
"""

    result = ask_ai(prompt)

    if result is None:
        result = "Your argument is weak.\nMy side is stronger.\nWhy ignore this?"

    return {"reply": result}


# =========================
# 🏁 DEBATE ANALYSIS
# =========================

@app.post("/debate-analysis")
def debate_analysis(data: DebateAnalysisInput):

    prompt = f"""
Analyze ONLY the user's argument.

TEXT:
{data.user_text}

STRICT OUTPUT FORMAT:

Grammar Errors: <number>
Grammar Score: <number>/10

Overall Score: <number>/10
Relevance: <number>/10
Clarity: <number>/10
Structure: <number>/10

Mistakes:
- real mistake from text
- real mistake from text

Improvements:
- based on mistake
- based on mistake

STRICT RULES:
- MUST include ALL fields
- MUST include Overall Score
- Scores must be between 0–10
- DO NOT invent mistakes
- DO NOT skip anything
- DO NOT output invalid format
"""

    result = ask_ai(prompt)

    if result is None or "Overall Score" not in result:
        return {"ai_feedback": "ERROR: AI failed. Please retry."}

    return {"ai_feedback": result}


# =========================
# 📖 STORY ANALYSIS
# =========================

@app.post("/story-analysis")
def story_analysis(data: StoryInput):

    words = ", ".join(data.words)

    prompt = f"""
Story:
{data.story}

Required Words:
{words}

STRICT OUTPUT FORMAT:

Grammar Score: <number>/10
Structure: <number>/10
Creativity: <number>/10
Clarity: <number>/10
Word Usage: <number>/10

Overall Score: <number>/10

Mistakes:
- real mistake
- real mistake

Improvements:
- based on mistake
- based on mistake

STRICT RULES:
- Must use real analysis
- No fake mistakes
- If perfect → Mistakes: None
- If perfect → Improvements: Good job
- MUST include Overall Score
"""

    result = ask_ai(prompt)

    if result is None or "Overall Score" not in result:
        return {"ai_feedback": "ERROR: AI failed. Please retry."}

    return {"ai_feedback": result}


# =========================
# ⚡ RAPID FIRE ANALYSIS
# =========================

@app.post("/rapid-fire-analysis")
def rapidfire_analysis(data: RapidFireInput):

    constraints = ", ".join(data.constraint_words)
    forbidden = ", ".join(data.forbidden_words)

    prompt = f"""
Analyze this speech STRICTLY.

Topic: {data.topic}

Speech:
{data.speech}

Must Use Words:
{constraints}

Forbidden Words:
{forbidden}

STRICT OUTPUT FORMAT:

Grammar Score: <number>/10
Relevance: <number>/10
Clarity: <number>/10
Structure: <number>/10
Constraint Usage: <number>/10
Forbidden Usage: <number>/10

Overall Score: <number>/10

Mistakes:
- real mistake OR None

Improvements:
- real improvement OR Good job

STRICT RULES:
- MUST include ALL fields
- MUST include Overall Score
- DO NOT say "could not analyze"
- DO NOT say "try again"
- DO NOT generate fake mistakes
- Scores must reflect actual speech
- If perfect → Mistakes: None
- If perfect → Improvements: Good job
"""

    result = ask_ai(prompt)

    if result is None or "Overall Score" not in result:
        return {"ai_feedback": "ERROR: AI failed. Please retry."}

    return {"ai_feedback": result}


# =========================
# ✅ ROOT
# =========================

@app.get("/")
def home():
    return {"status": "Backend running successfully"}