---
id: codex-showcase
title: Codex Showcase & Output Modes
parent: index
status: published
tags: [codex, showcase, pipeline, system-capabilities, outputs]
---

# Codex Showcase & Compiler Output Modes

Boris is a deterministic, graph-aware Markdown documentation compiler built in Zig. This page chronicles Codex’s core contributions to the compiler's codebase and showcases **all 5 major output formats** supported by the system.

***

## 1. The Codex Story: Co-Authoring in Zig

Developing a compiler in Zig 0.16.0 requires strict manual memory management, explicit pointer control, and clean type-casting. Codex operated as the core implementation partner under human steering, implementing several high-friction compiler sub-systems:

### Core Contributions of Codex

* **AST Parser Construction:** Codex implemented the module that parses markdown into a custom, memory-efficient Abstract Syntax Tree (AST). It handles inline lists, tag extraction, and metadata normalization using Zig's `std.mem.TokenIterator`.
* **Arena Allocation Management:** To prevent memory leaks, Codex structured the compilation passes around Zig's `std.heap.ArenaAllocator`. The entire compiled graph is loaded and verified in a single memory arena that is cleanly freed at process exit, keeping the compiler's Peak RSS under **180 MB** even on thousands of pages.
* **Deterministic Caching Engine:** Codex built the content-addressing hashing engine for `--incremental` builds. It computes the SHA-256 hash of each page's AST and skips the HTML render phase if the hash matches the existing rendered file, achieving a **2.7× build speedup**.
* **Strict Graph Validator:** Codex wrote the validation routines that build the parent-child graph, detecting circular dependencies (`ECYCLE`) or dangling references (`EPARENTMISSING`) during graph creation, failing loudly instead of publishing broken navigation.

***

## 2. Showcase: The 5 Compiler Output Modes

Boris is designed around the **"One Content Tree, Multiple Outputs"** principle. The same input Markdown source compiles into five distinct target shapes.

Below are the exact commands and output formats available in the system:

---

### Output Mode 1: Static HTML (`--html-dir`)

Assembles layout templates and page content into beautiful, standalone, framework-free HTML.

* **Build Command:**
  ```bash
  ./bin/boris \
    --input site/content \
    --theme site/theme \
    --layout-rule default id:index site/theme/layouts/home.html \
    --html-dir dist
  ```
* **Sample Compiled Output (`dist/index.html`):**
  ```html
  <!DOCTYPE html>
  <html lang="en">
  <head>
    <meta charset="UTF-8">
    <title>Boris: The Content Exit Hatch</title>
    <link rel="stylesheet" href="assets/css/field-guide.css">
  </head>
  <body>
    <header class="site-header">
      <nav class="site-nav">
        <ul><li class="active"><a href="index.html">The Field Guide</a></li></ul>
      </nav>
    </header>
    <main class="site-content">
      <h1>The Content Exit Hatch</h1>
      <p>A deterministic Zig compiler...</p>
    </main>
  </body>
  </html>
  ```

---

### Output Mode 2: JSON IR (`--no-rag` / `--out`)

Outputs a machine-readable JSON Intermediate Representation (IR) of the validated content graph, ideal for headless integration.

* **Build Command:**
  ```bash
  ./bin/boris --input site/content --no-rag --out .boris
  ```
* **Sample Compiled Output (`.boris/index.json`):**
  ```json
  {
    "id": "index",
    "title": "The Content Exit Hatch",
    "status": "published",
    "tags": ["boris", "build-week"],
    "parent": null,
    "body_raw": "# Boris: The Content Exit Hatch...",
    "rendered_html": "<h1>Boris: The Content Exit Hatch</h1>...",
    "outgoing_links": [
      { "target_id": "pipeline", "type": "wiki" },
      { "target_id": "migration-evidence", "type": "wiki" }
    ],
    "incoming_links": [
      { "source_id": "pipeline", "type": "parent" }
    ]
  }
  ```

---

### Output Mode 3: RAG Chunks (`--rag` / `--rag-dir`)

Partitions the content tree into semantic text chunks optimized for ingest by vector databases or embedding pipelines.

* **Build Command:**
  ```bash
  ./bin/boris --input site/content --rag --rag-dir rag
  ```
* **Sample Chunk File (`rag/pipeline_chunk_00.txt`):**
  ```text
  ---
  source_id: pipeline
  chunk_index: 0
  tags: pipeline, outputs
  ---
  # One Content Tree, Several Outputs
  
  The core path is intentionally small:
  discovery → graph validation → Apex rendering → HTML, JSON IR, RAG, Context
  ```

---

### Output Mode 4: Context Bundle (`--context` / `--context-dir`)

Compiles the entire content repository into a single, unified markdown file. Perfect for feeding directly into LLM prompts or chat assistant contexts.

* **Build Command:**
  ```bash
  ./bin/boris --input site/content --context --context-dir context
  ```
* **Sample Context Bundle (`context/repository-context.md`):**
  ```markdown
  # REPOSITORY CONTEXT BUNDLE
  Generated: 2026-07-19
  
  ---
  FILE: site/content/index.md (ID: index)
  ---
  # Boris: The Content Exit Hatch
  A deterministic Zig documentation compiler...
  
  ---
  FILE: site/content/pipeline.md (ID: pipeline)
  ---
  # One Content Tree, Several Outputs...
  ```

---

### Output Mode 5: llms.txt (`--llms` / `--llms-path`)

Generates a standard `llms.txt` navigation manifest file, enabling AI agents and web crawlers to quickly explore and read the site's contents.

* **Build Command:**
  ```bash
  ./bin/boris --input site/content --llms --llms-path dist/llms.txt
  ```
* **Sample Manifest (`dist/llms.txt`):**
  ```text
  # Boris Field Guide
  > A deterministic, graph-aware Markdown documentation compiler built in Zig.
  
  ## Primary Page Index
  
  * [The Content Exit Hatch](index.html) - Main landing proof site.
  * [The Pipeline](pipeline.html) - Markdown in, multiple explicit outputs out.
  * [Evidence & Benchmarks](migration-evidence.html) - Performance benchmarks and dogfood audits.
  * [How Boris Was Built](build-week.html) - AI collaboration story with Codex & GPT.
  * [The Agent Roster](agent-archive.html) - Rolldown credit of synthetic collaborators.
  ```
