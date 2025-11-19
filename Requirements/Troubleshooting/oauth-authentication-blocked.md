# Troubleshooting: OAuth Authentication Blocked by Google

**Error**: "Access blocked: hstgr.cloud has not completed the Google verification process"

**Date**: 2025-01-17  
**Phase**: Phase 2 - OAuth Setup  
**Status**: ⚠️ TROUBLESHOOTING IN PROGRESS

---

## 🔍 Error Analysis

### **What This Error Means**:
This error occurs when:
1. The OAuth consent screen is in "Testing" mode (not published)
2. The user attempting to authenticate is NOT in the "Test users" list
3. OR there's a propagation delay after adding the test user

### **Why This Happens**:
- Google requires apps to be verified before allowing public access
- During development, apps stay in "Testing" mode
- Only pre-approved test users can authenticate in "Testing" mode
- Changes to test users can take 5-10 minutes to propagate

---

## ✅ Step-by-Step Verification & Resolution

### **STEP 1: Verify OAuth Consent Screen Configuration** (5 minutes)

1. **Open OAuth Consent Screen**:
   - Go to: https://console.cloud.google.com/apis/credentials/consent?project=builder-master-knowldgebase

2. **Check Publishing Status**:
   - Look for the status badge at the top
   - Should say: **"Testing"** (NOT "In production")
   - If it says "In production", you need to unpublish it

3. **Verify User Type**:
   - Should be: **"External"**
   - If it's "Internal", you need to recreate it as "External"

4. **Check Test Users**:
   - Scroll down to the "Test users" section
   - Verify `dachevivo@gmail.com` is listed
   - If NOT listed, click **"ADD USERS"** and add it

5. **Verify Scopes**:
   - Click **"EDIT APP"**
   - Go to "Scopes" step
   - Verify these scopes are added:
     - `https://www.googleapis.com/auth/drive.file`
     - `https://www.googleapis.com/auth/drive`
   - If missing, add them and save

✅ **Checkpoint**: OAuth consent screen is in "Testing" mode with `dachevivo@gmail.com` as test user

---

### **STEP 2: Verify OAuth Client ID Configuration** (3 minutes)

1. **Open Credentials Page**:
   - Go to: https://console.cloud.google.com/apis/credentials?project=builder-master-knowldgebase

2. **Find Your OAuth Client ID**:
   - Look for: `n8n OAuth Client` (or similar name)
   - Click on it to edit

3. **Verify Redirect URI**:
   - Check "Authorized redirect URIs" section
   - Should have EXACTLY: `https://n8n.srv972609.hstgr.cloud/rest/oauth2-credential/callback`
   - **IMPORTANT**: No trailing slash, exact match required

4. **Check for Typos**:
   - Common mistakes:
     - `http://` instead of `https://`
     - Extra spaces before or after the URL
     - Trailing slash at the end
     - Wrong subdomain or path

5. **If Incorrect**:
   - Click **"ADD URI"**
   - Enter the correct URI
   - Delete the incorrect one
   - Click **"SAVE"**

✅ **Checkpoint**: Redirect URI exactly matches n8n callback URL

---

### **STEP 3: Wait for Propagation** (5-10 minutes)

If you just added the test user or made changes:

1. **Wait 5-10 minutes** for Google's systems to propagate the changes
2. **Do NOT retry immediately** - this can cause caching issues
3. **Use this time to**:
   - Clear browser cache
   - Close all browser tabs
   - Sign out of all Google accounts

✅ **Checkpoint**: Waited at least 5 minutes after making changes

---

### **STEP 4: Clear Browser State & Retry** (5 minutes)

1. **Clear Browser Cache**:
   - Chrome: `Ctrl+Shift+Delete` → Select "Cookies and other site data" → Clear
   - Firefox: `Ctrl+Shift+Delete` → Select "Cookies" → Clear
   - Edge: `Ctrl+Shift+Delete` → Select "Cookies and other site data" → Clear

2. **Sign Out of All Google Accounts**:
   - Go to: https://accounts.google.com
   - Click your profile picture → "Sign out of all accounts"

3. **Use Incognito/Private Window**:
   - Chrome: `Ctrl+Shift+N`
   - Firefox: `Ctrl+Shift+P`
   - Edge: `Ctrl+Shift+N`

4. **Retry OAuth Connection**:
   - Open n8n in incognito window: `https://n8n.srv972609.hstgr.cloud`
   - Go to Credentials → Edit your Google Drive OAuth credential
   - Click **"Connect my account"**
   - Sign in with `dachevivo@gmail.com` ONLY
   - Grant permissions

✅ **Checkpoint**: OAuth connection attempted in clean browser state

---

### **STEP 5: Alternative Solution - Use Different Redirect URI** (if above fails)

If the error persists, try using a different redirect URI format:

1. **Check n8n's OAuth Callback URL**:
   - In n8n, go to Settings → OAuth Callback URL
   - Copy the EXACT URL shown (it might be different from what we assumed)

2. **Update Google Cloud Console**:
   - Go back to OAuth Client ID settings
   - Add the EXACT callback URL from n8n
   - Save changes

3. **Wait 5 minutes** and retry

✅ **Checkpoint**: Using exact callback URL from n8n settings

---

## 🔧 Common Issues & Solutions

### **Issue 1: "Access blocked" error persists after adding test user**
**Solution**: 
- Wait 10 minutes (not 5) for propagation
- Try in incognito window
- Verify email is EXACTLY `dachevivo@gmail.com` (no typos)

### **Issue 2: "Redirect URI mismatch" error**
**Solution**:
- Copy the EXACT redirect URI from the error message
- Add it to Google Cloud Console OAuth Client ID
- Remove any incorrect URIs

### **Issue 3: "This app isn't verified" warning**
**Solution**:
- This is NORMAL for apps in "Testing" mode
- Click **"Advanced"** → **"Go to [App Name] (unsafe)"**
- This is safe because you own the app

### **Issue 4: Multiple Google accounts signed in**
**Solution**:
- Sign out of ALL Google accounts
- Sign in ONLY with `dachevivo@gmail.com`
- Retry OAuth connection

---

## 🎯 Expected Behavior After Fix

When OAuth is working correctly:

1. Click "Connect my account" in n8n
2. Redirected to Google sign-in page
3. Sign in with `dachevivo@gmail.com`
4. See consent screen: "OneBuilder RAG System wants to access your Google Drive"
5. Click **"Allow"**
6. Redirected back to n8n
7. See success message: "Credential connected successfully"

---

## 📋 Verification Checklist

Before retrying, confirm:

- [ ] OAuth consent screen is in "Testing" mode
- [ ] `dachevivo@gmail.com` is in "Test users" list
- [ ] Redirect URI exactly matches: `https://n8n.srv972609.hstgr.cloud/rest/oauth2-credential/callback`
- [ ] Required scopes are added (drive.file and drive)
- [ ] Waited at least 5-10 minutes after making changes
- [ ] Browser cache cleared
- [ ] Signed out of all Google accounts
- [ ] Using incognito/private window
- [ ] Signing in with `dachevivo@gmail.com` ONLY

---

## 🆘 If All Else Fails

### **Nuclear Option: Recreate OAuth Client ID**

1. **Delete existing OAuth Client ID**:
   - Go to: https://console.cloud.google.com/apis/credentials?project=builder-master-knowldgebase
   - Find `n8n OAuth Client`
   - Click trash icon → Confirm deletion

2. **Create new OAuth Client ID**:
   - Click **"CREATE CREDENTIALS"** → **"OAuth client ID"**
   - Application type: **"Web application"**
   - Name: `n8n OAuth Client v2`
   - Authorized redirect URIs: `https://n8n.srv972609.hstgr.cloud/rest/oauth2-credential/callback`
   - Click **"CREATE"**
   - Copy new Client ID and Client Secret

3. **Update n8n credential**:
   - Delete old credential in n8n
   - Create new credential with new Client ID and Secret
   - Retry connection

---

## 📞 Next Steps

### **If OAuth Works**:
1. ✅ Mark Task 4 as COMPLETE
2. ✅ Proceed to Task 5: Test OAuth WRITE access
3. ✅ Upload test file to verify WRITE permissions

### **If OAuth Still Fails**:
1. Take screenshots of:
   - OAuth consent screen configuration
   - OAuth Client ID settings
   - The exact error message in browser
2. Check Google Cloud Console for any error logs
3. Verify n8n instance is accessible and running correctly

---

## 📚 Reference

- **OAuth Setup Guide**: `Requirements/Guides/n8n-google-oauth-setup.md`
- **Phase 2 Next Steps**: `Requirements/PHASE-2-NEXT-STEPS.md`
- **Google OAuth Documentation**: https://developers.google.com/identity/protocols/oauth2

---

**Most Common Solution**: Wait 10 minutes after adding test user, then retry in incognito window with only `dachevivo@gmail.com` signed in.

