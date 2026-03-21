from fastapi import FastAPI
from pydantic import BaseModel
import requests
import language_tool_python

app = FastAPI()

# ✅ Grammar Tool
tool = language_tool_python.LanguageTool('en-US')

# ✅ GROQ CONFIG
GROQ_API_KEY = "YOUR_GROQ_API_KEY"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"


# =========================
# MODELS
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
# 🔥 DEBATE RESPONSE (UPGRADED)
# =========================

@app.post("/debate")
def debate(data: DebateInput):

    prompt = f"""
You are an expert-level debate opponent with strong critical thinking.

Debate Topic: {data.topic}
User Position: {data.side}

User Argument:
"{data.user_text}"

Your job:
- Take the exact OPPOSITE stance
- Identify weaknesses in user's argument
- Give 2-3 strong logical counterpoints
- Use confident, natural human tone
- Keep it SHORT (max 4 lines)
- DO NOT repeat user argument
- DO NOT agree
- End with ONE sharp challenging question

Make your response sound like a real competitive debater.
"""

    try:
        response = requests.post(
            GROQ_URL,
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama3-70b-8192",
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            }
        )

        reply = response.json()["choices"][0]["message"]["content"]

        return {"reply": reply}

    except Exception as e:
        return {"error": str(e)}


# =========================
# 🧠 NORMAL SPEECH ANALYSIS
# =========================

@app.post("/analyze")
def analyze(data: AnalysisInput):

    matches = tool.check(data.speech)
    error_count = len(matches)

    score = 10
    if error_count > 5:
        score -= 3
    elif error_count > 2:
        score -= 2

    corrections = []
    for m in matches[:5]:
        corrections.append({
            "error": m.message,
            "suggestions": m.replacements[:2]
        })

    return {
        "grammar_errors": error_count,
        "score": score,
        "corrections": corrections,
        "tips": [
            "Fix grammar mistakes",
            "Use clearer sentence structure",
            "Add more explanation"
        ]
    }


# =========================
# 🏁 FINAL DEBATE ANALYSIS (PRO LEVEL)
# =========================

@app.post("/debate-analysis")
def debate_analysis(data: DebateAnalysisInput):

    full_text = " ".join(data.conversation)

    # ✅ Grammar Check
    matches = tool.check(full_text)
    error_count = len(matches)

    grammar_score = 10
    if error_count > 8:
        grammar_score -= 4
    elif error_count > 4:
        grammar_score -= 2

    # ✅ AI FEEDBACK (VERY IMPORTANT PROMPT)
    prompt = f"""
You are a professional debate coach.

Analyze the user's debate performance based on this conversation:

{full_text}

Give output STRICTLY in this format:

Overall Score: X/10
Argument Strength: X/10
Relevance: X/10
Vocabulary: X/10
Persuasiveness: X/10

Mistakes:
- (3 clear mistakes)

Improvements:
- (3 practical improvements)

Better Sentence:
Rewrite one user sentence in a more powerful and professional way.

Rules:
- Be clear and structured
- Be helpful, not harsh
- Keep it easy to understand
"""

    try:
        response = requests.post(
            GROQ_URL,
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama3-70b-8192",
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            }
        )

        ai_feedback = response.json()["choices"][0]["message"]["content"]

        return {
            "grammar_errors": error_count,
            "grammar_score": grammar_score,
            "ai_feedback": ai_feedback
        }

    except Exception as e:
        return {"error": str(e)}