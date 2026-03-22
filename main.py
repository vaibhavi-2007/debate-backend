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
