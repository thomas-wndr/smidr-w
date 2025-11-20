# Smidr Agent Interface

Dette er en nettside for å chatte med din OpenAI-agent på `smidr.org`.

## 🔧 PHP Version (Current - for Hostinger Shared Hosting)

### Oppsett
1.  **Last opp filer**: Last opp alle PHP-filene til din Hostinger `public_html` mappe.
2.  **Konfigurer .env**:
    *   Åpne `.env` filen.
    *   Legg inn din `OPENAI_API_KEY`.
    *   Legg inn din `ASSISTANT_ID` (Workflow ID).
    *   Endre `APP_USERNAME` og `APP_PASSWORD` til ønsket brukernavn og passord.

### Sikkerhet
*   Passord og API-nøkler lagres i `.env` filen.
*   `.htaccess` filen sørger for at ingen kan lese `.env` filen fra nettleseren.
*   `api.php` fungerer som et mellomledd slik at API-nøkkelen din aldri eksponeres for brukeren.

### Utvidelse
For å legge til flere sider senere:
1.  Opprett nye `.php` filer.
2.  Inkluder sjekken for `$_SESSION['logged_in']` på toppen av hver fil (se `index.php` for eksempel).
3.  Legg til navigasjon i `index.php`.

---

## 🚀 Node.js Version (Alternative - for VPS/Node Hosting)

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
- Update `APP_USERS` with `email:password` pairs for anyone allowed to log in.
- `CORS_ORIGINS` can stay empty for local dev; set to your Hostinger domains for prod.

### OpenAI agent hook-up
1. In the Agent Builder dashboard, open the agent you want to expose.
2. Copy the `Agent ID` (workflow ID) from the **API** tab and set it in your `.env` file as `OPENAI_AGENT_ID=your_workflow_id_here`.
3. Generate a standard API key with access to that agent and set `OPENAI_API_KEY` in your `.env` file.

### Deploying on Hostinger
1. Build a Node project in hPanel → Websites → Node.js.
2. Upload the repo contents or connect via Git.
3. Set the **Application Startup File** to `server.js`.
4. Add the environment variables from `.env` in the Hostinger dashboard.
5. Enable HTTPS and keep `NODE_ENV=production` to enforce secure cookies.

