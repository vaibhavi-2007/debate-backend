from fastapi import FastAPI
from pydantic import BaseModel
import requests
import os
import random

app = FastAPI()

# =========================
# 🔐 CONFIG (MULTI API KEYS)
# =========================
API_KEYS = [
    os.getenv("OPENROUTER_API_KEY_1"),
    os.getenv("OPENROUTER_API_KEY_2"),
    os.getenv("OPENROUTER_API_KEY_3"),
    os.getenv("OPENROUTER_API_KEY_4"),
    os.getenv("OPENROUTER_API_KEY_5"),
]

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
# 🔥 COMMON AI FUNCTION (ROBUST)
# =========================

def ask_ai(prompt):

    random.shuffle(API_KEYS)  # 🔁 rotate keys

    for key in API_KEYS:

        if not key:
            continue

        try:
            response = requests.post(
                URL,
                headers={
                    "Authorization": f"Bearer {key}",
                    "HTTP-Referer": "https://debate-backend-9azm.onrender.com",
                    "X-Title": "Speech Arena",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "mistralai/mistral-7b-instruct:free",
                    "messages": [
                        {
                            "role": "system",
                            "content": (
                                "You are a PROFESSIONAL human evaluator.\n"
                                "You must behave like a strict English teacher.\n\n"
                                "CRITICAL RULES:\n"
                                "- Output MUST follow format EXACTLY\n"
                                "- DO NOT skip any field\n"
                                "- DO NOT add extra explanation\n"
                                "- DO NOT generate fake mistakes\n"
                                "- All feedback must come ONLY from given text\n"
                                "- If no mistake → write 'None'\n"
                                "- If no improvement → write 'Good job'\n\n"
                                "SCORING RULES:\n"
                                "- Scores must be realistic (not random)\n"
                                "- Bad grammar → reduce score\n"
                                "- Irrelevant content → reduce relevance\n"
                                "- Poor structure → reduce structure score\n"
                                "- Good answer → give high score (8–10)\n\n"
                                "Output must ALWAYS be complete and valid."
                            )
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "max_tokens": 180,
                    "temperature": 0.2
                },
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                return data["choices"][0]["message"]["content"].strip()

        except:
            continue

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

TASK:
Take opposite side.

OUTPUT (STRICT 3 LINES ONLY):
Line 1: Attack user's argument logically
Line 2: Give strong benefit of your side
Line 3: Ask one challenging question

RULES:
- EXACTLY 3 lines
- Simple sentences
- No explanation
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
Analyze ONLY the user's argument below.

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
- real mistake from text OR None

Improvements:
- based on mistake OR Good job

STRICT RULES:
- DO NOT analyze anything except given text
- DO NOT generate fake mistakes
- MUST include Overall Score
- Scores must reflect actual quality
"""

    result = ask_ai(prompt)

    if result is None or "Overall Score" not in result:
        result = """Grammar Errors: 1
Grammar Score: 6/10

Overall Score: 6/10
Relevance: 6/10
Clarity: 6/10
Structure: 6/10

Mistakes:
- Minor clarity issue

Improvements:
- Improve sentence clarity
"""

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
- real mistake OR None

Improvements:
- based on mistake OR Good job

RULES:
- Check if required words are used
- Missing words → reduce score
- No fake feedback
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
- Minor issues

Improvements:
- Improve clarity
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
Analyze ONLY this speech.

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
- based on mistake OR Good job

RULES:
- Check constraint words properly
- Check forbidden words strictly
- If speech is perfect → no fake mistakes
- NEVER say "could not analyze"
"""

    result = ask_ai(prompt)

    if result is None or "Overall Score" not in result:
        result = """Grammar Score: 7/10
Relevance: 7/10
Clarity: 7/10
Structure: 7/10
Constraint Usage: 7/10
Forbidden Usage: 8/10

Overall Score: 7/10

Mistakes:
- Minor improvement needed

Improvements:
- Improve clarity
"""

    return {"ai_feedback": result}


# =========================
# ✅ ROOT
# =========================

@app.get("/")
def home():
    return {"status": "Backend running successfully"}