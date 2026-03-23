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
                        "content": "You are a strict professional debate AI. Always follow instructions exactly. Keep answers short, relevant, and logical."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": 120,
                "temperature": 0.7
            },
            timeout=30
        )

        if response.status_code != 200:
            return f"⚠️ API Error: {response.text}"

        data = response.json()
        print("API RESPONSE:", data)

        if "choices" in data:
            return data["choices"][0]["message"]["content"].strip()

        return f"⚠️ Unexpected response: {data}"

    except Exception as e:
        return f"⚠️ Exception: {str(e)}"


# =========================
# 🔥 DEBATE API
# =========================

@app.post("/debate")
def debate(data: DebateInput):

    prompt = f"""
You are an expert competitive debater.

Topic: {data.topic}
User's position: {data.side}

User's argument:
{data.user_text}

STRICT RULES (FOLLOW ALL):
1. You MUST take the OPPOSITE side
2. Understand the user's argument deeply
3. Stay strictly on topic
4. Give EXACTLY 2 strong logical counterpoints
5. Keep response VERY SHORT (2–3 lines only)
6. Use simple, natural language
7. DO NOT repeat user's words
8. DO NOT give long explanations
9. END with ONE sharp question

OUTPUT FORMAT:
- Counterpoint 1
- Counterpoint 2
- Final question (same line or next line)
"""

    return {"reply": ask_ai(prompt)}


# =========================
# 🏁 DEBATE ANALYSIS API
# =========================

@app.post("/debate-analysis")
def debate_analysis(data: DebateAnalysisInput):

    full_text = " ".join(data.conversation)

    prompt = f"""
You are a professional debate evaluator.

Conversation:
{full_text}

STRICT RULES:
- Analyze ONLY:
  • Grammar
  • Relevance to topic
  • Argument clarity
  • Logical structure
- DO NOT analyze emotions or tone
- Keep response SHORT and PROFESSIONAL

OUTPUT FORMAT (STRICT):

Overall Score: X/10
Relevance: X/10
Clarity: X/10
Structure: X/10

Mistakes:
- point 1
- point 2
- point 3

Improvements:
- point 1
- point 2
- point 3
"""

    return {"ai_feedback": ask_ai(prompt)}