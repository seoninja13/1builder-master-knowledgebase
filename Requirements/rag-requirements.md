OneBuilder Master RAG: Architectural Blueprint
1. System Topology
We are building a "Drive-First" architecture. This means the file system (Google Drive) is the absolute source of truth, and the AI Index (Gemini) is a downstream reflection of that truth, synchronized by an orchestrator.

The Four Layers
Storage Layer (The "Truth"): Google Drive. All raw files reside here. No database maintenance; just file management.

Intelligence Layer (The "Brain"): Google Gemini File Search. Handles vectorization, storage, retrieval, and answer synthesis.

Control Layer (The "Manager"): Kestra. Handles scheduling, state synchronization, error recovery, and "big picture" logic.

Execution Layer (The "Worker"): n8n. Handles stateless, real-time tasks like "ingest this specific file" or "answer this specific query."

2. Data Architecture Strategy
2.1 The "Single Bucket" Policy
Physical Storage: A single Google Drive folder named OneBuilder Master Knowledge.

Organization: No subfolders. The physical location is irrelevant to the AI.

Categorization: Logical, not physical. We use Metadata Tags attached to the file inside the Gemini Index.

2.2 Metadata Taxonomy
The AI will classify every file with these attributes during ingestion. This allows precise filtering later.

Vertical: (e.g., SEO, PPC, Web Design, Lead Gen)

Horizontal: (e.g., Strategy, Tactics, Reporting, Revenue)

Geo: (e.g., Sacramento, National, Global)

Intent: (e.g., Guide, Checklist, Case Study, Contract)

Provenance: drive_file_id, modified_timestamp (Crucial for synchronization).

3. Detailed Workflow Architectures
Workflow A: The "Master Sync" Loop (Kestra)
Owned by: Kestra (Scheduled Batch Process)

This is the heartbeat of the system. It ensures the AI never hallucinates on old data.

**Sync Strategy:**
- **Primary Trigger**: Google Drive Push Notifications (immediate, event-driven)
- **Backup Trigger**: 5-minute polling (catches missed events, ensures consistency)
- **Rationale**: Push notifications provide near-instant ingestion, while polling serves as safety net

Snapshot State:

Fetch the current file list from Google Drive (Source).

Fetch the current file list from Gemini File Search (Index).

Delta Analysis (Logic):

Compare the two lists.

Identify New: Files in Drive but not in Index.

Identify Updated: Files in both, but Drive modified_time > Index metadata_time.

Identify Deleted: Files in Index but not in Drive.

Dispatch Orders:

For New/Updated: Trigger the Ingestion Worker (n8n Workflow B).

For Deleted: Trigger the Cleanup Worker (n8n) or call Gemini API directly to remove.

Error Handling:

If an ingestion fails, move the source file to a FAILED_INGEST folder in Drive and alert via Slack.

**Observability:**
- Kestra logs all sync operations (start time, files processed, success/failure)
- Tracks metrics: sync duration, files added/updated/deleted, error rates
- Provides audit trail for compliance and debugging

Workflow B: The "Smart Ingestion" Pipeline (n8n)
Owned by: n8n (Event-Driven Worker)
Orchestrated by: Kestra (Workflow A triggers this workflow)

This worker does not know about the "whole drive." It only knows how to process one file perfectly when told to do so.

Fetch: Download the binary file from the URL provided by the Master Sync.

Metadata Extraction (AI Step):

Check if manual tags were passed.

If not, read the document header/content using a fast LLM call.

Prompt Logic: "Analyze this text. Extract the Business Vertical, Geographic focus, and Document Type. Return as JSON."

Tagging & Indexing:

Combine inferred tags with system tags (Filename, Drive ID, Timestamp).

Upload **complete file** to Gemini File Search with customMetadata.

**Important**: Gemini File Search handles chunking, embedding, and indexing automatically. We do NOT pre-chunk content.

Ack: Report success back to the Master Sync (Kestra).

**Kestra Orchestration:**
- Kestra triggers this workflow when new/updated files are detected
- n8n executes the ingestion and reports status back to Kestra
- Kestra logs all ingestion operations for observability

Workflow C: The "Contextual Router" Query Engine (n8n)
Owned by: n8n (Real-Time API)
Orchestrated by: Kestra (All queries route through Kestra first)

**Query Flow Architecture (Kestra-Centric):**
```
ChatGPT (User Interface)
    ↓
Kestra (Central Orchestrator)
    ├─ Receives query
    ├─ Logs request (timestamp, user, query text)
    ├─ Routes to n8n Workflow C
    ├─ Tracks execution status
    └─ Manages observability
    ↓
n8n (Execution Worker - Workflow C)
    ├─ Intent classification
    ├─ Filter construction
    └─ Query Gemini File Search API
    ↓
Gemini File Search
    ├─ Retrieves relevant chunks
    ├─ Generates answer with citations
    └─ Returns results
    ↓
n8n (Receives results)
    ↓
Kestra (Logs response, tracks metrics: latency, success/failure)
    ↓
ChatGPT (Displays answer to user)
```

**Why Kestra Must Be in the Middle:**
- **Observability**: Track all queries, response times, and success rates
- **Error Logging**: Capture failures and retry logic
- **Audit Trail**: Complete history of all operations for compliance
- **Routing Logic**: Can route to different workflows based on query type
- **Metrics**: Monitor system health, query patterns, and performance

**Latency Trade-off**: Kestra adds ~100-200ms overhead, but this is acceptable for the observability benefits.

Intent Classification (The Router):

Receive User Query: "How do we handle SEO for windows in Sacramento?"

AI Logic: Map query to the Metadata Taxonomy.

Result: Vertical="SEO", Geo="Sacramento".

Filter Construction:

Convert the result into the Gemini File Search filter syntax (SQL-like string).

RAG Retrieval:

Execute the search against Gemini using the specific filter.

Benefit: This prevents the AI from reading "National Strategy" docs when you asked for "Sacramento" specifics.

Synthesis:

Gemini generates the answer using only the retrieved chunks.

Constraint: Must provide citations referencing the filename.

Workflow D: The "Content Acquisition" Pipeline (n8n)
Owned by: n8n (Event-Driven Worker)
Orchestrated by: Kestra (Routes programmatic ingestion requests)

**Purpose**: Acquire content from external sources and ingest into the RAG system.

**Supported Content Sources:**
- YouTube videos (transcript generation)
- Web pages (scraping and extraction)
- Podcasts (audio transcription)
- Direct file uploads

**Ingestion Flow (Programmatic):**
```
ChatGPT: "Index this YouTube URL"
    ↓
Kestra (Central Orchestrator)
    ├─ Receives ingestion request
    ├─ Logs request
    └─ Routes to n8n Workflow D
    ↓
n8n (Workflow D: Content Acquisition)
    ├─ Fetches content (e.g., YouTube transcript)
    ├─ Uploads to Google Drive (OAuth credentials)
    └─ Immediately uploads to Gemini File Search
    ↓
Gemini File Search
    ├─ Automatically chunks content
    ├─ Generates embeddings
    └─ Indexes file
    ↓
n8n reports success to Kestra
    ↓
Kestra logs completion
    ↓
ChatGPT: "Content indexed successfully"
```

**Dual Upload Strategy:**
- Upload to **Google Drive** (source of truth, OAuth credentials required)
- Upload to **Gemini File Search** (immediate availability for queries)
- Rationale: Ensures content is immediately searchable while maintaining Drive as source of truth

**Automatic Ingestion via Google Drive Push Notifications:**

When files are manually uploaded to Google Drive:
```
User uploads file to Google Drive
    ↓
Google Drive detects change
    ↓
Google sends push notification to n8n webhook
    ↓
n8n (Workflow D: Content Acquisition)
    ├─ Receives notification
    ├─ Calls Google Drive Changes API
    ├─ Filters for relevant changes
    ├─ Fetches file metadata
    └─ Notifies Kestra
    ↓
Kestra (Workflow A: Master Sync)
    ├─ Receives notification from n8n
    ├─ Logs ingestion request
    └─ Triggers n8n Workflow B
    ↓
n8n (Workflow B: Smart Ingestion)
    ├─ Downloads file from Drive
    ├─ Extracts metadata (AI classification)
    └─ Uploads to Gemini File Search
    ↓
Gemini File Search indexes file
    ↓
n8n reports success to Kestra
    ↓
Kestra logs completion
```

**Google Drive Push Notifications Setup:**
- n8n webhook endpoint: `https://n8n.srv972609.hstgr.cloud/webhook/drive-notifications`
- Notification channel registration via Google Drive API
- Channel lifecycle management (renewal before expiration)
- Fallback to 5-minute polling if push notifications fail

**Authentication:**
- OAuth credentials (user account) for WRITE access to Google Drive
- Service account for READ access and Gemini API calls

4. Integration Architecture (The MCP Server)
We use the Model Context Protocol (MCP) to bridge your IDE (VS Code) and Agents (ChatGPT) with the Orchestrators.

**CRITICAL PRINCIPLE: Kestra as Central Orchestrator**

ALL operations (queries and ingestion) MUST flow through Kestra for:
- **Centralized Logging**: Every operation is logged with timestamp, user, and status
- **Observability**: Track system health, performance metrics, and error rates
- **Error Handling**: Retry logic, failure notifications, and recovery procedures
- **Routing Logic**: Intelligent workflow routing based on request type
- **Audit Trail**: Complete history for compliance and debugging
- **Workflow Coordination**: Orchestrate complex multi-step processes

Kestra serves as the "brain" of the system - it provides visibility and control over ALL operations.

4.1 The "Manager" Interface (Official Kestra MCP)
Purpose: Orchestration visibility and control.

User: You (The Architect/Dev) inside VS Code.

Capabilities:

"List all failed sync jobs from yesterday."

"Trigger the Ingestion pipeline manually for this file."

"Show me the logs for the last deployment."

4.2 The "Knowledge" Interface (Custom Facade)
Purpose: Q&A and content generation.

User: Project Manager Agent (ChatGPT) or Coding Agent (Augment).

Capabilities:

kb.ask(question): Routes through Kestra to Workflow C (n8n Query Engine).

kb.add(url): Routes through Kestra to Workflow D (n8n Content Acquisition).

**Flow Architecture:**
- ChatGPT calls MCP function (kb.ask or kb.add)
- MCP routes request to Kestra
- Kestra logs request and routes to appropriate n8n workflow
- n8n executes the task
- n8n reports results back to Kestra
- Kestra logs completion and returns response to ChatGPT

5. Authentication Strategy

**Hybrid Authentication Approach:**

Due to Google Cloud limitations with personal accounts, we use a hybrid authentication strategy:

**5.1 Service Account (READ-only + Gemini API)**

**Purpose**: READ access to Google Drive, full access to Gemini/Vertex AI

**Credentials**: `builder-master-knowldgebase-79a4f60f66e1.json`

**Service Account Email**: `id-builder-masterknowldge@builder-master-knowldgebase.iam.gserviceaccount.com`

**Project ID**: `builder-master-knowldgebase`

**Permissions**:
- Google Drive API: READ access to shared folder "OneBuilder Master Knowledge"
- Gemini API: Full access for file upload, search, and retrieval
- Vertex AI API: Full access for AI operations

**Limitation**: Service accounts CANNOT write to personal Google Drive folders due to storage quota restrictions

**Use Cases**:
- Workflow A: Read Drive file list for sync comparison
- Workflow B: Read files from Drive for ingestion
- Workflow C: Query Gemini File Search API
- All Gemini API operations

**5.2 OAuth Credentials (WRITE access to Google Drive)**

**Purpose**: WRITE access to Google Drive for programmatic content uploads

**Authentication Type**: OAuth 2.0 (user account)

**User Account**: Your personal Google account (owner of "OneBuilder Master Knowledge" folder)

**Permissions**:
- Google Drive API: Full READ/WRITE access

**Use Cases**:
- Workflow D: Upload acquired content (YouTube transcripts, web scrapes) to Google Drive

**Setup Location**: n8n credentials configuration

**Why Hybrid Approach?**
- Service accounts cannot write to personal Drive folders (Google Cloud limitation)
- OAuth provides full access but requires user consent
- Best of both worlds: Service account for automated reads, OAuth for writes

**5.3 Google Drive Folder Configuration**

**Folder Name**: "OneBuilder Master Knowledge"

**Folder ID**: `1U3TvxcGrz2J4T8OIDjjrnY3P12-PL42_`

**Sharing**:
- Shared with service account: `id-builder-masterknowldge@builder-master-knowldgebase.iam.gserviceaccount.com`
- Permission: Viewer (READ-only)

**Organization**: Single flat folder (no subfolders)

6. Google Drive Push Notifications Architecture

**6.1 How Push Notifications Work**

Google Drive supports push notifications via the **Drive API Push Notifications** feature:

1. **Register a Notification Channel** (webhook) with Google Drive API
2. **Provide webhook URL** where Google will send notifications
3. **Specify resource to watch** (file, folder, or drive)
4. **Google sends POST requests** to webhook whenever changes occur
5. **Webhook receives notification** and triggers workflow

**6.2 Implementation Details**

**n8n Webhook Endpoint**: `https://n8n.srv972609.hstgr.cloud/webhook/drive-notifications`

**Notification Channel Registration**:
- Performed via Google Drive API `watch` method
- Requires: webhook URL, driveId (or fileId)
- Returns: channel ID and expiration timestamp

**Channel Lifecycle Management**:
- Channels expire after a certain time (typically 24 hours to 7 days)
- Must be renewed before expiration
- n8n workflow handles automatic renewal
- Fallback to polling if renewal fails

**Notification Flow**:
```
1. User uploads file to Google Drive
2. Google Drive detects change
3. Google sends POST to n8n webhook
4. n8n receives notification (contains resourceId, not file details)
5. n8n calls Google Drive Changes API to get actual change events
6. n8n filters for relevant changes (new files, updates)
7. n8n notifies Kestra of new content
8. Kestra triggers Workflow B (Smart Ingestion)
```

**6.3 Fallback Strategy**

If push notifications fail (e.g., channel expires, webhook unreachable):
- Kestra's 5-minute polling (Workflow A) serves as backup
- Ensures no files are missed
- Provides redundancy and reliability

**6.4 Benefits of Push Notifications**

- **Near-instant ingestion**: Files indexed within seconds of upload
- **Resource efficiency**: No constant polling required
- **Scalability**: Handles high-volume uploads without performance degradation
- **Reliability**: Combined with polling backup, ensures 100% coverage

**6.5 Personal Account Compatibility**

- ✅ Push notifications ARE available for personal Google accounts
- ✅ Domain verification is NO LONGER required (as of June 2022)
- ✅ Works with both personal drives and Shared Drives
- ⚠️ Requires publicly accessible webhook endpoint (n8n must be internet-accessible)

7. Governance & "Gatekeeper" Architecture
To ensure this system is "Production-Ready," we implement an automated Quality Assurance layer.

The Evaluation Gate (CI/CD)
Before any code change (e.g., changing the system prompt, switching LLM models) is deployed to Production:

The Gold Set: A locked list of 20 pairs of {Question, Ideal Answer/Source}.

The Gauntlet: Kestra runs these 20 questions against the new version of the pipeline.

The Metrics:

Hit Rate: Did the correct document appear in the top 5 results?

Latency: Did it respond in under 5 seconds?

The Rule: If the Score < 90%, the deployment fails. This prevents "upgrades" that make the system stupider.

8. Implementation Sequence (Logical Steps)

**Phase 1: Google Cloud Setup & Verification** ✅ COMPLETE
- Set up Google Cloud project
- Enable required APIs (Google Drive, Gemini, Vertex AI)
- Create service account with appropriate IAM roles
- Verify service account authentication
- Verify API access

**Phase 2: Google Drive Setup & Testing** ⏳ IN PROGRESS
- Create "OneBuilder Master Knowledge" folder in Google Drive
- Share folder with service account (READ-only access)
- Verify service account can read Drive files
- Set up OAuth credentials in n8n for WRITE access
- Test OAuth authentication for Drive writes
- **Update requirements document** ✅ COMPLETE

**Phase 3: n8n Configuration & Testing** ⏳ PENDING
- Configure service account credentials in n8n
- Configure OAuth credentials in n8n
- Test connectivity to Google Drive API
- Test connectivity to Gemini API
- Set up Google Drive push notifications webhook
- Test webhook reception and notification flow
- Create test workflows for each operation

**Phase 4: Workflow Implementation** ⏳ PENDING
- Build Workflow B (Smart Ingestion)
  - File download from Drive
  - Metadata extraction with AI
  - Upload to Gemini File Search
  - Status reporting to Kestra
- Build Workflow C (Query Engine)
  - Intent classification
  - Filter construction
  - Gemini query execution
  - Response formatting
- Build Workflow D (Content Acquisition)
  - YouTube transcript generation
  - Web scraping
  - File upload to Drive (OAuth)
  - Immediate Gemini indexing
  - Push notification handling

**Phase 5: Kestra Orchestration** ⏳ PENDING
- Build Workflow A (Master Sync)
  - Drive vs Gemini comparison
  - Delta analysis
  - Workflow triggering
  - Error handling
- Configure 5-minute polling schedule
- Set up observability and logging
- Configure error notifications (Slack)
- Test end-to-end orchestration

**Phase 6: MCP Integration** ⏳ PENDING
- Set up Kestra MCP server
- Create custom MCP facade for kb.ask() and kb.add()
- Configure routing through Kestra
- Test ChatGPT integration
- Test VS Code integration

**Phase 7: Testing & Validation** ⏳ PENDING
- End-to-end testing of query flow
- End-to-end testing of ingestion flow
- Test push notifications vs polling
- Test error handling and recovery
- Performance testing (latency, throughput)
- Create "Gold Set" for evaluation

**Phase 8: Production Deployment** ⏳ PENDING
- Deploy all workflows to production
- Enable push notifications
- Activate Kestra scheduling
- Turn on MCP server
- Monitor system health

**Current Status**: Phase 2 (Google Drive Setup) - Requirements documentation updated, ready to proceed to OAuth setup and Phase 3.