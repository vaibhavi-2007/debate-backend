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
                        "content": "You are a strict debate AI. Follow instructions EXACTLY. Never skip format."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": 120,
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
- Use very simple sentences
- Each line must be short
- Do NOT repeat user words
- Do NOT explain

OUTPUT EXAMPLE:
Your argument ignores real cost.
My side saves time and money.
Why ignore long-term benefits?
"""

    return {"reply": ask_ai(prompt)}


# =========================
# 🏁 DEBATE ANALYSIS API (FINAL FIX)
# =========================

@app.post("/debate-analysis")
def debate_analysis(data: DebateAnalysisInput):

    full_text = " ".join(data.conversation)

    prompt = f"""
Analyze the debate below carefully:

{full_text}

IMPORTANT:
- You MUST follow output format EXACTLY
- DO NOT skip any field
- DO NOT change format
- DO NOT add extra text

EVALUATE:
1. Grammar (VERY IMPORTANT)
2. Relevance to topic
3. Clarity
4. Logical structure

GRAMMAR RULE:
- Identify real grammar mistakes
- Count them correctly
- If grammar is good → score 7–10
- If grammar is average → score 4–6
- If grammar is poor → score 0–3
- NEVER give 0 unless extremely bad

RETURN EXACTLY IN THIS FORMAT:

Grammar Errors: <number>
Grammar Score: <score>/10

Overall Score: <score>/10
Relevance: <score>/10
Clarity: <score>/10
Structure: <score>/10

Mistakes:
- <specific grammar mistake>
- <unclear sentence or wording>
- <logical issue>

Improvements:
- <fix grammar>
- <improve clarity>
- <strengthen argument>

WARNING:
If format is not followed exactly, the answer is invalid.
"""

    result = ask_ai(prompt)

    # ✅ Safety fallback (ensures format always exists)
    if "Overall Score" not in result:
        result = """Grammar Errors: 0
Grammar Score: 6/10

Overall Score: 6/10
Relevance: 6/10
Clarity: 6/10
Structure: 6/10

Mistakes:
- Unable to analyze properly

Improvements:
- Try again
- Improve sentence clarity
- Use proper grammar
"""

    return {"ai_feedback": result}