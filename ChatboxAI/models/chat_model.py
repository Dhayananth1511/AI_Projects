import json
from models.database import db_manager

DEFAULT_SYSTEM_MESSAGE = {"role": "system", "content": "You are a smart AI agent And uses emojis 😊."}

class ChatModel:
    @staticmethod
    def get_user_chat_history(email):
        if not email:
            return [DEFAULT_SYSTEM_MESSAGE]
        
        email = email.lower().strip()
        if db_manager.is_mongo:
            doc = db_manager.chats_col.find_one({"email": email})
            if doc and "messages" in doc:
                return doc["messages"]
        else:
            conn = db_manager.sqlite_conn
            cursor = conn.cursor()
            cursor.execute("SELECT messages FROM chats WHERE email = ?", (email,))
            row = cursor.fetchone()
            if row:
                try:
                    return json.loads(row["messages"])
                except Exception:
                    pass
        
        return [DEFAULT_SYSTEM_MESSAGE]

    @staticmethod
    def update_user_chat_history(email, messages):
        if not email:
            return
        
        email = email.lower().strip()
        if db_manager.is_mongo:
            db_manager.chats_col.update_one(
                {"email": email},
                {"$set": {"messages": messages}},
                upsert=True
            )
        else:
            conn = db_manager.sqlite_conn
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO chats (email, messages)
                VALUES (?, ?)
            """, (email, json.dumps(messages)))
            conn.commit()

    @staticmethod
    def delete_user_chat_history(email):
        if not email:
            return
        
        email = email.lower().strip()
        if db_manager.is_mongo:
            db_manager.chats_col.delete_one({"email": email})
        else:
            conn = db_manager.sqlite_conn
            cursor = conn.cursor()
            cursor.execute("DELETE FROM chats WHERE email = ?", (email,))
            conn.commit()
