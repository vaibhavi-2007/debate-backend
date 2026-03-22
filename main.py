from fastapi import FastAPI
from pydantic import BaseModel
import requests

app = FastAPI()

# ✅ DIRECT API KEY (for now)
API_KEY = "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"

URL = "https://openrouter.ai/api/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "HTTP-Referer": "https://your-app.com",
    "X-Title": "Debate App",
    "Content-Type": "application/json"
}

class DebateInput(BaseModel):
    topic: str
    side: str
    user_text: str

class DebateAnalysisInput(BaseModel):
    conversation: list

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
            }
        )

        data = response.json()
        print("API RESPONSE:", data)

        if "choices" in data:
            return data["choices"][0]["message"]["content"]

        return str(data)

    except Exception as e:
        return f"⚠️ Error: {str(e)}"

@app.post("/debate")
def debate(data: DebateInput):

    prompt = f"""
Act as a debate opponent.

Topic: {data.topic}
User side: {data.side}
User argument: {data.user_text}

Give 2 strong counterpoints and end with a question.
"""

    return {"reply": ask_ai(prompt)}
