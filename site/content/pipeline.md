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
