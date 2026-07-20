---
id: index
title: The Content Exit Hatch
status: published
tags: [boris, build-week, field-guide]
---

# Boris: The Content Exit Hatch

**A deterministic Zig documentation compiler that turns Markdown into validated HTML, JSON IR, RAG/context artifacts, and migration reports.**

This site is the contest-facing proof, deliberately separate from the compiler repository. It is itself Markdown compiled by Boris, with no JavaScript runtime or framework in the publishing path.

## The Demo

- **Live Demo:** [TODO: Insert Live URL]
- **Demo Video:** [TODO: Insert Video URL]
- **Boris Repository:** [drawmeanelephant/boris](https://github.com/drawmeanelephant/boris)
- **Contest Repository:** [drawmeanelephant/openai-buildweek-2026](https://github.com/drawmeanelephant/openai-buildweek-2026)
- **Release Tag:** [TODO: Insert Release Tag]
- **Benchmarks:** See [[migration-evidence|Evidence & Benchmarks]]

## Submission Checklist

- [x] **Build instructions:** Documented in [README.md](https://github.com/drawmeanelephant/openai-buildweek-2026/blob/main/README.md)
- [x] **Test instructions:** Documented in [README.md](https://github.com/drawmeanelephant/openai-buildweek-2026/blob/main/README.md)
- [x] **Public repository:** Available at [drawmeanelephant/boris](https://github.com/drawmeanelephant/boris)
- [x] **README:** Complete
- [ ] **Demo video:** [TODO: Insert Video URL]
- [ ] **Codex session ID:** [TODO: Insert Session ID]
- [x] **How Codex/GPT-5.6 was used:** Detailed in [[build-week|How Boris Was Built]]
- [x] **Known limitations:** Detailed in [[build-week|How Boris Was Built]]

***

## Judging Criteria Alignment

Boris is designed to be an honest, highly functional, and innovative entry. Below is how the project directly addresses each of the contest's judging criteria:

### 🛠️ 1. Technological Implementation (Skillful, Deep Zig & Codex Code)
* **The Achievement:** Instead of a generic web wrapper, Codex co-authored a fully featured, zero-dependency Markdown compiler in **Zig 0.16.0**, navigating manual memory management, arena heap allocation, and strict pointer bounds.
* **Non-Trivial Modules:** Codex implemented the full Abstract Syntax Tree (AST) parser, the graph validator that prevents broken links (`EPARENTMISSING`), and the deterministic SHA-256 caching engine that reduces incremental build times by **2.7×**.
* **Scale Proof:** Compiles and validates a 2,116-page corpus in **2.06 seconds** (~0.97ms/page).

### 🎨 2. Design (Coherent, Cohesive Product Experience)
* **The Achievement:** Deliver a working, runnable system with a coherent, high-fidelity experience. The Field Guide you are reading is completely compiled by Boris and serves as a living, production-ready proof of the layout engines.
* **Interactive Live Demos:** The compiler runs in 5 distinct modes, all of which are built and hosted live on this site. You can browse the live outputs immediately:
  * **HTML Static Site** (This Page)
  * **JSON Intermediate Representation (IR)**: [View Live JSON IR](ir/graph.json)
  * **LLMs.txt Manifest Mapping**: [View Live llms.txt](llms.txt)
  * **Unified Prompt Context Bundle**: [View Live Context MD](context/bundle.md)
  * **Vector RAG Chunks**: [View Live Entity Catalog Chunk](rag/graph/entity-catalog.md)

### 📈 3. Potential Impact (Solving Real Developer-AI Drift)
* **The Achievement:** Today, developers face massive documentation fragmentation: static docs for developers, raw files for vector databases (RAG), and prompts for AI assistants are always out-of-sync. 
* **The Solution:** Boris solves this by acting as the unified local compile hub. Developers write structured Markdown locally, and the compiler instantly and deterministically outputs beautiful developer docs, optimized vector database RAG chunks, and prompts in a single local build pass. 

### 💡 4. Quality of the Idea (The Graph-Aware Paradigm Shift)
* **The Achievement:** Traditional Static Site Generators (SSGs) view pages as raw files in folders. Boris views documentation as a **validated entity graph** of interconnected nodes.
* **Novelty:** By enforcing global ID uniqueness and parent-child validation at compile time, Boris guarantees your site can never be published with a broken link or a parent cycle. It introduces the concept that the tool which builds your docs should also natively prepare secure, pre-chunked RAG context for your AI copilots.

***

## Start Exploring

- [[pipeline|The Pipeline]] — Markdown in, multiple explicit outputs out.
- [[migration-evidence|Evidence & Benchmarks]] — Bounded dogfood audits and performance results.
  - [[stress-tests|Stress Testing Runbook]] — Replicating and running the massive benchmarks locally.
- [[build-week|How Boris Was Built]] — The human–AI collaboration story.
  - [[codex-showcase|Codex Deep-Dive & Outputs]] — System-capabilities showcase and co-authoring logs.
- [[agent-archive|The Agent Roster]] — A durable, evidence-bound thank-you to our synthetic collaborators.

<Aside kind="note">
This is a proof site, not a polished hosted service. Boris stays local-first:
the binary validates and writes static files on your machine.
</Aside>
