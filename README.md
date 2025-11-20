# Smidr.org - OpenAI Integration Guide

## 🎯 Two Implementation Options

You have **two ways** to integrate OpenAI with your website:

### **Option 1: ChatKit (Recommended for Agent Builder)**
✅ **Use this if**: You created your AI in OpenAI's Agent Builder  
✅ **Pros**: Direct integration with workflows, simpler setup, pre-built UI  
✅ **ID Format**: `wf_xxxxxxxxxx` (workflow ID)

### **Option 2: Assistants API (Traditional)**
✅ **Use this if**: You created a traditional Assistant  
✅ **Pros**: More control, custom UI, works with Assistants  
✅ **ID Format**: `asst_xxxxxxxxxx` (assistant ID)

---

## 🚀 Setup Instructions

### **For ChatKit (Option 1)**

#### 1. Update Your `.env` File
```bash
OPENAI_API_KEY=sk-proj-your_actual_api_key_here
WORKFLOW_ID=wf_69145e0b97e481909af5dd3041c90917016e2b21a97dc5e6
APP_USERNAME=admin
APP_PASSWORD=your_secure_password
```

#### 2. Configure Domain Allowlist
1. Go to https://platform.openai.com/settings/organization/general
2. Find "ChatKit Domain Allowlist"
3. Add your domain: `smidr.org`
4. Save changes

#### 3. Upload Files to Hostinger
Upload these files to your Hostinger web directory:
- `index-chatkit.html` → Rename to `index.php` (or use as is)
- `chatkit-session.php`
- `login.php`
- `logout.php`
- `config.php`
- `.env` (with your actual credentials)

#### 4. Test Your Site
Visit `https://smidr.org` and you should see the ChatKit interface!

---

### **For Assistants API (Option 2)**

#### 1. Create an Assistant
1. Go to https://platform.openai.com/assistants
2. Click "Create" or "+ New Assistant"
3. Configure:
   - **Name**: Your assistant name
   - **Instructions**: Your AI's behavior instructions
   - **Model**: GPT-4 or GPT-4 Turbo
   - **Tools**: Enable as needed
4. Copy the **Assistant ID** (starts with `asst_`)

#### 2. Update Your `.env` File
```bash
OPENAI_API_KEY=sk-proj-your_actual_api_key_here
ASSISTANT_ID=asst_your_actual_assistant_id_here
APP_USERNAME=admin
APP_PASSWORD=your_secure_password
```

#### 3. Upload Files to Hostinger
Upload these files:
- `index.php`
- `api.php`
- `script.js`
- `style.css`
- `login.php`
- `logout.php`
- `config.php`
- `.env` (with your actual credentials)

#### 4. Test Your Site
Visit `https://smidr.org` and test the chat!

---

## 📁 File Structure

```
smidr.org/
├── .env                    # Your secret credentials (NEVER commit to Git!)
├── .env.example            # Template for .env file
├── .gitignore              # Prevents .env from being committed
├── config.php              # Loads environment variables
├── login.php               # Authentication endpoint
├── logout.php              # Logout handler
│
# ChatKit Implementation (Option 1)
├── index-chatkit.html      # ChatKit-based interface
├── chatkit-session.php     # Generates ChatKit client_secret
│
# Assistants API Implementation (Option 2)
├── index.php               # Traditional custom interface
├── api.php                 # Assistants API backend
├── script.js               # Frontend JavaScript
└── style.css               # Styling
```

---

## 🔒 Security Checklist

- [ ] `.env` file is NOT committed to Git (check `.gitignore`)
- [ ] Strong password set in `.env`
- [ ] API key is kept secret
- [ ] Domain allowlist configured (for ChatKit)
- [ ] HTTPS enabled on your domain

---

## 🐛 Troubleshooting

### ChatKit Not Loading
1. **Check domain allowlist**: Make sure `smidr.org` is in your OpenAI organization settings
2. **Check workflow ID**: Verify it starts with `wf_`
3. **Check API key**: Ensure it's valid and has correct permissions
4. **Check browser console**: Look for error messages

### Assistants API Errors
1. **"Invalid assistant_id"**: Make sure ID starts with `asst_`, not `wf_`
2. **"Failed to start run"**: Check that your Assistant exists and is published
3. **"Configuration missing"**: Verify `.env` file is loaded correctly

### Login Issues
1. Check `config.php` is loading `.env` correctly
2. Verify username/password in `.env` match your login attempt
3. Check PHP session is working

---

## 📚 Additional Resources

- [OpenAI ChatKit Documentation](https://platform.openai.com/docs/guides/chatkit)
- [OpenAI Assistants API Documentation](https://platform.openai.com/docs/assistants)
- [OpenAI Agent Builder](https://platform.openai.com/agents)

---

## 🆘 Need Help?

If you encounter issues:
1. Check the browser console for errors (F12 → Console tab)
2. Check PHP error logs on Hostinger
3. Verify all environment variables are set correctly
4. Ensure all files are uploaded to the correct directory

---

## 📝 Notes

- **ChatKit** is the newer, simpler approach for Agent Builder workflows
- **Assistants API** gives you more control but requires more setup
- You can use **either** approach, but not both simultaneously
- Keep your `.env` file secure and never share it publicly
