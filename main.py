from fastapi import FastAPI
from pydantic import BaseModel
import requests
import os

app = FastAPI()

# =========================
# 🔐 OPENROUTER CONFIG
# =========================
API_KEY = os.getenv("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")

URL = "https://openrouter.ai/api/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# =========================
# 📦 MODELS
# =========================

class DebateInput(BaseModel):
    topic: str
    side: str
    user_text: str

class AnalysisInput(BaseModel):
    topic: str
    speech: str

class DebateAnalysisInput(BaseModel):
    conversation: list


# =========================
# 🔥 COMMON AI FUNCTION
# =========================

def ask_ai(prompt):
    try:
        response = requests.post(
            URL,
            headers=headers,
            json={
                "model": "mistralai/mistral-7b-instruct",
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            },
            timeout=30
        )

        data = response.json()

        if "choices" in data:
            return data["choices"][0]["message"]["content"]

        return str(data)

    except Exception as e:
        return f"⚠️ Error: {str(e)}"


# =========================
# 🔥 DEBATE
# =========================

@app.post("/debate")
def debate(data: DebateInput):

    prompt = f"""
Act as a strong debate opponent.

Topic: {data.topic}
User side: {data.side}

User argument:
{data.user_text}

- Oppose the user
- Give 2 strong points
- Keep short
- End with a question
"""

    return {"reply": ask_ai(prompt)}


# =========================
# 🧠 ANALYSIS
# =========================

@app.post("/analyze")
def analyze(data: AnalysisInput):

    prompt = f"""
Analyze this speech:

{data.speech}

Give:
- Score out of 10
- 3 mistakes
- 3 improvements
"""

    return {"analysis": ask_ai(prompt)}


# =========================
# 🏁 DEBATE ANALYSIS
# =========================

@app.post("/debate-analysis")
def debate_analysis(data: DebateAnalysisInput):

    full_text = " ".join(data.conversation)

    prompt = f"""
You are a debate coach.

Conversation:
{full_text}

Give:
- Overall Score
- Argument Strength
- 3 mistakes
- 3 improvements
"""

    return {"ai_feedback": ask_ai(prompt)}
