# Deployment Checklist for ChatKit Implementation

## 📋 Pre-Deployment

- [ ] Domain allowlist configured on OpenAI Platform
  - Go to: https://platform.openai.com/settings/organization/general
  - Add domain: `smidr.org`
  - Save changes

- [ ] `.env` file updated with correct values
  ```bash
  OPENAI_API_KEY=sk-proj-your_actual_key
  WORKFLOW_ID=wf_69145e0b97e481909af5dd3041c90917016e2b21a97dc5e6
  APP_USERNAME=admin
  APP_PASSWORD=your_secure_password
  ```

## 📤 Files to Upload to Hostinger

### Required Files (ChatKit Implementation)
- [ ] `index-chatkit.html` (rename to `index.php` or set as main page)
- [ ] `chatkit-session.php`
- [ ] `login.php`
- [ ] `logout.php`
- [ ] `config.php`
- [ ] `.env` (with your actual credentials - DO NOT upload .env.example)
- [ ] `.htaccess`

### Optional Files (Keep for backup)
- [ ] `index.php` (old implementation)
- [ ] `api.php` (old implementation)
- [ ] `script.js` (old implementation)
- [ ] `style.css` (old implementation)

## 🔧 Deployment Steps

### Step 1: Access Hostinger
1. Log in to Hostinger control panel
2. Go to File Manager
3. Navigate to your `smidr.org` directory

### Step 2: Backup Current Files
1. Download or rename current `index.php` to `index-old.php`
2. Keep a backup of all current files

### Step 3: Upload New Files
1. Upload `chatkit-session.php`
2. Upload `index-chatkit.html`
3. Rename `index-chatkit.html` to `index.php` (or configure as main page)

### Step 4: Update .env File
1. Edit `.env` file on server
2. Add the line:
   ```
   WORKFLOW_ID=wf_69145e0b97e481909af5dd3041c90917016e2b21a97dc5e6
   ```
3. Verify all other values are correct
4. Save the file

### Step 5: Set Permissions
1. Set `.env` permissions to 600 (read/write for owner only)
2. Set PHP files to 644 (standard)

## ✅ Testing

### Test 1: Login
- [ ] Visit https://smidr.org
- [ ] You should see the login page
- [ ] Enter credentials and verify login works

### Test 2: ChatKit Loading
- [ ] After login, you should see "Laster chat..." message
- [ ] ChatKit interface should load within a few seconds
- [ ] If it doesn't load, check browser console (F12) for errors

### Test 3: Chat Functionality
- [ ] Send a test message
- [ ] Verify you get a response from your Agent Builder workflow
- [ ] Test multiple messages to ensure conversation works

### Test 4: Logout
- [ ] Click "Logg ut" button
- [ ] Verify you're logged out and redirected to login page

## 🐛 Troubleshooting

### ChatKit doesn't load
1. **Check browser console** (F12 → Console tab)
   - Look for errors related to ChatKit
   - Check if `client_secret` is being fetched

2. **Check domain allowlist**
   - Verify `smidr.org` is in the allowlist
   - Try adding `www.smidr.org` as well

3. **Check PHP errors**
   - Look at Hostinger error logs
   - Verify `chatkit-session.php` is working

4. **Check .env file**
   - Verify `WORKFLOW_ID` is correct
   - Verify `OPENAI_API_KEY` is valid

### "Configuration missing" error
- Check that `.env` file exists on server
- Verify `config.php` is loading the `.env` file
- Check file permissions

### Login not working
- Verify credentials in `.env` file
- Check that `login.php` is working
- Verify PHP sessions are enabled

## 📊 Success Criteria

✅ You should see:
1. Login page loads correctly
2. After login, ChatKit interface appears
3. Can send messages and receive responses
4. Logout works properly
5. No errors in browser console
6. No PHP errors in server logs

## 🔒 Security Check

- [ ] `.env` file is NOT publicly accessible
- [ ] `.env` is NOT in Git repository
- [ ] API key is not exposed in browser
- [ ] HTTPS is enabled
- [ ] Strong password is set

## 📝 Notes

- Keep the old implementation files as backup
- You can switch back by renaming files
- Monitor usage on OpenAI Platform to track API calls
- Consider setting up usage limits on OpenAI Platform

---

## 🆘 If Something Goes Wrong

1. **Rename `index.php` back to `index-chatkit.html`**
2. **Rename `index-old.php` to `index.php`**
3. **Your old implementation will be restored**

---

**Last Updated**: 2025-11-20
**Implementation**: ChatKit with Agent Builder Workflow
