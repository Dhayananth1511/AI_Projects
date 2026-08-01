import os
from flask import Flask, jsonify
from config import Config
from models.database import db_manager
from controllers.auth_controller import auth_blueprint
from controllers.chat_controller import chat_blueprint

# Initialize Flask App
app = Flask(__name__)
app.secret_key = Config.SECRET_KEY

# Register MVC Controller Blueprints
app.register_blueprint(auth_blueprint)
app.register_blueprint(chat_blueprint)

@app.route("/healthz")
def healthz():
    return jsonify({
        "status": "ok",
        "database": "mongodb" if db_manager.is_mongo else "sqlite"
    }), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    # Run server locally
    app.run(host="0.0.0.0", port=port, debug=False)
