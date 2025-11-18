const loginSection = document.getElementById('login-section');
const appSection = document.getElementById('app-section');
const loginForm = document.getElementById('login-form');
const queryForm = document.getElementById('query-form');
const loginFeedback = document.getElementById('login-feedback');
const agentReply = document.getElementById('agent-reply');
const welcomeText = document.getElementById('welcome-text');
const logoutButton = document.getElementById('logout-button');
const API_BASE_URL = (window.__APP_CONFIG__?.apiBaseUrl || '').replace(/\/$/, '');
const CREDENTIALS_MODE = API_BASE_URL ? 'include' : 'same-origin';

function buildUrl(path) {
  if (!API_BASE_URL) {
    return path;
  }
  return `${API_BASE_URL}${path}`;
}

async function checkSession() {
  const response = await fetch(buildUrl('/api/session'), {
    headers: { 'Accept': 'application/json' },
    credentials: CREDENTIALS_MODE,
  });
  const data = await response.json();
  toggleUI(data.authenticated, data.username);
}

function toggleUI(authenticated, username) {
  if (authenticated) {
    loginSection.classList.add('hidden');
    appSection.classList.remove('hidden');
    welcomeText.textContent = username ? `Innlogget som ${username}` : '';
  } else {
    loginSection.classList.remove('hidden');
    appSection.classList.add('hidden');
    loginForm.reset();
  }
}

loginForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  loginFeedback.textContent = '';
  const formData = new FormData(loginForm);
  const payload = Object.fromEntries(formData.entries());
  const response = await fetch(buildUrl('/api/login'), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: CREDENTIALS_MODE,
    body: JSON.stringify(payload),
  });
  const data = await response.json();
  if (!response.ok) {
    loginFeedback.textContent = data.error || 'Innlogging feilet.';
    loginFeedback.style.color = '#b00020';
    return;
  }
  loginFeedback.textContent = '';
  toggleUI(true, payload.username);
});

queryForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  const submitButton = queryForm.querySelector('button[type="submit"]');
  submitButton.disabled = true;
  agentReply.textContent = 'Henter svar...';
  const formData = new FormData(queryForm);
  const payload = Object.fromEntries(formData.entries());
  const response = await fetch(buildUrl('/api/query'), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: CREDENTIALS_MODE,
    body: JSON.stringify(payload),
  });
  submitButton.disabled = false;
  const data = await response.json();
  if (!response.ok) {
    agentReply.textContent = data.error || 'Noe gikk galt.';
    return;
  }
  agentReply.textContent = data.reply || 'Agenten svarte uten tekst.';
});

logoutButton.addEventListener('click', async () => {
  await fetch(buildUrl('/api/logout'), {
    method: 'POST',
    credentials: CREDENTIALS_MODE,
  });
  agentReply.textContent = 'Ingen forespørsel enda.';
  toggleUI(false);
});

checkSession();
