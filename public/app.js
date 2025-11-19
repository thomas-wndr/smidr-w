const loginModal = document.getElementById('login-modal');
const loginForm = document.getElementById('login-form');
const loginError = document.getElementById('login-error');
const chatForm = document.getElementById('chat-form');
const chatMessage = document.getElementById('chat-message');
const chatLog = document.getElementById('chat-log');
const userEmailEl = document.getElementById('user-email');
const logoutBtn = document.getElementById('logout-btn');
const template = document.getElementById('message-template');

let conversation = [];
let userEmail = null;

const formatTime = (date) =>
  date.toLocaleTimeString([], {
    hour: '2-digit',
    minute: '2-digit',
  });

const renderMessage = ({ role, content }) => {
  const fragment = template.content.cloneNode(true);
  const bubble = fragment.querySelector('.bubble');
  const author = fragment.querySelector('.author');
  const time = fragment.querySelector('.time');
  const body = fragment.querySelector('.content');

  bubble.classList.add(role === 'user' ? 'user' : 'agent');
  author.textContent = role === 'user' ? (userEmail || 'You') : 'Smidr Agent';
  time.textContent = formatTime(new Date());
  body.textContent = typeof content === 'string' ? content : JSON.stringify(content);

  chatLog.appendChild(fragment);
  chatLog.scrollTop = chatLog.scrollHeight;
};

const toggleModal = (show) => {
  loginModal.classList.toggle('open', show);
};

const fetchSession = async () => {
  try {
    const res = await fetch('/api/session', { credentials: 'include' });
    if (!res.ok) {
      throw new Error('No session');
    }
    const data = await res.json();
    userEmail = data.user.email;
    userEmailEl.textContent = userEmail;
    toggleModal(false);
  } catch {
    toggleModal(true);
  }
};

loginForm?.addEventListener('submit', async (event) => {
  event.preventDefault();
  loginError.textContent = '';
  const email = document.getElementById('login-email').value.trim();
  const password = document.getElementById('login-password').value;
  try {
    const res = await fetch('/api/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ email, password }),
    });
    if (!res.ok) {
      throw new Error('Invalid login');
    }
    const data = await res.json();
    userEmail = data.user.email;
    userEmailEl.textContent = userEmail;
    conversation = [];
    chatLog.innerHTML = '';
    toggleModal(false);
  } catch (error) {
    loginError.textContent = 'Login failed. Check your credentials.';
    console.error(error);
  }
});

logoutBtn?.addEventListener('click', async () => {
  await fetch('/api/logout', { method: 'POST', credentials: 'include' });
  userEmail = null;
  userEmailEl.textContent = '';
  toggleModal(true);
});

chatForm?.addEventListener('submit', async (event) => {
  event.preventDefault();
  const message = chatMessage.value.trim();
  if (!message || !userEmail) return;

  renderMessage({ role: 'user', content: message });
  chatMessage.value = '';

  try {
    const res = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ message, conversation }),
    });
    if (!res.ok) {
      throw new Error('Chat failed');
    }
    const data = await res.json();
    const reply = data.reply || 'No reply';
    renderMessage({ role: 'assistant', content: reply });
    conversation.push({ role: 'user', content: message });
    conversation.push({ role: 'assistant', content: reply });
  } catch (error) {
    renderMessage({ role: 'assistant', content: 'There was an error talking to the agent.' });
    console.error(error);
  }
});

fetchSession();


