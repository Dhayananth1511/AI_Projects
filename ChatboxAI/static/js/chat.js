/* =============================================================
   Rocky AI — Chat Application JS
   File:    static/js/chat.js
   ============================================================= */

/* ── SVG Icon Strings ────────────────────────────────────────── */
const ICON_COPY = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
</svg>`;
const ICON_CHECK = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
    <polyline points="20 6 9 17 4 12"/>
</svg>`;

/* ── Theme Management ────────────────────────────────────────── */
const THEMES = ['dark', 'light'];
let currentTheme = localStorage.getItem('rocky-theme') || 'dark';

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

/* ── Textarea Auto-Resize ────────────────────────────────────── */
const textarea = document.getElementById('userInput');

textarea.addEventListener('keydown', function (e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

textarea.addEventListener('input', function () {
    this.style.height = '24px';
    this.style.height = Math.min(this.scrollHeight, 160) + 'px';
});

/* ── Copy Helper ─────────────────────────────────────────────── */
function triggerCopy(btn, text, resetLabel = 'Copy') {
    function markCopied() {
        btn.innerHTML = `${ICON_CHECK} Copied!`;
        btn.classList.add('copied');
        setTimeout(() => {
            btn.innerHTML = `${ICON_COPY} ${resetLabel}`;
            btn.classList.remove('copied');
        }, 2000);
    }

    function fallbackCopy() {
        const ta = document.createElement('textarea');
        ta.value = text;
        ta.style.cssText = 'position:fixed;top:0;left:0;width:1px;height:1px;opacity:0.01;border:none;outline:none;pointer-events:none;';
        document.body.appendChild(ta);
        ta.focus();
        ta.select();
        try { document.execCommand('copy'); markCopied(); } catch (e) { console.warn('Copy failed:', e); }
        document.body.removeChild(ta);
    }

    if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(text).then(markCopied).catch(fallbackCopy);
    } else {
        fallbackCopy();
    }
}

/* ── Code Block Enhancement ──────────────────────────────────── */
function enhanceCodeBlocks(container) {
    container.querySelectorAll('pre').forEach(pre => {
        if (pre.querySelector('.code-header')) return;

        const code = pre.querySelector('code');
        if (!code) return;

        const langClass = [...code.classList].find(c => c.startsWith('language-'));
        const lang      = langClass ? langClass.replace('language-', '') : 'code';

        const header  = document.createElement('div');
        header.className = 'code-header';

        const langLabel = document.createElement('span');
        langLabel.className   = 'code-lang';
        langLabel.textContent = lang;

        const copyBtn = document.createElement('button');
        copyBtn.className = 'copy-btn';
        copyBtn.innerHTML = `${ICON_COPY} Copy`;
        copyBtn.title = 'Copy code';
        copyBtn.addEventListener('click', () => triggerCopy(copyBtn, code.innerText, 'Copy'));

        header.append(langLabel, copyBtn);
        pre.insertBefore(header, pre.firstChild);
    });
}

/* ── DOM Helpers ─────────────────────────────────────────────── */
function escHtml(s) {
    return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

function scrollToBottom() {
    const chatbox = document.getElementById('chatbox');
    chatbox.scrollTop = chatbox.scrollHeight;
}

/* ── Send Message ────────────────────────────────────────────── */
async function sendMessage() {
    const input   = document.getElementById('userInput');
    const sendBtn = document.getElementById('sendBtn');
    const chatbox = document.getElementById('chatbox');
    const message = input.value.trim();
    if (!message) return;

    // Remove welcome state
    document.getElementById('welcome')?.remove();

    /* -- User Bubble -- */
    const userRow  = document.createElement('div');
    userRow.className = 'message-row user-row';

    const userWrap = document.createElement('div');
    userWrap.className = 'user-message-wrap';

    const userMsg  = document.createElement('div');
    userMsg.className = 'message user';
    userMsg.innerHTML = escHtml(message).replace(/\n/g, '<br>');

    const userCopyBar = document.createElement('div');
    userCopyBar.className = 'copy-response-bar user-copy-bar';

    const userCopyBtn = document.createElement('button');
    userCopyBtn.className = 'copy-btn copy-response-btn';
    userCopyBtn.innerHTML = `${ICON_COPY} Copy`;
    userCopyBtn.title = 'Copy message';
    userCopyBtn.addEventListener('click', () => triggerCopy(userCopyBtn, userMsg.innerText, 'Copy'));

    userCopyBar.append(userCopyBtn);
    userWrap.append(userCopyBar, userMsg);
    userRow.append(userWrap);
    chatbox.append(userRow);
    scrollToBottom();

    // Reset input
    input.value        = '';
    input.style.height = '24px';
    input.disabled     = true;
    sendBtn.disabled   = true;

    /* -- Typing Indicator -- */
    chatbox.insertAdjacentHTML('beforeend', `
        <div class="message-row bot-row" id="typing">
            <div class="avatar">🤖</div>
            <div class="message bot" style="padding:14px 18px">
                <span class="typing-dot"></span>
                <span class="typing-dot"></span>
                <span class="typing-dot"></span>
            </div>
        </div>
    `);
    scrollToBottom();

    try {
        const res  = await fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message })
        });
        const data = await res.json();
        document.getElementById('typing')?.remove();

        if (!res.ok) throw new Error(data.error || `Error ${res.status}`);

        /* -- Bot Bubble -- */
        const row       = document.createElement('div');
        row.className   = 'message-row bot-row';

        const avatarEl  = document.createElement('div');
        avatarEl.className   = 'avatar';
        avatarEl.textContent = '🤖';

        const wrap = document.createElement('div');
        wrap.className = 'bot-message-wrap';

        const msgEl = document.createElement('div');
        msgEl.className = 'message bot';
        msgEl.innerHTML = marked.parse(data.reply);

        const copyBar    = document.createElement('div');
        copyBar.className = 'copy-response-bar';

        const copyRespBtn = document.createElement('button');
        copyRespBtn.className = 'copy-btn copy-response-btn';
        copyRespBtn.innerHTML = `${ICON_COPY} Copy response`;
        copyRespBtn.title = 'Copy full response';
        copyRespBtn.addEventListener('click', () => triggerCopy(copyRespBtn, msgEl.innerText, 'Copy response'));

        copyBar.append(copyRespBtn);
        wrap.append(msgEl, copyBar);
        row.append(avatarEl, wrap);
        chatbox.append(row);

        enhanceCodeBlocks(msgEl);

    } catch (err) {
        document.getElementById('typing')?.remove();
        chatbox.insertAdjacentHTML('beforeend', `
            <div class="message-row bot-row">
                <div class="avatar">⚠️</div>
                <div class="message bot" style="color:#f87171">${escHtml(err.message)}</div>
            </div>
        `);
    } finally {
        input.disabled   = false;
        sendBtn.disabled = false;
        input.focus();
        scrollToBottom();
    }
}
