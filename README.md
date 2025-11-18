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
