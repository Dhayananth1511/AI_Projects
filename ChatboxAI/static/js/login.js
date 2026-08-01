/* =============================================================
   Rocky AI — Login Page JS
   File:    static/js/login.js
   ============================================================= */

/* ── Tab Switching ──────────────────────────────────────────── */
function switchTab(tab) {
    const tabs   = document.querySelectorAll('.tab-btn');
    const forms  = document.querySelectorAll('.auth-form');
    const status = document.getElementById('statusBox');

    status.style.display = 'none';
    tabs.forEach(t  => t.classList.remove('active'));
    forms.forEach(f => f.classList.remove('active'));

    if (tab === 'login') {
        tabs[0].classList.add('active');
        document.getElementById('loginForm').classList.add('active');
    } else {
        tabs[1].classList.add('active');
        document.getElementById('signupForm').classList.add('active');
    }
}

/* ── Status / Error Display ─────────────────────────────────── */
function showStatus(msg, isSuccess = false) {
    const box = document.getElementById('statusBox');
    box.textContent = msg;
    box.style.background   = isSuccess ? 'rgba(16,163,127,0.08)' : 'rgba(239,68,68,0.08)';
    box.style.borderColor  = isSuccess ? 'rgba(16,163,127,0.22)' : 'rgba(239,68,68,0.22)';
    box.style.color        = isSuccess ? '#10a37f' : '#ef4444';
    box.style.display      = 'block';
}

/* ── Local Login ─────────────────────────────────────────────── */
async function handleLocalLogin(event) {
    event.preventDefault();
    const email    = document.getElementById('loginEmail').value.trim();
    const password = document.getElementById('loginPassword').value;
    const btn      = document.getElementById('loginSubmit');

    document.getElementById('statusBox').style.display = 'none';
    btn.disabled    = true;
    btn.textContent = 'Logging in…';

    try {
        const res  = await fetch('/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });
        const data = await res.json();

        if (res.ok) {
            window.location.href = '/';
        } else {
            showStatus(data.error || 'Authentication failed.');
        }
    } catch {
        showStatus('Network error. Please try again.');
    } finally {
        btn.disabled    = false;
        btn.textContent = 'Login';
    }
}

/* ── Local Sign-Up ──────────────────────────────────────────── */
async function handleLocalSignup(event) {
    event.preventDefault();
    const name     = document.getElementById('signupName').value.trim();
    const email    = document.getElementById('signupEmail').value.trim();
    const password = document.getElementById('signupPassword').value;
    const btn      = document.getElementById('signupSubmit');

    document.getElementById('statusBox').style.display = 'none';
    btn.disabled    = true;
    btn.textContent = 'Registering…';

    try {
        const res  = await fetch('/auth/signup', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, email, password })
        });
        const data = await res.json();

        if (res.ok) {
            // Auto-login after successful registration
            const loginRes = await fetch('/auth/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password })
            });
            if (loginRes.ok) {
                window.location.href = '/';
                return;
            }
            showStatus('Registered! Please sign in.', true);
            switchTab('login');
        } else {
            showStatus(data.error || 'Registration failed.');
        }
    } catch {
        showStatus('Network error. Please try again.');
    } finally {
        btn.disabled    = false;
        btn.textContent = 'Create Account';
    }
}

/* ── Google Sign-In Callback ────────────────────────────────── */
async function handleCredentialResponse(response) {
    document.getElementById('statusBox').style.display = 'none';

    try {
        const res  = await fetch('/auth/google', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ credential: response.credential })
        });
        const data = await res.json();

        if (res.ok) {
            window.location.href = '/';
        } else {
            showStatus(data.error || 'Google Sign-In failed.');
        }
    } catch {
        showStatus('Could not reach authentication endpoint.');
    }
}
