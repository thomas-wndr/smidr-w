## Smidr Agent Portal

Password-gated chat surface for the OpenAI Agent Builder bot that will live on `smidr.org`.

### Stack
- `express` server that serves the static UI and proxies chat requests to OpenAI.
- Minimal cookie-based session store kept in memory (replace with Redis or your auth provider in production).
- Vanilla HTML/CSS/JS frontend with a central chat rail.

### Getting started
```bash
npm install
cp env.example .env # edit with real credentials
npm run dev
```
- Update `APP_USERS` with `email:password` pairs for anyone allowed to log in. For production, swap this with Supabase/Auth0/etc.
- `CORS_ORIGINS` can stay empty for local dev; set to your Hostinger domains for prod.

### OpenAI agent hook-up
1. In the Agent Builder dashboard, open the agent you want to expose.
2. Copy the `Agent ID` (workflow ID) from the **API** tab and set it in your `.env` file as `OPENAI_AGENT_ID=your_workflow_id_here`.
3. Generate a standard API key with access to that agent and set `OPENAI_API_KEY` in your `.env` file.

Every chat request hits `/api/chat`, which forwards the full conversation transcript to `openai.responses.create({ agent_id })`. User email is attached in `metadata` so your agent can personalize responses if needed.

### Deploying on Hostinger
1. Build a Node project in hPanel → Websites → Node.js.
2. Upload the repo contents or connect via Git.
3. Set the **Application Startup File** to `server.js`.
4. Add the environment variables from `.env` in the Hostinger dashboard.
5. Enable HTTPS and keep `NODE_ENV=production` to enforce secure cookies.

### Next steps / hardening
- Migrate sessions to a persistent store (Redis) or integrate a managed auth provider.
- Add rate limiting per user/IP before the chat endpoint.
- Replace the static credential list with your CRM or identity system.
- Consider logging request/response pairs to CloudWatch/Logtail for auditing.

With the basics wired, you can customize the UI inside `public/` to match the rest of smidr.org and embed supporting copy/links around the chat rail.


