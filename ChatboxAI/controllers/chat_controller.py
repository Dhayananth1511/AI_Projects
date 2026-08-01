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

def auto_generate_title(text, max_len=30):
    """Generate a clean title from the user's first prompt."""
    clean = text.strip().replace("\n", " ")
    if len(clean) > max_len:
        return clean[:max_len].rsplit(" ", 1)[0] + "..."
    return clean.capitalize() or "New Chat"

@chat_blueprint.route("/")
@login_required
def home():
    return render_template("index.html", user_name=g.user_name)

# ── Session Management Endpoints ───────────────────────────────

@chat_blueprint.route("/api/sessions", methods=["GET"])
@login_required
def list_sessions():
    """List all chat sessions for the logged-in user."""
    sessions = ChatModel.list_user_sessions(g.user_email)
    return jsonify({"sessions": sessions})

@chat_blueprint.route("/api/sessions/new", methods=["POST"])
@login_required
def new_session():
    """Create a new chat session."""
    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "New Chat").strip()
    session = ChatModel.create_new_session(g.user_email, title=title)
    return jsonify({"session": session}), 201

@chat_blueprint.route("/api/sessions/<session_id>", methods=["GET"])
@login_required
def get_session(session_id):
    """Get history messages for a specific session."""
    messages = ChatModel.get_session_messages(g.user_email, session_id)
    visible = [m for m in messages if m.get("role") in ("user", "assistant")]
    return jsonify({"session_id": session_id, "history": visible})

@chat_blueprint.route("/api/sessions/<session_id>", methods=["DELETE"])
@login_required
def delete_session(session_id):
    """Delete a specific chat session."""
    ChatModel.delete_session(g.user_email, session_id)
    # Return updated list of sessions
    remaining = ChatModel.list_user_sessions(g.user_email)
    return jsonify({"status": "deleted", "sessions": remaining})

# ── Chat Logic Endpoint ────────────────────────────────────────

@chat_blueprint.route("/chat", methods=["POST"])
@login_required
def chat():
    data = request.get_json(silent=True) or {}
    user_input = (data.get("message") or "").strip()
    session_id = data.get("session_id")

    if not user_input:
        return jsonify({"error": "Message is required."}), 400

    # Ensure valid session_id or get/create current
    sessions = ChatModel.list_user_sessions(g.user_email)
    if not session_id or not any(s["session_id"] == session_id for s in sessions):
        if sessions:
            session_id = sessions[0]["session_id"]
        else:
            new_s = ChatModel.create_new_session(g.user_email)
            session_id = new_s["session_id"]
            sessions = [new_s]

    # Find target session title
    current_session = next((s for s in sessions if s["session_id"] == session_id), None)
    current_title = current_session["title"] if current_session else "New Chat"

    # Load messages
    messages = ChatModel.get_session_messages(g.user_email, session_id)

    # Determine if this is the first user message in an untitled chat
    user_msgs_count = sum(1 for m in messages if m.get("role") == "user")
    new_title = None
    if user_msgs_count == 0 or current_title == "New Chat":
        new_title = auto_generate_title(user_input)

    # Append user command
    messages.append({"role": "user", "content": user_input})
    messages = trim_memory(messages)

    try:
        reply = agent_decide(messages, user_input)
    except Exception as e:
        print(f"[Chat Controller] AI Agent Failure: {e}")
        return jsonify({"error": "AI service failed. Please try again."}), 502

    # Append response
    messages.append({"role": "assistant", "content": reply})

    # Save back to database
    ChatModel.update_session_messages(g.user_email, session_id, messages, title=new_title)

    return jsonify({
        "reply": reply,
        "session_id": session_id,
        "title": new_title or current_title
    })

@chat_blueprint.route("/reset", methods=["POST"])
@login_required
def reset_memory():
    data = request.get_json(silent=True) or {}
    session_id = data.get("session_id")
    if session_id:
        ChatModel.delete_session(g.user_email, session_id)
    else:
        ChatModel.delete_user_chat_history(g.user_email)
    remaining = ChatModel.list_user_sessions(g.user_email)
    return jsonify({"status": "cleared", "sessions": remaining})

@chat_blueprint.route("/history", methods=["GET"])
@login_required
def get_history():
    session_id = request.args.get("session_id")
    if not session_id:
        sessions = ChatModel.list_user_sessions(g.user_email)
        session_id = sessions[0]["session_id"] if sessions else None

    messages = ChatModel.get_session_messages(g.user_email, session_id)
    visible = [m for m in messages if m.get("role") in ("user", "assistant")]
    return jsonify({"session_id": session_id, "history": visible})
