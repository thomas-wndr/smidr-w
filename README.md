# Smidr webagent

En enkel, innlogget webflate for å snakke med agentene dine i OpenAI Agent Builder. Løsningen kjører uten rammeverk (kun standard Python + statiske filer) slik at den fungerer både på Hostinger og GitHub Pages.

## Struktur

- `server.py` – minimal HTTP-server som håndterer innlogging, økter og proxy-kall til OpenAI sitt Responses-API.
- `index.html`, `styles.css`, `app.js`, `config.js` – svart/hvitt front-end som viser et innloggingskort og et sentrert chatgrensesnitt.

## Miljøvariabler

**Lokalt:** Kopier `.env.example` til `.env` og fyll inn verdiene dine. Filen `.env` er ignorert i Git.

**På Hostinger:** Last opp `.env`-filen din til `public_html/` (samme mappe som `server.py`) via File Manager eller FTP. Serveren leser automatisk fra `.env`-filen hvis den finnes. Du kan også sette miljøvariabler via systemet hvis Hostinger støtter det, men `.env`-filen er enklest.

| Variabel | Standard | Beskrivelse |
| --- | --- | --- |
| `OPENAI_API_KEY` | *(ingen)* | **Påkrevd.** Nøkkel som kan kalle agenten(e) dine. |
| `ADMIN_USERNAME` | `admin` | Brukes når `APP_USERS` ikke er satt. |
| `ADMIN_PASSWORD` | `change-me` | Passord for standardbrukeren. |
| `APP_USERS` | *(tom)* | JSON som beskriver flere brukere/tilganger. Eksempel under. |
| `DEFAULT_ALLOWED_PAGES` | `default` | Kommaseparerte sider som standardbrukeren får tilgang til. |
| `ALLOWED_ORIGINS` | *(tom)* | Kommaseparerte opprinnelser som får kalle API-et via CORS. Sett til `https://smidr.org` hvis frontenden ligger et annet sted. |
| `SESSION_COOKIE_SAMESITE` | *(auto)* | Overstyr `SameSite` for sesjonskapselen. |
| `SESSION_COOKIE_SECURE` | *(auto)* | Sett til `true` når du bruker `SameSite=None`. |
| `HOST` | `0.0.0.0` | Adresse serveren binder seg til. |
| `PORT` | `8000` | HTTP-port. |

### Flere brukere / tilgangsstyring

Sett `APP_USERS` til en JSON-struktur som beskriver brukere, passord og hvilke "pages" de får se i UI-et (benyttes i senere utvidelser):

```json
[
  { "username": "anne", "password": "supersecret", "pages": ["agent-a", "agent-b"] },
  { "username": "per", "password": "hunter2", "pages": ["agent-c"] }
]
```

Hvis `APP_USERS` ikke er satt, brukes `ADMIN_USERNAME`/`ADMIN_PASSWORD` og `DEFAULT_ALLOWED_PAGES`.

## Frontend-konfigurasjon

`config.js` beskriver hvordan klienten finner API-et og hvilket agent-ID-felt som skal forhåndsutfylles:

```js
window.__APP_CONFIG__ = {
  apiBaseUrl: '',         // pek mot https://smidr.org når frontenden hostes et annet sted
  defaultAgentId: ''      // valgfritt: forhåndsverdien i agent-feltet
};
```

La `apiBaseUrl` stå tom hvis UI-et lever på samme domene som `server.py`. Dersom du bruker GitHub Pages eller et annet CDN, sett `apiBaseUrl` til Hostinger-domenet der Python-serveren kjører og legg samme domene til i `ALLOWED_ORIGINS`.

## Kjøre lokalt

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
export OPENAI_API_KEY="sk-..."
python server.py
```

Serveren svarer på `http://localhost:8000`. Når du har logget inn kan du skrive inn agent-ID og melding – svar vises i chatvinduet.

## Utrulling

- **Hostinger:** Repositoryet kan nå klones rett inn i `public_html/`. Etter `git pull` ligger `index.html`, `styles.css`, `app.js` og `config.js` i roten, så du trenger ingen ekstra flytte-steg. Last opp `.env`-filen din til samme mappe via File Manager eller FTP. Start Python-appen (eller kjør via `gunicorn`/FastCGI) slik du gjorde tidligere.
- **GitHub Pages:** Workflowen `.github/workflows/deploy.yml` pakker de samme rotfilene i en `site/`-mappe og publiserer dem via GitHub Actions når du pusher til `main`. Sørg for at Pages er aktivert (Settings → Pages → GitHub Actions).

Når GitHub Actions/Hostinger er ferdig deployet, peker domenet `smidr.org` til den siste versjonen og du kan administrere tilgangene ved å oppdatere `.env` og kjøre `git push`.
