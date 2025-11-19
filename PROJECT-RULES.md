# 1BuilderRAG Project Rules

**Project Name**: `1BuilderRAG`  
**Repository**: `c:\Users\IvoD\repos\1builder-master-knowledgebase`  
**Last Updated**: 2025-01-17

---

## 🔑 CRITICAL PROJECT IDENTIFIERS

### **Project Naming Convention:**
- **ALL n8n workflows** MUST use prefix: `1BuilderRAG-`
- **Examples**: 
  - ✅ `1BuilderRAG-webhook-drive-notifications`
  - ✅ `1BuilderRAG-smart-ingestion`
  - ✅ `1BuilderRAG-query-engine`
  - ❌ DO NOT use generic names without prefix

### **Current n8n Workflows:**
- **Webhook Workflow**: https://n8n.srv972609.hstgr.cloud/workflow/a5IiavhYT3sOMo4b
  - **Name**: `1BuilderRAG-webhook-drive-notifications`
  - **Purpose**: Receives Google Drive push notifications and triggers ingestion pipeline
  - **Status**: Created (Inactive - requires activation)
  - **Documentation**: `Requirements/Workflows/1BuilderRAG-webhook-drive-notifications.md`

- **OAuth Write Test Workflow**: https://n8n.srv972609.hstgr.cloud/workflow/fZxelIocWUaJOWqP
  - **Name**: `1BuilderRAG-OAuth Write test`
  - **Purpose**: OAuth write test workflow (Phase 2)
  - **Status**: Inactive (test workflow only)

### **Google Drive Configuration:**
- **Folder Name**: "OneBuilder Master Knowledge"
- **Folder ID**: `1U3TvxcGrz2J4T8OIDjjrnY3P12-PL42_`
- **Folder URL**: https://drive.google.com/drive/folders/1U3TvxcGrz2J4T8OIDjjrnY3P12-PL42_
- **Owner**: `dachevivo@gmail.com`

### **n8n Instance:**
- **Base URL**: https://n8n.srv972609.hstgr.cloud
- **Webhook Endpoint**: https://n8n.srv972609.hstgr.cloud/webhook/drive-notifications

### **Google Cloud Project:**
- **Project ID**: `builder-master-knowldgebase`
- **Project Number**: `856637549932`
- **Service Account**: `id-builder-masterknowldge@builder-master-knowldgebase.iam.gserviceaccount.com`

---

## 📋 WORKFLOW NAMING REFERENCE

### **Workflow A: Master Sync (Kestra)**
- **n8n Workflow Name**: `1BuilderRAG-master-sync`
- **Purpose**: Synchronize Google Drive with Gemini File Search index
- **Trigger**: Scheduled (5-minute polling) + Push notifications

### **Workflow B: Smart Ingestion (n8n)**
- **n8n Workflow Name**: `1BuilderRAG-smart-ingestion`
- **Purpose**: Process individual files and upload to Gemini
- **Trigger**: Called by Workflow A when new/updated files detected

### **Workflow C: Query Engine (n8n)**
- **n8n Workflow Name**: `1BuilderRAG-query-engine`
- **Purpose**: Answer user questions using RAG system
- **Trigger**: Webhook from ChatGPT/MCP

### **Workflow D: Content Acquisition (n8n)**
- **n8n Workflow Name**: `1BuilderRAG-content-acquisition`
- **Purpose**: Acquire content from external sources (YouTube, web, podcasts)
- **Trigger**: Webhook from ChatGPT/MCP or manual

### **Webhook Workflow (n8n)**
- **n8n Workflow Name**: `1BuilderRAG-webhook-drive-notifications`
- **Purpose**: Receive Google Drive push notifications
- **Trigger**: POST requests from Google Drive API
- **Current URL**: https://n8n.srv972609.hstgr.cloud/workflow/a5IiavhYT3sOMo4b
- **Status**: Created (Inactive - requires activation)

---

## 🚫 DO NOT REFERENCE

### **Incorrect Workflow URLs:**
- ❌ https://n8n.srv972609.hstgr.cloud/workflow/B2tNNaSkbLD8gDxw
  - This workflow is NOT related to the 1BuilderRAG project
  - DO NOT modify or reference this workflow

---

## 📚 DOCUMENTATION INDEX

### **Primary Handover Document:**
- `Docs/handover/conversation-handover-knowledge-transfer.md`

### **Core Requirements:**
- `Requirements/rag-requirements.md` (524 lines)

### **Architecture Documentation:**
- `Requirements/Architecture/kestra-centric-architecture-diagram.md`
- `Requirements/Architecture/ingestion-architecture.md`

### **Workflow Specifications:**
- `Requirements/Workflows/workflow-d-content-acquisition.md`
- `Requirements/Workflows/1BuilderRAG-webhook-drive-notifications.md`

### **Testing Documentation:**
- `Requirements/Testing/end-to-end-test-plan.md`

### **Scripts:**
- `Requirements/Scripts/register-drive-webhook.py`
- `Requirements/Scripts/renew-drive-webhook.py`

### **Guides:**
- `Requirements/Guides/n8n-google-oauth-setup.md`

### **Phase 2 Status:**
- `Requirements/PHASE-2-FINAL-STATUS-SNAPSHOT.md`
- `Requirements/PHASE-2-STATUS-REPORT.md`
- `Requirements/PHASE-2-NEXT-STEPS.md`

---

## 🔐 AUTHENTICATION

### **Service Account (READ Access):**
- **Email**: `id-builder-masterknowldge@builder-master-knowldgebase.iam.gserviceaccount.com`
- **Key File**: `Requirements/Credentials/builder-master-knowldgebase-79a4f60f66e1.json`
- **Permissions**: Viewer (READ-only) on Google Drive folder
- **Use Cases**: Workflows A, B, C (reading files, querying Gemini)

### **OAuth Credentials (WRITE Access):**
- **User**: `dachevivo@gmail.com`
- **Credential Name in n8n**: `Google Drive - Personal Account (OAuth)`
- **Status**: ✅ Connected
- **Scopes**: `https://www.googleapis.com/auth/drive`
- **Use Cases**: Workflow D (content acquisition, uploading files)

---

## 🎯 CURRENT PHASE

**Phase 2**: Google Drive & Authentication Setup  
**Status**: 83% complete (5 of 6 tasks done)  
**Next Task**: Test OAuth WRITE access (Task 5)

---

## 📝 NOTES

- This file serves as the single source of truth for project-specific identifiers
- Always reference this file when working with n8n workflows
- Update this file when new workflows are created or configuration changes
- DO NOT confuse this project with other projects in different repositories

