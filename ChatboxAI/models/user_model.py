from models.database import db_manager

class UserModel:
    @staticmethod
    def save_user(email, password_hash, name, auth_provider, picture=None):
        email = email.lower().strip()
        if db_manager.is_mongo:
            user_data = {
                "email": email,
                "password_hash": password_hash,
                "name": name,
                "auth_provider": auth_provider,
                "picture": picture
            }
            db_manager.users_col.update_one(
                {"email": email},
                {"$set": user_data},
                upsert=True
            )
        else:
            conn = db_manager.sqlite_conn
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO users (email, password_hash, name, auth_provider, picture)
                VALUES (?, ?, ?, ?, ?)
            """, (email, password_hash, name, auth_provider, picture))
            conn.commit()

    @staticmethod
    def find_user_by_email(email):
        if not email:
            return None
        email = email.lower().strip()
        if db_manager.is_mongo:
            return db_manager.users_col.find_one({"email": email})
        else:
            conn = db_manager.sqlite_conn
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
            row = cursor.fetchone()
            if row:
                return {
                    "email": row["email"],
                    "password_hash": row["password_hash"],
                    "name": row["name"],
                    "auth_provider": row["auth_provider"],
                    "picture": row["picture"]
                }
            return None
