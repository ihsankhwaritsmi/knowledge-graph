# Omni-Disciplinary Knowledge Graph

A self-organizing personal knowledge base powered by the [Cline](https://github.com/cline/cline) autonomous agent in VS Code. Inspired by Andrej Karpathy's "LLM Wiki" concept.

No vector databases. No graph databases. No servers. Just Markdown files, a rules engine, and an AI that builds and queries the graph for you.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## The Idea

You accumulate knowledge across a dozen domains — papers you read, meeting notes, code you studied, datasets you explored, ideas you had. It lives in scattered files and fades from memory.

This system turns all of it into a connected, queryable knowledge graph that an AI agent maintains and reasons over. Drop in a file. Tell Cline to process it. Come back later and ask a question — Cline retrieves the relevant context from your own graph before answering, not from its training data.

It works for anything: a research project, a hobby deep-dive, a startup, a novel you're writing, a personal reading log, competitive analysis, a D&D campaign. Any domain, any mix of domains.

---

## How It Works End to End

```
Clone repo
    ↓
Tell Cline: "Read cline_bootstrap.md and execute the instructions."
    ↓
Cline builds your workspace (folders, indexes, rules engine)
    ↓
Drop files into 01_raw_inputs/ — PDFs, notes, CSVs, code, transcripts, anything
    ↓
Tell Cline: "Process new data"
    ↓
Cline extracts concepts, writes structured nodes, links related ideas, flags contradictions
    ↓
Close VS Code. Come back tomorrow. Start a new Cline session.
    ↓
Ask anything: "Query the graph: [your question]"
    ↓
Cline reads your graph, reasons across it, falls back to the web if needed
    ↓
You get a grounded answer from your own accumulated knowledge
    ↓
Keep adding files. Keep asking. Keep building.
```

---

## Prerequisites

- [VS Code](https://code.visualstudio.com/)
- [Cline extension](https://marketplace.visualstudio.com/items?itemName=saoudrizwan.claude-dev) with any LLM API key (Anthropic, OpenAI, Gemini, local via Ollama, etc.)

That's it. No installs, no databases, no configuration beyond what the bootstrap generates. Drop any file type — PDF, Word, Excel, image, CSV, code, plain text — and Cline reads it using the tools already on your OS.

---

## Getting Started

```bash
git clone <your-repo-url>
cd <your-repo-folder>
```

Open the folder in VS Code, open the Cline chat panel, and run:

```
Read cline_bootstrap.md and execute the instructions.
```

Cline builds everything. You'll get a confirmation when it's ready.

---

## Directory Structure

```
.
├── 01_raw_inputs/              # Drop your files here (never committed to git)
├── 02_nodes/                   # Generated knowledge graph nodes (never committed)
├── 03_indexes/                 # All index and config files (never committed)
│   ├── retrieval_protocol.md   ← full retrieval logic, loaded on demand
│   ├── input_manifest.md       ← source file tracking and change detection
│   ├── query_log.md            ← append-only history of every query run
│   ├── cluster_index.md        ← discipline-level pre-filter for large graphs
│   ├── node_registry.md        ← one row per node, primary retrieval index
│   ├── master_index.md         ← human-readable table of contents
│   └── source_config.md        ← external source settings
├── 04_synthesis/               # Cross-domain reports (never committed)
├── .clinerules                 # Lean rules engine, loaded every session
├── .gitignore                  # Your data never gets committed
└── cline_bootstrap.md          # One-time setup directive
```

Everything under `01_raw_inputs/`, `02_nodes/`, `03_indexes/`, and `04_synthesis/` is gitignored — your personal knowledge never leaves your machine.

---

## Commands

### `Process new data`
Scans `01_raw_inputs/` for new files, extracts structured knowledge into nodes, links related concepts, and updates all indexes including the manifest and query log.

### `Query the graph: [question]`
Standard query — reads up to 8 nodes. Retrieves from the local graph first, falls back to external sources if needed. Returns a confidence label, sources consulted, and any gaps.

```
Query the graph: What are the common failure modes across the architecture papers I uploaded?
Query the graph: What's the strongest counterargument to my current thesis?
Query the graph: What did I learn about fermentation that applies to this new recipe idea?
```

### `Query the graph [deep]: [question]`
Same as above but reads up to 15 nodes. Use for complex, cross-domain, or comprehensive questions where breadth matters more than speed.

### `Synthesize across domains`
Finds nodes from different disciplines and writes a report applying the principles of one to the problems of another. Runs in deep mode automatically. Adds backlinks to all source nodes.

### `Sync graph`
Run this at the start of any session where `01_raw_inputs/` may have changed. Diffs the folder against the manifest and handles every case:
- **New** → processes and creates a node
- **Updated** → re-extracts, rewrites the node, updates connections and `last_verified`
- **Deleted** → removes the node, cleans up all references in other nodes
- **Unchanged** → skipped
- **Broken links** → scans all nodes for `[[WikiLinks]]` pointing to deleted files and reports them

### `Resolve contradiction: [node A] vs [node B]`
Reads both nodes, identifies the exact conflicting claims, searches the graph for related evidence, and writes a reasoned resolution. Classifies the conflict as outdated, contextual, or genuinely open. Updates both nodes and optionally creates a synthesis document for unresolved questions.

### `Search external: [topic]`
Forces a search against Wikipedia, ArXiv, and DuckDuckGo regardless of local graph state. Findings can be saved as nodes.

### `Compress node: [node name]`
Rewrites a verbose node body as a compact bullet-point list. YAML stays untouched. Updates `last_verified`.

### `Update README`
Writes a `README.md` in the workspace root — a living snapshot of what's in the graph: disciplines, all nodes, all sources, synthesis reports, and recent queries.

---

## How Retrieval Works

The retrieval logic lives in `03_indexes/retrieval_protocol.md` and is only loaded when a query runs — keeping `.clinerules` lean for every other session. No embeddings, no vector math — the LLM does the relevance judgment.

**Step 0 — HyDE**
Generates a hypothetical one-sentence summary of what the ideal answer node would say. Used as a second match signal alongside raw keywords — surfaces nodes that are semantically relevant even when exact words don't match.

**Step 1 — Cluster Pre-filter**
Reads `cluster_index.md` — one row per discipline with a 2–3 sentence coverage summary. Narrows candidates to 1–3 disciplines before touching the full registry. At 300 nodes this means scoring ~20 rows instead of 300.

**Step 2 — Registry Scan**
Reads `node_registry.md` and scores each row against both the raw query and the HyDE summary. Assesses confidence: sufficient / partial / insufficient.

**Step 3 — Tiered Node Read**
Reads the YAML block only (lines 1–30) for each candidate — summary, tags, and the `keywords` field. Full file read only if confirmed relevant. Budget: 8 nodes normal, 15 nodes deep mode. Nodes with a stale `last_verified` date are flagged in the answer.

**Step 4 — Connection Traversal**
Follows `connections:` and `contradicts:` links up to 2 hops — only when the linked node's registry row also scores relevant.

**Step 5 — External Search**
Triggered when confidence is partial or insufficient. Hits Wikipedia, ArXiv, and DuckDuckGo via `curl` with two queries: one from raw keywords, one from the HyDE summary. Significant findings auto-saved as `confidence: low` nodes.

**Step 6 — Answer + Log**
Returns: confidence label · answer · sources · gaps. Appends one row to `query_log.md` for every query run.

---

## Node Structure

Every node is a Markdown file with a YAML header:

```yaml
title: ""
type: ""          # research_paper | strategy | codebase | transcript | abstract_concept | dataset | synthesis | external
discipline: ""
tags: []          # broad categories
keywords: []      # specific terms, entities, acronyms — secondary retrieval signal
summary: ""       # one sentence, mandatory
assumptions: []
connections: []   # [[WikiLink]] to related nodes
contradicts: []   # [[WikiLink]] to conflicting nodes
source: ""
confidence: ""    # high | medium | low
date_added: ""    # set once, never changed
last_verified: "" # updated whenever the node is confirmed current
```

---

## License

[MIT](LICENSE)
