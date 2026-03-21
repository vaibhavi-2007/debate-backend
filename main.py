from fastapi import FastAPI
from pydantic import BaseModel
import requests
import os

app = FastAPI()

# =========================
# 🔐 HUGGING FACE CONFIG
# =========================
HF_API_KEY = os.getenv("HF_API_KEY")
HF_URL = "https://api-inference.huggingface.co/models/google/flan-t5-large"

headers = {
    "Authorization": f"Bearer {HF_API_KEY}",
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
# 🔥 DEBATE RESPONSE
# =========================

@app.post("/debate")
def debate(data: DebateInput):

    prompt = f"""
Act as a competitive debate opponent.

Topic: {data.topic}
User supports: {data.side}

User argument:
{data.user_text}

Your response rules:
- Take the opposite stance
- Give 2–3 strong logical counterpoints
- Keep response short (3–4 lines)
- Be natural and confident
- Attack weak points in argument
- End with ONE challenging question
"""

    try:
        response = requests.post(
            HF_URL,
            headers=headers,
            json={"inputs": prompt}
        )

        result = response.json()

        if isinstance(result, list):
            reply = result[0].get("generated_text", "")
        else:
            reply = "⚠️ AI not responding properly"

    except Exception as e:
        reply = f"⚠️ Error: {str(e)}"

    return {"reply": reply}


# =========================
# 🧠 SPEECH ANALYSIS
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

Keep it short and clear.
"""

    try:
        response = requests.post(
            HF_URL,
            headers=headers,
            json={"inputs": prompt}
        )

        result = response.json()

        if isinstance(result, list):
            analysis = result[0].get("generated_text", "")
        else:
            analysis = "⚠️ Analysis failed"

    except Exception as e:
        analysis = f"⚠️ Error: {str(e)}"

    return {"analysis": analysis}


# =========================
# 🏁 DEBATE ANALYSIS
# =========================

@app.post("/debate-analysis")
def debate_analysis(data: DebateAnalysisInput):

    full_text = " ".join(data.conversation)

    prompt = f"""
You are a professional debate coach.

Analyze this debate conversation:

{full_text}

Give output EXACTLY like this:

Overall Score: X/10
Argument Strength: X/10
Relevance: X/10
Vocabulary: X/10
Persuasiveness: X/10

Mistakes:
- point 1
- point 2
- point 3

Improvements:
- point 1
- point 2
- point 3

Better Sentence:
Rewrite one user sentence clearly.
"""

    try:
        response = requests.post(
            HF_URL,
            headers=headers,
            json={"inputs": prompt}
        )

        result = response.json()

        if isinstance(result, list):
            feedback = result[0].get("generated_text", "")
        else:
            feedback = "⚠️ Feedback failed"

    except Exception as e:
        feedback = f"⚠️ Error: {str(e)}"

    return {"ai_feedback": feedback}