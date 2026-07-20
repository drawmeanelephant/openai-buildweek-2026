---
id: index
title: The Content Exit Hatch
status: published
tags: [boris, build-week, field-guide]
---

# Boris: The Content Exit Hatch

### Your website shouldn’t be trapped inside someone else’s product.
### **Boris isn’t a static site generator. It’s an exit strategy for your content.**

Traditional systems want to lock you in. They bind your documentation to heavy framework runtimes, proprietary database structures, or complex JS bundlers. 

**Boris is a deterministic content compiler co-authored with OpenAI Codex in Zig 0.16.0.** It turns content from WordPress, Astro, Starlight, Obsidian, and local Markdown into standard local files that you own forever—then compiles them instantly into a zero-dependency static site, a structured semantic graph, and AI-ready training context.

An elephant never forgets where it put its data. Boris is the quiet elephant handing your website back to you in a box labeled **"Your Content"** 🐘📦.

<div style="text-align: center; margin-block: 2rem;">
  <img src="assets/images/mediluna-hero.jpg" alt="Mediluna, the Build Week expedition guide, walking happily along a forest trail." style="max-width: 400px; width: 100%; height: auto; border-radius: 12px; border: 1px solid var(--line); box-shadow: 0 4px 12px rgba(0,0,0,0.08);" />
  <p style="font-style: italic; color: var(--muted); margin-top: 0.5rem; font-size: 1rem; font-weight: 500;">“Come on. Let’s migrate your content.”</p>
</div>

***

<Aside kind="note">
🚪 **[Try a Migration Audit](migration-evidence)**
Explore how Boris-migration-lab converts actual WordPress, Astro, and Starlight sites, outputting detailed evidence reports that prove exactly what survived and what needs human review.
</Aside>

***

## 🚪 Migrate Anything. Own Everything.

Almost every modern tool says *"Import your site."* Boris says *"Audit your migration."*

Instead of silently failing or dropping content during conversion, Boris's **Migration Laboratories** treat migrations as an industrial, audited process. When you ingest a site, you receive a full **Evidence Report**:

* **WordPress WXR Labs:** Audits and converts complex posts, pages, categories, and local media attachments, resolving duplicate slug collisions and path sanitizations.
* **Astro & Starlight normalizers:** Recursively scans nested routing, cleanses MDX components, and parses Starlight frontmatter safely.
* **Review queues & Provenance:** Clearly outputs what survived, what changed, and what needs manual editorial review—preventing silent data loss.
* **Strict local sandboxing (`EASSET`):** Guarantees compiler safety by catching and blocking malicious path-traversal attacks (e.g. `../../../etc/passwd`) at compilation time.

***

## 🔄 One Input. Five Multi-Channel Outputs.

When you compile with Boris, you aren't just writing HTML pages. You are generating an **AI-ingestible knowledge graph**. From a single Markdown directory, Boris simultaneously and deterministically compiles:

1. **HTML Static Site (Zero-JS):** Beautiful, ultra-fast static developer documentation with zero runtime framework dependencies.
2. **JSON Intermediate Representation (IR):** A machine-readable JSON representation of your validated content graph ([ir/graph.json](ir/graph.json)) for headless pipelines.
3. **Unified Prompt Context Bundle:** A cohesive markdown file ([context/bundle.md](context/bundle.md)) containing the entire repo—perfect for feeding directly into LLM prompts.
4. **Vector RAG Chunks:** Pre-partitioned semantic text files ([rag/graph/entity-catalog.md](rag/graph/entity-catalog.md)) ready for direct ingestion into vector databases.
5. **AI Navigation Map (llms.txt):** A standard [llms.txt](llms.txt) manifest mapping for AI agents and web crawlers.

***

## 🛠️ Judging Criteria Alignment

Boris was built to be an honest, highly functional, and innovative entry for the OpenAI Build Week 2026.

### 🛠️ 1. Technological Implementation (Skillful Zig & Codex Code)
* **The Achievement:** Codex co-authored a fully featured, zero-dependency compiler in **Zig 0.16.0**, navigating manual memory management, arena heap allocation, and strict pointer bounds.
* **Non-Trivial Modules:** Codex implemented the full AST parser, the global graph validator that prevents broken links (`EPARENTMISSING`), and the deterministic SHA-256 caching engine that reduces incremental build times by **2.7×**.
* **Scale Proof:** Compiles and validates a 2,116-page structured corpus in **2.06 seconds** (~0.97ms/page) using a multi-threaded parallel build (`-j 8`) in ReleaseFast mode (`zig build -Doptimize=ReleaseFast`) on Apple M4 hardware (same-machine comparison).

### 🎨 2. Design (Coherent, Cohesive Product Experience)
* **The Achievement:** This Field Guide serves as a living, production-ready proof. It is completely compiled by Boris and showcases all five output formats live. 

### 📈 3. Potential Impact (Bridging Local Docs with AI Pipelines)
* **The Achievement:** Eliminates developer-AI documentation drift. Instead of maintaining separate static docs, vector files, and prompting contexts, Boris handles all of them deterministically in a single local compile pass.

### 💡 4. Quality of the Idea (The Graph-Aware Paradigm Shift)
* **The Achievement:** Traditional static site generators view pages as raw files in directories. Boris views your content as a **validated entity graph** of interconnected nodes, ensuring parent-child safety and global ID uniqueness at compile time.

***

## Start Exploring

- [[pipeline|The Pipeline]] — Markdown in, multiple explicit outputs out.
- [[migration-evidence|Evidence & Benchmarks]] — Bounded dogfood audits, Astro vs. Boris shootouts, and performance results.
  - [[stress-tests|Stress Testing Runbook]] — Replicating and running the massive benchmarks locally.
- [[build-week|How Boris Was Built]] — The human–AI collaboration story.
  - [[codex-showcase|Codex Deep-Dive & Outputs]] — System-capabilities showcase and co-authoring logs.
- [[agent-archive|The Agent Roster]] — A durable, evidence-bound thank-you to our synthetic collaborators.

***

## Submission Info & Checklist

- **Live Demo:** [drawmeanelephant.github.io/openai-buildweek-2026](https://drawmeanelephant.github.io/openai-buildweek-2026/)
- **Demo Video:** [Pending final upload during checkout](https://github.com/drawmeanelephant/openai-buildweek-2026)
- **Release Tag:** [v0.7.0](https://github.com/drawmeanelephant/boris/releases/tag/v0.7.0)
- **Codex session ID:** `bee98e9f-de65-4009-9b61-0fe980843ace`

- [x] **Build instructions:** Documented in [README.md](https://github.com/drawmeanelephant/openai-buildweek-2026/blob/main/README.md)
- [x] **Test instructions:** Documented in [README.md](https://github.com/drawmeanelephant/openai-buildweek-2026/blob/main/README.md)
- [x] **Public repository:** Available at [drawmeanelephant/boris](https://github.com/drawmeanelephant/boris)
- [x] **README:** Complete
- [x] **Demo video:** [Pending final upload during checkout](https://github.com/drawmeanelephant/openai-buildweek-2026)
- [x] **Codex session ID:** `bee98e9f-de65-4009-9b61-0fe980843ace`
- [x] **How Codex/GPT-5.6 was used:** Detailed in [[build-week|How Boris Was Built]]
- [x] **Known limitations:** Detailed in [[build-week|How Boris Was Built]]

<Aside kind="note">
This is a proof site, not a polished hosted service. Boris stays local-first:
the binary validates and writes static files on your machine.
</Aside>
