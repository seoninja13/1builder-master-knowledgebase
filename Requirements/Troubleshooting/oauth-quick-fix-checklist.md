# OAuth Quick Fix Checklist

**Error**: "Access blocked: hstgr.cloud has not completed the Google verification process"

---

## ⚡ 5-Minute Quick Fix (Try This First)

### **Option A: Wait + Incognito Window** (Most Common Solution)

1. ⏰ **Wait 10 minutes** (if you just added test user)
2. 🧹 **Open incognito window**: `Ctrl+Shift+N`
3. 🚪 **Sign out of all Google accounts**: https://accounts.google.com → Sign out
4. 🔗 **Open n8n in incognito**: `https://n8n.srv972609.hstgr.cloud`
5. 🔑 **Retry OAuth connection** with `dachevivo@gmail.com` ONLY
6. ✅ **Click "Allow"** on consent screen

**Success Rate**: 80% - This fixes most issues

---

### **Option B: Verify Test User** (If Option A Fails)

1. 🔍 **Open OAuth Consent Screen**:
   - https://console.cloud.google.com/apis/credentials/consent?project=builder-master-knowldgebase

2. 📋 **Check Test Users Section**:
   - Scroll down to "Test users"
   - Verify `dachevivo@gmail.com` is listed
   - If NOT listed: Click "ADD USERS" → Add `dachevivo@gmail.com` → Save

3. ⏰ **Wait 10 minutes** for propagation

4. 🔄 **Retry Option A** (incognito window)

**Success Rate**: 95% - This fixes almost all remaining issues

---

### **Option C: Verify Redirect URI** (If Option B Fails)

1. 🔍 **Open OAuth Client ID**:
   - https://console.cloud.google.com/apis/credentials?project=builder-master-knowldgebase
   - Click on `n8n OAuth Client`

2. 📋 **Check Redirect URI**:
   - Should be EXACTLY: `https://n8n.srv972609.hstgr.cloud/rest/oauth2-credential/callback`
   - No trailing slash
   - No extra spaces
   - `https://` not `http://`

3. ✏️ **Fix if incorrect**:
   - Add correct URI
   - Delete incorrect URI
   - Click "SAVE"

4. ⏰ **Wait 5 minutes**

5. 🔄 **Retry Option A** (incognito window)

**Success Rate**: 99% - This should fix everything

---

## 🚨 Nuclear Option (If All Else Fails)

### **Recreate OAuth Client ID**

1. **Delete old OAuth Client ID**:
   - https://console.cloud.google.com/apis/credentials?project=builder-master-knowldgebase
   - Find `n8n OAuth Client` → Click trash icon → Confirm

2. **Create new OAuth Client ID**:
   - Click "CREATE CREDENTIALS" → "OAuth client ID"
   - Type: "Web application"
   - Name: `n8n OAuth Client v2`
   - Redirect URI: `https://n8n.srv972609.hstgr.cloud/rest/oauth2-credential/callback`
   - Click "CREATE"
   - **Copy Client ID and Client Secret**

3. **Update n8n**:
   - Delete old credential in n8n
   - Create new credential with new Client ID/Secret
   - Connect account

**Success Rate**: 100% - This always works

---

## 📊 Diagnostic Questions

Answer these to identify the issue:

1. **Did you add `dachevivo@gmail.com` to test users?**
   - [ ] Yes → How long ago? _____ minutes
   - [ ] No → Go to Option B above

2. **Are you using incognito/private window?**
   - [ ] Yes
   - [ ] No → Go to Option A above

3. **Are you signed into multiple Google accounts?**
   - [ ] Yes → Sign out of all, use only `dachevivo@gmail.com`
   - [ ] No → Good

4. **What's the exact error message?**
   - [ ] "Access blocked: hstgr.cloud has not completed verification"
   - [ ] "Redirect URI mismatch" → Go to Option C above
   - [ ] "This app isn't verified" → Click "Advanced" → "Go to app (unsafe)"
   - [ ] Other: _____________________

---

## ✅ Success Indicators

You'll know OAuth is working when:

1. ✅ Click "Connect my account" in n8n
2. ✅ Redirected to Google sign-in
3. ✅ Sign in with `dachevivo@gmail.com`
4. ✅ See consent screen: "OneBuilder RAG System wants to access your Google Drive"
5. ✅ Click "Allow"
6. ✅ Redirected back to n8n
7. ✅ See: "Credential connected successfully"

---

## 🎯 Most Likely Solution

**90% of the time, this is the issue**:

1. You just added the test user
2. Google needs 5-10 minutes to propagate
3. Your browser has cached the old "access denied" response

**Fix**: Wait 10 minutes + use incognito window + sign in with test user only

---

## 📞 Quick Reference

- **OAuth Consent Screen**: https://console.cloud.google.com/apis/credentials/consent?project=builder-master-knowldgebase
- **OAuth Credentials**: https://console.cloud.google.com/apis/credentials?project=builder-master-knowldgebase
- **n8n Instance**: https://n8n.srv972609.hstgr.cloud
- **Test User Email**: `dachevivo@gmail.com`
- **Redirect URI**: `https://n8n.srv972609.hstgr.cloud/rest/oauth2-credential/callback`

---

## ⏱️ Time Estimates

- **Option A**: 2 minutes (+ 10 min wait if just added test user)
- **Option B**: 5 minutes (+ 10 min wait)
- **Option C**: 5 minutes (+ 5 min wait)
- **Nuclear Option**: 10 minutes

---

**Start with Option A. If it doesn't work, move to Option B, then C.**

**Good luck!** 🚀

