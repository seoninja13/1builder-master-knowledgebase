# RAG System Ingestion Architecture

## Overview
This document defines how content flows from external sources into the Gemini File Search index.

---

## Two Ingestion Paths

### **Path 1: Immediate Ingestion (Ad-Hoc)**
**Use Case:** User explicitly requests ingestion via ChatGPT  
**Trigger:** Manual command (e.g., "Index this YouTube URL")  
**Latency:** Immediate (no waiting for sync)

```
ChatGPT: "Index this YouTube URL: [URL]"
    ↓
n8n Webhook (Workflow D: Content Acquisition)
    ↓
n8n: Fetch content (transcript, scrape, etc.)
    ↓
n8n: Upload to Google Drive (OAuth credentials)
    ↓
n8n: IMMEDIATELY upload to Gemini File Search
    ↓
ChatGPT: "Content indexed successfully"
```

**Key Point:** Content is uploaded to BOTH Drive AND Gemini in the same workflow.

---

### **Path 2: Scheduled Sync (Catch-All)**
**Use Case:** User manually uploads files to Drive, or Path 1 failed  
**Trigger:** Kestra scheduled job (every 5 minutes)  
**Latency:** Up to 5 minutes

```
Kestra: Scheduled job runs every 5 minutes
    ↓
Kestra: Fetch file list from Google Drive
    ↓
Kestra: Fetch file list from Gemini File Search
    ↓
Kestra: Compare lists (delta analysis)
    ↓
Kestra: Identify new/updated/deleted files
    ↓
For each new/updated file:
    Kestra → n8n Webhook (Workflow B: Smart Ingestion)
        ↓
    n8n: Download file from Drive
        ↓
    n8n: Extract metadata (AI classification)
        ↓
    n8n: Upload to Gemini File Search
        ↓
    n8n: Report success to Kestra
```

**Key Point:** This catches any files that were manually uploaded or missed by Path 1.

---

## Detailed Workflow Specifications

### **Workflow D: Content Acquisition (n8n - Ad-Hoc Path)**

**Trigger:** Webhook from ChatGPT/MCP  
**Input:** `{source_type, url, metadata_overrides}`

**Steps:**
1. **Validate Input**
   - Check source_type is supported
   - Validate URL format

2. **Fetch Content**
   - YouTube: Generate transcript (YouTube API or Whisper)
   - Web: Scrape content (Crawl4AI)
   - Podcast: Download and transcribe audio
   - PDF: Download file

3. **Transform Content**
   - Convert to standard format (TXT/MD)
   - Generate filename: `YYYY-MM-DD_Source_Title_ID.txt`
   - Embed metadata in file header

4. **Dual Upload (Critical Step)**
   ```
   Parallel execution:
   ├─ Upload to Google Drive (OAuth credentials)
   │  └─ Folder: "OneBuilder Master Knowledge"
   │
   └─ Upload to Gemini File Search (Service Account)
      └─ With customMetadata (vertical, horizontal, geo, intent)
   ```

5. **Return Success**
   - Response: `{success: true, drive_file_id, gemini_file_id}`

**Why Dual Upload?**
- ✅ Immediate availability in Gemini (no waiting for sync)
- ✅ Drive serves as backup/source of truth
- ✅ Scheduled sync catches any failures

---

### **Workflow A: Master Sync (Kestra - Scheduled Path)**

**Trigger:** Scheduled (every 5 minutes)  
**Owner:** Kestra

**Steps:**
1. **Fetch Drive File List**
   - Use Service Account (READ access)
   - Get: file_id, name, modified_time

2. **Fetch Gemini File List**
   - Use Service Account
   - Get: file_id, name, metadata

3. **Delta Analysis**
   ```
   New Files: In Drive but not in Gemini
   Updated Files: In both, but Drive modified_time > Gemini metadata_time
   Deleted Files: In Gemini but not in Drive
   ```

4. **Dispatch Actions**
   - For each New/Updated file:
     - Trigger n8n Webhook (Workflow B)
     - Pass: {drive_file_id, drive_file_url}
   
   - For each Deleted file:
     - Call Gemini API directly to remove from index

5. **Error Handling**
   - Log failed ingestions
   - Send Slack alert if failures exceed threshold
   - Retry failed files on next sync

---

### **Workflow B: Smart Ingestion (n8n - Triggered by Workflow A)**

**Trigger:** Webhook from Kestra (Workflow A)  
**Input:** `{drive_file_id, drive_file_url}`

**Steps:**
1. **Download File**
   - Use Service Account (READ access)
   - Download complete file from Drive

2. **Extract Metadata**
   - Check if file has embedded metadata (from Workflow D)
   - If not, use AI to extract:
     - Vertical, Horizontal, Geo, Intent
   - Combine with system metadata:
     - drive_file_id, filename, modified_timestamp

3. **Upload to Gemini**
   - Upload complete file (not chunked)
   - Attach customMetadata JSON
   - Gemini automatically chunks/embeds/indexes

4. **Report Success**
   - Return to Kestra: {success: true, gemini_file_id}

---

## Why This Architecture Works

### **Immediate Ingestion (Path 1)**
- ✅ User gets instant feedback
- ✅ Content available immediately for queries
- ✅ No waiting for scheduled sync

### **Scheduled Sync (Path 2)**
- ✅ Catches manual uploads (you drag files to Drive)
- ✅ Recovers from Path 1 failures
- ✅ Ensures Drive and Gemini stay in sync
- ✅ Handles deleted files

### **Dual Upload Strategy**
- ✅ Drive = Source of truth (backup, manual access)
- ✅ Gemini = Query index (fast retrieval)
- ✅ Scheduled sync = Safety net (catches everything)

---

## Sync Frequency Recommendation

### **Option A: 5-Minute Sync (Recommended)**
- **Pros:** Near-real-time for manual uploads, catches failures quickly
- **Cons:** More API calls (but still within quota)
- **API Usage:** ~288 calls/day (well within 10,000 quota)

### **Option B: 4-Hour Sync (Original Design)**
- **Pros:** Fewer API calls, less overhead
- **Cons:** Manual uploads take up to 4 hours to be indexed
- **API Usage:** ~6 calls/day

**Recommendation:** Use **5-minute sync** since Path 1 handles most ingestion immediately.

---

## Error Handling

### **Path 1 Failures (Ad-Hoc Ingestion)**
- If Drive upload fails: Retry 3x, then return error to user
- If Gemini upload fails: File still in Drive, Path 2 will catch it
- User gets immediate feedback on success/failure

### **Path 2 Failures (Scheduled Sync)**
- Log failure details in Kestra
- Retry on next sync (5 minutes later)
- Send Slack alert if same file fails 3 times
- Manual intervention required after 3 failures

---

## Authentication Summary

| Operation | Credential Type | Reason |
|-----------|----------------|--------|
| **Path 1: Upload to Drive** | OAuth (your account) | Needs WRITE access |
| **Path 1: Upload to Gemini** | Service Account | Has Vertex AI permissions |
| **Path 2: Read from Drive** | Service Account | READ-only access sufficient |
| **Path 2: Upload to Gemini** | Service Account | Has Vertex AI permissions |

---

## Implementation Priority

1. **Phase 1:** Implement Path 2 (Scheduled Sync) - Foundation
2. **Phase 2:** Implement Path 1 (Ad-Hoc Ingestion) - User experience
3. **Phase 3:** Optimize sync frequency based on usage patterns

