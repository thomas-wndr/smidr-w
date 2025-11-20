# Smidr Agent Interface

Dette er en enkel nettside for å chatte med din OpenAI-agent.

## Oppsett

1.  **Last opp filer**: Last opp alle filene til din Hostinger `public_html` mappe (eller en undermappe).
2.  **Konfigurer .env**:
    *   Åpne `.env` filen.
    *   Legg inn din `OPENAI_API_KEY`.
    *   Legg inn din `ASSISTANT_ID` (Workflow ID).
    *   Endre `APP_USERNAME` og `APP_PASSWORD` til ønsket brukernavn og passord.

## Sikkerhet

*   Passord og API-nøkler lagres i `.env` filen.
*   `.htaccess` filen sørger for at ingen kan lese `.env` filen fra nettleseren.
*   `api.php` fungerer som et mellomledd slik at API-nøkkelen din aldri eksponeres for brukeren.

## Utvidelse

For å legge til flere sider senere:
1.  Opprett nye `.php` filer.
2.  Inkluder sjekken for `$_SESSION['logged_in']` på toppen av hver fil (se `index.php` for eksempel).
3.  Legg til navigasjon i `index.php`.
