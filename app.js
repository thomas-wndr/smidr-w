const loginCard = document.getElementById('login-card');
const chatCard = document.getElementById('chat-card');
const loginForm = document.getElementById('login-form');
const chatForm = document.getElementById('chat-form');
const loginFeedback = document.getElementById('login-feedback');
const sessionStatus = document.getElementById('session-status');
const accessPill = document.getElementById('access-pill');
const logoutButton = document.getElementById('logout-button');
const chatWindow = document.getElementById('chat-window');
const messageInput = document.getElementById('message-input');
const sendButton = document.getElementById('send-button');
const agentIdInput = document.getElementById('agent-id');

const STORAGE_KEY = 'smidr-agent-id';
const API_BASE_URL = (window.__APP_CONFIG__?.apiBaseUrl || '').replace(/\/$/, '');
const storedAgentId = localStorage.getItem(STORAGE_KEY);
const DEFAULT_AGENT_ID = storedAgentId || window.__APP_CONFIG__?.defaultAgentId || '';
const CREDENTIALS_MODE = API_BASE_URL ? 'include' : 'same-origin';

if (DEFAULT_AGENT_ID) {
  agentIdInput.value = DEFAULT_AGENT_ID;
}

const state = {
  username: null,
  allowedPages: [],
};

function buildUrl(path) {
  if (!API_BASE_URL) return path;
  return `${API_BASE_URL}${path}`;
}

function toggleUI(authenticated) {
  if (authenticated) {
    loginCard.classList.add('hidden');
    chatCard.classList.remove('hidden');
    messageInput.focus();
  } else {
    loginCard.classList.remove('hidden');
    chatCard.classList.add('hidden');
    loginForm.reset();
    loginFeedback.textContent = '';
    chatWindow.innerHTML = `
      <div class="message system">
        <p>Ingen samtale enda. Send en melding for å starte.</p>
      </div>
    `;
  }
}

function updateAccessPill(pages) {
  if (!pages || pages.length === 0) {
    accessPill.textContent = 'Ingen sider tildelt';
    accessPill.classList.add('muted');
  } else {
    accessPill.textContent = `Tilgang: ${pages.join(', ')}`;
    accessPill.classList.remove('muted');
  }
}

function appendMessage(role, text) {
  const bubble = document.createElement('div');
  bubble.className = `message ${role}`;
  bubble.textContent = text;
  chatWindow.appendChild(bubble);
  chatWindow.scrollTop = chatWindow.scrollHeight;
  return bubble;
}

async function checkSession() {
  try {
    const response = await fetch(buildUrl('/api/session'), {
      headers: { Accept: 'application/json' },
      credentials: CREDENTIALS_MODE,
    });
    const data = await response.json();
    if (data.authenticated) {
      state.username = data.username;
      state.allowedPages = data.allowedPages || [];
      sessionStatus.textContent = `Innlogget som ${data.username || 'ukjent bruker'}`;
      updateAccessPill(state.allowedPages);
      toggleUI(true);
    } else {
      state.username = null;
      state.allowedPages = [];
      sessionStatus.textContent = 'Ikke innlogget';
      updateAccessPill([]);
      toggleUI(false);
    }
  } catch {
    sessionStatus.textContent = 'Kunne ikke sjekke økt';
    toggleUI(false);
  }
}

loginForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  loginFeedback.textContent = '';
  const formData = new FormData(loginForm);
  const payload = Object.fromEntries(formData.entries());
  try {
    const response = await fetch(buildUrl('/api/login'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: CREDENTIALS_MODE,
      body: JSON.stringify(payload),
    });
    const data = await response.json();
    if (!response.ok) {
      loginFeedback.textContent = data.error || 'Innlogging feilet.';
      return;
    }
    state.username = payload.username;
    state.allowedPages = data.allowedPages || [];
    sessionStatus.textContent = `Innlogget som ${state.username}`;
    updateAccessPill(state.allowedPages);
    toggleUI(true);
  } catch (error) {
    loginFeedback.textContent = 'Nettverksfeil. Prøv igjen.';
  }
});

chatForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  const agentId = agentIdInput.value.trim();
  const message = messageInput.value.trim();
  if (!agentId) {
    appendMessage('system', 'Oppgi en agent-ID før du sender meldinger.');
    return;
  }
  if (!message) {
    return;
  }
  localStorage.setItem(STORAGE_KEY, agentId);
  appendMessage('user', message);
  messageInput.value = '';
  messageInput.focus();
  sendButton.disabled = true;
  const thinkingBubble = appendMessage('agent', '...');
  try {
    const response = await fetch(buildUrl('/api/query'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: CREDENTIALS_MODE,
      body: JSON.stringify({ agentId, message }),
    });
    const data = await response.json();
    if (!response.ok) {
      thinkingBubble.textContent = data.error || 'Noe gikk galt.';
      thinkingBubble.className = 'message system';
      return;
    }
    thinkingBubble.textContent = data.reply || 'Agenten svarte uten tekst.';
    thinkingBubble.className = 'message agent';
  } catch (error) {
    thinkingBubble.textContent = 'Kunne ikke kontakte agenten. Prøv igjen.';
    thinkingBubble.className = 'message system';
  } finally {
    sendButton.disabled = false;
  }
});

logoutButton.addEventListener('click', async () => {
  try {
    await fetch(buildUrl('/api/logout'), {
      method: 'POST',
      credentials: CREDENTIALS_MODE,
    });
  } finally {
    state.username = null;
    state.allowedPages = [];
    sessionStatus.textContent = 'Ikke innlogget';
    updateAccessPill([]);
    toggleUI(false);
  }
});

checkSession();

