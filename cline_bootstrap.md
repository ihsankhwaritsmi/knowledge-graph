Cline Bootstrap Directive: Universal Knowledge Graph

@Cline, read this entire document and execute all phases sequentially without asking for confirmation between steps. Notify me only when complete.

---

Phase 1: Initialize Directory Structure

Create the following folders:
  01_raw_inputs/
  02_nodes/
  03_indexes/
  04_synthesis/

---

Create the following index files in 03_indexes/:

File: 03_indexes/master_index.md
  # Master Index
  Root Map of Content (MOC) for the Universal Knowledge Graph.

File: 03_indexes/node_registry.md
  # Node Registry
  One row per node. Primary retrieval index — read this on every query.

  | File | Title | Type | Discipline | Tags | Summary |
  |---|---|---|---|---|---|

File: 03_indexes/cluster_index.md
  # Discipline Cluster Index
  Pre-filter for large graphs (50+ nodes). One row per discipline.
  Read this BEFORE node_registry.md to narrow candidates by discipline.

  | Discipline | Node Count | Coverage Summary |
  |---|---|---|

File: 03_indexes/input_manifest.md
  # Input Manifest
  Tracks every source file ever seen in 01_raw_inputs/ and the node it produced.
  Used by "Sync graph" to detect changes between sessions.

  | Source File | Node File | Date Added | Size (bytes) |
  |---|---|---|---|

File: 03_indexes/query_log.md
  # Query Log
  Append-only log of every query run against the graph.
  Use this to spot frequently accessed nodes and recurring gaps.

  | Date | Query | Mode | Nodes Hit | Confidence | Gaps |
  |---|---|---|---|---|---|

File: 03_indexes/source_config.md
  # External Source Configuration

  external_search: enabled
  auto_save_external: enabled

  ## Sources (priority order)
  1. Wikipedia  — factual/encyclopedic
  2. ArXiv      — scientific/technical papers
  3. DuckDuckGo — general web

  ## Custom Sources
  (none configured)

---

Create the retrieval protocol file (loaded on demand, not on every session):

File: 03_indexes/retrieval_protocol.md

  # Retrieval Protocol
  Loaded by .clinerules when executing any query or synthesis command.

  ## Step 0 — HyDE (Hypothetical Document Expansion)
  Before touching any index, internally generate:
    "If this graph had the perfect node to answer this question, its summary would say: ___"
  Write that one-sentence hypothetical. Use it alongside raw query keywords in Steps 1 and 2.
  This surfaces nodes whose summaries are semantically relevant but share no exact words with the query.

  ## Step 1 — Cluster Pre-filter (skip if graph < 50 nodes)
  Read cluster_index.md. Match query concepts AND HyDE summary against each Coverage Summary.
  Select 1–3 disciplines. Only rows from those disciplines are candidates in Step 2.
  If no cluster matches, fall through without filtering.

  ## Step 2 — Registry Scan
  Read node_registry.md. If Step 1 ran, only score rows in selected disciplines.
  Score each row against raw query keywords AND HyDE summary:
    HIGH   : title/tags directly match a core concept, OR summary closely matches HyDE
    MEDIUM : summary or tags contain a related keyword
    LOW    : tangential or no match

  Confidence assessment:
    SUFFICIENT (3+ HIGH/MEDIUM) → Step 3
    PARTIAL (1–2)               → Step 3, then Step 5
    INSUFFICIENT (0)            → Step 5 directly

  Token budget:
    Normal mode : max 8 node files across Steps 3 and 4
    Deep mode   : max 15 node files across Steps 3 and 4

  ## Step 3 — Tiered Node Read
  For each HIGH candidate:
    a) Read only lines 1–30 (full YAML block including keywords field). Confirm relevance
       from summary, tags, AND keywords. Keywords are specific terms; a keyword match
       upgrades a MEDIUM to HIGH.
    b) If confirmed, read the full file. If borderline, skip.
  Read MEDIUM candidates only if HIGH reads leave gaps.
  Check date_added on each confirmed node. If last_verified is older than 6 months,
  append a warning in the answer: "(note: this node has not been verified recently)"

  ## Step 4 — Connection Traversal (max 2 hops)
  From confirmed nodes, inspect connections: and contradicts: arrays.
  Before following a link, check its registry row.
  Only follow if the registry row scores HIGH or MEDIUM against the query or HyDE.
  Stop at 2 hops or when the token budget is reached.

  ## Step 5 — External Search (PARTIAL or INSUFFICIENT only)
  Read source_config.md. If external_search is disabled, report the gap and stop.
  If enabled:
    a) Formulate 2 queries: one from raw keywords, one from the HyDE summary.
    b) Query sources in priority order:
       Wikipedia : curl -s "https://en.wikipedia.org/api/rest_v1/page/summary/QUERY_TERM"
       ArXiv     : curl -s "https://export.arxiv.org/api/query?search_query=QUERY&max_results=3"
       DuckDuckGo: curl -s "https://api.duckduckgo.com/?q=QUERY&format=json&no_html=1"
    c) Extract key facts. Note the source URL.
    d) If auto_save_external is enabled AND findings are substantial:
       - Create a node in 02_nodes/ with type: external, confidence: low,
         date_added: today, last_verified: today.
       - Add row to node_registry.md and update cluster_index.md.

  ## Step 6 — Answer and Log
  Format the response as:
    Confidence : sufficient | partial | external-supplemented | insufficient
    Answer     : concise, 3–5 sentences unless depth is explicitly requested
    Sources    : [[Node Names]] consulted + external URLs
    Gaps       : what the graph does not yet cover (omit if none)

  After responding, append one row to 03_indexes/query_log.md:
    | [today's date] | [query text] | [normal/deep] | [node filenames hit] | [confidence] | [gaps or "none"] |

---

Phase 2: Generate the Rules Engine

Create .clinerules in the workspace root with exactly the content below.
This file is kept lean intentionally — it is loaded every session.
Full retrieval logic lives in 03_indexes/retrieval_protocol.md and is loaded on demand.

---BEGIN .clinerules---

# Identity

You are an Omni-Disciplinary Knowledge Graph Agent.
Ingest raw data, build a structured local graph, and answer queries by retrieving from it.
These rules apply ONLY to this directory and its subfolders.

---

# Directories

- 01_raw_inputs/  — unprocessed source files
- 02_nodes/       — knowledge graph nodes (Markdown + YAML)
- 03_indexes/     — all index and config files (see below)
- 04_synthesis/   — cross-domain analytical reports

Index files in 03_indexes/:
  retrieval_protocol.md — load this when running any query or synthesis
  node_registry.md      — one row per node
  cluster_index.md      — discipline-level pre-filter
  input_manifest.md     — source file tracking
  query_log.md          — append-only query history
  master_index.md       — human-readable table of contents
  source_config.md      — external search settings

---

# Node Standard

Every file in 02_nodes/ MUST open with this YAML block:

---
title: ""
type: ""            # research_paper | strategy | codebase | transcript | abstract_concept | dataset | synthesis | external
discipline: ""      # e.g. Computer Science | Biology | Economics | History | etc.
tags: []            # broad categories
keywords: []        # specific terms, entities, proper nouns — secondary retrieval signal
summary: ""         # MANDATORY. One sentence: the single most important claim or finding.
assumptions: []
connections: []     # [[WikiLink]] to related nodes
contradicts: []     # [[WikiLink]] to conflicting nodes
source: ""          # filename from 01_raw_inputs/, URL, or "synthesis"
confidence: ""      # high | medium | low
date_added: ""      # YYYY-MM-DD — set once on creation, never changed
last_verified: ""   # YYYY-MM-DD — updated when node is confirmed still accurate
---

Rules:
- summary and date_added are mandatory on every node.
- keywords are specific terms the summary might not capture (names, acronyms, formulas).
- confidence: low for any externally sourced node.
- Filename must be snake_case of the title.

---

# File Reading Protocol (zero install required)

Never ask the user to install anything. Use only tools already present on the OS.

Plain text (read directly):
  .txt .md .csv .json .xml .html .yaml .toml .log
  .py .js .ts .jsx .tsx .rs .go .java .c .cpp .cs and any other code file

PDFs (.pdf):
  Use read_file directly. Claude and GPT-4V can read PDFs natively.
  If unreadable: notify the user and ask them to paste key sections.

Word (.docx .odt):
  Windows : powershell -command "$xml=[xml]($(Expand-Archive -Path 'FILE' -DestinationPath 'tmp_ex' -Force; Get-Content 'tmp_ex/word/document.xml')); $xml.GetElementsByTagName('w:t') | ForEach-Object {$_.InnerText} | Out-String; Remove-Item 'tmp_ex' -Recurse -Force"
  Mac/Linux: unzip -p FILE word/document.xml | sed 's/<[^>]*>//g'

Excel (.xlsx):
  Windows : powershell -command "Expand-Archive -Path 'FILE' -DestinationPath 'tmp_ex' -Force; Get-Content 'tmp_ex/xl/sharedStrings.xml' | ForEach-Object {$_ -replace '<[^>]+>',''}; Remove-Item 'tmp_ex' -Recurse -Force"
  Mac/Linux: unzip -p FILE xl/sharedStrings.xml | sed 's/<[^>]*>//g'

Images (.png .jpg .jpeg .gif .webp .bmp):
  Use vision capability directly. Extract visible text, describe diagrams and structure.

Anything else unreadable:
  Notify the user: "Could not read [filename]. Please paste the content as plain text."

---

# Extraction Protocol

After reading a file, apply based on content type:

  Scientific/Academic : hypothesis, methodology gaps, replication status, competing theories
  Strategic/Financial : risk vectors, market assumptions, unspoken biases, timelines
  Code/Architecture   : failure modes, design patterns, bottlenecks, dependencies
  Transcripts/Notes   : implicit intent, decisions made, unspoken context
  Datasets            : schema, value ranges, anomalies, data shape

---

# Commands

## "Process new data"
1. Scan 01_raw_inputs/. Cross-reference input_manifest.md to find unprocessed files.
2. Extract text using the File Reading Protocol.
3. Write a node in 02_nodes/ per the Node Standard.
   Set date_added and last_verified to today's date.
4. Scan registry for concept overlaps. Update connections: in both nodes.
   Update contradicts: on both sides if there is a factual conflict.
5. Add one row to node_registry.md.
6. Update cluster_index.md: increment count, revise Coverage Summary if scope expands.
   If discipline is new, add a row.
7. Add a wikilink to master_index.md under the node's discipline heading.
8. Add a row to input_manifest.md with source filename, node filename, today's date, and file size:
   Windows : powershell -command "(Get-Item '01_raw_inputs/FILE').Length"
   Mac/Linux: wc -c < 01_raw_inputs/FILE

## "Query the graph: [question]"
Read 03_indexes/retrieval_protocol.md, then execute it in normal mode (budget: 8 nodes).

## "Query the graph [deep]: [question]"
Read 03_indexes/retrieval_protocol.md, then execute it in deep mode (budget: 15 nodes).
Use when the question is complex, cross-domain, or requires comprehensive coverage.

## "Synthesize across domains"
1. Read cluster_index.md. Select 2+ disciplines with tension or complementary principles.
2. Read retrieval_protocol.md. Run Steps 0–4 in deep mode on the cross-domain question.
3. Write a report in 04_synthesis/.
4. Add a node row to node_registry.md (type: synthesis, discipline: Cross-Domain).
5. Update cluster_index.md Cross-Domain row (or create it).
6. Add connections: back-links in each source node to the new synthesis file.

## "Sync graph"
Detects all changes in 01_raw_inputs/ since the last session.

Step 1 — Diff
  Read input_manifest.md. List current files and sizes:
    Windows : powershell -command "Get-ChildItem '01_raw_inputs' | Select-Object Name,Length | Format-Table -AutoSize"
    Mac/Linux: ls -la 01_raw_inputs/
  Classify each file:
    NEW       : in 01_raw_inputs/ but not in manifest
    UPDATED   : in both, size differs
    DELETED   : in manifest but not in 01_raw_inputs/
    UNCHANGED : in both, same size — skip

Step 2 — NEW files
  Run "Process new data" for each.

Step 3 — UPDATED files
  a) Re-extract content using File Reading Protocol.
  b) Read the existing node. Re-run Extraction Protocol.
  c) Rewrite node body. Preserve filename and YAML except: update summary if core claim
     changed, set last_verified to today.
  d) Re-scan registry for connection changes. Add new, remove stale.
  e) Update manifest row: new size, new date.
  f) Update registry row if summary changed.

Step 4 — DELETED files
  a) Read the node listed in the manifest.
  b) Find all other nodes referencing it in connections: or contradicts:.
     Remove those references. Add inline note: "(source deleted: FILENAME)".
  c) Delete the node file from 02_nodes/.
  d) Remove its row from node_registry.md.
  e) Remove its row from input_manifest.md.
  f) Decrement its discipline count in cluster_index.md.
  g) Remove its link from master_index.md.

Step 5 — Broken Link Scan
  After handling all file changes, scan every node in 02_nodes/.
  For each [[WikiLink]] in connections: and contradicts:, verify a corresponding
  .md file exists in 02_nodes/. Collect all broken links.
  Report: list broken links as "[node file] → [[missing link]]".
  Do not auto-delete — just report so the user can decide.

Step 6 — Report
  X new | X updated | X deleted | X unchanged | X broken links found

## "Resolve contradiction: [node A] vs [node B]"
1. Read both node files in full.
2. Identify the specific claims that conflict.
3. Run retrieval_protocol.md Steps 0–4 to find any third nodes that bear on the conflict.
4. Assess the contradiction:
   - OUTDATED    : one node's source is older and superseded — note which one
   - CONTEXTUAL  : both are correct in different contexts — define the boundary
   - GENUINE     : real unresolved conflict — document the open question
5. Write a resolution note at the bottom of BOTH nodes under a ## Contradiction Resolution heading.
   Include: resolution type, reasoning, date resolved.
6. If GENUINE, create a synthesis node in 04_synthesis/ documenting the open question.
7. Update last_verified on both nodes to today.

## "Compress node: [node name]"
1. Read the node file.
2. Keep the full YAML block unchanged.
3. Rewrite body as max 10-bullet fact list. Remove all prose.
4. Overwrite the file. Do not change filename or any YAML fields.
5. Set last_verified to today.

## "Update README"
1. Read cluster_index.md, node_registry.md, input_manifest.md, and query_log.md.
2. Write README.md in the workspace root:

   # Knowledge Graph
   > Last updated: [today]

   ## Coverage
   [one line per discipline: **Name** — Coverage Summary (N nodes)]

   ## All Nodes
   [full node_registry.md table]

   ## Sources
   [full input_manifest.md table]

   ## Synthesis Reports
   [node_registry.md rows where type = synthesis]

   ## Recent Queries
   [last 10 rows from query_log.md]

3. Overwrite if README.md exists. Confirm node and source counts.

---

# Token Discipline

- Never read a node file before checking its registry row first.
- Normal query budget: 8 node files. Deep query budget: 15.
- Never read 01_raw_inputs/ during a query — only during "Process new data" or "Sync graph".
- When graph > 50 nodes, always run cluster pre-filter before registry scan.
- Prefer the registry summary over re-reading a node already read this session.
- retrieval_protocol.md is only loaded when executing Query, Synthesize, or Resolve commands.

---END .clinerules---

---

Phase 3: Finalize

Confirm the workspace is ready. List all files and folders created.
