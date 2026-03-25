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
    conversation: list

class StoryInput(BaseModel):
    words: list
    story: str

class RapidFireInput(BaseModel):
    topic: str
    speech: str
    constraint_words: list
    forbidden_words: list

# =========================
# 🔥 COMMON AI FUNCTION (STRICT)
# =========================

def ask_ai(prompt):
    try:
        response = requests.post(
            URL,
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "HTTP-Referer": "https://debate-backend-9azm.onrender.com",
                "X-Title": "Debate App",
                "Content-Type": "application/json"
            },
            json={
                "model": "meta-llama/llama-3-8b-instruct",
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "You are a STRICT AI evaluator.\n"
                            "You MUST follow the exact output format.\n"
                            "Do NOT skip any field.\n"
                            "Do NOT add extra explanation.\n"
                            "Only output the required format.\n"
                            "If format is broken, response is invalid."
                        )
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": 200,
                "temperature": 0.3
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
Line 3: Ask one short question

RULES:
- Only 3 lines
- Simple sentences
- No explanation
"""

    result = ask_ai(prompt)

    if result is None:
        result = "Your argument is weak.\nMy side is better.\nWhy ignore this?"

    return {"reply": result}


# =========================
# 🏁 DEBATE ANALYSIS
# =========================

@app.post("/debate-analysis")
def debate_analysis(data: DebateAnalysisInput):

    full_text = " ".join(data.conversation)

    prompt = f"""
Analyze the debate:

{full_text}

STRICT OUTPUT FORMAT:

Grammar Errors: <number>
Grammar Score: <number>/10

Overall Score: <number>/10
Relevance: <number>/10
Clarity: <number>/10
Structure: <number>/10

Mistakes:
- point
- point

Improvements:
- point
- point

RULES:
- Do NOT skip any field
- All scores must be 0–10
- Must include Overall Score
"""

    result = ask_ai(prompt)

    if result is None or "Overall Score" not in result:
        result = """Grammar Errors: 0
Grammar Score: 6/10

Overall Score: 6/10
Relevance: 6/10
Clarity: 6/10
Structure: 6/10

Mistakes:
- Analysis failed

Improvements:
- Try again
- Improve clarity
"""

    return {"ai_feedback": result}


# =========================
# 📖 STORY ANALYSIS
# =========================

@app.post("/story-analysis")
def story_analysis(data: StoryInput):

    words = ", ".join(data.words) if isinstance(data.words, list) else str(data.words)

    prompt = f"""
Story:
{data.story}

Words:
{words}

STRICT OUTPUT FORMAT:

Grammar Score: <number>/10
Structure: <number>/10
Creativity: <number>/10
Clarity: <number>/10
Word Usage: <number>/10

Overall Score: <number>/10

Mistakes:
- point
- point

Improvements:
- point
- point

RULES:
- Must include all fields
- Scores between 0–10
- Must include Overall Score
"""

    result = ask_ai(prompt)

    if result is None or "Overall Score" not in result:
        result = """Grammar Score: 6/10
Structure: 6/10
Creativity: 6/10
Clarity: 6/10
Word Usage: 6/10

Overall Score: 6/10

Mistakes:
- Analysis failed

Improvements:
- Improve grammar
"""

    return {"ai_feedback": result}


# =========================
# ⚡ RAPID FIRE ANALYSIS
# =========================

@app.post("/rapid-fire-analysis")
def rapidfire_analysis(data: RapidFireInput):

    constraints = ", ".join(data.constraint_words)
    forbidden = ", ".join(data.forbidden_words)

    prompt = f"""
Topic: {data.topic}

Speech:
{data.speech}

Must use:
{constraints}

Avoid:
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
- point
- point

Improvements:
- point
- point

RULES:
- Must include ALL fields
- Scores must be 0–10
- MUST include Overall Score
- No extra text outside format
"""

    result = ask_ai(prompt)

    if result is None or "Overall Score" not in result:
        result = """Grammar Score: 6/10
Relevance: 6/10
Clarity: 6/10
Structure: 6/10
Constraint Usage: 5/10
Forbidden Usage: 7/10

Overall Score: 6/10

Mistakes:
- Could not analyze properly

Improvements:
- Try again
"""

    return {"ai_feedback": result}


# =========================
# ✅ ROOT
# =========================

@app.get("/")
def home():
    return {"status": "Backend running successfully"}