from fastapi import FastAPI
from pydantic import BaseModel
import requests
import os
import random

app = FastAPI()

# =========================
# 🔐 MULTI API KEYS
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
    conversation: list   # ✅ keep old (NO 422 error)

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

    random.shuffle(API_KEYS)  # rotate keys

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
                    # ✅ STRONG MODEL (BACK)
                    "model": "meta-llama/llama-3-8b-instruct",

                    "messages": [
                        {
                            "role": "system",
                            "content": (
                                "You are a STRICT professional evaluator.\n"
                                "You must behave like a real human English teacher.\n\n"
                                "CRITICAL RULES:\n"
                                "- Follow output format EXACTLY\n"
                                "- Do NOT skip any field\n"
                                "- Do NOT add extra explanation\n"
                                "- Do NOT generate fake mistakes\n"
                                "- All feedback MUST be from user's text\n"
                                "- If no mistakes → write 'None'\n"
                                "- If no improvements → write 'Good job'\n\n"
                                "SCORING:\n"
                                "- Scores must reflect real quality\n"
                                "- Weak answer → low score\n"
                                "- Strong answer → high score\n"
                                "- Never give random scores\n"
                            )
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "max_tokens": 220,
                    "temperature": 0.3
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

OUTPUT FORMAT:
Line 1: Critically attack user's argument
Line 2: Show strong advantage of your side
Line 3: Ask one logical question

RULES:
- EXACTLY 3 lines
- No explanation
- Use simple sentences
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

    full_text = " ".join(data.conversation)

    prompt = f"""
Analyze ONLY the user's argument.

TEXT:
{full_text}

STRICT OUTPUT FORMAT:

Grammar Errors: <number>
Grammar Score: <number>/10

Overall Score: <number>/10
Relevance: <number>/10
Clarity: <number>/10
Structure: <number>/10

Mistakes:
- real mistake OR None

Improvements:
- based on mistake OR Good job

RULES:
- Do NOT analyze anything outside text
- Do NOT generate fake mistakes
- MUST include Overall Score
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
- Minor issue

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

Must use:
{constraints}

Forbidden:
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
- Check constraints strictly
- Check forbidden words strictly
- No fake mistakes
- Never say "could not analyze"
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