from fastapi import FastAPI
from pydantic import BaseModel
import requests
import os

app = FastAPI()

# =========================
# 🔐 HUGGING FACE CONFIG (UPDATED)
# =========================
HF_API_KEY = os.getenv("HF_API_KEY")

HF_URL = "https://router.huggingface.co/hf-inference/models/google/flan-t5-base"

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

def query_hf(prompt):
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
            return result[0].get("generated_text", "⚠️ Empty response")

        elif "error" in result:
            return f"⚠️ HF Error: {result['error']}"

        else:
            return "⚠️ Unexpected response"

    except Exception as e:
        return f"⚠️ Exception: {str(e)}"


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

- Oppose user
- Give 2 strong points
- Keep short
- End with a question
"""

    return {"reply": query_hf(prompt)}


# =========================
# 🧠 ANALYSIS
# =========================

@app.post("/analyze")
def analyze(data: AnalysisInput):

    prompt = f"""
Analyze this speech:

{data.speech}

Give:
- Score /10
- 3 mistakes
- 3 improvements
"""

    return {"analysis": query_hf(prompt)}


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

    return {"ai_feedback": query_hf(prompt)}
