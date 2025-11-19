# Google Drive Webhook Automation - Complete System

## 🎯 **FULLY AUTOMATED SYSTEM - NO MANUAL INTERVENTION REQUIRED**

This document explains how the Google Drive push notification system works automatically.

---

## 📊 **ARCHITECTURE OVERVIEW**

### **The Complete Flow**

```
User uploads file to Google Drive
    ↓
Google detects change
    ↓
Google sends POST to: https://n8n.srv972609.hstgr.cloud/webhook/drive-notifications
    Headers: x-goog-resource-state: update
    ↓
n8n Workflow "1BuilderRAG-webhook-drive-notifications" executes:
    1. Extract notification headers
    2. Initialize pageToken (sets to 15983288 if not already set)
    3. Get Drive Changes using DYNAMIC pageToken (stored in workflow static data)
    4. Update pageToken automatically for next execution
    5. Filter for folder: 1U3TvxcGrz2J4T8OIDjjrnY3P12-PL42_
    6. Notify Kestra
    ↓
Done! File processed automatically
```

---

## 🔧 **HOW PAGETOKENS WORK (AUTOMATIC)**

### **What is a pageToken?**
A pageToken is a cursor that tracks "which changes have I already processed?"

### **How it updates automatically:**

```javascript
// In "Initialize Page Token" node (Code node):
// CRITICAL: Check if staticData exists first!
if (!$workflow.staticData) {
  $workflow.staticData = {};
}
if (!$workflow.staticData.pageToken) {
  $workflow.staticData.pageToken = '15983288';
}
// Ensures pageToken is always set before API call

// In "Get Drive Changes" node:
pageToken: "={{ $workflow.staticData.pageToken }}"
// Uses the initialized token from static data

// In "Update Page Token" node (Code node):
const newPageToken = $input.item.json.newStartPageToken;
if (newPageToken) {
  $workflow.staticData.pageToken = newPageToken;
  console.log('Updated pageToken to:', newPageToken);
}
// Automatically saves new token for next execution
```

### **Example Timeline:**

| Time | Event | PageToken Used | New PageToken Saved |
|------|-------|----------------|---------------------|
| 10:00 AM | First file uploaded | 15983288 | 15983300 |
| 10:05 AM | Second file uploaded | 15983300 | 15983315 |
| 10:10 AM | Third file uploaded | 15983315 | 15983328 |

**Result**: No duplicates, no missed files, fully automatic!

---

## 🔄 **WEBHOOK RENEWAL (EVERY 7 DAYS)**

### **Current Status: MANUAL (Needs Automation)**

Google Drive webhooks expire after 7 days. Currently, you must manually run the registration workflow.

### **To Automate Webhook Renewal:**

Create a scheduled workflow that runs every 6 days:

1. **Create new workflow**: `1BuilderRAG-auto-renew-webhook`
2. **Add Schedule Trigger**: Every 6 days
3. **Add HTTP Request nodes**:
   - Get fresh pageToken
   - Register new webhook
4. **Activate the workflow**

**This will ensure the webhook never expires.**

---

## ✅ **WHAT'S ALREADY AUTOMATED**

1. ✅ **PageToken updates** - Automatically updates after each execution
2. ✅ **File change detection** - Google automatically sends notifications
3. ✅ **Duplicate prevention** - PageToken ensures each change is processed once
4. ✅ **Folder filtering** - Only processes files in the target folder
5. ✅ **Kestra notification** - Automatically triggers downstream processing

---

## ⚠️ **WHAT NEEDS MANUAL SETUP (ONE-TIME)**

1. ❌ **Webhook renewal** - Currently manual every 7 days (can be automated)
2. ✅ **OAuth credentials** - Already configured in n8n
3. ✅ **Workflow configuration** - Already set up and active

---

## 🚀 **TESTING THE SYSTEM**

### **Test Steps:**

1. **Upload a file** to Google Drive folder: `1U3TvxcGrz2J4T8OIDjjrnY3P12-PL42_`
2. **Wait 1-2 minutes** for Google to send notification
3. **Check n8n executions**: https://n8n.srv972609.hstgr.cloud/workflow/a5IiavhYT3sOMo4b/executions
4. **You should see**:
   - New execution with `x-goog-resource-state: update`
   - File details in the execution data
   - PageToken automatically updated

### **What You'll See:**

```json
{
  "headers": {
    "x-goog-resource-state": "update",
    "x-goog-channel-id": "1builderrag-oauth-20251117-161234"
  },
  "changes": [
    {
      "file": {
        "id": "abc123",
        "name": "my-test-file.md",
        "mimeType": "text/markdown",
        "modifiedTime": "2025-11-18T02:15:00Z",
        "parents": ["1U3TvxcGrz2J4T8OIDjjrnY3P12-PL42_"]
      }
    }
  ],
  "newStartPageToken": "15983350"
}
```

---

## 🔍 **TROUBLESHOOTING**

### **No execution appears after uploading file:**

1. **Check webhook expiration**: Has it been more than 7 days since registration?
   - Solution: Run `1BuilderRAG-register-webhook-oauth` workflow
2. **Check workflow is active**: Is the main workflow enabled?
   - Solution: Activate `1BuilderRAG-webhook-drive-notifications`
3. **Check file location**: Is the file in the correct folder?
   - Folder ID: `1U3TvxcGrz2J4T8OIDjjrnY3P12-PL42_`

### **Duplicate executions:**

This should NOT happen with the new dynamic pageToken system. If it does:
1. Check that "Update Page Token" node is connected
2. Check workflow static data has pageToken stored

---

## 📝 **SUMMARY**

**What's Automatic:**
- ✅ File change detection
- ✅ PageToken updates
- ✅ Duplicate prevention
- ✅ Folder filtering
- ✅ Downstream processing

**What Needs Attention:**
- ⚠️ Webhook renewal every 7 days (can be automated with scheduled workflow)

**Current Webhook Expiration:**
- Check `Requirements/Credentials/drive-webhook-channel.json` for expiration date

---

## 🎯 **NEXT STEPS**

1. **Test the system** by uploading a file
2. **Verify execution** appears in n8n
3. **Create auto-renewal workflow** (optional but recommended)
4. **Set calendar reminder** for webhook renewal if not automated

---

**System Status**: ✅ READY FOR TESTING

