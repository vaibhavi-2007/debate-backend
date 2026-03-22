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
                "X-Title": "Debate App"
            },
           json={
    "model": "meta-llama/llama-3-8b-instruct",
    "messages": [
        {"role": "user", "content": prompt}
    ]
},
            timeout=30
        )

        # 🔥 IMPORTANT CHECK
        if response.status_code != 200:
            return f"⚠️ API Error: {response.text}"

        data = response.json()
        print("API RESPONSE:", data)

        if "choices" in data:
            return data["choices"][0]["message"]["content"]

        return f"⚠️ Unexpected response: {data}"

    except Exception as e:
        return f"⚠️ Exception: {str(e)}"

# =========================
# 🔥 DEBATE API
# =========================

@app.post("/debate")
def debate(data: DebateInput):

    prompt = f"""
Act as a strong debate opponent.

Topic: {data.topic}
User side: {data.side}

User argument:
{data.user_text}

- Take opposite side
- Give 2 strong counterpoints
- STRICTLY limit to 2-3 lines
- Do NOT explain too much
- End with a sharp question
- must be short and simple
"""

    return {"reply": ask_ai(prompt)}


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
- do not explain too much 
- should be short and simple but detailed
"""

    return {"ai_feedback": ask_ai(prompt)}