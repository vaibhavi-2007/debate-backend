from fastapi import FastAPI
from pydantic import BaseModel
import requests
import os

app = FastAPI()

# =========================
# 🔐 OPENROUTER CONFIG
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
# 🔥 COMMON AI FUNCTION
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
                        "content": "You are a strict AI evaluator. Follow format EXACTLY. Never skip fields."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": 150,
                "temperature": 0.4
            },
            timeout=30
        )

        data = response.json()

        if "choices" in data:
            return data["choices"][0]["message"]["content"].strip()

        return "⚠️ AI error"

    except Exception as e:
        return f"⚠️ {str(e)}"

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
- Take opposite side
- Give ONLY 2 short points + 1 question

RULES:
- Line 1: Attack user's argument
- Line 2: Show benefit of your side
- Line 3: Ask one short question
- Use simple sentences
- Do NOT explain

OUTPUT:
Your argument is weak.
My side gives better results.
Why ignore this advantage?
"""

    return {"reply": ask_ai(prompt)}

# =========================
# 🏁 DEBATE ANALYSIS
# =========================

@app.post("/debate-analysis")
def debate_analysis(data: DebateAnalysisInput):

    full_text = " ".join(data.conversation)

    prompt = f"""
Analyze the debate:

{full_text}

STRICT RULES:
- Follow format EXACTLY
- Do NOT skip anything

EVALUATE:
Grammar, Relevance, Clarity, Structure

OUTPUT:

Grammar Errors: <number>
Grammar Score: <score>/10

Overall Score: <score>/10
Relevance: <score>/10
Clarity: <score>/10
Structure: <score>/10

Mistakes:
- grammar issue
- unclear sentence
- weak logic

Improvements:
- fix grammar
- improve clarity
- strengthen argument
"""

    result = ask_ai(prompt)

    if "Overall Score" not in result:
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
- Use correct grammar
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

Given words:
{words}

CHECK:
- Grammar
- Structure
- Creativity
- Clarity
- Word usage (important)

RULES:
- Missing words → reduce score
- Creative story → high score

OUTPUT:

Grammar Score: X/10
Structure: X/10
Creativity: X/10
Clarity: X/10
Word Usage: X/10

Overall Score: X/10

Mistakes:
- grammar issue
- missing words
- weak story

Improvements:
- improve grammar
- use all words
- add creativity
"""

    return {"ai_feedback": ask_ai(prompt)}

# =========================
# ⚡ RAPID FIRE ANALYSIS
# =========================

@app.post("/rapidfire-analysis")
def rapidfire_analysis(data: RapidFireInput):

    constraints = ", ".join(data.constraint_words)
    forbidden = ", ".join(data.forbidden_words)

    prompt = f"""
Topic: {data.topic}

Speech:
{data.speech}

Must use words:
{constraints}

Forbidden words:
{forbidden}

CHECK:
- Grammar
- Relevance
- Clarity
- Structure
- Constraint usage
- Forbidden usage

RULES:
- Missing constraint word → reduce score
- Using forbidden word → heavy penalty

OUTPUT:

Grammar Score: X/10
Relevance: X/10
Clarity: X/10
Structure: X/10
Constraint Usage: X/10
Forbidden Usage: X/10

Overall Score: X/10

Mistakes:
- grammar issue
- missing constraint word
- forbidden word used

Improvements:
- fix grammar
- use required words
- avoid forbidden words
"""

    return {"ai_feedback": ask_ai(prompt)}

# =========================
# ✅ ROOT (HEALTH CHECK)
# =========================

@app.get("/")
def home():
    return {"status": "Backend running successfully"}