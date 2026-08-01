# services/agent.py

from services.tools import calculator
from services.brain import ask_llm

def agent_decide(messages, user_input):
    # Rule-based tool usage
    if "calculate" in user_input.lower():
        expression = user_input.lower().replace("calculate", "").strip()
        result = calculator(expression)
        return f"🧮 Result: {result}"

    # Otherwise use LLM
    return ask_llm(messages)
