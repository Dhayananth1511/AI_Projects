import jwt
import requests
import datetime
from flask import Blueprint, request, jsonify, redirect, url_for, g, render_template, make_response
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config
from models.user_model import UserModel

auth_blueprint = Blueprint('auth', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.cookies.get("auth_token")
        if not token:
            if request.path.startswith("/api/") or request.headers.get("Accept") == "application/json" or request.path == "/chat" or request.path == "/reset":
                return jsonify({"error": "Unauthorized"}), 401
            return redirect(url_for('auth.login_page'))
        
        try:
            payload = jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])
            g.user_email = payload["email"]
            g.user_name = payload.get("name", "User")
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            if request.path.startswith("/api/") or request.headers.get("Accept") == "application/json" or request.path == "/chat" or request.path == "/reset":
                return jsonify({"error": "Unauthorized / Session Expired"}), 401
            
            resp = make_response(redirect(url_for('auth.login_page')))
            resp.set_cookie("auth_token", "", expires=0)
            return resp
            
        return f(*args, **kwargs)
    return decorated_function

def get_current_user():
    email = getattr(g, 'user_email', None)
    name = getattr(g, 'user_name', None)
    if email:
        return {"email": email, "name": name}
    return None

def create_jwt_token(email, name):
    payload = {
        "email": email.lower().strip(),
        "name": name,
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=7)
    }
    return jwt.encode(payload, Config.SECRET_KEY, algorithm="HS256")

@auth_blueprint.route("/login", methods=["GET"])
def login_page():
    # If already logged in, redirect to home
    token = request.cookies.get("auth_token")
    if token:
        try:
            jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])
            return redirect(url_for('chat.home'))
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            pass
    return render_template("login.html", google_client_id=Config.GOOGLE_CLIENT_ID)

@auth_blueprint.route("/auth/signup", methods=["POST"])
def signup():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password")
    name = (data.get("name") or "").strip()

    if not email or not password or not name:
        return jsonify({"error": "Name, email, and password are required fields."}), 400

    existing_user = UserModel.find_user_by_email(email)
    if existing_user:
        return jsonify({"error": "User with this email already exists."}), 400

    password_hash = generate_password_hash(password)
    UserModel.save_user(email, password_hash, name, auth_provider="local")
    
    return jsonify({"status": "signup successful"}), 201

@auth_blueprint.route("/auth/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password are required."}), 400

    user = UserModel.find_user_by_email(email)
    if not user:
        return jsonify({"error": "Invalid email or password."}), 401

    if user["auth_provider"] == "google":
        return jsonify({"error": "This account is registered with Google. Please use Google Login."}), 400

    if not check_password_hash(user["password_hash"], password):
        return jsonify({"error": "Invalid email or password."}), 401

    # Create token and set cookie
    token = create_jwt_token(email, user["name"])
    
    resp = make_response(jsonify({"status": "login successful", "name": user["name"]}))
    resp.set_cookie("auth_token", token, httponly=True, samesite="Lax")
    return resp

@auth_blueprint.route("/auth/google", methods=["POST"])
def google_auth():
    data = request.get_json(silent=True) or {}
    credential = data.get("credential")
    
    if not credential:
        return jsonify({"error": "Credential token is required."}), 400

    # Verify ID Token directly via Google Identity tokeninfo API
    verify_url = f"https://oauth2.googleapis.com/tokeninfo?id_token={credential}"
    try:
        res = requests.get(verify_url, timeout=10)
    except requests.RequestException as e:
        print(f"[Auth Controller] Google verification endpoint error: {e}")
        return jsonify({"error": "Auth server unreachable."}), 503

    if res.status_code != 200:
        return jsonify({"error": "Invalid credential token."}), 400

    token_info = res.json()
    
    # Optional Audience check if client ID is set
    if Config.GOOGLE_CLIENT_ID and token_info.get("aud") != Config.GOOGLE_CLIENT_ID:
        return jsonify({"error": "Audience mismatch."}), 400

    email = token_info.get("email", "").lower().strip()
    name = token_info.get("name", "Google User")
    picture = token_info.get("picture")

    if not email:
        return jsonify({"error": "Email not released by Google."}), 400

    # Ensure user exists (Google authentication provider automatically registers users)
    UserModel.save_user(email, password_hash=None, name=name, auth_provider="google", picture=picture)

    token = create_jwt_token(email, name)
    resp = make_response(jsonify({"status": "google login successful", "name": name}))
    resp.set_cookie("auth_token", token, httponly=True, samesite="Lax")
    return resp

@auth_blueprint.route("/logout")
def logout():
    resp = make_response(redirect(url_for('auth.login_page')))
    resp.set_cookie("auth_token", "", expires=0)
    return resp
