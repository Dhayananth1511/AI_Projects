import json
import uuid
import datetime
from models.database import db_manager

DEFAULT_SYSTEM_MESSAGE = {
    "role": "system",
    "content": (
        "You are Rocky, a helpful and friendly AI assistant. "
        "Always format your responses clearly using Markdown: "
        "use **bold** for key terms, bullet lists (- item) for enumerations, "
        "numbered lists for steps, `code` for inline code, and fenced code blocks (```language) for any code snippets. "
        "Keep responses concise and well-structured. Use emojis sparingly to add personality. "
        "Never output raw unformatted walls of text."
    )
}

class ChatModel:
    @staticmethod
    def _now_iso():
        return datetime.datetime.now(datetime.timezone.utc).isoformat()

    @staticmethod
    def list_user_sessions(email):
        """List all chat sessions for a user, sorted by updated_at descending."""
        if not email:
            return []

        email = email.lower().strip()
        sessions = []

        if db_manager.is_mongo:
            cursor = db_manager.sessions_col.find({"email": email}).sort("updated_at", -1)
            for doc in cursor:
                sessions.append({
                    "session_id": doc["session_id"],
                    "title": doc.get("title", "New Chat"),
                    "created_at": doc.get("created_at", ""),
                    "updated_at": doc.get("updated_at", "")
                })
        else:
            conn = db_manager.sqlite_conn
            cursor = conn.cursor()
            cursor.execute(
                "SELECT session_id, title, created_at, updated_at FROM chat_sessions WHERE email = ? ORDER BY updated_at DESC",
                (email,)
            )
            rows = cursor.fetchall()
            for row in rows:
                sessions.append({
                    "session_id": row["session_id"],
                    "title": row["title"],
                    "created_at": row["created_at"],
                    "updated_at": row["updated_at"]
                })

        # If user has no sessions yet, create one default session
        if not sessions:
            new_session = ChatModel.create_new_session(email, title="New Chat")
            sessions.append(new_session)

        return sessions

    @staticmethod
    def create_new_session(email, title="New Chat"):
        """Create a new chat session for a user and return session metadata."""
        if not email:
            return None

        email = email.lower().strip()
        session_id = str(uuid.uuid4())
        now = ChatModel._now_iso()
        initial_messages = [DEFAULT_SYSTEM_MESSAGE]

        if db_manager.is_mongo:
            doc = {
                "session_id": session_id,
                "email": email,
                "title": title,
                "created_at": now,
                "updated_at": now,
                "messages": initial_messages
            }
            db_manager.sessions_col.insert_one(doc)
        else:
            conn = db_manager.sqlite_conn
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO chat_sessions (session_id, email, title, created_at, updated_at, messages)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (session_id, email, title, now, now, json.dumps(initial_messages)))
            conn.commit()

        return {
            "session_id": session_id,
            "title": title,
            "created_at": now,
            "updated_at": now
        }

    @staticmethod
    def get_session_messages(email, session_id):
        """Retrieve the messages array for a given session ID."""
        if not email or not session_id:
            return [DEFAULT_SYSTEM_MESSAGE]

        email = email.lower().strip()
        if db_manager.is_mongo:
            doc = db_manager.sessions_col.find_one({"email": email, "session_id": session_id})
            if doc and "messages" in doc:
                return doc["messages"]
        else:
            conn = db_manager.sqlite_conn
            cursor = conn.cursor()
            cursor.execute("SELECT messages FROM chat_sessions WHERE email = ? AND session_id = ?", (email, session_id))
            row = cursor.fetchone()
            if row:
                try:
                    return json.loads(row["messages"])
                except Exception:
                    pass

        return [DEFAULT_SYSTEM_MESSAGE]

    @staticmethod
    def update_session_messages(email, session_id, messages, title=None):
        """Update messages (and optionally title) for a session ID."""
        if not email or not session_id:
            return

        email = email.lower().strip()
        now = ChatModel._now_iso()

        if db_manager.is_mongo:
            update_fields = {"messages": messages, "updated_at": now}
            if title:
                update_fields["title"] = title
            db_manager.sessions_col.update_one(
                {"email": email, "session_id": session_id},
                {"$set": update_fields}
            )
        else:
            conn = db_manager.sqlite_conn
            cursor = conn.cursor()
            if title:
                cursor.execute("""
                    UPDATE chat_sessions
                    SET messages = ?, updated_at = ?, title = ?
                    WHERE email = ? AND session_id = ?
                """, (json.dumps(messages), now, title, email, session_id))
            else:
                cursor.execute("""
                    UPDATE chat_sessions
                    SET messages = ?, updated_at = ?
                    WHERE email = ? AND session_id = ?
                """, (json.dumps(messages), now, email, session_id))
            conn.commit()

    @staticmethod
    def delete_session(email, session_id):
        """Delete a specific chat session."""
        if not email or not session_id:
            return

        email = email.lower().strip()
        if db_manager.is_mongo:
            db_manager.sessions_col.delete_one({"email": email, "session_id": session_id})
        else:
            conn = db_manager.sqlite_conn
            cursor = conn.cursor()
            cursor.execute("DELETE FROM chat_sessions WHERE email = ? AND session_id = ?", (email, session_id))
            conn.commit()

    # ── Legacy single-session compatibility methods ──────────────
    @staticmethod
    def get_user_chat_history(email):
        sessions = ChatModel.list_user_sessions(email)
        if sessions:
            return ChatModel.get_session_messages(email, sessions[0]["session_id"])
        return [DEFAULT_SYSTEM_MESSAGE]

    @staticmethod
    def update_user_chat_history(email, messages):
        sessions = ChatModel.list_user_sessions(email)
        if sessions:
            ChatModel.update_session_messages(email, sessions[0]["session_id"], messages)

    @staticmethod
    def delete_user_chat_history(email):
        sessions = ChatModel.list_user_sessions(email)
        for s in sessions:
            ChatModel.delete_session(email, s["session_id"])
