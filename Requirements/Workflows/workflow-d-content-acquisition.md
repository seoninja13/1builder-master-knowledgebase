# Workflow D: Content Acquisition Pipeline

## Overview
**Owner**: n8n (Event-Driven Worker)  
**Purpose**: Acquire content from external sources and upload to Google Drive  
**Trigger**: Manual webhook or scheduled batch  
**Output**: Files in "OneBuilder Master Knowledge" folder

---

## Architecture Position

```
External Sources (YouTube, Web, Podcasts, etc.)
    ↓
[Workflow D: Content Acquisition] ← YOU ARE HERE
    ↓
Google Drive ("OneBuilder Master Knowledge")
    ↓
[Workflow A: Master Sync] (Detects new files)
    ↓
[Workflow B: Smart Ingestion] (Processes files)
    ↓
Gemini File Search (Indexed and searchable)
```

---

## Input Schema

```json
{
  "source_type": "youtube",  // Required: youtube, podcast, web, pdf_url, api
  "urls": [                  // Required: Array of URLs to process
    "https://youtube.com/watch?v=VIDEO_ID_1",
    "https://youtube.com/watch?v=VIDEO_ID_2"
  ],
  "metadata_overrides": {    // Optional: Manual metadata
    "vertical": "SEO",
    "horizontal": "Strategy",
    "geo": "Sacramento"
  },
  "options": {               // Optional: Processing options
    "transcript_method": "youtube_api",  // or "whisper"
    "language": "en",
    "skip_existing": true    // Don't re-acquire if file exists
  }
}
```

---

## Processing Flow

### Step 1: Input Validation
- Validate source_type is supported
- Validate URLs are well-formed
- Check for duplicate URLs in batch
- Estimate processing time and cost

### Step 2: Content Acquisition (Per URL)
**For YouTube:**
1. Extract video ID from URL
2. Fetch video metadata (YouTube Data API v3)
3. Generate transcript:
   - Option A: YouTube API (auto-generated captions)
   - Option B: Whisper API (higher quality, costs money)
4. Format transcript as readable text

**For Other Sources:**
- Podcast: Download audio → Transcribe with Whisper
- Web: Scrape HTML → Clean and extract main content
- PDF URL: Download PDF file directly
- API: Fetch data → Transform to text format

### Step 3: Content Transformation
1. Convert content to standard format (TXT or Markdown)
2. Generate filename using convention:
   ```
   YYYY-MM-DD_Source_Title_UniqueID.txt
   ```
3. Embed source metadata in file header:
   ```markdown
   ---
   source_type: youtube
   source_url: https://youtube.com/watch?v=abc123
   title: Video Title
   channel: Channel Name
   publish_date: 2024-12-01
   duration: 1234
   acquired_date: 2025-01-17
   ---
   
   [Transcript content here...]
   ```

### Step 4: Upload to Google Drive
1. Authenticate using OAuth credentials (your account)
2. Upload file to folder ID: `1U3TvxcGrz2J4T8OIDjjrnY3P12-PL42_`
3. Capture Drive file ID
4. Log successful upload

### Step 5: Error Handling
**If acquisition fails:**
- Log error details: {url, error_type, error_message, timestamp}
- Continue with next URL (don't stop batch)
- Increment failure counter

**If upload fails:**
- Retry up to 3 times with exponential backoff
- If still fails, log error and continue

### Step 6: Completion Report
After processing all URLs:
1. Generate summary:
   ```json
   {
     "total_urls": 50,
     "successful": 45,
     "failed": 5,
     "duration_seconds": 320,
     "files_uploaded": [
       {"url": "...", "filename": "...", "drive_file_id": "..."},
       ...
     ],
     "failures": [
       {"url": "...", "error": "Transcript unavailable"},
       ...
     ]
   }
   ```
2. Send Slack notification with summary
3. Store detailed log in n8n execution data

---

## Output

### Files Created in Google Drive
- Location: `OneBuilder Master Knowledge` folder
- Format: TXT or Markdown files
- Naming: `YYYY-MM-DD_Source_Title_UniqueID.txt`
- Content: Source metadata + main content

### Acquisition Log
Stored in n8n execution data or separate log file:
```json
{
  "execution_id": "exec_123",
  "timestamp": "2025-01-17T19:00:00Z",
  "source_type": "youtube",
  "total_urls": 50,
  "successful": 45,
  "failed": 5,
  "files": [...],
  "errors": [...]
}
```

---

## Handoff to Existing Workflows

Once files are uploaded to Google Drive:

1. **Workflow A (Master Sync)** runs on schedule (every 4 hours)
   - Detects new files in Drive
   - Compares with Gemini index
   - Identifies files needing ingestion

2. **Workflow B (Smart Ingestion)** processes each file
   - Downloads file from Drive
   - Extracts metadata (reads embedded metadata + AI classification)
   - Chunks content
   - Uploads to Gemini File Search with metadata
   - Creates vector embeddings

3. **Files become searchable** via Workflow C (Query Engine)

---

## Authentication

### Credentials Used
- **Google Drive Upload**: OAuth credentials (your account)
  - Credential name: `Google Drive - Personal Account (OAuth)`
  - Reason: Needs WRITE access to upload files
  
- **YouTube API**: YouTube Data API v3 key
  - Stored in n8n credentials
  - Used for fetching video metadata and transcripts

- **Whisper API** (if used): OpenAI API key
  - Stored in n8n credentials
  - Used for high-quality transcription

---

## Error Handling Matrix

| Error Type | Handling Strategy | Recovery |
|------------|------------------|----------|
| Invalid URL | Skip, log error | Manual review |
| Video unavailable | Skip, log error | Check if video was deleted |
| No transcript | Try Whisper API fallback | Manual transcription |
| API rate limit | Pause, retry after delay | Resume batch later |
| Upload failure | Retry 3x with backoff | Manual upload if fails |
| Network timeout | Retry 3x | Check connectivity |

---

## Performance Considerations

### YouTube Transcript Generation
- **YouTube API**: ~1-2 seconds per video (fast, free, lower quality)
- **Whisper API**: ~30-60 seconds per video (slower, costs $0.006/min, higher quality)

### Batch Processing
- **Small batch** (1-10 URLs): Process sequentially
- **Large batch** (50+ URLs): Process in parallel (max 5 concurrent)
- **Estimated time**: ~2-5 minutes per 50 videos (YouTube API)

### Cost Estimation
- **YouTube API**: Free (10,000 quota units/day, 1 unit per video)
- **Whisper API**: $0.006/minute of audio (~$0.10 per 15-min video)
- **Google Drive Storage**: Uses your personal quota

---

## Future Enhancements

1. **Deduplication**: Check if content already exists before acquiring
2. **Scheduling**: Periodic acquisition from RSS feeds or channels
3. **Quality Control**: Preview transcripts before uploading
4. **Batch Management**: Pause/resume large batches
5. **Source Monitoring**: Auto-detect new content from subscribed sources

