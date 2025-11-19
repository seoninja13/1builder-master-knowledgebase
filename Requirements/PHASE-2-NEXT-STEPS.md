# Phase 2: Next Steps to Completion

**Current Status**: 50% Complete (3 of 6 tasks done)  
**Remaining Time**: ~25-30 minutes  
**Blocker**: None - Ready to proceed

---

## 🎯 What Needs to Be Done

You need to complete **2 remaining tasks**:

1. ✅ **Task 4**: Set up OAuth credentials in n8n for WRITE access (~15-20 min)
2. ✅ **Task 5**: Test OAuth authentication for Drive writes (~10 min)

---

## 📋 Quick Start Checklist

### **Before You Begin**:
- [ ] Have access to Google Cloud Console
- [ ] Have access to n8n instance: `https://n8n.srv972609.hstgr.cloud/workflow/B2tNNaSkbLD8gDxw`
- [ ] Have Google account credentials: `dachevivo@gmail.com`
- [ ] Have guide open: `Requirements/Guides/n8n-google-oauth-setup.md`

---

## 🚀 Step-by-Step Instructions

### **STEP 1: Configure OAuth Consent Screen** (5 minutes)

1. Open: https://console.cloud.google.com/apis/credentials/consent?project=builder-master-knowldgebase
2. Select **"External"** user type
3. Click **"CREATE"**
4. Fill in:
   - App name: `OneBuilder RAG System`
   - User support email: `dachevivo@gmail.com`
   - Developer contact: `dachevivo@gmail.com`
5. Click **"SAVE AND CONTINUE"**
6. On "Scopes" page:
   - Click **"ADD OR REMOVE SCOPES"**
   - Add: `https://www.googleapis.com/auth/drive.file`
   - Add: `https://www.googleapis.com/auth/drive`
   - Click **"UPDATE"** → **"SAVE AND CONTINUE"**
7. On "Test users" page:
   - Click **"ADD USERS"**
   - Add: `dachevivo@gmail.com`
   - Click **"SAVE AND CONTINUE"**
8. Click **"BACK TO DASHBOARD"**

✅ **Checkpoint**: OAuth consent screen configured

---

### **STEP 2: Create OAuth Client ID** (5 minutes)

1. Open: https://console.cloud.google.com/apis/credentials?project=builder-master-knowldgebase
2. Click **"CREATE CREDENTIALS"** → **"OAuth client ID"**
3. Application type: **"Web application"**
4. Name: `n8n OAuth Client`
5. **Authorized redirect URIs**:
   - Click **"ADD URI"**
   - Enter: `https://n8n.srv972609.hstgr.cloud/rest/oauth2-credential/callback`
6. Click **"CREATE"**
7. **IMPORTANT**: Copy the **Client ID** and **Client Secret**
   - Save them temporarily (you'll need them in the next step)

✅ **Checkpoint**: OAuth Client ID created, credentials copied

---

### **STEP 3: Configure OAuth in n8n** (10 minutes)

1. Open n8n: `https://n8n.srv972609.hstgr.cloud/workflow/B2tNNaSkbLD8gDxw`
2. Go to **Credentials** (left sidebar)
3. Click **"Add Credential"**
4. Search for: **"Google Drive OAuth2 API"**
5. Fill in:
   - **Credential Name**: `Google Drive - Personal Account (OAuth)`
   - **Client ID**: [Paste from Step 2]
   - **Client Secret**: [Paste from Step 2]
6. Click **"Connect my account"**
7. Sign in with: `dachevivo@gmail.com`
8. Grant permissions (click **"Allow"**)
9. You'll be redirected back to n8n
10. Click **"Save"**

✅ **Checkpoint**: OAuth credentials configured in n8n

---

### **STEP 4: Test OAuth Connection** (5 minutes)

1. In n8n, create a **new workflow** (or use existing test workflow)
2. Add a **"Google Drive"** node
3. Configure the node:
   - **Credential**: Select `Google Drive - Personal Account (OAuth)`
   - **Resource**: `File`
   - **Operation**: `Upload`
   - **File Name**: `oauth-test-file.txt`
   - **Folder ID**: `1U3TvxcGrz2J4T8OIDjjrnY3P12-PL42_`
   - **File Content**: `OAuth test successful - $(new Date().toISOString())`
4. Click **"Execute Node"**
5. Verify:
   - ✅ Node executes successfully (green checkmark)
   - ✅ Response shows file ID
   - ✅ File appears in Google Drive folder

✅ **Checkpoint**: OAuth WRITE access verified

---

### **STEP 5: Verify File in Google Drive** (2 minutes)

1. Open: https://drive.google.com/drive/folders/1U3TvxcGrz2J4T8OIDjjrnY3P12-PL42_
2. Verify you see: `oauth-test-file.txt`
3. Open the file and verify content
4. (Optional) Delete the test file

✅ **Checkpoint**: End-to-end test complete

---

## ✅ Phase 2 Completion Verification

After completing all steps above, verify:

- [x] Google Drive folder exists: `1U3TvxcGrz2J4T8OIDjjrnY3P12-PL42_`
- [x] Service account has READ access (verified in earlier testing)
- [ ] OAuth consent screen configured in Google Cloud
- [ ] OAuth Client ID created
- [ ] OAuth credentials configured in n8n
- [ ] Test file uploaded successfully via OAuth
- [ ] Test file visible in Google Drive
- [x] Requirements document updated

**When all checkboxes are checked, Phase 2 is COMPLETE** ✅

---

## 🎬 After Phase 2 Completion

Once Phase 2 is complete, you can proceed to **Phase 3: n8n Configuration & Testing**:

1. Configure service account credentials in n8n
2. Test connectivity to Gemini API
3. Set up Google Drive push notifications webhook
4. Create test workflows for Workflows B, C, and D

---

## 🆘 Troubleshooting

### **Issue**: "Access blocked: This app's request is invalid"
**Solution**: Make sure you added `dachevivo@gmail.com` to "Test users" in OAuth consent screen (Step 1, item 7)

### **Issue**: "Redirect URI mismatch"
**Solution**: Verify the redirect URI in Google Cloud Console exactly matches:
`https://n8n.srv972609.hstgr.cloud/rest/oauth2-credential/callback`

### **Issue**: n8n OAuth connection fails
**Solution**: 
1. Check that Client ID and Client Secret are correct
2. Verify redirect URI is correct
3. Try clearing browser cache and reconnecting

### **Issue**: File upload fails in n8n
**Solution**:
1. Verify OAuth credential is selected (not service account)
2. Check folder ID is correct: `1U3TvxcGrz2J4T8OIDjjrnY3P12-PL42_`
3. Verify your Google account has access to the folder

---

## 📚 Reference Documents

- **OAuth Setup Guide**: `Requirements/Guides/n8n-google-oauth-setup.md`
- **Phase 2 Status Report**: `Requirements/PHASE-2-STATUS-REPORT.md`
- **Test Script**: `Requirements/Scripts/test-drive-api.py`
- **Requirements Document**: `Requirements/rag-requirements.md`

---

## 📞 Need Help?

If you encounter issues:
1. Check the troubleshooting section above
2. Review the OAuth setup guide: `Requirements/Guides/n8n-google-oauth-setup.md`
3. Verify all prerequisites are met
4. Check Google Cloud Console for any error messages

---

**Estimated Total Time**: 25-30 minutes  
**Difficulty**: Easy (following step-by-step guide)  
**Prerequisites**: All met ✅  
**Blockers**: None ✅

**Ready to proceed? Start with STEP 1 above!** 🚀

