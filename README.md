<div align="center">

# Genesise

**A self-organizing, AI-maintained knowledge base that lives entirely on your machine.**

_Inspired by [Andrej Karpathy's LLM Wiki](https://gist.github.com/karpathy) concept._

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
![Works with Cline](https://img.shields.io/badge/Works%20with-Cline-blueviolet)
![Works with Claude Code](https://img.shields.io/badge/Works%20with-Claude%20Code-orange)
![pip install genesise](https://img.shields.io/badge/pip%20install-genesise-brightgreen)
![Privacy First](https://img.shields.io/badge/Privacy-Local%20Only-blue)

[Quick Start](#quick-start) · [How It Works](#how-it-works) · [CLI Reference](#cli-reference) · [Agent Commands](#agent-commands) · [Privacy & Security](#privacy--security)

</div>

---

## Overview

Drop any file into a folder. Tell your AI agent to process it. Come back later and ask a question — the agent retrieves the answer from _your own documents_, not from its training data.

No vector databases. No embedding models. No servers. No API keys for retrieval. Just Markdown files, a rules engine, and an AI agent that builds and queries the graph for you — across sessions, across tools, with full privacy.

> Works with **Cline** (VS Code) and **Claude Code** (terminal). Use either or switch freely.

---

## Features

- **Universal ingestion** — PDF, Word, Excel, images, CSV, code, plain text
- **Auto-linked graph** — nodes connect automatically via `[[WikiLinks]]`; contradictions between sources are flagged
- **RAG without a vector DB** — 7-step retrieval protocol using HyDE, cluster pre-filtering, tiered reads, and graph traversal
- **Scales cleanly** — discipline cluster index keeps query cost flat at 50, 200, or 500 nodes
- **Smart gap-fill** — uses the model's trained knowledge by default; external web search available as opt-in
- **Privacy-first** — clearance levels (`public / internal / confidential / external`), query sanitization, GDPR-inspired data principles
- **Session-persistent** — pick up exactly where you left off; `gns sync` handles additions, updates, and deletions
- **Two tools, one graph** — identical rules for Cline (`.clinerules`) and Claude Code (`CLAUDE.md`), same files underneath

---

## System Requirements

| Dependency                      | Platform           | Purpose                                          | How to check                |
| ------------------------------- | ------------------ | ------------------------------------------------ | --------------------------- |
| **Python 3.11+**                | All                | `gns` CLI — sync, lint, rename, and other tools   | `python --version`          |
| **PowerShell 5.0+**             | Windows only       | Read `.docx`, `.xlsx` files                      | `$PSVersionTable.PSVersion` |
| **poppler-utils** (`pdftotext`) | Linux/Mac fallback | PDF text extraction if native read fails         | `pdftotext -v`              |
| **unzip**                       | Linux/Mac          | Read `.docx` / `.xlsx` XML                       | `unzip -v`                  |

> **Windows users:** PowerShell ships with Windows 10/11 — no action needed.
> **Linux/Mac users:** `sudo apt install poppler-utils` or `brew install poppler` for PDF fallback.
> Claude Code reads PDFs natively; `pdftotext` is only a fallback for edge cases.

---

## Quick Start

**Prerequisites:** [Cline](https://marketplace.visualstudio.com/items?itemName=saoudrizwan.claude-dev) (VS Code) or [Claude Code](https://docs.anthropic.com/en/docs/claude-code) (CLI), with any LLM API key configured.

```bash
# 1. Install the CLI
pip install genesise

# 2. Create and enter your knowledge base directory
mkdir my-knowledge-base
cd my-knowledge-base

# 3. Initialize the workspace
gns init
```

`gns init` creates the folder structure, index files, and writes `bootstrap.md` into the directory. No cloning required.

Then, in your agent's chat panel, run:

```
Read bootstrap.md and execute Phase 2 and Phase 3.
```

The agent generates the rules engine (`CLAUDE.md` / `.clinerules`) and confirms when ready.

> **Already initialized?** Re-running `gns init` is safe — it skips existing folders and index files. Re-running bootstrap Phase 2/3 regenerates only the rules files.

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

```bash
# 1. Drop new or updated files into 01_raw_inputs/ alongside existing ones

# 2. Run sync — detects changes, handles deletions, reports what needs agent attention
gns sync

# 3. If gns sync reports NEW or UPDATED files, tell your agent
Process new data

# 4. Keep querying as normal
Query the graph: How does the new paper relate to my earlier research notes?
```

> `gns sync` uses SHA-256 hashing to detect changes — it never re-processes unchanged files, and it fully cascades deletions (removes cross-references, registry rows, and master index links) without needing the LLM.

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

## CLI Reference

Install once, run anywhere inside a workspace:

```bash
pip install genesise
```

The CLI is named `gns`. Running `gns` with no arguments shows help.

---

### `gns init [PATH]`

Scaffold a new workspace. Safe to re-run — existing folders and index files are not overwritten.

```
gns init [PATH] [OPTIONS]

Arguments:
  PATH    Directory to initialize. Defaults to current directory.

Options:
  -f, --force    Overwrite existing index files.
```

**Creates:**

| Path | Description |
| --- | --- |
| `01_raw_inputs/` | Drop source files here |
| `02_nodes/` | Generated knowledge nodes |
| `03_indexes/` | Retrieval indexes and config |
| `04_synthesis/` | Cross-domain reports |
| `03_indexes/master_index.md` | Root Map of Content (MOC) |
| `03_indexes/node_registry.md` | Primary retrieval index — one row per node |
| `03_indexes/cluster_index.md` | Discipline pre-filter for large graphs |
| `03_indexes/input_manifest.md` | Source file tracking with SHA-256 hashes |
| `03_indexes/query_log.md` | Append-only query history |
| `03_indexes/source_config.md` | Gap-fill mode and external source settings |
| `bootstrap.md` | Agent setup instructions — give this to your agent after `gns init` |

> `retrieval_protocol.md`, `CLAUDE.md`, and `.clinerules` are generated by the agent when it reads `bootstrap.md`, not by `gns init`.

---

### `gns sync`

Detect changes in `01_raw_inputs/` and update the graph indexes. Runs without the LLM — reports which files need agent processing.

```
gns sync [OPTIONS]

Options:
  --json    Output results as JSON instead of formatted text.
```

**What it does:**

1. Computes SHA-256 hashes for all files in `01_raw_inputs/`
2. Compares against `input_manifest.md` to classify each file:
   - **NEW** — not in manifest
   - **UPDATED** — hash changed
   - **DELETED** — in manifest but no longer on disk
   - **UNCHANGED** — hash matches
3. For **deleted** files: cascades the removal — updates every node that links to the deleted node, removes the registry row, decrements discipline cluster counts, removes the manifest row, and updates `master_index.md`
4. For **updated** files: updates the SHA-256 and `date_added` in the manifest
5. Scans all nodes for broken WikiLinks and reports the count

**Output (text mode):** summary table of counts, list of new/updated files, broken link count.

After `gns sync` reports NEW or UPDATED files, run `Process new data` in your agent to ingest them.

---

### `gns lint`

Validate graph integrity. Exits with code 1 if any errors are found.

```
gns lint [OPTIONS]

Options:
  --fix    Auto-fix table rows. (Not yet implemented.)
```

**Checks performed:**

| Check | What it validates |
| --- | --- |
| **YAML — opening marker** | Each node starts with `---` |
| **YAML — closing marker** | Frontmatter has a closing `---` |
| **YAML — syntax** | Frontmatter parses as valid YAML |
| **YAML — mandatory fields** | `summary`, `date_added`, and `clearance` are present |
| **Table columns** | All data rows in `node_registry.md` and `cluster_index.md` have the same column count as the header |
| **WikiLinks** | Every `[[link]]` in `connections:` and `contradicts:` points to an existing node in `02_nodes/` |

---

### `gns list`

Display all nodes grouped by discipline as a formatted table.

```
gns list [OPTIONS]

Options:
  -d, --discipline TEXT    Filter by discipline (substring match, case-insensitive).
  -c, --clearance TEXT     Filter by clearance level (exact match, case-insensitive).
```

**Output columns:** `#` · `Title` · `Type` · `Clearance` · `Summary`

Clearance is color-coded: green = public, yellow = internal, red = confidential, blue = external.

---

### `gns flag-stale`

Audit all nodes for staleness based on `last_verified` date.

```
gns flag-stale [OPTIONS]

Options:
  -s, --stale-only    Show only stale nodes (last verified > 6 months ago).
```

**Staleness thresholds:**

| Status | Condition |
| --- | --- |
| `STALE` | `last_verified` > 180 days ago |
| `AGING` | `last_verified` 90–180 days ago |
| `CURRENT` | `last_verified` < 90 days ago |
| `UNKNOWN` | No `last_verified` field present |

**Output:** nodes grouped by status category, each showing file, title, discipline, and last verified date.

---

### `gns verify NODE`

Stamp `last_verified: <today>` on a node without changing its content. Safe to run on current nodes.

```
gns verify NODE

Arguments:
  NODE    Node filename stem or full filename (e.g. my_node or my_node.md).
          Accepts case-insensitive fuzzy matching if no exact match is found.
```

---

### `gns rename OLD NEW`

Rename a node file and cascade the change everywhere in the graph.

```
gns rename OLD_NAME NEW_NAME

Arguments:
  OLD_NAME    Current node filename stem (without .md).
  NEW_NAME    New node filename stem (without .md).
```

**Cascade operations:**

1. Updates the `title:` YAML field to the title-cased version of `NEW_NAME`
2. Replaces every `[[OLD_NAME]]` WikiLink in all other nodes with `[[NEW_NAME]]`
3. Updates the row in `node_registry.md`
4. Updates the row in `input_manifest.md`
5. Updates the link in `master_index.md`
6. Deletes the old `.md` file

**Output:** confirmation with old → new filename and count of cross-references updated.

---

### `gns summary`

Print a health and coverage snapshot of the graph. No arguments.

```
gns summary
```

**Output sections:**

| Section | Contents |
| --- | --- |
| **Node counts by type** | Table of node types and counts |
| **Node counts by discipline** | Table of disciplines and counts |
| **Node counts by clearance** | Table of clearance levels and counts |
| **Staleness** | Count and list of nodes older than 180 days |
| **Query statistics** | Total queries, queries with gaps, top 5 keywords |
| **Coverage assessment** | Best-covered disciplines, thin areas (single-node disciplines), gap-query flags |

---

## Agent Commands

Tell these phrases to your agent in the chat panel. They require the LLM and follow the rules defined in `CLAUDE.md` / `.clinerules`.

| Command | What it does |
| --- | --- |
| `Process new data` | Ingest files from `01_raw_inputs/`, create nodes, update all indexes |
| `Query the graph: [question]` | Retrieve and reason — up to 8 nodes, gap-fill if needed |
| `Query the graph [deep]: [question]` | Same, up to 15 nodes — use for complex cross-domain questions |
| `Synthesize across domains` | Cross-discipline report; inherits highest source clearance |
| `Resolve contradiction: [A] vs [B]` | Read both nodes, classify conflict, write resolution |
| `Search external: [topic]` | Force web search (requires `gap_fill_mode: external` in `source_config.md`) |
| `Compress node: [name]` | Rewrite node body as 10-bullet list; YAML frontmatter untouched |
| `Set clearance: [name] to [level]` | Update node clearance; flags affected synthesis reports |
| `Merge nodes: [A] into [B]` | Combine two duplicate/overlapping nodes; cascades all cross-references |
| `Sync graph` | Run `gns sync`, then process any NEW/UPDATED files with the agent |
| `Lint graph` | Run `gns lint` and report results |
| `List nodes` | List all nodes in the graph |

---

## Directory Structure

```
.
├── src/genesise/               ← genesise CLI package (pip install genesise)
│   ├── main.py                 ← Typer app, command registration
│   ├── console.py              ← platform-aware Rich console (UTF-8 on Windows)
│   ├── engine/                 ← workspace detection, hashing, atomic writes, manifest/registry I/O
│   │   ├── workspace.py        ← find_workspace(), require_workspace()
│   │   ├── nodes.py            ← YAML parsing, field updates, WikiLink replace/remove
│   │   ├── hashing.py          ← SHA-256 file hashing
│   │   ├── atomic.py           ← .tmp + os.replace() safe writes
│   │   ├── manifest.py         ← ManifestEntry dataclass, read/write input_manifest.md
│   │   └── registry.py         ← RegistryEntry dataclass, read/write node_registry.md
│   └── commands/               ← one module per CLI command
│       ├── init.py
│       ├── sync.py
│       ├── lint.py
│       ├── list_nodes.py
│       ├── flag_stale.py
│       ├── verify.py
│       ├── rename.py
│       └── summary.py
├── 01_raw_inputs/              ← drop your files here (gitignored)
├── 02_nodes/                   ← generated knowledge nodes (gitignored)
├── 03_indexes/                 ← retrieval indexes and config (gitignored)
│   ├── retrieval_protocol.md   ← 7-step retrieval logic, loaded on demand (agent-generated)
│   ├── node_registry.md        ← one row per node — the primary retrieval index
│   ├── cluster_index.md        ← discipline pre-filter, keeps queries fast at scale
│   ├── input_manifest.md       ← source file tracking for sync and change detection
│   ├── query_log.md            ← append-only query history
│   ├── master_index.md         ← human-readable table of contents
│   └── source_config.md        ← gap-fill mode and external source settings
├── 04_synthesis/               ← cross-domain reports (gitignored)
├── .clinerules                 ← rules engine for Cline (gitignored, agent-generated)
├── CLAUDE.md                   ← rules engine for Claude Code (gitignored, agent-generated)
├── pyproject.toml              ← package definition for genesise
├── .gitignore
└── bootstrap.md                ← agent setup instructions (written by gns init, gitignored)
```

> All user data is gitignored. `.clinerules`, `CLAUDE.md`, and `bootstrap.md` are generated artifacts — only `src/` needs to be committed (for contributors). End users install via `pip install genesise` and never need to clone.

---

## Node Format

Every file in `02_nodes/` is a Markdown file with a typed YAML frontmatter block. The linter enforces `summary`, `date_added`, and `clearance` as mandatory fields.

```yaml
---
title: ""
type: ""          # research_paper | strategy | codebase | transcript | abstract_concept | dataset | synthesis | external
discipline: ""
clearance: ""     # public | internal | confidential | external
tags: []
keywords: []      # specific terms and entities — secondary retrieval signal
summary: ""       # ONE sentence — mandatory; primary retrieval signal
assumptions: []
connections: []   # [[WikiLink]] format — related nodes
contradicts: []   # [[WikiLink]] format — conflicting nodes
source: ""
confidence: ""    # high | medium | low
date_added: ""    # set once, never changed
last_verified: "" # updated by gns verify, sync, compress, or resolve
---
```

WikiLinks use the node filename stem without the `.md` extension: `[[my_node]]`.

---

## Index File Formats

All indexes are plain Markdown tables. The CLI reads and writes them directly.

### `node_registry.md`

| File | Title | Type | Discipline | Clearance | Tags | Summary |
| --- | --- | --- | --- | --- | --- | --- |

One row per node. This is the primary retrieval index scanned during Step 2 of the retrieval protocol.

### `cluster_index.md`

| Discipline | Node Count | Coverage Summary |
| --- | --- | --- |

One row per discipline. Used in Step 1 to narrow the search space before scanning the full registry.

### `input_manifest.md`

| Source File | Node File | Date Added | SHA-256 |
| --- | --- | --- | --- |

One row per source file. `gns sync` reads this to detect new, updated, and deleted files.

### `query_log.md`

| Date | Query | Mode | Nodes Hit | Confidence | Gaps |
| --- | --- | --- | --- | --- | --- |

Append-only. Every agent query appends one row. `gns summary` reads this for keyword analysis.

---

## Privacy & Security

### Clearance Levels

| Level | Meaning | External search |
| --- | --- | --- |
| `public` | No restrictions | Safe to use directly |
| `internal` | Stays within the graph | Must be abstracted first |
| `confidential` | Sensitive content | Blocks external search entirely |
| `external` | Sourced from outside | Always `confidence: low` |

Synthesis reports automatically inherit the **highest** clearance of any source node.

### Gap-Fill Modes

Set `gap_fill_mode` in `03_indexes/source_config.md`:

| Mode | Behaviour | Data leaves machine? |
| --- | --- | --- |
| `parametric` _(default)_ | Model answers from trained knowledge | Never |
| `external` | Searches open-access sources + any enabled institutional sources | Yes — sanitized |
| `none` | Reports the gap only | Never |

### External Search Sources

When `gap_fill_mode: external`, the agent queries sources in priority order.

**Open-access (always available):**

| Source | Coverage | API |
| --- | --- | --- |
| Wikipedia | Encyclopedic / factual | Free, no key |
| ArXiv | CS, physics, math, biology preprints | Free, no key |
| PubMed | Biomedical and life sciences | Free, no key |
| Semantic Scholar | Cross-discipline academic search | Free, no key |
| DuckDuckGo | General web | Free, no key |

**Institutional (uncomment in `source_config.md` when you have access):**

| Source | Coverage | Access |
| --- | --- | --- |
| IEEE Xplore | Engineering, electronics, computer science | API key or institutional VPN |
| Elsevier / ScienceDirect | Broad sciences | API key or institutional VPN |
| MDPI | Open-access multidisciplinary journals | API key or institutional VPN |
| Springer | Broad sciences and engineering | API key or institutional VPN |

> **VPN tip:** If your institution provides VPN access, connecting before running a query unlocks paywalled full-text on IEEE, Elsevier, and Springer without needing a personal API key. Tell the agent `"I'm on my institution VPN"` and it will attempt institutional sources before falling back to DuckDuckGo.

### Query Sanitization

When `external` mode is enabled, every search query goes through three gates before leaving the machine:

1. **Clearance check** — any `confidential` node in context aborts the search
2. **Abstraction** — internal names, codenames, employee names, and financial figures are forbidden in queries and must be rewritten to their generic concept
   - `"Project Orion SSO failure"` → `"Single Sign-On implementation failure analysis"`
   - `"Q3 Helios revenue shortfall"` → `"revenue forecasting gap analysis techniques"`
3. **Fallback** — if a term can't be safely abstracted, the agent falls back to `parametric` automatically

### GDPR-Inspired Principles

| Principle | How it's applied |
| --- | --- |
| **Data minimisation** | Extract concepts, not verbatim source text |
| **Purpose limitation** | Clearance level governs what each node can be used for |
| **Accuracy** | `last_verified` tracks staleness; nodes older than 6 months are flagged |
| **Right to erasure** | Deletion cascades to all references — no orphaned links or registry rows |
| **No unnecessary external transmission** | `parametric` is the default; `external` requires explicit opt-in |

---

## Troubleshooting

**Bootstrap ran but the workspace looks empty**
The agent may have confirmed too early. Run `List nodes` — if it returns nothing, re-run bootstrap. The idempotency rule ensures existing data is never overwritten.

**`gns sync` marks everything as UPDATED even though files haven't changed**
The manifest was written with file sizes (old format) and the sync engine now expects SHA-256 hashes. Fix: run `Process new data` on the affected files to rewrite their manifest rows with correct hashes, or manually update the SHA-256 column in `03_indexes/input_manifest.md`.

**PDF won't read / comes back garbled**
Claude reads PDFs natively. If a file fails, ask the agent: `"The file [name] is unreadable — please ask me to paste the content."` For scanned PDFs (image-only), vision extraction is used automatically but quality depends on scan resolution.

**Word or Excel file fails on Mac/Linux**
The `unzip` command must be installed: `sudo apt install unzip` (Linux) or it ships with macOS by default. If the XML extracted is blank, the `.docx` may use a non-standard internal structure — paste the content manually.

**`gns` command not found**
Python's scripts directory must be on your PATH. On Windows: check that Python was added to PATH during installation, or run `pip show genesise` to find the install location and add its `Scripts/` folder to PATH. On Mac/Linux: `export PATH="$HOME/.local/bin:$PATH"`.

**Institutional sources return 401 / no results**
Check that the API key is set in `03_indexes/source_config.md` under `ieee_api_key:`, `elsevier_api_key:`, or `springer_api_key:`. Keys are institution-specific — obtain them from your library's database access page. If on VPN without a key, MDPI and PubMed still work (no key required).

**Node registry or cluster index got corrupted**
The engine writes to a `.tmp` file before overwriting the real file. If an index looks broken, check for a leftover `.tmp` file in `03_indexes/` — it may contain the last good write. Rename it to replace the corrupted file, then run `gns lint` to verify.

**`Process new data` keeps asking about duplicates for every file**
The duplicate check compares core keywords against the registry. If your files share a lot of common terminology (e.g. many papers on the same topic), you'll get frequent prompts. Answer "new node" once and the agent will link them via `connections:` rather than merging. Use `Merge nodes` later if you decide consolidation makes sense.

**Agent ignores the rules / doesn't follow the protocol**
`CLAUDE.md` (Claude Code) and `.clinerules` (Cline) must exist in the workspace root — both are gitignored and generated by bootstrap. If they're missing, re-run bootstrap (safe to do on an existing workspace).

---

## vs. Karpathy's Original LLM Wiki

| | Karpathy's LLM Wiki | Genesise |
| --- | --- | --- |
| Note creation | You write manually | Agent extracts automatically |
| Structure | Freeform Markdown | Typed YAML schema |
| Graph | None | Bidirectional links + contradiction tracking |
| Retrieval | Ad-hoc | 7-step protocol with HyDE and cluster pre-filter |
| Scale | Degrades | Flat cost via cluster index |
| Gap fill | None | Parametric (default) or sanitized external |
| Privacy | None | Clearance levels + query sanitization |
| Sync | Manual | Diff-based auto-sync with SHA-256 change detection |

---

## License

[MIT](LICENSE)
