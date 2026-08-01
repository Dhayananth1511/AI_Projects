# services/agent.py

import re
from services.tools import calculator, web_search, get_current_datetime
from services.brain import ask_llm

LIVE_INFO_KEYWORDS = [
    "news", "latest", "today", "current", "weather", "score", "stock",
    "price", "who is", "what is the current", "recent", "2025", "2026",
    "search", "lookup", "find", "happening", "event", "winner", "president",
    "prime minister", "ceo", "update", "release", "version"
]

def needs_web_search(user_input):
    """Determine if a query requires live web search information."""
    text = user_input.lower().strip()
    
    # Direct explicit triggers
    if text.startswith("search ") or text.startswith("find ") or text.startswith("google "):
        return True
    
    # Keyword detection
    for kw in LIVE_INFO_KEYWORDS:
        if re.search(r'\b' + re.escape(kw) + r'\b', text):
            return True

    # Question patterns asking about real-world current state
    if any(text.startswith(prefix) for prefix in ["what happened", "who won", "what is the price", "how much is"]):
        return True

    return False

def agent_decide(messages, user_input):
    current_time_str = get_current_datetime()
    
    # Rule 1: Explicit calculation tool call
    if "calculate" in user_input.lower() or re.match(r'^\s*[\d\s\+\-\*\/\(\)\.]+\s*$', user_input):
        expression = user_input.lower().replace("calculate", "").strip()
        result = calculator(expression)
        return f"🧮 **Result:** `{result}`"

    # Ensure system message contains active real-time context
    enhanced_messages = list(messages)
    
    # Rule 2: Web Search for Real-Time / Current Information
    if needs_web_search(user_input):
        search_query = user_input.replace("search", "").replace("find", "").strip() or user_input
        print(f"[Agent] Performing live web search for: '{search_query}'")
        
        search_results = web_search(search_query)
        
        # Inject live context into system message
        context_prompt = (
            f"[SYSTEM CONTEXT: Current Local Date & Time is {current_time_str}]\n"
            f"[REAL-TIME WEB SEARCH RESULTS FOR '{search_query}']:\n"
            f"{search_results}\n\n"
            f"Instructions: Use the above live web search results to provide an up-to-date, accurate, and well-structured response. "
            f"Synthesize the answer clearly in Markdown."
        )
        
        # Insert context into the system message or as system instruction
        if enhanced_messages and enhanced_messages[0].get("role") == "system":
            enhanced_messages[0] = {
                "role": "system",
                "content": enhanced_messages[0]["content"] + "\n\n" + context_prompt
            }
        else:
            enhanced_messages.insert(0, {"role": "system", "content": context_prompt})
            
    else:
        # Standard query: ensure current date/time is known to the LLM
        date_context = f"\n\n[SYSTEM CONTEXT: Current Date & Time is {current_time_str}]"
        if enhanced_messages and enhanced_messages[0].get("role") == "system":
            enhanced_messages[0] = {
                "role": "system",
                "content": enhanced_messages[0]["content"] + date_context
            }

    # Query LLM with enriched real-time context
    return ask_llm(enhanced_messages)
