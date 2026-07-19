---
id: index
title: The Content Exit Hatch
status: published
tags: [boris, build-week, field-guide]
---

# Boris: The Content Exit Hatch

Boris is a deterministic documentation compiler and static-site generator.
Give it Markdown and a small amount of frontmatter; it validates the content
graph and publishes a fast static site. The same source tree can also emit JSON
IR, RAG corpora, context bundles, and `llms.txt`.

This site is the contest-facing proof, deliberately separate from the compiler
repository. It is itself Markdown compiled by Boris, with no JavaScript runtime
or framework in the publishing path.

## Start here

- [[pipeline|The pipeline]] — Markdown in, multiple explicit outputs out.
- [[migration-evidence|Migration evidence]] — bounded, read-only dogfood rather
  than hand-wavy importer claims.
- [[build-week|How Boris was built]] — the human–AI collaboration, including
  limits and scope cuts.
- [[agent-archive|The agent archive]] — a durable, evidence-bound thank-you.

<Aside kind="note">
This is a proof site, not a polished hosted service. Boris stays local-first:
the binary validates and writes static files on your machine.
</Aside>

## The short version

| If you need | Boris gives you |
|---|---|
| A lean docs publishing path | A Zig binary with no Node runtime in the publish path |
| Reliable structure | Compile-time validation for `parent`, wiki targets, headings, and includes |
| Several machine-friendly views | HTML, JSON IR, RAG, Context Bundles, and `llms.txt` from one source tree |
| An exit from a hosted platform | A bounded Markdown/frontmatter target and read-only migration laboratories |
