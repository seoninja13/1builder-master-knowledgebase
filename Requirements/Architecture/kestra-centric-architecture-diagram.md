# Kestra-Centric RAG Architecture

## Complete System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE LAYER                             │
│                                                                          │
│  ┌──────────────┐                                                       │
│  │   ChatGPT    │  (User asks questions or requests content ingestion) │
│  │  (via MCP)   │                                                       │
│  └──────┬───────┘                                                       │
│         │                                                                │
└─────────┼────────────────────────────────────────────────────────────────┘
          │
          │ ALL operations route through Kestra
          ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    KESTRA - CENTRAL ORCHESTRATOR                         │
│                         (The "Brain")                                    │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  • Receives ALL requests (queries + ingestion)                  │   │
│  │  • Logs every operation (timestamp, user, status)               │   │
│  │  • Routes to appropriate n8n workflow                           │   │
│  │  • Tracks execution status and metrics                          │   │
│  │  • Handles errors and retry logic                               │   │
│  │  • Provides complete audit trail                                │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                 │
│  │  Workflow A  │  │  Query Flow  │  │  Ingestion   │                 │
│  │ Master Sync  │  │   Routing    │  │   Routing    │                 │
│  │ (5-min poll) │  │              │  │              │                 │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘                 │
└─────────┼─────────────────┼─────────────────┼──────────────────────────┘
          │                 │                 │
          │                 │                 │
          ▼                 ▼                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      n8n - EXECUTION LAYER                               │
│                         (The "Worker")                                   │
│                                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                 │
│  │  Workflow B  │  │  Workflow C  │  │  Workflow D  │                 │
│  │    Smart     │  │   Query      │  │   Content    │                 │
│  │  Ingestion   │  │   Engine     │  │ Acquisition  │                 │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘                 │
│         │                 │                 │                           │
│         │                 │                 │                           │
└─────────┼─────────────────┼─────────────────┼───────────────────────────┘
          │                 │                 │
          │                 │                 │
          ▼                 ▼                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    STORAGE & INTELLIGENCE LAYERS                         │
│                                                                          │
│  ┌─────────────────────────┐      ┌─────────────────────────┐          │
│  │    Google Drive         │      │  Google Gemini          │          │
│  │  (Source of Truth)      │      │  File Search            │          │
│  │                         │      │  (AI Index)             │          │
│  │  • All files stored     │      │  • Auto chunking        │          │
│  │  • Single flat folder   │      │  • Auto embedding       │          │
│  │  • Push notifications   │      │  • Auto indexing        │          │
│  │  • Metadata tags        │      │  • RAG retrieval        │          │
│  └─────────────────────────┘      └─────────────────────────┘          │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

## Query Flow (Kestra-Centric)

```
User: "How do we handle SEO for windows in Sacramento?"
    │
    ▼
ChatGPT (MCP Client)
    │ kb.ask(question)
    ▼
Kestra (Central Orchestrator)
    ├─ Log: [2025-01-17 10:30:15] Query received from User
    ├─ Route: Query → n8n Workflow C
    └─ Track: Execution ID #12345
    │
    ▼
n8n Workflow C (Query Engine)
    ├─ Intent Classification: Vertical=SEO, Geo=Sacramento
    ├─ Filter Construction: metadata.vertical='SEO' AND metadata.geo='Sacramento'
    └─ Query Gemini File Search API
    │
    ▼
Gemini File Search
    ├─ Retrieve relevant chunks (filtered by metadata)
    ├─ Generate answer with citations
    └─ Return: "Based on 3 documents..."
    │
    ▼
n8n Workflow C
    └─ Format response with citations
    │
    ▼
Kestra (Central Orchestrator)
    ├─ Log: [2025-01-17 10:30:17] Query completed (2.1s)
    ├─ Metrics: Success, Latency=2100ms, Documents=3
    └─ Return response to ChatGPT
    │
    ▼
ChatGPT
    └─ Display answer to user
```

**Total Latency**: ~2.1 seconds (Kestra overhead: ~200ms)

---

## Ingestion Flow - Path 1: Programmatic (via ChatGPT)

```
User: "Index this YouTube video: https://youtube.com/watch?v=..."
    │
    ▼
ChatGPT (MCP Client)
    │ kb.add(url)
    ▼
Kestra (Central Orchestrator)
    ├─ Log: [2025-01-17 10:35:00] Ingestion request received
    ├─ Route: Content Acquisition → n8n Workflow D
    └─ Track: Execution ID #12346
    │
    ▼
n8n Workflow D (Content Acquisition)
    ├─ Fetch YouTube transcript
    ├─ Upload to Google Drive (OAuth credentials)
    └─ Upload to Gemini File Search (immediate indexing)
    │
    ▼
Gemini File Search
    ├─ Auto-chunk transcript
    ├─ Auto-generate embeddings
    └─ Auto-index content
    │
    ▼
n8n Workflow D
    └─ Report success to Kestra
    │
    ▼
Kestra (Central Orchestrator)
    ├─ Log: [2025-01-17 10:35:45] Ingestion completed (45s)
    ├─ Metrics: Success, File=youtube_transcript.txt, Size=15KB
    └─ Return success to ChatGPT
    │
    ▼
ChatGPT
    └─ "Content indexed successfully! Ready for queries."
```

---

## Ingestion Flow - Path 2: Automatic (Google Drive Upload)

```
User manually uploads file to Google Drive
    │
    ▼
Google Drive
    └─ Detects file change
    │
    ▼
Google Drive Push Notification
    └─ POST to n8n webhook: https://n8n.srv972609.hstgr.cloud/webhook/drive-notifications
    │
    ▼
n8n Webhook (Workflow D)
    ├─ Receive notification (resourceId only)
    ├─ Call Google Drive Changes API
    ├─ Filter for relevant changes
    ├─ Fetch file metadata
    └─ Notify Kestra
    │
    ▼
Kestra (Workflow A: Master Sync)
    ├─ Log: [2025-01-17 10:40:00] New file detected via push notification
    ├─ Route: Ingestion → n8n Workflow B
    └─ Track: Execution ID #12347
    │
    ▼
n8n Workflow B (Smart Ingestion)
    ├─ Download file from Google Drive (service account)
    ├─ Extract metadata with AI (Vertical, Geo, Intent)
    └─ Upload to Gemini File Search with metadata
    │
    ▼
Gemini File Search
    ├─ Auto-chunk content
    ├─ Auto-generate embeddings
    └─ Auto-index with metadata tags
    │
    ▼
n8n Workflow B
    └─ Report success to Kestra
    │
    ▼
Kestra (Central Orchestrator)
    ├─ Log: [2025-01-17 10:40:15] Ingestion completed (15s)
    └─ Metrics: Success, File=strategy_doc.pdf, Size=2.3MB
```

**Total Time**: ~15 seconds from upload to searchable

---

## Authentication Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    AUTHENTICATION STRATEGY                   │
└─────────────────────────────────────────────────────────────┘

Service Account (READ + Gemini)
    ├─ Credentials: builder-master-knowldgebase-79a4f60f66e1.json
    ├─ Email: id-builder-masterknowldge@builder-master-knowldgebase.iam.gserviceaccount.com
    ├─ Permissions:
    │   ├─ Google Drive: READ-only (shared folder)
    │   ├─ Gemini API: Full access
    │   └─ Vertex AI API: Full access
    └─ Use Cases:
        ├─ Workflow A: Read Drive file list
        ├─ Workflow B: Download files from Drive
        └─ Workflow C: Query Gemini API

OAuth Credentials (WRITE to Drive)
    ├─ Authentication: OAuth 2.0 (user account)
    ├─ Permissions: Google Drive Full READ/WRITE
    └─ Use Cases:
        └─ Workflow D: Upload acquired content to Drive
```

---

## Why Kestra-Centric Architecture?

### 1. **Observability**
- Every operation logged with timestamp, user, and status
- Track query patterns, response times, and error rates
- Monitor system health in real-time

### 2. **Error Handling**
- Centralized retry logic
- Failure notifications (Slack alerts)
- Automatic recovery procedures

### 3. **Audit Trail**
- Complete history of all operations
- Compliance and debugging support
- Track who did what and when

### 4. **Routing Logic**
- Intelligent workflow routing based on request type
- Can add new workflows without changing client code
- A/B testing and gradual rollouts

### 5. **Metrics & Analytics**
- Track success rates, latency, throughput
- Identify bottlenecks and optimization opportunities
- Data-driven decision making

### 6. **Workflow Coordination**
- Orchestrate complex multi-step processes
- Manage dependencies between workflows
- Ensure consistency across operations

---

## Trade-offs

| Aspect | Direct (ChatGPT → n8n) | Kestra-Centric (ChatGPT → Kestra → n8n) |
|--------|------------------------|------------------------------------------|
| **Latency** | ~1.9s | ~2.1s (+200ms) |
| **Observability** | ❌ None | ✅ Complete |
| **Error Tracking** | ❌ Limited | ✅ Comprehensive |
| **Audit Trail** | ❌ None | ✅ Full history |
| **Routing Flexibility** | ❌ Hardcoded | ✅ Dynamic |
| **Metrics** | ❌ None | ✅ Detailed |

**Verdict**: The 200ms latency overhead is acceptable for the significant observability and control benefits.

