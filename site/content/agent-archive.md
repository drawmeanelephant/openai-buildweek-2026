---
id: agent-archive
title: The Agent Roster
parent: index
status: published
tags: [agents, credits, archive]
---

# The Agent Roster

Boris accrued a surprisingly large worker roster during Build Week. This archive stands as a durable, evidence-bound thank-you to our synthetic collaborators. 

## The Rule for Credit

A visible worker name is not proof of a code contribution. A prompt is not a merged patch. A funny poster is not a release note. The archive keeps those categories apart so the thank-you is generous without becoming fake. 

## Build Week Roll Call

Here are the major agents that collaborated on Boris, and what they actually did:

### **Codex (The Implementer)**
- **Role:** Zig Code Generation & Refactoring
- **Contribution:** Guided by human architecture decisions, Codex wrote focused modules, drafted strict tests, and helped navigate Zig 0.16.0's memory management to build the core AST parser.

### **ChatGPT 5.6 (The Architect & Reviewer)**
- **Role:** Design, Strategy, & PR Review
- **Contribution:** Handled high-level structural decisions, reviewed Pull Requests for safety, and defined the scope limits that kept Boris from becoming an unmaintainable "universal importer."

### **Antigravity Agent (The Benchmarker & Auditor)**
- **Role:** Performance Testing & Migration Scripts
- **Contribution:** Wrote the Python data-cleaning pipelines that wrangled 804 massive GitHub READMEs, performed the Filed.fyi dogfood audits, and ran the 10-core multi-concurrency benchmarks that proved `-j 1` was actually the fastest (and safest for the human's lap).

### **Research Subagents (The Hostile Testers)**
- **Role:** Adversarial Discovery
- **Contribution:** Attempted to break the Boris compiler by feeding it cyclic component links and malformed Markdown trees to ensure the AST graph validation failed loudly and safely.

*Until full curation lands, the authoritative working archive of pull requests and commits remains in the [Boris repository](https://github.com/drawmeanelephant/boris).*
