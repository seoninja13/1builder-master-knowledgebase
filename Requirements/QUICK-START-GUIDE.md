# 1BuilderRAG Webhook Integration - Quick Start Guide

**Last Updated**: 2025-11-17  
**Estimated Time**: 10-15 minutes

---

## 🚀 Quick Start (5 Steps)

### **Step 1: Open the Workflow** (1 min)

Open the webhook workflow in n8n:
- **URL**: https://n8n.srv972609.hstgr.cloud/workflow/a5IiavhYT3sOMo4b
- **Name**: `1BuilderRAG-webhook-drive-notifications`

---

### **Step 2: Configure Credentials** (3 min)

**RECOMMENDED: Use Existing OAuth Credential**

1. Click on the **"Get Drive Changes"** node (3rd node in the workflow)
2. In the node panel, find the **Authentication** section
3. Select **"Predefined Credential Type"**
4. For **Credential Type**, select: **"Google Drive OAuth2 API"**
5. For **Credential**, select: **"Google Drive - 1builderMasterKnowledge"** (already exists)
6. Click **Save** (bottom-right corner)

**Why this works**: You already have this OAuth credential set up and working from Phase 2!

---

### **Step 3: Activate the Workflow** (1 min)

1. In the top-right corner, find the **Inactive/Active** toggle
2. Click to **Activate** the workflow
3. Verify the toggle shows **"Active"** with a green checkmark ✅

---

### **Step 4: Register Webhook with Google Drive** (3 min)

Open PowerShell or Command Prompt and run:

```powershell
cd c:\Users\IvoD\repos\1builder-master-knowledgebase\Requirements\Scripts
python register-drive-webhook.py
```

**Expected Output**:
```
✅ Service account loaded: id-builder-masterknowldge@...
✅ WEBHOOK REGISTERED SUCCESSFULLY!
Channel ID: 1builderrag-...
Expiration: 2025-11-24T...
✅ Channel info saved to: ...drive-webhook-channel.json
```

**If you get an error**: Make sure Python is installed and the service account JSON file exists.

---

### **Step 5: Test the Integration** (5 min)

1. **Upload a test file** to Google Drive:
   - Go to: https://drive.google.com/drive/folders/1U3TvxcGrz2J4T8OIDjjrnY3P12-PL42_
   - Click **"New"** → **"File upload"**
   - Upload any text file (e.g., `test.txt`)

2. **Wait 30 seconds**

3. **Check n8n execution history**:
   - Go to: https://n8n.srv972609.hstgr.cloud/executions
   - Look for a new execution of `1BuilderRAG-webhook-drive-notifications`
   - Status should be: **Success** ✅

4. **Verify the execution**:
   - Click on the execution to see details
   - Check that all 5 nodes executed successfully
   - Verify file details were extracted correctly

---

## ✅ Success Checklist

- [ ] Workflow opened in n8n
- [ ] "Get Drive Changes" node configured with OAuth credential
- [ ] Workflow activated (green toggle)
- [ ] Webhook registered with Google Drive (script ran successfully)
- [ ] Test file uploaded to Google Drive
- [ ] n8n execution history shows successful run
- [ ] All 5 nodes in workflow executed without errors

---

## 🔧 Troubleshooting

### **Problem: Can't find "Google Drive OAuth2 API" credential type**

**Solution**: 
1. In the "Get Drive Changes" node, make sure **Authentication** is set to **"Predefined Credential Type"**
2. The dropdown should then show various Google credential types
3. Look for "Google Drive OAuth2 API" or similar

### **Problem: Webhook registration script fails**

**Solution**:
1. Check Python is installed: `python --version`
2. Install required packages: `pip install google-auth google-api-python-client`
3. Verify service account file exists: `Requirements/Credentials/builder-master-knowldgebase-79a4f60f66e1.json`

### **Problem: Workflow doesn't trigger after file upload**

**Solution**:
1. Check workflow is **Active** (green toggle)
2. Check webhook channel hasn't expired: `cat Requirements/Credentials/drive-webhook-channel.json`
3. Re-register webhook: `python Requirements/Scripts/register-drive-webhook.py`
4. Wait up to 1 minute for Google Drive to send notification

### **Problem: "Get Drive Changes" node fails**

**Solution**:
1. Verify credential is selected in the node
2. Check credential has access to Google Drive API
3. Try using the existing OAuth credential instead of service account

---

## 📚 Additional Resources

- **Full Documentation**: `Requirements/Workflows/1BuilderRAG-webhook-drive-notifications.md`
- **Test Plan**: `Requirements/Testing/end-to-end-test-plan.md`
- **Task Summary**: `Requirements/TASK-COMPLETION-SUMMARY.md`
- **Project Rules**: `PROJECT-RULES.md`

---

## 🎯 What Happens Next?

Once the webhook is working:

1. **Automatic Detection**: Any file uploaded to the Google Drive folder triggers the workflow
2. **Real-time Processing**: n8n receives notification within 30 seconds
3. **Kestra Orchestration**: Workflow notifies Kestra to start ingestion
4. **Gemini Indexing**: File is processed and indexed in Gemini File Search
5. **Searchable**: File becomes searchable in your RAG system

**Total Time**: Upload → Searchable in <5 minutes

---

## 💡 Pro Tips

1. **Monitor Channel Expiration**: Webhook channels expire after 7 days. Set a reminder to renew:
   ```bash
   python Requirements/Scripts/renew-drive-webhook.py
   ```

2. **Check Execution History Regularly**: Visit https://n8n.srv972609.hstgr.cloud/executions to monitor workflow runs

3. **Use Test Files**: Always test with small text files first before uploading large PDFs or videos

4. **Keep Workflow Active**: If you deactivate the workflow, remember to reactivate it before uploading files

---

## 🆘 Need Help?

If you encounter issues not covered here:

1. Check the full documentation in `Requirements/Workflows/1BuilderRAG-webhook-drive-notifications.md`
2. Review the test plan in `Requirements/Testing/end-to-end-test-plan.md`
3. Check n8n execution logs for detailed error messages
4. Verify all credentials are valid and not expired

---

**You're all set! Start with Step 1 above.** 🚀

