# services/brain.py

import requests
from config import Config

def ask_llm(messages):
    headers = {
        "Authorization": f"Bearer {Config.HF_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": Config.MODEL,
        "messages": messages,
    }

    try:
        response = requests.post(Config.HF_API_URL, headers=headers, json=payload, timeout=30)
    except requests.RequestException as e:
        print(f"[Brain Service] Request Exception: {e}")
        return "AI service timed out or is unreachable right now."

    if response.status_code == 200:
        try:
            return response.json()["choices"][0]["message"]["content"]
        except (KeyError, IndexError, ValueError) as e:
            print(f"[Brain Service] Json Parsing Exception: {e}")
            return "Failed to parse AI response."
    else:
        print(f"[Brain Service] API Error ({response.status_code}): {response.text}")
        return f"AI Error ({response.status_code})"
