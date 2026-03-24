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
                "X-Title": "Debate App",
                "Content-Type": "application/json"
            },
            json={
                "model": "meta-llama/llama-3-8b-instruct",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a strict debate AI. Follow instructions exactly. Never ignore format."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": 100,
                "temperature": 0.5
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
# 🔥 DEBATE API (FIXED)
# =========================

@app.post("/debate")
def debate(data: DebateInput):

    prompt = f"""
Topic: {data.topic}
User side: {data.side}

User argument:
{data.user_text}

TASK:
- Take the opposite side
- Give ONLY 2 short points

RULES:
- Point 1: Directly attack user's argument
- Point 2: Show benefit of your side
- Use very simple sentences
- Each point must be ONE line only
- Total output max 2–3 lines
- Do NOT repeat user words
- Do NOT give explanation
- End with ONE short question

EXAMPLE OUTPUT:
Your argument ignores real cost.
My side improves efficiency and saves money.
Why overlook long-term benefits?
"""

    return {"reply": ask_ai(prompt)}


# =========================
# 🏁 DEBATE ANALYSIS API (FIXED)
# =========================

@app.post("/debate-analysis")
def debate_analysis(data: DebateAnalysisInput):

    full_text = " ".join(data.conversation)

    prompt = f"""
Analyze this debate strictly:

{full_text}

FOCUS:
1. Grammar mistakes (VERY IMPORTANT)
2. Relevance to topic
3. Clarity
4. Logical structure

GRAMMAR RULE:
- Count grammar mistakes properly
- If no mistakes → give high score (7–10)
- If many mistakes → low score
- DO NOT return 0 unless extremely bad

OUTPUT FORMAT:

Grammar Errors: number
Grammar Score: X/10

Overall Score: X/10
Relevance: X/10
Clarity: X/10
Structure: X/10

Mistakes:
- grammar mistake example
- unclear sentence
- weak logic

Improvements:
- fix grammar
- improve clarity
- strengthen argument
"""

    return {"ai_feedback": ask_ai(prompt)}