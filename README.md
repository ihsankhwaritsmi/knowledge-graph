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

That's it. No databases, no Python environments, no configuration files beyond what the bootstrap generates.

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
├── 01_raw_inputs/         # Drop your files here (never committed to git)
├── 02_nodes/              # Generated knowledge graph nodes (never committed)
├── 03_indexes/            # Retrieval indexes (never committed)
│   ├── cluster_index.md   ← discipline-level pre-filter, keeps queries fast at scale
│   ├── node_registry.md   ← one row per node, primary retrieval index
│   ├── master_index.md    ← human-readable table of contents
│   └── source_config.md   ← external source settings
├── 04_synthesis/          # Cross-domain reports (never committed)
├── .clinerules            # Rules engine Cline reads on every session
├── .gitignore             # Your data never gets committed
└── cline_bootstrap.md     # The one-time setup directive
```

Everything in `01_raw_inputs/`, `02_nodes/`, `03_indexes/`, and `04_synthesis/` is gitignored — your personal knowledge never leaves your machine.

---

## Commands

### `Process new data`
Scans `01_raw_inputs/` for new files, extracts structured knowledge into nodes, links related concepts across the graph, and updates all indexes.

### `Query the graph: [your question]`
Retrieves relevant nodes from your graph, reasons across them, and falls back to external sources if needed. Always returns a confidence label and lists exactly which sources it used.

```
Query the graph: What are the common failure modes across the three architecture papers I uploaded?
Query the graph: Based on my notes, what's the strongest counterargument to my current thesis?
Query the graph: What did I learn about fermentation last month that applies to this new recipe idea?
```

### `Synthesize across domains`
Finds nodes from different disciplines and writes a report applying the principles of one to the problems of another. Adds backlinks so source nodes know they contributed.

### `Search external: [topic]`
Forces a search against Wikipedia, ArXiv, and DuckDuckGo regardless of local graph state. Findings can be saved as nodes tagged `[EXTERNAL]`.

### `Compress node: [node name]`
Rewrites a verbose node body as a compact bullet-point list. YAML metadata stays untouched.

---

## How Retrieval Works

Queries use a 7-step protocol. No embeddings, no vector math — the LLM does the relevance judgment.

**Step 0 — HyDE (Hypothetical Document Expansion)**
Before reading any file, Cline internally drafts what the ideal answer node's summary would say. This becomes a second match signal alongside your raw keywords — finding nodes that are semantically relevant even when exact words don't match.

**Step 1 — Cluster Pre-filter**
Reads `cluster_index.md` — a small table with one row per discipline and a 2–3 sentence description of what that cluster covers. Narrows the search to 1–3 relevant disciplines before scanning the full registry. At 300 nodes, this means scoring 20 rows instead of 300.

**Step 2 — Registry Scan**
Reads `node_registry.md` and scores each row against both the raw query and the HyDE summary. Assesses confidence: sufficient / partial / insufficient.

**Step 3 — Tiered Node Read**
Reads only the YAML block (lines 1–25) of each candidate first. Opens the full file only if the summary confirms relevance. Hard cap: 8 node files per query.

**Step 4 — Connection Traversal**
Follows `connections:` and `contradicts:` links up to 2 hops — only when the linked node's registry row also scores relevant.

**Step 5 — External Search** (partial or insufficient only)
Hits Wikipedia, ArXiv, and DuckDuckGo via `curl` — no API keys needed. Fires two queries: one from your keywords, one from the HyDE summary. Significant findings are optionally auto-saved as low-confidence nodes.

**Step 6 — Structured Answer**
Every response: confidence label · concise answer · sources consulted · gaps identified.

---

## Working with PDFs and Large Datasets

| Platform | Command |
|---|---|
| macOS | `brew install poppler` |
| Linux | `sudo apt install poppler-utils` |
| Windows | install `pdftotext` via [Xpdf tools](https://www.xpdfreader.com/download.html) |
| All | Python with `pandas` for CSV sampling |

Cline invokes these automatically when it encounters binary files.

---

## License

[MIT](LICENSE)
