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

## Start Exploring

- [[pipeline|The Pipeline]] — Markdown in, multiple explicit outputs out.
- [[migration-evidence|Evidence & Benchmarks]] — Bounded dogfood audits and performance results.
- [[build-week|How Boris Was Built]] — The human–AI collaboration story.
- [[agent-archive|The Agent Roster]] — A durable, evidence-bound thank-you to our synthetic collaborators.

<Aside kind="note">
This is a proof site, not a polished hosted service. Boris stays local-first:
the binary validates and writes static files on your machine.
</Aside>
