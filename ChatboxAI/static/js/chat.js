/* =============================================================
   Rocky AI — Chat Application JS (ChatGPT Multi-Session Sidebar)
   File:    static/js/chat.js
   ============================================================= */

/* ── SVG Icons ───────────────────────────────────────────────── */
const ICON_COPY = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <rect x="9" y="9" width="13" height="13" rx="2"/>
    <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
</svg>`;
const ICON_CHECK = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
    <polyline points="20 6 9 17 4 12"/>
</svg>`;
const ICON_TRASH = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <polyline points="3 6 5 6 21 6"></polyline>
    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
</svg>`;

/* ── State ───────────────────────────────────────────────────── */
let activeSessionId = null;
let userSessions    = [];

/* ── Theme ───────────────────────────────────────────────────── */
const THEMES       = ['dark', 'light'];
let   currentTheme = localStorage.getItem('rocky-theme') || 'dark';

function applyTheme(t) {
    currentTheme = t;
    document.documentElement.setAttribute('data-theme', t);
    document.getElementById('btn-dark').classList.toggle('active',  t === 'dark');
    document.getElementById('btn-light').classList.toggle('active', t === 'light');
    localStorage.setItem('rocky-theme', t);
}

function cycleTheme() {
    applyTheme(THEMES[(THEMES.indexOf(currentTheme) + 1) % THEMES.length]);
}

document.getElementById('btn-dark').addEventListener('click',  e => { e.stopPropagation(); applyTheme('dark');  });
document.getElementById('btn-light').addEventListener('click', e => { e.stopPropagation(); applyTheme('light'); });
applyTheme(currentTheme);

/* ── Sidebar Toggle ──────────────────────────────────────────── */
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    if (sidebar) sidebar.classList.toggle('collapsed');
}

/* ── Textarea Auto-Resize ────────────────────────────────────── */
const textarea = document.getElementById('userInput');

textarea.addEventListener('keydown', e => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); }
});

textarea.addEventListener('input', function () {
    this.style.height = '24px';
    this.style.height = Math.min(this.scrollHeight, 160) + 'px';
});

/* ── Helpers ─────────────────────────────────────────────────── */
function escHtml(s) {
    return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

function scrollToBottom() {
    const c = document.getElementById('chatbox');
    c.scrollTop = c.scrollHeight;
}

/* ── Copy Helper ─────────────────────────────────────────────── */
function triggerCopy(btn, text, resetLabel = 'Copy') {
    const markCopied = () => {
        btn.innerHTML = `${ICON_CHECK} Copied!`;
        btn.classList.add('copied');
        setTimeout(() => { btn.innerHTML = `${ICON_COPY} ${resetLabel}`; btn.classList.remove('copied'); }, 2000);
    };
    const fallback = () => {
        const ta = Object.assign(document.createElement('textarea'), {
            value: text,
            style: 'position:fixed;top:0;left:0;width:1px;height:1px;opacity:0.01;border:none;outline:none;pointer-events:none;'
        });
        document.body.appendChild(ta);
        ta.focus(); ta.select();
        try { document.execCommand('copy'); markCopied(); } catch(e) {}
        document.body.removeChild(ta);
    };
    if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(text).then(markCopied).catch(fallback);
    } else { fallback(); }
}

/* ── Code Block Enhancement ──────────────────────────────────── */
function enhanceCodeBlocks(container) {
    container.querySelectorAll('pre').forEach(pre => {
        if (pre.querySelector('.code-header')) return;
        const code = pre.querySelector('code');
        if (!code) return;

        const langClass = [...code.classList].find(c => c.startsWith('language-'));
        const lang      = langClass ? langClass.replace('language-', '') : 'code';

        const header    = document.createElement('div');
        header.className = 'code-header';

        const label     = document.createElement('span');
        label.className   = 'code-lang';
        label.textContent = lang;

        const copyBtn   = document.createElement('button');
        copyBtn.className = 'copy-btn';
        copyBtn.innerHTML = `${ICON_COPY} Copy`;
        copyBtn.title = 'Copy code';
        copyBtn.addEventListener('click', () => triggerCopy(copyBtn, code.innerText, 'Copy'));

        header.append(label, copyBtn);
        pre.insertBefore(header, pre.firstChild);
    });
}

/* ── Build Message Bubble ────────────────────────────────────── */
function buildBubble(role, content) {
    const isUser = role === 'user';

    const row = document.createElement('div');
    row.className = `message-row ${isUser ? 'user-row' : 'bot-row'}`;

    if (!isUser) {
        const avatar = document.createElement('div');
        avatar.className   = 'avatar';
        avatar.textContent = '🤖';
        row.append(avatar);
    }

    const wrap = document.createElement('div');
    wrap.className = isUser ? 'user-message-wrap' : 'bot-message-wrap';

    const msgEl = document.createElement('div');
    msgEl.className = `message ${isUser ? 'user' : 'bot'}`;

    if (isUser) {
        msgEl.innerHTML = escHtml(content).replace(/\n/g, '<br>');
    } else {
        msgEl.innerHTML = marked.parse(content);
        enhanceCodeBlocks(msgEl);
    }

    /* Copy bar */
    const copyBar = document.createElement('div');
    copyBar.className = `copy-response-bar${isUser ? ' user-copy-bar' : ''}`;

    const copyBtn = document.createElement('button');
    copyBtn.className = 'copy-btn copy-response-btn';
    copyBtn.innerHTML = `${ICON_COPY} ${isUser ? 'Copy' : 'Copy response'}`;
    copyBtn.title = isUser ? 'Copy message' : 'Copy full response';
    copyBtn.addEventListener('click', () => triggerCopy(copyBtn, msgEl.innerText, copyBtn.title));

    copyBar.append(copyBtn);

    if (isUser) {
        wrap.append(copyBar, msgEl);
    } else {
        wrap.append(msgEl, copyBar);
    }

    row.append(wrap);
    return row;
}

/* ── Show Welcome Screen ─────────────────────────────────────── */
function renderWelcome() {
    const chatbox = document.getElementById('chatbox');
    chatbox.innerHTML = `
        <div class="welcome" id="welcome">
            <div class="welcome-icon" aria-hidden="true">🤖</div>
            <h2>Hey, I'm Rocky</h2>
            <p>Ask me anything — I'm here to help you think, create, and explore.</p>
        </div>`;
}

/* ── Render Sidebar Session List ─────────────────────────────── */
function renderSidebar() {
    const container = document.getElementById('sessionList');
    if (!container) return;

    container.innerHTML = '';

    userSessions.forEach(sess => {
        const item = document.createElement('div');
        item.className = `session-item ${sess.session_id === activeSessionId ? 'active' : ''}`;
        item.onclick = () => switchSession(sess.session_id);

        const left = document.createElement('div');
        left.className = 'session-item-left';

        const icon = document.createElement('span');
        icon.className = 'session-icon';
        icon.textContent = '💬';

        const title = document.createElement('span');
        title.className = 'session-title';
        title.textContent = sess.title || 'New Chat';

        left.append(icon, title);

        const delBtn = document.createElement('button');
        delBtn.className = 'btn-delete-session';
        delBtn.title = 'Delete chat';
        delBtn.innerHTML = ICON_TRASH;
        delBtn.onclick = (e) => deleteSession(sess.session_id, e);

        item.append(left, delBtn);
        container.append(item);
    });
}

/* ── Load Session History ────────────────────────────────────── */
async function loadSessionHistory(sessionId) {
    activeSessionId = sessionId;
    renderSidebar();

    const chatbox = document.getElementById('chatbox');
    chatbox.innerHTML = '';

    try {
        const res = await fetch(`/api/sessions/${sessionId}`);
        if (!res.ok) throw new Error('Failed to load session');

        const data = await res.json();
        const history = data.history || [];

        if (history.length === 0) {
            renderWelcome();
            return;
        }

        history.forEach(msg => {
            chatbox.append(buildBubble(msg.role, msg.content));
        });

        scrollToBottom();
    } catch (e) {
        console.warn('[Rocky] Could not load session history:', e);
        renderWelcome();
    }
}

/* ── Switch Active Session ───────────────────────────────────── */
function switchSession(sessionId) {
    if (sessionId === activeSessionId) return;
    loadSessionHistory(sessionId);
}

/* ── Create New Chat ─────────────────────────────────────────── */
async function createNewChat() {
    try {
        const res = await fetch('/api/sessions/new', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title: 'New Chat' })
        });
        if (!res.ok) throw new Error('Failed to create session');

        const data = await res.json();
        const newSess = data.session;

        userSessions.unshift(newSess);
        activeSessionId = newSess.session_id;

        renderSidebar();
        renderWelcome();

        const input = document.getElementById('userInput');
        input.value = '';
        input.focus();
    } catch (e) {
        console.error('[Rocky] Error creating new chat:', e);
    }
}

/* ── Delete Session ─────────────────────────────────────────── */
async function deleteSession(sessionId, event) {
    if (event) event.stopPropagation();

    if (userSessions.length <= 1) {
        /* If only one session left, reset it instead of leaving empty sidebar */
        try {
            await fetch(`/api/sessions/${sessionId}`, { method: 'DELETE' });
            await createNewChat();
        } catch (e) {}
        return;
    }

    try {
        const res = await fetch(`/api/sessions/${sessionId}`, { method: 'DELETE' });
        if (!res.ok) throw new Error('Failed to delete session');

        userSessions = userSessions.filter(s => s.session_id !== sessionId);

        if (activeSessionId === sessionId) {
            activeSessionId = userSessions[0] ? userSessions[0].session_id : null;
            if (activeSessionId) {
                loadSessionHistory(activeSessionId);
            } else {
                createNewChat();
            }
        } else {
            renderSidebar();
        }
    } catch (e) {
        console.error('[Rocky] Error deleting chat session:', e);
    }
}

/* ── Fetch Initial Sessions on Boot ──────────────────────────── */
async function fetchSessions() {
    try {
        const res = await fetch('/api/sessions');
        if (!res.ok) return;

        const data = await res.json();
        userSessions = data.sessions || [];

        if (userSessions.length > 0) {
            activeSessionId = userSessions[0].session_id;
            renderSidebar();
            loadSessionHistory(activeSessionId);
        } else {
            createNewChat();
        }
    } catch (e) {
        console.warn('[Rocky] Could not fetch session list:', e);
    }
}

/* ── Send Message ────────────────────────────────────────────── */
async function sendMessage() {
    const input   = document.getElementById('userInput');
    const sendBtn = document.getElementById('sendBtn');
    const chatbox = document.getElementById('chatbox');
    const message = input.value.trim();
    if (!message) return;

    /* Remove welcome screen if present */
    document.getElementById('welcome')?.remove();

    /* Optimistically render user bubble */
    chatbox.append(buildBubble('user', message));
    scrollToBottom();

    input.value        = '';
    input.style.height = '24px';
    input.disabled     = true;
    sendBtn.disabled   = true;

    /* Typing indicator */
    const typing = document.createElement('div');
    typing.id        = 'typing';
    typing.className = 'message-row bot-row';
    typing.innerHTML = `
        <div class="avatar">🤖</div>
        <div class="message bot" style="padding:14px 18px">
            <span class="typing-dot"></span>
            <span class="typing-dot"></span>
            <span class="typing-dot"></span>
        </div>`;
    chatbox.append(typing);
    scrollToBottom();

    try {
        const res  = await fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: message,
                session_id: activeSessionId
            })
        });
        const data = await res.json();
        document.getElementById('typing')?.remove();

        if (!res.ok) throw new Error(data.error || `Error ${res.status}`);

        chatbox.append(buildBubble('assistant', data.reply));

        /* If session title was updated by server, update local state & sidebar UI */
        if (data.title && activeSessionId) {
            const sess = userSessions.find(s => s.session_id === activeSessionId);
            if (sess) {
                sess.title = data.title;
                renderSidebar();
            }
        }

    } catch (err) {
        document.getElementById('typing')?.remove();
        const errRow = document.createElement('div');
        errRow.className = 'message-row bot-row';
        errRow.innerHTML = `
            <div class="avatar">⚠️</div>
            <div class="message bot" style="color:#f87171">${escHtml(err.message)}</div>`;
        chatbox.append(errRow);
    } finally {
        input.disabled   = false;
        sendBtn.disabled = false;
        input.focus();
        scrollToBottom();
    }
}

/* ── Boot ────────────────────────────────────────────────────── */
document.addEventListener('DOMContentLoaded', fetchSessions);
