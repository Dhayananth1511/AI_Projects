import sqlite3
import json
from config import Config

class DatabaseManager:
    def __init__(self):
        self.is_mongo = False
        self.mongo_client = None
        self.db = None

        if Config.MONGO_URI:
            try:
                from pymongo import MongoClient
                self.mongo_client = MongoClient(Config.MONGO_URI)
                # Test connection
                self.mongo_client.admin.command('ping')
                self.db = self.mongo_client['rocky_ai_db']
                self.users_col = self.db['users']
                self.chats_col = self.db['chats']
                self.is_mongo = True
                print("[DB] Successfully connected to Cloud Database (MongoDB Atlas).")
            except Exception as e:
                print(f"[DB Warning] Failed to connect to MongoDB Atlas: {e}. Falling back to SQLite...")
                self._init_sqlite()
        else:
            print("[DB Info] No MONGO_URI provided in configuration. Using local SQLite fallback database.")
            self._init_sqlite()

    def _init_sqlite(self):
        self.is_mongo = False
        db_path = "chats.db"
        self.sqlite_conn = sqlite3.connect(db_path, check_same_thread=False)
        self.sqlite_conn.row_factory = sqlite3.Row
        
        cursor = self.sqlite_conn.cursor()
        
        # Create users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT,
                name TEXT NOT NULL,
                auth_provider TEXT NOT NULL,
                picture TEXT
            )
        """)
        
        # Create chats table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                messages TEXT NOT NULL
            )
        """)
        
        self.sqlite_conn.commit()
        print("[DB] SQLite Database initialized locally.")

db_manager = DatabaseManager()
