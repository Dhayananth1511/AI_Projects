from flask import Blueprint, request, jsonify, render_template, g
from controllers.auth_controller import login_required
from models.chat_model import ChatModel
from services.agent import agent_decide

chat_blueprint = Blueprint('chat', __name__)

def trim_memory(messages, max_chars=4000):
    # Keep system message (index 0) and slide the rest to stay under bounds
    total = sum(len(m["content"]) for m in messages)
    while total > max_chars and len(messages) > 2:
        messages.pop(1)
        total = sum(len(m["content"]) for m in messages)
    return messages

@chat_blueprint.route("/")
@login_required
def home():
    return render_template("index.html", user_name=g.user_name)

@chat_blueprint.route("/chat", methods=["POST"])
@login_required
def chat():
    data = request.get_json(silent=True) or {}
    user_input = (data.get("message") or "").strip()
    if not user_input:
        return jsonify({"error": "Message is required."}), 400

    # Load from cloud or local Fallback DB for this specific user
    messages = ChatModel.get_user_chat_history(g.user_email)
    
    # Append user command
    messages.append({"role": "user", "content": user_input})
    
    # Prevent overflow
    messages = trim_memory(messages)

    try:
        reply = agent_decide(messages, user_input)
    except Exception as e:
        print(f"[Chat Controller] AI Agent Failure: {e}")
        return jsonify({"error": "AI service failed. Please try again."}), 502

    # Append response
    messages.append({"role": "assistant", "content": reply})

    # Save details back to client history
    ChatModel.update_user_chat_history(g.user_email, messages)

    return jsonify({"reply": reply})

@chat_blueprint.route("/reset", methods=["POST"])
@login_required
def reset_memory():
    # Remove chat instance from DB for this user
    ChatModel.delete_user_chat_history(g.user_email)
    return jsonify({"status": "memory cleared"})
