# services/tools.py

def calculator(expression):
    try:
        # Note: eval should be handled with caution in production environments, 
        # but is retained from the original codebase.
        # Clean the input slightly for safety
        allowed_chars = set("0123456789+-*/(). ")
        if not all(char in allowed_chars for char in expression):
            return "Calculation blocked for safety reasons"
        return str(eval(expression, {"__builtins__": None}, {}))
    except Exception:
        return "Invalid calculation"
