# Google Drive Webhook Troubleshooting Report

**Date**: 2025-11-17  
**Issue**: Google Drive push notifications not triggering n8n workflow  
**Status**: ⚠️ IDENTIFIED - Multiple Issues Found

---

## 🔍 Investigation Summary

### ✅ What's Working:
1. **n8n Webhook Endpoint**: Accessible and responding correctly
2. **Workflow Configuration**: Properly configured and active
3. **Manual Webhook Test**: Successfully triggered workflow (execution #8707)
4. **Credentials**: OAuth credential properly configured

### ❌ What's NOT Working:
1. **Google Drive Push Notifications**: Not being sent to webhook
2. **Webhook Registration**: Multiple critical issues identified

---

## 🚨 ROOT CAUSES IDENTIFIED

### **Issue #1: CRITICAL - Domain Verification Required**

**Problem**: Google Drive push notifications require domain verification.

**Evidence**:
- Your webhook URL: `https://n8n.srv972609.hstgr.cloud/webhook/drive-notifications`
- Domain: `n8n.srv972609.hstgr.cloud`
- **This domain must be verified in Google Search Console**

**Why This Matters**:
Google Drive API will ONLY send push notifications to verified domains. Without verification, the webhook registration succeeds but notifications are silently dropped.

**Solution**:
You must verify ownership of `n8n.srv972609.hstgr.cloud` in Google Search Console:
1. Go to: https://search.google.com/search-console
2. Add property: `n8n.srv972609.hstgr.cloud`
3. Verify ownership (DNS TXT record or HTML file)
4. Re-register the webhook after verification

**Reference**: https://developers.google.com/drive/api/guides/push#verify-domain

---

### **Issue #2: CRITICAL - Invalid pageToken in Workflow**

**Problem**: The "Get Drive Changes" node uses `pageToken=1`, which is invalid.

**Evidence from Execution #8707**:
```json
{
  "changes": []
}
```

**Why This Matters**:
- The Google Drive Changes API requires a valid `pageToken`
- `pageToken=1` is not a valid token - it should be obtained from `changes.getStartPageToken`
- Even if Google sends a push notification, the workflow can't retrieve the actual changes

**Current Workflow Configuration**:
<augment_code_snippet path="Requirements/Workflows/1BuilderRAG-webhook-drive-notifications.md" mode="EXCERPT">
````markdown
{
  "name": "pageToken",
  "value": "1"
}
````
</augment_code_snippet>

**Solution**:
Replace hardcoded `pageToken=1` with a dynamic token:
1. Store the pageToken in workflow static data
2. Get initial token from `changes.getStartPageToken` API
3. Update token after each successful changes retrieval

---

### **Issue #3: Service Account Permissions**

**Problem**: Service account may not have permission to watch the folder.

**Your Service Account**:
- Email: `id-builder-masterknowldge@builder-master-knowldgebase.iam.gserviceaccount.com`
- Registered webhook for folder: `1U3TvxcGrz2J4T8OIDjjrnY3P12-PL42_`

**Required Permissions**:
- Service account must have **Viewer** or **Editor** access to the folder
- Folder owner: `dachevivo@gmail.com`

**Verification**:
Check if service account has access:
1. Open folder: https://drive.google.com/drive/folders/1U3TvxcGrz2J4T8OIDjjrnY3P12-PL42_
2. Right-click → Share
3. Check if `id-builder-masterknowldge@builder-master-knowldgebase.iam.gserviceaccount.com` is listed
4. If not, add it with **Viewer** access

---

### **Issue #4: Webhook Registration Scope**

**Problem**: You registered a webhook to watch a specific folder, but Google Drive push notifications work differently.

**How Google Drive Push Notifications Work**:
1. You can only watch the **entire Drive** (all files), not individual folders
2. The `fileId` parameter in `files().watch()` should be the **Drive ID**, not a folder ID
3. To watch "My Drive", use: `fileId='root'` or the actual Drive ID
4. You then filter changes in your webhook handler (which you're already doing)

**Your Current Registration**:
```python
response = service.files().watch(
    fileId=FOLDER_ID,  # ❌ This is wrong - should be Drive ID or 'root'
    body=body
).execute()
```

**Correct Registration**:
```python
response = service.files().watch(
    fileId='root',  # ✅ Watch entire "My Drive"
    body=body
).execute()
```

---

## 🔧 SOLUTIONS

### **Solution 1: Verify Domain (CRITICAL - Must Do First)**

**Steps**:
1. Go to Google Search Console: https://search.google.com/search-console
2. Click "Add Property"
3. Enter: `n8n.srv972609.hstgr.cloud`
4. Choose verification method:
   - **DNS TXT Record** (recommended if you control DNS)
   - **HTML File Upload** (if you have access to n8n server)
5. Complete verification
6. Wait 24-48 hours for verification to propagate

**DNS TXT Record Method**:
- Add TXT record to `srv972609.hstgr.cloud` domain
- Name: `n8n.srv972609.hstgr.cloud`
- Value: (provided by Google Search Console)

**Alternative**: If you don't control the domain, you may need to:
- Use a custom domain you own
- Or use Google Cloud Run/App Engine with automatic domain verification

---

### **Solution 2: Fix pageToken in Workflow**

I'll create an updated workflow configuration that properly handles pageToken.

---

### **Solution 3: Update Webhook Registration Script**

I'll create an updated registration script that:
1. Watches the entire Drive (not just a folder)
2. Gets a valid starting pageToken
3. Stores the token for the workflow to use

---

### **Solution 4: Verify Service Account Access**

**Quick Check**:
```powershell
cd Requirements\Scripts
python -c "from google.oauth2 import service_account; from googleapiclient.discovery import build; creds = service_account.Credentials.from_service_account_file('..\\Credentials\\builder-master-knowldgebase-79a4f60f66e1.json', scopes=['https://www.googleapis.com/auth/drive.readonly']); service = build('drive', 'v3', credentials=creds); result = service.files().get(fileId='1U3TvxcGrz2J4T8OIDjjrnY3P12-PL42_', fields='id,name,owners').execute(); print(result)"
```

If this fails, the service account doesn't have access to the folder.

---

## 📋 ACTION PLAN

### **Immediate Actions (Required)**:

1. **[ ] Verify Domain in Google Search Console** (CRITICAL)
   - This is the #1 blocker
   - Without this, Google will never send notifications
   - Estimated time: 30 min setup + 24-48 hours propagation

2. **[ ] Update Webhook Registration Script**
   - Watch entire Drive instead of folder
   - Get valid starting pageToken
   - Store token for workflow

3. **[ ] Update n8n Workflow**
   - Use dynamic pageToken from static data
   - Update token after each successful retrieval

4. **[ ] Verify Service Account Access**
   - Ensure service account can read the folder
   - Add to folder sharing if needed

### **Testing After Fixes**:

1. **[ ] Re-register webhook** with updated script
2. **[ ] Upload test file** to Google Drive
3. **[ ] Wait 1-2 minutes** for notification
4. **[ ] Check n8n execution history**
5. **[ ] Verify changes were retrieved**

---

## 🎯 Expected Timeline

- **Domain Verification**: 24-48 hours (Google's processing time)
- **Script Updates**: 30 minutes
- **Workflow Updates**: 15 minutes
- **Testing**: 10 minutes

**Total**: ~1 hour of work + 24-48 hours waiting for domain verification

---

## 📚 References

- [Google Drive Push Notifications](https://developers.google.com/drive/api/guides/push)
- [Domain Verification](https://developers.google.com/drive/api/guides/push#verify-domain)
- [Changes API](https://developers.google.com/drive/api/reference/rest/v3/changes)
- [Watch Files](https://developers.google.com/drive/api/reference/rest/v3/files/watch)

---

**Next Steps**: I'll create the updated scripts and workflow configuration for you.

