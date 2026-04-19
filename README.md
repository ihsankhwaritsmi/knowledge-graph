<div align="center">

# 🧠 Knowledge Graph

**A self-organizing, AI-maintained knowledge base that lives entirely on your machine.**

_Inspired by [Andrej Karpathy's LLM Wiki](https://gist.github.com/karpathy) concept._

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
![Works with Cline](https://img.shields.io/badge/Works%20with-Cline-blueviolet)
![Works with Claude Code](https://img.shields.io/badge/Works%20with-Claude%20Code-orange)
![No Install](https://img.shields.io/badge/Install-None%20Required-brightgreen)
![Privacy First](https://img.shields.io/badge/Privacy-Local%20Only-blue)

[Quick Start](#quick-start) · [How It Works](#how-it-works) · [Commands](#commands) · [Privacy & Security](#privacy--security)

</div>

---

## What Is This?

Drop any file into a folder. Tell your AI agent to process it. Come back later and ask a question — the agent retrieves the answer from _your own documents_, not from its training data.

No vector databases. No embedding models. No servers. No API keys for retrieval. Just Markdown files, a rules engine, and an AI agent that builds and queries the graph for you — across sessions, across tools, with full privacy.

> Works with **Cline** (VS Code) and **Claude Code** (terminal). Use either or switch freely.

---

## ✨ Features

- 📥 **Universal ingestion** — PDF, Word, Excel, images, CSV, code, plain text — read using tools already on your OS (see [System Requirements](#system-requirements))
- 🕸️ **Auto-linked graph** — nodes connect automatically via `[[WikiLinks]]`; contradictions between sources are flagged
- 🔍 **RAG without a vector DB** — 7-step retrieval protocol using HyDE, cluster pre-filtering, tiered reads, and graph traversal
- 🧩 **Scales cleanly** — discipline cluster index keeps query cost flat at 50, 200, or 500 nodes
- 🌐 **Smart gap-fill** — uses the model's trained knowledge by default; external web search available as opt-in
- 🔒 **Privacy-first** — clearance levels (`public / internal / confidential / external`), query sanitization, GDPR-inspired data principles
- 🔄 **Session-persistent** — pick up exactly where you left off; `Sync graph` handles additions, updates, and deletions
- 🛠️ **Two tools, one graph** — identical rules for Cline (`.clinerules`) and Claude Code (`CLAUDE.md`), same files underneath

---

## System Requirements

No Python packages, npm modules, or servers needed. The system uses tools already present on your OS.

| Dependency                      | Platform           | Purpose                                  | How to check                |
| ------------------------------- | ------------------ | ---------------------------------------- | --------------------------- |
| **Python 3**                    | All                | `Sync graph` scripted diff               | `python --version`          |
| **PowerShell 5.0+**             | Windows only       | Read `.docx`, `.xlsx`; get file sizes    | `$PSVersionTable.PSVersion` |
| **poppler-utils** (`pdftotext`) | Linux/Mac fallback | PDF text extraction if native read fails | `pdftotext -v`              |
| **unzip**                       | Linux/Mac          | Read `.docx` / `.xlsx` XML               | `unzip -v`                  |

> **Windows users:** PowerShell ships with Windows 10/11 — no action needed.
> **Linux/Mac users:** `sudo apt install poppler-utils` or `brew install poppler` for PDF fallback.
> Claude Code reads PDFs natively; `pdftotext` is only a fallback for edge cases.

---

## Quick Start

**Prerequisites:** [Cline](https://marketplace.visualstudio.com/items?itemName=saoudrizwan.claude-dev) (VS Code) or [Claude Code](https://docs.anthropic.com/en/docs/claude-code) (CLI), with any LLM API key configured.

```bash
git clone https://github.com/ihsankhwaritsmi/knowledge-graph
cd knowledge-graph
```

Then, in your agent's chat panel, run:

```
Read bootstrap.md and execute the instructions.
```

That's it. The agent builds the full workspace — folders, indexes, and rules engine — and confirms when ready.

> **Already initialized?** Re-running bootstrap on an existing workspace is safe — the agent will create any missing folders and index files but will not overwrite existing ones. Your nodes and indexes are preserved.

**First time — ingest your files:**

```
# 1. Drop files into 01_raw_inputs/ — anything goes (PDF, Word, Excel, images, CSV, code, text)

# 2. Tell your agent
Process new data

# 3. Ask questions
Query the graph: What are the key assumptions in the papers I uploaded?
Query the graph [deep]: What connections exist between my research notes and the dataset analysis?
```

**Adding or updating files later:**

```
# 1. Drop new or updated files into 01_raw_inputs/ alongside existing ones

# 2. Run sync — detects new, updated, and deleted files automatically
Sync graph

# 3. Keep querying as normal
Query the graph: How does the new paper relate to my earlier research notes?
```

> `Sync graph` runs a Python diff against the manifest so it never re-processes unchanged files. New files get full node creation; updated files get their node rewritten; deleted files have their references cleaned up across the graph.

---

## How It Works

```
01_raw_inputs/                    You drop files here
      │
      ▼
 File Reading                     PDF → native vision  ·  .docx/.xlsx → built-in OS tools
      │                           images → vision  ·  everything else → direct read
      ▼
Extraction Protocol               Scientific · Strategic · Code · Transcripts · Datasets
      │
      ▼
  02_nodes/                       Structured Markdown nodes with YAML frontmatter
      │                           auto-linked · contradiction-flagged · clearance-tagged
      ▼
  03_indexes/                     node_registry · cluster_index · input_manifest · query_log
      │
      ▼
 Query issued ──► HyDE ──► Cluster filter ──► Registry scan ──► Tiered read ──► Traversal
                                                                                     │
                                                             ┌───────────────────────┘
                                                             ▼
                                                       Gap detected?
                                                       │         │
                                               Parametric    External (opt-in,
                                               model know-   sanitized, clearance-
                                               ledge (default) checked)
                                                             │
                                                             ▼
                                             Structured answer + query_log entry
```

---

## Retrieval Protocol

Retrieval logic lives in `03_indexes/retrieval_protocol.md` and loads **on demand** — the rules file stays lean for every non-query session.

| Step                   | What happens                                                                          | Cost           |
| ---------------------- | ------------------------------------------------------------------------------------- | -------------- |
| **0 — HyDE**           | Generates a hypothetical ideal-answer summary as a second match signal                | 0 file reads   |
| **1 — Cluster filter** | Narrows to 1–3 disciplines via `cluster_index.md`                                     | 1 file read    |
| **2 — Registry scan**  | `grep` pre-scan first (zero token cost), then score matched rows; assesses confidence | 1 file read    |
| **3 — Tiered read**    | YAML block (30 lines) first; full file only if confirmed relevant                     | Up to 8 or 15  |
| **4 — Traversal**      | Follows `connections:` / `contradicts:` up to 2 hops                                  | Within budget  |
| **5 — Gap fill**       | Parametric (default) or sanitized external search (opt-in)                            | 0–3 curl calls |
| **6 — Answer + log**   | Structured response; appends row to `query_log.md`                                    | —              |

Confidence is assessed after Step 2 and determines the path:

```
3+ matches → SUFFICIENT  →  local graph only
1–2 matches → PARTIAL    →  local graph + gap fill
0 matches  → INSUFFICIENT →  gap fill only
```

---

## Commands

| Command                              | What it does                                                                   |
| ------------------------------------ | ------------------------------------------------------------------------------ |
| `Process new data`                   | Ingest files from `01_raw_inputs/`, create nodes, update all indexes           |
| `Query the graph: [question]`        | Retrieve and reason — up to 8 nodes, gap-fill if needed                        |
| `Query the graph [deep]: [question]` | Same, up to 15 nodes — use for complex cross-domain questions                  |
| `Synthesize across domains`          | Cross-discipline report; inherits highest source clearance                     |
| `Sync graph`                         | Scripted Python diff vs manifest — handles new, updated, deleted, broken links |
| `Lint graph`                         | Check all nodes for broken YAML, malformed table rows, and orphaned WikiLinks  |
| `Resolve contradiction: [A] vs [B]`  | Read both nodes, classify conflict, write resolution                           |
| `Search external: [topic]`           | Force web search (requires `gap_fill_mode: external` in config)                |
| `Compress node: [name]`              | Rewrite node body as 10-bullet list; YAML untouched                            |
| `Set clearance: [name] to [level]`   | Update node clearance; flags affected synthesis reports                        |
| `Merge nodes: [A] into [B]`          | Combine two duplicate/overlapping nodes; cascades all cross-references         |
| `List nodes`                         | Compact table of all nodes grouped by discipline — no node files read          |
| `Show graph summary`                 | Health snapshot: node counts, coverage gaps, stale nodes, top queries          |

---

## Directory Structure

```
.
├── 01_raw_inputs/              ← drop your files here (gitignored)
├── 02_nodes/                   ← generated knowledge nodes (gitignored)
├── 03_indexes/                 ← retrieval indexes and config (gitignored)
│   ├── retrieval_protocol.md   ← 7-step retrieval logic, loaded on demand
│   ├── node_registry.md        ← one row per node — the primary retrieval index
│   ├── cluster_index.md        ← discipline pre-filter, keeps queries fast at scale
│   ├── input_manifest.md       ← source file tracking for sync and change detection
│   ├── query_log.md            ← append-only query history
│   ├── master_index.md         ← human-readable table of contents
│   └── source_config.md        ← gap-fill mode and external source settings
├── 04_synthesis/               ← cross-domain reports (gitignored)
├── .clinerules                 ← rules engine for Cline (gitignored, generated)
├── CLAUDE.md                   ← rules engine for Claude Code (gitignored, generated)
├── .gitignore
└── bootstrap.md                ← one-time setup — the committed source of truth
```

> All user data is gitignored. `.clinerules` and `CLAUDE.md` are generated artifacts — `bootstrap.md` is the only file that needs to be committed.

---

## Node Structure

Every node in `02_nodes/` is a Markdown file with a typed YAML header:

```yaml
---
title: ""
type: "" # research_paper | strategy | codebase | transcript | abstract_concept | dataset | synthesis | external
discipline: ""
clearance: "" # public | internal | confidential | external
tags: []
keywords: [] # specific terms and entities — secondary retrieval signal
summary: "" # ONE sentence — mandatory, primary retrieval signal
assumptions: []
connections: [] # [[WikiLink]] format
contradicts: [] # [[WikiLink]] format
source: ""
confidence: "" # high | medium | low
date_added: "" # set once, never changed
last_verified: "" # updated on sync, compress, or resolve
---
```

---

## Privacy & Security

### Clearance Levels

| Level          | Meaning                | External search                    |
| -------------- | ---------------------- | ---------------------------------- |
| `public`       | No restrictions        | ✅ Safe to use directly            |
| `internal`     | Stays within the graph | ⚠️ Must be abstracted first        |
| `confidential` | Sensitive content      | ❌ Blocks external search entirely |
| `external`     | Sourced from outside   | Always `confidence: low`           |

Synthesis reports automatically inherit the **highest** clearance of any source node.

### Gap-Fill Modes

Set in `03_indexes/source_config.md`:

| Mode                     | Behaviour                                                        | Data leaves machine? |
| ------------------------ | ---------------------------------------------------------------- | -------------------- |
| `parametric` _(default)_ | Model answers from trained knowledge                             | ❌ Never             |
| `external`               | Searches open-access sources + any enabled institutional sources | ⚠️ Yes — sanitized   |
| `none`                   | Reports the gap only                                             | ❌ Never             |

### External Search Sources

When `gap_fill_mode: external`, the agent queries sources in priority order. Open-access sources are always available; institutional sources require a subscription or institutional VPN.

**Open-access (always available):**

| Source           | Coverage                             | API          |
| ---------------- | ------------------------------------ | ------------ |
| Wikipedia        | Encyclopedic / factual               | Free, no key |
| ArXiv            | CS, physics, math, biology preprints | Free, no key |
| PubMed           | Biomedical and life sciences         | Free, no key |
| Semantic Scholar | Cross-discipline academic search     | Free, no key |
| DuckDuckGo       | General web                          | Free, no key |

**Institutional (uncomment in `source_config.md` when you have access):**

| Source                   | Coverage                                   | Access                       |
| ------------------------ | ------------------------------------------ | ---------------------------- |
| IEEE Xplore              | Engineering, electronics, computer science | API key or institutional VPN |
| Elsevier / ScienceDirect | Broad sciences                             | API key or institutional VPN |
| MDPI                     | Open-access multidisciplinary journals     | API key or institutional VPN |
| Springer                 | Broad sciences and engineering             | API key or institutional VPN |

> **VPN tip:** If your institution provides VPN access, connecting before running a query unlocks paywalled full-text on IEEE, Elsevier, and Springer without needing a personal API key. Tell the agent `"I'm on my institution VPN"` and it will attempt institutional sources before falling back to DuckDuckGo.

### Query Sanitization

When `external` mode is enabled, every search query goes through three gates before leaving the machine:

1. **Clearance check** — any `confidential` node in context → search aborted
2. **Abstraction** — internal names, codenames, employee names, and financial figures are forbidden in queries; they must be rewritten to their generic concept
   - `"Project Orion SSO failure"` → `"Single Sign-On implementation failure analysis"`
   - `"Q3 Helios revenue shortfall"` → `"revenue forecasting gap analysis techniques"`
3. **Fallback** — if a term can't be safely abstracted, the agent falls back to `parametric` automatically

### GDPR-Inspired Principles

| Principle                                | How it's applied                                                         |
| ---------------------------------------- | ------------------------------------------------------------------------ |
| **Data minimisation**                    | Extract concepts, not verbatim source text                               |
| **Purpose limitation**                   | Clearance level governs what each node can be used for                   |
| **Accuracy**                             | `last_verified` tracks staleness; nodes older than 6 months are flagged  |
| **Right to erasure**                     | Deletion cascades to all references — no orphaned links or registry rows |
| **No unnecessary external transmission** | `parametric` is the default; `external` requires explicit opt-in         |

---

## vs. Karpathy's Original LLM Wiki

|               | Karpathy's LLM Wiki | This system                                      |
| ------------- | ------------------- | ------------------------------------------------ |
| Note creation | You write manually  | Agent extracts automatically                     |
| Structure     | Freeform Markdown   | Typed YAML schema                                |
| Graph         | None                | Bidirectional links + contradiction tracking     |
| Retrieval     | Ad-hoc              | 7-step protocol with HyDE and cluster pre-filter |
| Scale         | Degrades            | Flat cost via cluster index                      |
| Gap fill      | None                | Parametric (default) or sanitized external       |
| Privacy       | None                | Clearance levels + query sanitization            |
| Sync          | Manual              | Diff-based auto-sync                             |

---

## Troubleshooting

**Bootstrap ran but the workspace looks empty**
The agent may have confirmed too early. Run `List nodes` — if it returns nothing, re-run bootstrap. The idempotency rule ensures existing data is never overwritten.

**`Sync graph` marks everything as UPDATED even though files haven't changed**
The manifest was written with file sizes (old format) and the sync script now expects SHA-256 hashes. Fix: run `Process new data` on the affected files to rewrite their manifest rows with correct hashes, or manually update the SHA-256 column in `03_indexes/input_manifest.md`.

**PDF won't read / comes back garbled**
Claude reads PDFs natively. If a file fails, ask the agent: `"The file [name] is unreadable — please ask me to paste the content."` For scanned PDFs (image-only), vision extraction is used automatically but quality depends on scan resolution.

**Word or Excel file fails on Mac/Linux**
The `unzip` command must be installed: `sudo apt install unzip` (Linux) or it ships with macOS by default. If the XML extracted is blank, the `.docx` may use a non-standard internal structure — paste the content manually.

**`Sync graph` Python script fails with `FileNotFoundError`**
Python 3 must be on your PATH: `python --version` or `python3 --version`. On Windows, ensure Python was added to PATH during installation. The script is written to `%TEMP%\kg_sync.py` (Windows) or `/tmp/kg_sync.py` (Mac/Linux).

**Institutional sources return 401 / no results**
Check that the API key is set in `03_indexes/source_config.md` under `ieee_api_key:`, `elsevier_api_key:`, or `springer_api_key:`. Keys are institution-specific — obtain them from your library's database access page. If on VPN without a key, MDPI and PubMed still work (no key required).

**Node registry or cluster index got corrupted**
The atomic write protocol in the rules engine writes to a `.tmp` file before overwriting the real file. If an index looks broken, check for a leftover `.tmp` file in `03_indexes/` — it may contain the last good write. Rename it to replace the corrupted file, then run `Lint graph` to verify.

**Agent ignores the rules / doesn't follow the protocol**
`CLAUDE.md` (Claude Code) and `.clinerules` (Cline) must exist in the workspace root — both are gitignored and generated by bootstrap. If they're missing, re-run bootstrap (safe to do on an existing workspace).

---

## License

[MIT](LICENSE)
