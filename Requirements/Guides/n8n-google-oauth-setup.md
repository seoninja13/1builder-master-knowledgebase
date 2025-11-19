# n8n Google OAuth Setup Guide

## Purpose
Configure n8n to use YOUR Google account OAuth credentials for WRITE operations to Google Drive (specifically for Workflow D: Content Acquisition Pipeline).

---

## Prerequisites
- n8n instance running and accessible
- Google Cloud project: `builder-master-knowldgebase`
- Your Google account: `dachevivo@gmail.com`

---

## Step 1: Enable OAuth in Google Cloud Console

### 1.1 Configure OAuth Consent Screen
1. Go to: https://console.cloud.google.com/apis/credentials/consent?project=builder-master-knowldgebase
2. Select **"External"** user type (for personal accounts)
3. Click **"CREATE"**
4. Fill in required fields:
   - **App name**: OneBuilder RAG System
   - **User support email**: dachevivo@gmail.com
   - **Developer contact**: dachevivo@gmail.com
5. Click **"SAVE AND CONTINUE"**
6. On "Scopes" page, click **"ADD OR REMOVE SCOPES"**
7. Add these scopes:
   - `https://www.googleapis.com/auth/drive.file` (Create and manage Drive files)
   - `https://www.googleapis.com/auth/drive` (Full Drive access)
8. Click **"UPDATE"** → **"SAVE AND CONTINUE"**
9. On "Test users" page, click **"ADD USERS"**
10. Add: `dachevivo@gmail.com`
11. Click **"SAVE AND CONTINUE"** → **"BACK TO DASHBOARD"**

### 1.2 Create OAuth Client ID
1. Go to: https://console.cloud.google.com/apis/credentials?project=builder-master-knowldgebase
2. Click **"CREATE CREDENTIALS"** → **"OAuth client ID"**
3. Application type: **"Web application"**
4. Name: `n8n OAuth Client`
5. **Authorized redirect URIs**: Add your n8n OAuth callback URL
   - Format: `https://your-n8n-instance.com/rest/oauth2-credential/callback`
   - Example: `http://localhost:5678/rest/oauth2-credential/callback` (for local n8n)
6. Click **"CREATE"**
7. **IMPORTANT**: Copy the **Client ID** and **Client Secret** (you'll need these in n8n)

---

## Step 2: Configure OAuth Credentials in n8n

### 2.1 Add Google Drive OAuth2 Credential
1. Open n8n UI
2. Go to **Credentials** (left sidebar)
3. Click **"Add Credential"**
4. Search for and select **"Google Drive OAuth2 API"**
5. Fill in the fields:
   - **Credential Name**: `Google Drive - Personal Account (OAuth)`
   - **Client ID**: [Paste from Step 1.2]
   - **Client Secret**: [Paste from Step 1.2]
6. Click **"Connect my account"**
7. You'll be redirected to Google OAuth consent screen
8. Sign in with `dachevivo@gmail.com`
9. Grant permissions to access Google Drive
10. You'll be redirected back to n8n
11. Click **"Save"**

### 2.2 Verify Credential Works
1. Create a test workflow in n8n
2. Add a **"Google Drive"** node
3. Select the credential you just created
4. Action: **"List"** (list files in a folder)
5. Folder ID: `1U3TvxcGrz2J4T8OIDjjrnY3P12-PL42_` (OneBuilder Master Knowledge)
6. Execute the node
7. Verify it lists files successfully

---

## Step 3: Authentication Strategy Summary

### Credential Usage by Workflow

| Workflow | Operation | Credential Type | Credential Name |
|----------|-----------|----------------|-----------------|
| **Workflow A** (Master Sync) | Read Drive files | Service Account | `builder-master-knowldgebase-79a4f60f66e1.json` |
| **Workflow B** (Smart Ingestion) | Read Drive files | Service Account | `builder-master-knowldgebase-79a4f60f66e1.json` |
| **Workflow B** (Smart Ingestion) | Upload to Gemini | Service Account | `builder-master-knowldgebase-79a4f60f66e1.json` |
| **Workflow C** (Query Engine) | Query Gemini | Service Account | `builder-master-knowldgebase-79a4f60f66e1.json` |
| **Workflow D** (Content Acquisition) | Write to Drive | OAuth (Your Account) | `Google Drive - Personal Account (OAuth)` |

### Why This Hybrid Approach?
- ✅ Service account for READ operations (no quota issues)
- ✅ Your OAuth for WRITE operations (uses your storage quota)
- ✅ Maintains security (service account can't write, only read)
- ✅ Works with personal Google accounts (no Workspace needed)

---

## Troubleshooting

### Issue: "Access blocked: This app's request is invalid"
**Solution**: Make sure you added your email to "Test users" in OAuth consent screen (Step 1.1)

### Issue: "Redirect URI mismatch"
**Solution**: Verify the redirect URI in Google Cloud Console matches your n8n instance URL exactly

### Issue: OAuth token expired
**Solution**: n8n automatically refreshes tokens. If it fails, re-authenticate by editing the credential and clicking "Connect my account" again

---

## Security Notes
- OAuth tokens are stored securely in n8n's credential storage
- Tokens are automatically refreshed before expiration
- You can revoke access anytime at: https://myaccount.google.com/permissions
- Service account credentials remain separate and unaffected

