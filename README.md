# 🤖 Rocky AI – Intelligent Multi-Session AI Agent Web Application

Rocky AI is a state-of-the-art **ChatGPT-style AI Assistant** built with Python Flask using a robust **Model-View-Controller (MVC)** architecture.  
It combines cloud-persistent conversation memory, secure multi-provider authentication (Google OAuth 2.0 + Local JWT), live web search tools, and a modern glassmorphism interface.

---
## 🧠 AI Model Information

- **Model Name:** `meta-llama/Llama-3.1-8B-Instruct`
- **Model Provider:** :Meta
- **API Platform:** :Hugging Face Router API

---

## 🌟 Key Features

### 🔐 Secure Multi-Provider Authentication
- **Google Sign-In:** One-tap OAuth 2.0 integration via Google Identity Services.
- **Local Email/Password:** Secure signup and login powered by `werkzeug.security` password hashing.
- **JWT Session Security:** Authentication state stored in secure, `HttpOnly` signed cookies with JWT verification middleware (`@login_required`).

### 💬 ChatGPT-Style Multi-Session History
- **Sidebar Drawer:** Collapsible left sidebar listing all user chat threads with a `+ New Chat` button.
- **Auto-Titling:** Conversation threads automatically generate descriptive titles from the user's first prompt.
- **Session Management:** Switch seamlessly between active chat threads without page reloads, or delete specific sessions with one click.
- **Cloud-Persistent Memory:** Per-user chat history is stored securely in the database and restored across sessions.

### 🌐 Real-Time Web Search & Live Tools
- **Live Search Agent:** Automatically detects real-time or current news/event queries and performs live web searches (via DDGS) to deliver up-to-date answers with source links.
- **Live Date/Time Context:** Injects current timestamp awareness into AI agent prompts.
- **Math Calculator Tool:** Built-in safe expression evaluator for math queries.

### 🎨 Modern UI & Rich Code Formatting
- **Glassmorphism Aesthetic:** Sleek dark/light theme switcher with animated ambient blobs.
- **Markdown & Code Highlighting:** Bot responses render clean Markdown, structured lists, and code blocks (via `marked.js`) with one-click copy buttons.
- **Responsive Layout:** Optimized for desktop and mobile viewports.

---

## 📁 Project Architecture (MVC Standard)

```
Rocky-AI-Intelligent-AI-Agent-Web-Application/
├── ChatboxAI/
│   ├── app.py                      # Flask Application Entry Point & Blueprints
│   ├── config.py                   # Centralised Environment Configuration
│   ├── .env                        # Local Secrets (Gitignored)
│   ├── .env.example                # Environment Variable Template
│   ├── requirements.txt            # Python Dependencies
│   │
│   ├── controllers/                # [CONTROLLER LAYER]
│   │   ├── auth_controller.py      # Login, Signup, Logout, Google OAuth
│   │   └── chat_controller.py      # /chat, /api/sessions, /history REST routes
│   │
│   ├── models/                     # [MODEL LAYER]
│   │   ├── database.py             # MongoDB Atlas Client & SQLite Local Fallback
│   │   ├── user_model.py           # User Authentication CRUD
│   │   └── chat_model.py           # Multi-Session Chat Memory CRUD
│   │
│   ├── services/                   # [SERVICE / AGENT LAYER]
│   │   ├── agent.py                # Smart Intent Router (Web Search & Tools)
│   │   ├── brain.py                # Hugging Face LLM API Client
│   │   └── tools.py                # Web Search, Math, & Datetime Tools
│   │
│   ├── static/                     # [STATIC ASSETS]
│   │   ├── css/
│   │   │   ├── login.css           # Auth Page Styles
│   │   │   └── chat.css            # Chat & Sidebar Styles
│   │   └── js/
│   │       ├── login.js            # Client Auth & Tab Logic
│   │       └── chat.js             # Session State & Real-time Chat UI
│   │
│   └── templates/                  # [VIEW LAYER]
│       ├── login.html              # Login & Signup View
│       └── index.html              # Main Chat & Sidebar View
│
├── .gitignore                      # Git Exclusion Rules
└── README.md                       # Documentation
```

---

## 🛠️ Tech Stack

- **Backend:** Python 3.13, Flask, PyJWT, Werkzeug, requests
- **Database:** MongoDB Atlas (Cloud) / SQLite (Local Fallback)
- **Frontend:** HTML5, CSS3 (Vanilla Vanilla Glassmorphism), JavaScript (ES6+), marked.js
- **AI Model:** `meta-llama/Llama-3.1-8B-Instruct` via Hugging Face Router API
- **Web Search:** `ddgs` (DuckDuckGo Search)
- **Auth Protocols:** OAuth 2.0 (Google Identity Services), JWT (JSON Web Tokens)

---

## ⚙️ Environment Variables

Create a `.env` file inside the `ChatboxAI/` directory based on `.env.example`:

```env
# Flask Security Key
SECRET_KEY=your-super-secret-jwt-key

# Hugging Face API Token (obtain from https://huggingface.co/settings/tokens)
HF_TOKEN=hf_your_huggingface_token

# MongoDB Atlas URI (Leave empty to use local SQLite chats.db fallback)
MONGO_URI=mongodb+srv://<username>:<password>@cluster.mongodb.net/rocky_ai_db

# Google OAuth 2.0 Client ID (obtain from Google Cloud Console)
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com

# LLM Model Choice
LLM_MODEL=meta-llama/Llama-3.1-8B-Instruct
```

---

## 🚀 Getting Started Locally

### 1. Clone the Repository
```bash
git clone https://github.com/Dhayananth1511/Rocky-AI-Intelligent-AI-Agent-Web-Application.git
cd Rocky-AI-Intelligent-AI-Agent-Web-Application/ChatboxAI
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment
Copy `.env.example` to `.env` and add your Hugging Face API token:
```bash
cp .env.example .env
```

### 4. Run the Application
```bash
python app.py
```
Open your browser and navigate to `http://127.0.0.1:5000`.

---

## 🌐 Live Demo & Deployment

- **Live Web App:** [https://ai-projects-blae.onrender.com](https://ai-projects-blae.onrender.com)
- **GitHub Repository:** [Dhayananth1511/Rocky-AI-Intelligent-AI-Agent-Web-Application](https://github.com/Dhayananth1511/Rocky-AI-Intelligent-AI-Agent-Web-Application)

---

## 👨‍💻 Author

- **Dhayananth N**
- AI & Full-Stack Developer
- GitHub: [@Dhayananth1511](https://github.com/Dhayananth1511)
