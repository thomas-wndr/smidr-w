# Smidr.org - Project Status & Handover

**Last Updated:** November 20, 2025
**Current Status:** ✅ Operational with OpenAI ChatKit

## 🎯 Project Overview
This project hosts a chat interface for `smidr.org` that connects to an OpenAI Agent Builder workflow. 

**Key Technology:**
- **Frontend:** OpenAI ChatKit (Web Component)
- **Backend:** PHP (for secure session token generation)
- **Auth:** Simple PHP session-based login
- **Hosting:** Hostinger

---

## 🏗️ Current Architecture

The project is currently configured to use **OpenAI ChatKit**, which connects directly to the Agent Builder workflow (`wf_...` ID).

### **Active Files**
| File | Purpose |
|------|---------|
| `index-chatkit.html` | **Main Interface**. Contains the ChatKit widget. (Should be renamed to `index.php` or set as default). |
| `chatkit-session.php` | **Backend Endpoint**. Generates secure `client_secret` tokens for ChatKit using the API key. |
| `login.php` | Handles user authentication. |
| `logout.php` | Destroys the session. |
| `config.php` | Loads environment variables from `.env`. |
| `.env` | **Critical**. Stores secrets (API Key, Workflow ID, Password). **Not in Git**. |

### **Legacy Files (Not in use)**
*These files were for the previous Assistants API implementation and can be archived or ignored.*
- `index.php` (Old custom chat UI)
- `api.php` (Old backend for Assistants API)
- `script.js` (Old frontend logic)
- `style.css` (Old styling)

---

## ⚙️ Configuration

### **1. Environment Variables (.env)**
The `.env` file on Hostinger is correctly configured with the following structure:

```bash
# OpenAI Configuration
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# ChatKit Configuration (Active)
WORKFLOW_ID=wf_69145e0b97e481909af5dd3041c90917016e2b21a97dc5e6

# Application Authentication
APP_USERNAME=admin
APP_PASSWORD=your_secure_password
```

### **2. OpenAI Platform Settings**
- **Domain Allowlist**: `smidr.org` has been added to the "ChatKit Domain Allowlist" in OpenAI Organization Settings. This is required for the widget to load.

---

## 🚀 Deployment Status

1. **Files Uploaded**: `chatkit-session.php` and `index-chatkit.html` are uploaded to Hostinger.
2. **Configuration**: `.env` file on Hostinger has been updated with the correct `WORKFLOW_ID`.
3. **Verification**: The site loads the ChatKit interface successfully after login.

---

## � Handover Notes for Future Agents

If you are picking up this project:

1. **The "Truth" is ChatKit**: Ignore the old `api.php` / `script.js` implementation unless specifically asked to revert. Focus on `index-chatkit.html` and `chatkit-session.php`.
2. **Workflow ID**: The project uses an Agent Builder workflow (`wf_...`), NOT an Assistant ID (`asst_...`).
3. **Deployment**: Hostinger Git deployment was problematic due to existing files. We used manual file upload via Hostinger File Manager.
4. **Next Tasks**:
   - Rename `index-chatkit.html` to `index.php` on the server to make it the default page.
   - Customize the ChatKit theme if requested (done in `index-chatkit.html`).

---

## � Security Reminders
- **NEVER** commit the `.env` file to GitHub.
- **NEVER** expose the `OPENAI_API_KEY` in frontend code (HTML/JS). It must only be used in `chatkit-session.php`.
