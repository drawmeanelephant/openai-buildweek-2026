---
id: build-week
title: How Boris Was Built
parent: index
status: published
tags: [build-week, codex, collaboration]
---

# How Boris Was Built

Boris began as a rough idea: use Apex Markdown in-process from Zig, build a strict local documentation compiler, and keep the publishing path free of JavaScript runtime machinery. It was human-steered continuously through ChatGPT 5.6, Codex, and delegated agents from the initial scaffold through the current design and release decisions.

## What the collaboration actually looked like

We used AI explicitly for:
- **Architecture and scope decisions:** Defining the boundaries of the graph validation and what features to cut.
- **Delegated implementation:** Handing off focused Zig parser or validation work to Codex.
- **PR review and repair:** Fixing broken tests and debugging memory leaks in Zig.
- **Hostile testing:** Prompting agents to actively attempt to break the source graph or find edge cases.
- **Migration audits:** Running agents against WordPress WXR files and Astro archives to normalize frontmatter.
- **Documentation and release gates:** Having agents draft runbooks and enforce release checklists.
- **Source-RAG packaging:** Building the pipelines that emit context bundles and JSON IR.
- **Design and demo iteration:** Iterating on the HTML/CSS outputs and testing various design prototypes.

The human set goals, chose the product boundaries, read the output, and made acceptance decisions. Every useful claim had to survive a build, a test, a contract check, or a documented limitation.

## Preserving the Honest Failures

The project deliberately rejected arbitrary executable MDX, a JS app shell, runtime component frameworks, and “universal converter” promises. The journey was not perfect, and we preserve the honest failures:
- **Oversized importer experiments** that tried to do too much automatically.
- **Bad mascot/image experiments** that drifted from the core aesthetic.
- **Branch mistakes and stale reports** that needed active repair work to get back on track.

These failures are part of the story because scope control is engineering, not an afterthought.

## Why the record matters

The contest asks how Codex and GPT-5.6 were used. The honest answer is not that an agent pressed a button and a compiler appeared, nor is it generic AI hype claiming independent creation. It is that a long-running human–AI collaboration repeatedly made a technical claim, tested it, narrowed it, and kept what held up.
