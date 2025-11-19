# Google Drive Webhook Fix - Quick Start Guide

**Status**: ✅ Ready to run  
**Time Required**: 5 minutes  
**Difficulty**: Easy

---

## 🎯 What This Fixes

Your Google Drive webhook **IS receiving notifications from Google** (confirmed!), but it can't retrieve the actual file changes because:

1. ❌ Using `files().watch()` instead of `changes().watch()` API
2. ❌ Using invalid `pageToken=1` instead of a real token

**Good News**: No domain verification needed! Google is already sending notifications.

---

## 🚀 Quick Fix (One Command)

### **Step 1: Run the Master Fix Script**

```powershell
cd c:\Users\IvoD\repos\1builder-master-knowledgebase\Requirements\Scripts
python fix-everything.py
```

This script will:
- ✅ Stop the old webhook channel
- ✅ Get a valid pageToken from Google Drive API
- ✅ Register a NEW webhook using the correct API
- ✅ Save all configuration files
- ✅ Show you the exact pageToken to use

**Time**: 30 seconds

---

### **Step 2: Update n8n Workflow (Manual)**

The script will give you a pageToken like: `12345`

1. Open: https://n8n.srv972609.hstgr.cloud/workflow/a5IiavhYT3sOMo4b
2. Click the **"Get Drive Changes"** node
3. Find **Query Parameters** → **pageToken**
4. Change from: `1`
5. Change to: `<the pageToken from the script>`
6. Click **Save**
7. Ensure workflow is **ACTIVE** (toggle in top-right)

**Time**: 2 minutes

---

### **Step 3: Test It!**

1. Upload a test file to Google Drive:
   https://drive.google.com/drive/folders/1U3TvxcGrz2J4T8OIDjjrnY3P12-PL42_

2. Wait 1-2 minutes

3. Check n8n executions:
   https://n8n.srv972609.hstgr.cloud/workflow/a5IiavhYT3sOMo4b/executions

4. You should see a new execution with actual file changes! 🎉

**Time**: 2 minutes

---

## 📁 Files Created

After running the script, you'll have:

- `Requirements/Credentials/drive-webhook-channel.json` - Channel info
- `Requirements/Credentials/drive-page-token.json` - The pageToken

---

## 🔧 Alternative Scripts (If Needed)

If you want to run steps individually:

### **Option 1: Complete Fix (Recommended)**
```powershell
python fix-everything.py
```

### **Option 2: Step-by-Step**
```powershell
# Fix webhook registration
python fix-webhook-complete.py

# Get instructions for n8n update
python update-n8n-workflow.py
```

---

## ❓ Troubleshooting

### **Script fails with "Service account file not found"**
- Check that `Requirements/Credentials/builder-master-knowldgebase-79a4f60f66e1.json` exists
- Make sure you're running from the correct directory

### **Script fails with "Permission denied"**
- Verify service account has access to Google Drive
- Check that the service account is shared on the folder

### **Webhook still not working after update**
- Verify the pageToken was updated in n8n
- Check that the workflow is ACTIVE
- Wait 2-3 minutes after uploading a file
- Check n8n execution history for errors

### **Need to re-register webhook**
- Webhook channels expire after 7 days
- Just run `fix-everything.py` again before expiration

---

## 📚 What Changed

### **Before (Broken)**
```python
# Wrong API - watches a specific file/folder
service.files().watch(
    fileId=FOLDER_ID,
    body=body
).execute()

# Invalid pageToken in n8n
pageToken = "1"  # ❌ Not a real token
```

### **After (Fixed)**
```python
# Correct API - watches entire Drive
service.changes().watch(
    pageToken=page_token,  # ✅ Real token from API
    body=body
).execute()

# Valid pageToken in n8n
pageToken = "12345"  # ✅ Real token from getStartPageToken()
```

---

## ✅ Success Criteria

After completing all steps, you should see:

1. ✅ Script completes without errors
2. ✅ New webhook channel registered
3. ✅ pageToken saved to files
4. ✅ n8n workflow updated with new pageToken
5. ✅ Test file upload triggers n8n execution
6. ✅ Execution shows actual file changes (not empty)
7. ✅ Kestra receives notification

---

## 🆘 Need Help?

If you encounter any issues:

1. Check the error message from the script
2. Verify service account permissions
3. Check n8n execution logs for errors
4. Review `Requirements/TROUBLESHOOTING-WEBHOOK-ISSUE.md`

---

**Ready?** Run `python fix-everything.py` and follow the instructions! 🚀

