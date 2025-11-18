# Smidr webagent

En enkel innlogget webflate for å sende meldinger til landmåleragenten (eller andre agenter) du har laget i OpenAI Agent Builder. Løsningen kjører uten eksterne rammeverk slik at den kan brukes i miljøer uten tilgang til npm/pip, og består av:

- `server.py` – et lite HTTP-API som håndterer innlogging, økter og proxy-kall til OpenAI sitt Responses-API.
- `public/` – statiske filer (HTML/CSS/JS) med hvit bakgrunn og svart tekst.

## Konfigurasjon

Serveren leser følgende miljøvariabler:

| Variabel | Standard | Beskrivelse |
| --- | --- | --- |
| `ADMIN_USERNAME` | `admin` | Brukernavn for innlogging. |
| `ADMIN_PASSWORD` | `change-me` | Passord for innlogging. |
| `OPENAI_API_KEY` | *(ingen)* | Påkrevd. API-nøkkel med tilgang til agentene dine. |
| `HOST` | `0.0.0.0` | Adresse serveren binder seg til. |
| `PORT` | `8000` | HTTP-port. |
| `ALLOWED_ORIGINS` | *(tom)* | Kommaseparert liste med opprinnelser (f.eks. `https://dittnavn.github.io`) som får kalle API-et via CORS. Bruk `*` for å åpne for alle (anbefales ikke). |
| `SESSION_COOKIE_SAMESITE` | *(auto)* | Sett til `None`, `Lax` eller `Strict` for å overstyre standardverdi. |
| `SESSION_COOKIE_SECURE` | *(auto)* | Sett til `true` for å tvinge `Secure`-flagg på informasjonskapselen (kreves når `SameSite=None`). |

Når `ALLOWED_ORIGINS` er satt, eksponeres API-et via CORS og informasjonskapselen får automatisk `SameSite=None; Secure` dersom du ikke overstyrer dette eksplisitt.

## Frontend-konfigurasjon

Filene under `public/` kan publiseres som statisk side (for eksempel på GitHub Pages). `public/config.js` inneholder et lite konfigurasjonsobjekt du kan endre:

```js
window.__APP_CONFIG__ = {
  apiBaseUrl: '' // pek mot "https://smidr.org" når frontenden kjører et annet sted
};
```

La verdien være tom når du kjører frontenden fra samme domene som `server.py`. Sett den til `https://smidr.org` (eller et Hostinger-subdomene) dersom du f.eks. hoster UI-et på GitHub Pages og proxier API-et via Hostinger.

## Kjøre lokalt

```bash
export ADMIN_USERNAME="ditt-brukernavn"
export ADMIN_PASSWORD="ditt-passord"
export OPENAI_API_KEY="sk-..."
python server.py
```

Applikasjonen er nå tilgjengelig på `http://localhost:8000`. Når du har logget inn, skriver du inn agent-IDen (fra OpenAI Agent Builder) og meldingen du ønsker å sende. Svar fra agenten vises umiddelbart i grensesnittet.

## Utrulling

Løsningen krever kun Python 3.9+ og tilgang ut mot `api.openai.com`. Den kan kjøres som en systemd-tjeneste, Docker-container eller via Hostinger sin Python-støtte. Husk å legge inn miljøvariablene over i Hostinger sitt kontrollpanel og å sikre forbindelsen med HTTPS når du publiserer til `smidr.org`.

### Deploy til GitHub Pages

Repositoryet inneholder workflowen `.github/workflows/deploy.yml` som automatisk bygger og publiserer katalogen `public/` til GitHub Pages når du pusher til `main`.

1. Aktiver GitHub Pages i repoet ditt (Settings → Pages → "Build and deployment" → GitHub Actions).
2. Oppdater `public/config.js` slik at `apiBaseUrl` peker på domenet der `server.py` kjører (for eksempel `https://smidr.org`).
3. På Hostinger setter du `ALLOWED_ORIGINS=https://<brukernavn>.github.io` og sørger for HTTPS. Dette lar GitHub Pages-frontend kommunisere med API-et.
4. Dersom du bruker GitHub Pages må informasjonskapselen være tilgjengelig på tvers av domener. Sett derfor eventuelt `SESSION_COOKIE_SAMESITE=None` og `SESSION_COOKIE_SECURE=true` hvis du ønsker å overstyre standarden.

Når workflowen har kjørt ferdig finner du en "Deployments"-oppføring i GitHub som peker til den publiserte siden. Backend (Hostinger) oppdateres som tidligere – GitHub Pages leverer kun frontend.
