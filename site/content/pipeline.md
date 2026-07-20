---
id: pipeline
title: One Content Tree, Several Outputs
parent: index
status: published
tags: [pipeline, outputs]
---

# One Content Tree, Several Outputs

The core path is intentionally small:

```text
Markdown + frontmatter
       │
       ▼
discovery → graph validation → Apex rendering
       │
       ├── HTML site
       ├── JSON IR
       ├── RAG / context bundles
       └── migration reports
```

<div style="text-align: center; margin-block: 2rem;">
  <img src="assets/images/mediluna-compiler.png" alt="Mediluna feeding Markdown papers into a whimsical compiling machine while Boris the friendly elephant supervises happily." style="max-width: 450px; width: 100%; height: auto; border-radius: 12px; border: 1px solid var(--line); box-shadow: 0 4px 12px rgba(0,0,0,0.08);" />
  <p style="font-style: italic; color: var(--muted); margin-top: 0.5rem; font-size: 1rem; font-weight: 500;">“One single compile pass, and our expedition maps are ready!”</p>
</div>

The important part is not “five outputs” as a party trick. Each output comes
from the same resolved content graph, so a page ID, parent edge, and source
provenance do not need to be rediscovered from generated HTML.

## Structure fails loud

A Boris page can declare a parent, link another page, and include a shared
fragment. Those references are checked before publication. Broken structure
produces diagnostics instead of quietly publishing navigation that is wrong.

## Why the outputs stay separate

HTML is the default product output. IR, RAG, Context Bundles, and `llms.txt`
are explicit build modes so their artifacts and contracts remain inspectable.
That makes automation useful without turning a documentation site into an AI
service.
