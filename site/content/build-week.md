---
id: build-week
title: How Boris Was Built
parent: index
status: published
tags: [build-week, codex, collaboration]
---

# How Boris Was Built

Boris began as a human-directed idea: use Apex Markdown in-process from Zig,
build a strict local documentation compiler, and keep the publishing path free
of JavaScript runtime machinery. ChatGPT 5.6 and Codex were involved from the
initial scaffold through the current design and release decisions.

## What the collaboration actually looked like

- The human set goals, chose the product boundaries, read the output, and made
  acceptance decisions.
- Codex helped turn those decisions into modules, contracts, tests, release
  gates, and documentation.
- External agents were used for bounded migration experiments, hostile testing,
  visual prototyping, and independent review packets.
- Every useful claim had to survive a build, a test, a contract check, or a
  documented limitation.

## What did not make the cut

The project deliberately rejected arbitrary executable MDX, a JS app shell,
runtime component frameworks, and “universal converter” promises. There were
also failed art experiments and over-eager exploratory passes. Those are part
of the story because scope control is engineering, not an afterthought.

## Why the record matters

The contest asks how Codex and GPT-5.6 were used. The honest answer is not that
an agent pressed a button and a compiler appeared. It is that a long-running
human–AI collaboration repeatedly made a technical claim, tested it, narrowed
it, and kept what held up.
