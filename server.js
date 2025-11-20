import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import cookieParser from 'cookie-parser';
import path from 'path';
import crypto from 'crypto';
import { fileURLToPath } from 'url';
import OpenAI from 'openai';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 8080;
const SESSION_TTL_MS = 1000 * 60 * 60 * 12; // 12 hours

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const allowedOrigins = (process.env.CORS_ORIGINS || '')
  .split(',')
  .map((origin) => origin.trim())
  .filter(Boolean);

const USERS = (process.env.APP_USERS || '')
  .split(',')
  .map((entry) => entry.trim())
  .filter(Boolean)
  .map((entry) => {
    const [email, password] = entry.split(':');
    return { email: email?.toLowerCase(), password };
  });

if (!process.env.OPENAI_API_KEY) {
  console.warn('[startup] OPENAI_API_KEY is not set. Chat endpoint will fail until configured.');
}

if (!process.env.OPENAI_AGENT_ID) {
  console.warn('[startup] OPENAI_AGENT_ID is not set. Responses will fall back to direct model calls.');
}

if (!process.env.OPENAI_MODEL) {
  console.warn('[startup] OPENAI_MODEL is not set. Defaulting to gpt-4.1-mini');
}

const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });
const sessions = new Map();

app.use(
  cors({
    origin: (origin, callback) => {
      if (!origin || allowedOrigins.length === 0 || allowedOrigins.includes(origin)) {
        return callback(null, true);
      }
      return callback(new Error('Not allowed by CORS'));
    },
    credentials: true,
  })
);
app.use(express.json());
app.use(cookieParser());
app.use(express.static(path.join(__dirname, 'public')));

const requireAuth = (req, res, next) => {
  const token = req.cookies?.session_token;
  if (!token) {
    return res.status(401).json({ error: 'not_authenticated' });
  }
  const session = sessions.get(token);
  if (!session || session.expiresAt < Date.now()) {
    sessions.delete(token);
    return res.status(401).json({ error: 'session_expired' });
  }
  req.user = session.user;
  return next();
};

const issueSession = (user) => {
  const token = crypto.randomBytes(32).toString('hex');
  sessions.set(token, {
    user,
    issuedAt: Date.now(),
    expiresAt: Date.now() + SESSION_TTL_MS,
  });
  return token;
};

app.post('/api/login', (req, res) => {
  const { email, password } = req.body || {};
  if (!email || !password) {
    return res.status(400).json({ error: 'missing_credentials' });
  }
  const match = USERS.find((user) => user.email === email.toLowerCase() && user.password === password);
  if (!match) {
    return res.status(401).json({ error: 'invalid_credentials' });
  }
  const token = issueSession({ email: match.email });
  res.cookie('session_token', token, {
    httpOnly: true,
    sameSite: 'lax',
    secure: process.env.NODE_ENV === 'production',
    maxAge: SESSION_TTL_MS,
  });
  return res.json({ ok: true, user: { email: match.email } });
});

app.post('/api/logout', (req, res) => {
  const token = req.cookies?.session_token;
  if (token) {
    sessions.delete(token);
    res.clearCookie('session_token');
  }
  return res.json({ ok: true });
});

app.get('/api/session', requireAuth, (req, res) => {
  return res.json({ user: req.user });
});

app.post('/api/chat', requireAuth, async (req, res) => {
  const { message, conversation } = req.body || {};
  if (!message) {
    return res.status(400).json({ error: 'missing_message' });
  }
  const hasAgent = Boolean(process.env.OPENAI_AGENT_ID);
  const hasModel = Boolean(process.env.OPENAI_MODEL);
  if (!hasAgent && !hasModel) {
    return res.status(500).json({ error: 'model_not_configured' });
  }
  try {
    const response = await openai.responses.create({
      ...(hasAgent ? { agent_id: process.env.OPENAI_AGENT_ID } : {}),
      ...(hasAgent ? {} : { model: process.env.OPENAI_MODEL || 'gpt-4.1-mini' }),
      input: [
        ...(Array.isArray(conversation) ? conversation : []),
        { role: 'user', content: message },
      ],
      metadata: {
        userEmail: req.user.email,
        source: 'smidr-web',
      },
    });
    const assistantMessage = response.output?.[0]?.content?.[0]?.text || 'No response';
    return res.json({ reply: assistantMessage });
  } catch (error) {
    console.error('[chat] error', error);
    return res.status(500).json({ error: 'chat_failed' });
  }
});

app.get('*', (_req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

app.listen(PORT, () => {
  console.log(`smidr agent web listening on port ${PORT}`);
});


