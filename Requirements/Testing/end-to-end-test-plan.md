# 1BuilderRAG End-to-End Test Plan

**Project**: 1BuilderRAG (OneBuilder Master Knowledge RAG System)  
**Test Scope**: Google Drive → n8n Webhook → Kestra → Workflow B → Gemini File Search  
**Last Updated**: 2025-11-17

---

## 🎯 Test Objectives

1. Verify Google Drive push notifications trigger n8n webhook
2. Verify n8n processes file change notifications correctly
3. Verify Kestra receives and orchestrates ingestion workflow
4. Verify Workflow B (Smart Ingestion) processes files correctly
5. Verify files are indexed in Gemini File Search
6. Verify end-to-end latency is acceptable (<5 minutes)

---

## 📋 Prerequisites

### **Before Starting Tests:**

- [ ] n8n webhook workflow created and active (`1BuilderRAG-webhook-drive-notifications`)
- [ ] Google Drive push notification channel registered (run `register-drive-webhook.py`)
- [ ] Service account has READ access to Google Drive folder
- [ ] OAuth credentials configured in n8n (for Workflow D if needed)
- [ ] Kestra instance accessible and configured
- [ ] Gemini API credentials configured

### **Required Access:**

- [ ] Google Drive folder: https://drive.google.com/drive/folders/1U3TvxcGrz2J4T8OIDjjrnY3P12-PL42_
- [ ] n8n instance: https://n8n.srv972609.hstgr.cloud
- [ ] Kestra instance: [URL TBD]
- [ ] Google Cloud Console: https://console.cloud.google.com/

---

## 🧪 Test Suite

### **Test 1: Webhook Registration**

**Objective**: Verify Google Drive push notification channel is registered correctly

**Steps:**
1. Run webhook registration script:
   ```bash
   cd Requirements/Scripts
   python register-drive-webhook.py
   ```

2. Verify output shows:
   - ✅ Service account loaded successfully
   - ✅ Channel ID generated
   - ✅ Webhook registered successfully
   - ✅ Channel info saved to `drive-webhook-channel.json`

3. Check channel expiration date (should be ~7 days from now)

**Expected Results:**
- Script completes without errors
- Channel info file created: `Requirements/Credentials/drive-webhook-channel.json`
- Channel expiration is 7 days in the future

**Verification:**
```bash
cat Requirements/Credentials/drive-webhook-channel.json
```

**Troubleshooting:**
- If "403 Forbidden": Service account lacks permissions
- If "404 Not Found": Folder ID is incorrect
- If "Invalid webhook URL": n8n webhook endpoint not accessible

---

### **Test 2: n8n Webhook Workflow**

**Objective**: Verify n8n webhook workflow receives and processes notifications

**Steps:**
1. Open n8n workflow: https://n8n.srv972609.hstgr.cloud/workflow/[WORKFLOW_ID]
2. Verify workflow is **ACTIVE** (toggle in top-right corner)
3. Check webhook URL matches: `https://n8n.srv972609.hstgr.cloud/webhook/drive-notifications`
4. Review workflow nodes:
   - Webhook Trigger node
   - Google Drive Changes API call node
   - Filter/Transform nodes
   - Kestra notification node

**Expected Results:**
- Workflow status: ACTIVE ✅
- Webhook URL configured correctly
- All nodes properly connected

**Verification:**
- Click "Test workflow" button
- Manually trigger webhook with test payload
- Check execution history for successful test run

**Troubleshooting:**
- If webhook not accessible: Check n8n instance firewall/network settings
- If workflow inactive: Activate workflow in n8n UI
- If nodes missing: Create workflow from scratch (see workflow configuration section)

---

### **Test 3: Manual File Upload (Simple Text File)**

**Objective**: Verify end-to-end flow with a simple text file

**Test File:**
- **Name**: `test-rag-ingestion-2025-11-17.txt`
- **Content**:
  ```
  This is a test document for the 1BuilderRAG system.
  
  Vertical: SEO
  Horizontal: Strategy
  Geo: Sacramento
  Intent: Test Document
  
  This document tests the automatic ingestion pipeline from Google Drive to Gemini File Search.
  ```

**Steps:**
1. Upload test file to Google Drive folder:
   - URL: https://drive.google.com/drive/folders/1U3TvxcGrz2J4T8OIDjjrnY3P12-PL42_
   - Method: Drag and drop or "New" → "File upload"

2. **Immediate Verification (within 30 seconds):**
   - Check n8n execution history: https://n8n.srv972609.hstgr.cloud/executions
   - Look for new execution of `1BuilderRAG-webhook-drive-notifications`
   - Verify execution status: SUCCESS ✅

3. **Kestra Verification (within 1 minute):**
   - Check Kestra logs for ingestion request
   - Verify Kestra triggered Workflow B (Smart Ingestion)

4. **Workflow B Verification (within 2-3 minutes):**
   - Check n8n execution history for `1BuilderRAG-smart-ingestion`
   - Verify file downloaded from Drive
   - Verify metadata extraction completed
   - Verify upload to Gemini File Search succeeded

5. **Gemini Verification (within 5 minutes):**
   - Query Gemini File Search: "What test documents do we have?"
   - Expected response should mention the test file

**Expected Results:**
- ✅ n8n webhook triggered within 30 seconds
- ✅ Kestra received notification within 1 minute
- ✅ Workflow B completed within 3 minutes
- ✅ File searchable in Gemini within 5 minutes

**Verification Commands:**
```bash
# Check n8n executions
curl -X GET https://n8n.srv972609.hstgr.cloud/api/v1/executions \
  -H "X-N8N-API-KEY: [YOUR_API_KEY]"

# Check Kestra logs
# [Kestra CLI command TBD]
```

**Troubleshooting:**
- **Webhook not triggered**: Check channel expiration, re-register if needed
- **Kestra not notified**: Check n8n → Kestra connection
- **Workflow B fails**: Check service account permissions, Gemini API credentials
- **File not searchable**: Check Gemini indexing status, may take up to 10 minutes

---

### **Test 4: PDF File Upload**

**Objective**: Verify PDF file processing

**Test File:**
- **Name**: `test-seo-strategy-sacramento.pdf`
- **Content**: Any PDF document (can be a sample SEO strategy document)

**Steps:**
1. Upload PDF to Google Drive folder
2. Follow same verification steps as Test 3
3. Verify PDF content is extracted and indexed

**Expected Results:**
- ✅ PDF processed successfully
- ✅ Text extracted from PDF
- ✅ Content searchable in Gemini

**Troubleshooting:**
- If PDF extraction fails: Check Gemini API supports PDF format
- If content not searchable: Verify PDF is not image-based (scanned document)

---

### **Test 5: Multiple File Upload (Batch)**

**Objective**: Verify system handles multiple simultaneous uploads

**Test Files:**
- `test-file-1.txt`
- `test-file-2.txt`
- `test-file-3.txt`

**Steps:**
1. Upload all 3 files simultaneously to Google Drive
2. Verify n8n receives 3 separate webhook notifications
3. Verify Kestra processes all 3 files
4. Verify all 3 files indexed in Gemini

**Expected Results:**
- ✅ All 3 files trigger separate webhook notifications
- ✅ All 3 files processed by Workflow B
- ✅ All 3 files searchable in Gemini

**Troubleshooting:**
- If some files missed: Check webhook notification delivery
- If processing fails: Check rate limits on Gemini API

---

### **Test 6: File Update (Modification)**

**Objective**: Verify system detects and processes file updates

**Steps:**
1. Upload initial file: `test-update.txt` with content "Version 1"
2. Wait for ingestion to complete
3. Update file content to "Version 2" (edit in Google Drive)
4. Verify webhook triggered for update
5. Verify Gemini index updated with new content

**Expected Results:**
- ✅ Update detected by webhook
- ✅ File re-processed by Workflow B
- ✅ Gemini index reflects updated content

**Troubleshooting:**
- If update not detected: Check Google Drive Changes API response
- If old content still returned: Check Gemini index update latency

---

### **Test 7: File Deletion**

**Objective**: Verify system handles file deletions

**Steps:**
1. Upload test file: `test-delete.txt`
2. Wait for ingestion to complete
3. Delete file from Google Drive
4. Verify webhook triggered for deletion
5. Verify file removed from Gemini index

**Expected Results:**
- ✅ Deletion detected by webhook
- ✅ Kestra triggers cleanup workflow
- ✅ File no longer searchable in Gemini

**Troubleshooting:**
- If deletion not detected: Check webhook notification includes deletion events
- If file still searchable: Manually remove from Gemini index

---

### **Test 8: Channel Expiration and Renewal**

**Objective**: Verify webhook channel renewal process

**Steps:**
1. Check current channel expiration:
   ```bash
   cat Requirements/Credentials/drive-webhook-channel.json
   ```

2. Run renewal script:
   ```bash
   python Requirements/Scripts/renew-drive-webhook.py
   ```

3. Verify new channel registered
4. Upload test file to verify new channel works

**Expected Results:**
- ✅ Old channel stopped successfully
- ✅ New channel registered with new expiration date
- ✅ Webhook continues to receive notifications

**Troubleshooting:**
- If renewal fails: Manually run `register-drive-webhook.py`
- If notifications stop: Check channel expiration, re-register immediately

---

### **Test 9: Error Handling - Invalid File**

**Objective**: Verify system handles unsupported file types gracefully

**Test File:**
- **Name**: `test-invalid.xyz` (unsupported format)

**Steps:**
1. Upload invalid file to Google Drive
2. Verify webhook triggered
3. Verify Workflow B handles error gracefully
4. Verify error logged in Kestra

**Expected Results:**
- ✅ Webhook triggered
- ✅ Workflow B detects unsupported format
- ✅ Error logged, no system crash
- ✅ Other files continue to process normally

**Troubleshooting:**
- If system crashes: Add error handling to Workflow B
- If error not logged: Improve error reporting in Kestra

---

### **Test 10: End-to-End Latency Measurement**

**Objective**: Measure total time from upload to searchable

**Steps:**
1. Note timestamp: Upload file to Google Drive
2. Note timestamp: n8n webhook triggered
3. Note timestamp: Kestra notification received
4. Note timestamp: Workflow B started
5. Note timestamp: Workflow B completed
6. Note timestamp: File searchable in Gemini

**Expected Results:**
- Upload → Webhook: <30 seconds
- Webhook → Kestra: <10 seconds
- Kestra → Workflow B: <10 seconds
- Workflow B execution: <2 minutes
- Gemini indexing: <3 minutes
- **Total: <5 minutes**

**Troubleshooting:**
- If latency >5 minutes: Identify bottleneck (webhook, Kestra, Workflow B, or Gemini)
- If webhook delay: Check Google Drive notification delivery
- If Workflow B slow: Optimize file processing logic

---

## 📊 Test Results Template

| Test # | Test Name | Status | Duration | Notes |
|--------|-----------|--------|----------|-------|
| 1 | Webhook Registration | ⏳ | - | - |
| 2 | n8n Webhook Workflow | ⏳ | - | - |
| 3 | Manual File Upload (Text) | ⏳ | - | - |
| 4 | PDF File Upload | ⏳ | - | - |
| 5 | Multiple File Upload | ⏳ | - | - |
| 6 | File Update | ⏳ | - | - |
| 7 | File Deletion | ⏳ | - | - |
| 8 | Channel Renewal | ⏳ | - | - |
| 9 | Error Handling | ⏳ | - | - |
| 10 | Latency Measurement | ⏳ | - | - |

**Legend:**
- ⏳ Not Started
- 🔄 In Progress
- ✅ Passed
- ❌ Failed
- ⚠️ Partial Pass

---

## 🔧 Common Troubleshooting Steps

### **Webhook Not Triggering:**
1. Check channel expiration: `cat Requirements/Credentials/drive-webhook-channel.json`
2. Re-register channel: `python Requirements/Scripts/register-drive-webhook.py`
3. Verify n8n webhook URL is accessible: `curl https://n8n.srv972609.hstgr.cloud/webhook/drive-notifications`
4. Check Google Cloud Console for API errors

### **n8n Workflow Errors:**
1. Check n8n execution history for error details
2. Verify service account credentials are valid
3. Check Google Drive API quota limits
4. Review node configurations for typos

### **Kestra Not Receiving Notifications:**
1. Check n8n → Kestra connection settings
2. Verify Kestra webhook endpoint is correct
3. Check Kestra logs for incoming requests
4. Test Kestra endpoint manually with curl

### **Workflow B Failures:**
1. Check service account has READ access to Drive folder
2. Verify Gemini API credentials are valid
3. Check Gemini API quota limits
4. Review file format compatibility

### **Gemini Indexing Issues:**
1. Check Gemini File Search API status
2. Verify file size is within limits (<10MB recommended)
3. Check file format is supported (TXT, PDF, DOCX, etc.)
4. Allow up to 10 minutes for indexing to complete

---

## 📝 Test Execution Log

**Test Date**: [YYYY-MM-DD]
**Tester**: [Name]
**Environment**: Production / Staging

### **Pre-Test Checklist:**
- [ ] All prerequisites met
- [ ] Service account credentials valid
- [ ] n8n instance accessible
- [ ] Kestra instance accessible
- [ ] Google Drive folder accessible

### **Test Execution:**
[Record test execution details, timestamps, and observations here]

### **Issues Found:**
[List any issues discovered during testing]

### **Action Items:**
[List follow-up tasks and improvements needed]

---

## 🎯 Success Criteria

**Test suite is considered PASSED if:**
- ✅ All 10 tests pass
- ✅ End-to-end latency <5 minutes
- ✅ No data loss (all uploaded files indexed)
- ✅ Error handling works correctly
- ✅ Channel renewal process works

**Test suite is considered FAILED if:**
- ❌ Any critical test fails (Tests 1-3)
- ❌ End-to-end latency >10 minutes
- ❌ Data loss occurs (files not indexed)
- ❌ System crashes on error

---

## 📚 Related Documentation

- **Project Rules**: `PROJECT-RULES.md`
- **RAG Requirements**: `Requirements/rag-requirements.md`
- **Webhook Registration Script**: `Requirements/Scripts/register-drive-webhook.py`
- **Webhook Renewal Script**: `Requirements/Scripts/renew-drive-webhook.py`
- **Architecture Diagram**: `Requirements/Architecture/kestra-centric-architecture-diagram.md`

