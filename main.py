from fastapi import FastAPI
from pydantic import BaseModel
import requests
import os

app = FastAPI()

# =========================
# 🔐 HUGGING FACE CONFIG
# =========================
HF_API_KEY = os.getenv("HF_API_KEY")

HF_URL = "https://api-inference.huggingface.co/models/google/flan-t5-base"

headers = {
    "Authorization": f"Bearer {HF_API_KEY}"
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
# 🔥 COMMON FUNCTION
# =========================

def query_huggingface(prompt):
    try:
        response = requests.post(
            HF_URL,
            headers=headers,
            json={
                "inputs": prompt,
                "options": {"wait_for_model": True}
            }
        )

        result = response.json()

        print("HF RESPONSE:", result)

        if isinstance(result, list):
            return result[0].get("generated_text", "⚠️ Empty AI response")

        elif "error" in result:
            return f"⚠️ HF Error: {result['error']}"

        else:
            return "⚠️ Unexpected response"

    except Exception as e:
        return f"⚠️ Exception: {str(e)}"


# =========================
# 🔥 DEBATE RESPONSE
# =========================

@app.post("/debate")
def debate(data: DebateInput):

    prompt = f"""
Act as a strong debate opponent.

Topic: {data.topic}
User side: {data.side}

User argument:
{data.user_text}

Rules:
- Oppose the user
- Give 2 strong counterpoints
- Keep it short
- End with a question
"""

    reply = query_huggingface(prompt)

    return {"reply": reply}


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

    result = query_huggingface(prompt)

    return {"analysis": result}


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

    feedback = query_huggingface(prompt)

    return {"ai_feedback": feedback}
