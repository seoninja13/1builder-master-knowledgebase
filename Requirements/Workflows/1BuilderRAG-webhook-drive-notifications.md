# 1BuilderRAG Webhook Workflow Documentation

**Workflow Name**: `1BuilderRAG-webhook-drive-notifications`  
**Workflow ID**: `a5IiavhYT3sOMo4b`  
**Workflow URL**: https://n8n.srv972609.hstgr.cloud/workflow/a5IiavhYT3sOMo4b  
**Webhook Endpoint**: https://n8n.srv972609.hstgr.cloud/webhook/drive-notifications  
**Status**: Created (Inactive - needs activation)  
**Created**: 2025-11-17

---

## 📋 Overview

This workflow receives Google Drive push notifications when files are uploaded, modified, or deleted in the monitored folder. It processes the notifications, retrieves file details, filters for relevant changes, and notifies Kestra to trigger the ingestion pipeline.

---

## 🔄 Workflow Architecture

```
Google Drive Push Notification
          ↓
Extract Notification Data
          ↓
Get Drive Changes (API Call)
          ↓
Filter Folder Changes
          ↓
Notify Kestra
```

---

## 🔧 Node Configuration

### **Node 1: Google Drive Push Notification** (Webhook Trigger)
- **Type**: `n8n-nodes-base.webhook`
- **Path**: `/drive-notifications`
- **HTTP Method**: POST
- **Response Mode**: On Received (immediate response)
- **Purpose**: Receives push notifications from Google Drive API

**Webhook URL**:
- **Test**: https://n8n.srv972609.hstgr.cloud/webhook-test/drive-notifications
- **Production**: https://n8n.srv972609.hstgr.cloud/webhook/drive-notifications

**Expected Headers from Google Drive**:
- `x-goog-channel-id`: Unique channel identifier
- `x-goog-resource-id`: Resource being watched
- `x-goog-resource-state`: State of the resource (sync, add, remove, update, trash, untrash, change)
- `x-goog-changed`: What changed (content, parents, children, permissions)

---

### **Node 2: Extract Notification Data** (Set)
- **Type**: `n8n-nodes-base.set`
- **Purpose**: Extracts relevant headers from the webhook notification

**Extracted Fields**:
- `channelId`: From `x-goog-channel-id` header
- `resourceId`: From `x-goog-resource-id` header
- `resourceState`: From `x-goog-resource-state` header
- `changed`: From `x-goog-changed` header

---

### **Node 3: Get Drive Changes** (HTTP Request)
- **Type**: `n8n-nodes-base.httpRequest`
- **Method**: GET
- **URL**: https://www.googleapis.com/drive/v3/changes
- **Authentication**: Google API (predefined credential type)
- **Purpose**: Retrieves actual file details from Google Drive Changes API

**Query Parameters**:
- `pageToken`: 1 (starting point)
- `fields`: `changes(file(id,name,mimeType,modifiedTime,parents))`

**Note**: This node requires Google API credentials to be configured in n8n.

---

### **Node 4: Filter Folder Changes** (Filter)
- **Type**: `n8n-nodes-base.filter`
- **Purpose**: Filters changes to only include files in the monitored folder

**Filter Condition**:
- `file.parents[0]` equals `1U3TvxcGrz2J4T8OIDjjrnY3P12-PL42_`

**Result**: Only files in the "OneBuilder Master Knowledge" folder pass through.

---

### **Node 5: Notify Kestra** (HTTP Request)
- **Type**: `n8n-nodes-base.httpRequest`
- **Method**: POST
- **URL**: http://kestra:8080/api/v1/executions/webhook/1builderrag/workflow-a-master-sync
- **Purpose**: Notifies Kestra to trigger Workflow A (Master Sync)

**Body Parameters**:
- `fileId`: File ID from Google Drive
- `fileName`: File name
- `mimeType`: File MIME type
- `modifiedTime`: Last modification timestamp
- `source`: "drive-push-notification"

---

## 🚀 Activation Instructions

### **Step 1: Configure Google Service Account Credentials**

**Option A: Use Existing OAuth Credential (Recommended)**
1. Open workflow: https://n8n.srv972609.hstgr.cloud/workflow/a5IiavhYT3sOMo4b
2. Click on "Get Drive Changes" node
3. Change **Authentication** to: "Predefined Credential Type"
4. Select **Credential Type**: "Google Drive OAuth2 API"
5. Select existing credential: "Google Drive - 1builderMasterKnowledge"
6. Save workflow

**Option B: Create Service Account Credential (Alternative)**
1. Open n8n: https://n8n.srv972609.hstgr.cloud
2. Navigate to **Credentials** → **Add Credential**
3. Search for and select **"Google Service Account"**
4. Upload service account key: `Requirements/Credentials/builder-master-knowldgebase-79a4f60f66e1.json`
5. Save credential as: "Google Drive - 1BuilderRAG Service Account"

### **Step 2: Verify Workflow Configuration**

1. Open workflow: https://n8n.srv972609.hstgr.cloud/workflow/a5IiavhYT3sOMo4b
2. Click on "Get Drive Changes" node
3. Verify credential is selected (either OAuth or Service Account from Step 1)
4. Save workflow if any changes were made

### **Step 3: Activate Workflow**

1. Click the **Activate** toggle in the top-right corner
2. Verify status changes to **Active** ✅

### **Step 4: Register Webhook with Google Drive**

Run the registration script:
```bash
cd Requirements/Scripts
python register-drive-webhook.py
```

This will:
- Register the webhook endpoint with Google Drive API
- Create a push notification channel
- Save channel info to `Requirements/Credentials/drive-webhook-channel.json`

---

## 🧪 Testing

### **Test 1: Manual Webhook Trigger**

Test the webhook endpoint directly:
```bash
curl -X POST https://n8n.srv972609.hstgr.cloud/webhook/drive-notifications \
  -H "Content-Type: application/json" \
  -H "x-goog-channel-id: test-channel" \
  -H "x-goog-resource-id: test-resource" \
  -H "x-goog-resource-state: update" \
  -H "x-goog-changed: content" \
  -d '{}'
```

**Expected Result**: Workflow executes, check execution history in n8n.

### **Test 2: Upload File to Google Drive**

1. Upload a test file to: https://drive.google.com/drive/folders/1U3TvxcGrz2J4T8OIDjjrnY3P12-PL42_
2. Wait 30 seconds
3. Check n8n execution history: https://n8n.srv972609.hstgr.cloud/executions
4. Verify workflow executed successfully

---

## 🔍 Monitoring

### **Check Workflow Executions**

1. Open n8n: https://n8n.srv972609.hstgr.cloud
2. Navigate to **Executions** tab
3. Filter by workflow: "1BuilderRAG-webhook-drive-notifications"
4. Review execution logs for errors

### **Check Channel Status**

View current channel registration:
```bash
cat Requirements/Credentials/drive-webhook-channel.json
```

Check expiration date and renew if needed:
```bash
python Requirements/Scripts/renew-drive-webhook.py
```

---

## ⚠️ Troubleshooting

### **Webhook Not Triggering**

1. **Check channel expiration**:
   ```bash
   cat Requirements/Credentials/drive-webhook-channel.json
   ```
   If expired, re-register:
   ```bash
   python Requirements/Scripts/register-drive-webhook.py
   ```

2. **Verify workflow is active**: Check toggle in n8n UI

3. **Test webhook endpoint**:
   ```bash
   curl -I https://n8n.srv972609.hstgr.cloud/webhook/drive-notifications
   ```
   Should return 200 OK

### **"Get Drive Changes" Node Fails**

1. **Check Google API credentials**: Verify service account key is valid
2. **Check API quota**: Visit Google Cloud Console → APIs & Services → Quotas
3. **Verify service account permissions**: Service account must have READ access to Drive folder

### **Kestra Not Receiving Notifications**

1. **Check Kestra URL**: Verify `http://kestra:8080` is accessible from n8n
2. **Check Kestra webhook endpoint**: Verify `/api/v1/executions/webhook/1builderrag/workflow-a-master-sync` exists
3. **Review Kestra logs**: Check for incoming webhook requests

---

## 📚 Related Documentation

- **Test Plan**: `Requirements/Testing/end-to-end-test-plan.md`
- **Registration Script**: `Requirements/Scripts/register-drive-webhook.py`
- **Renewal Script**: `Requirements/Scripts/renew-drive-webhook.py`
- **Project Rules**: `PROJECT-RULES.md`

