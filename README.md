# OpenAI Build Week 2026 — Boris Field Guide

This is the public contest companion for [Boris](https://github.com/drawmeanelephant/boris): a small, deployable site built by Boris rather than a second copy of the compiler.

It keeps the two concerns separate:

- **Boris** is the Zig documentation compiler, its contracts, tests, migration laboratories, and release history.
- **This repository** is the human-facing proof: a compact product walkthrough, migration evidence, and a carefully curated Build Week archive.

No compiler source is vendored here. The site has no JavaScript runtime, package manager, framework, remote fonts, or build-time service dependency.

## Build locally

Build Boris once in a sibling checkout (Zig 0.16 and CMake are required there):

```bash
git clone https://github.com/drawmeanelephant/boris.git
cd boris
zig build
```

Then, from this repository, point `BORIS` at that binary and build the field guide:

```bash
export BORIS=../boris/zig-out/bin/boris

"$BORIS" \
  --input site/content \
  --theme site/theme \
  --layout-rule default id:index site/theme/layouts/home.html \
  --html-dir dist \
  --quiet

open dist/index.html
```

The same content tree can independently produce Boris's machine-readable outputs:

```bash
"$BORIS" --input site/content --out .boris --quiet
"$BORIS" --input site/content --rag --quiet
"$BORIS" --input site/content --context --quiet
"$BORIS" --input site/content --llms --quiet
```

Generated output is intentionally ignored. A deploy workflow may publish `dist/`, but this repository keeps source, theme, and reproducible instructions as the durable record.

## Publish to GitHub Pages

The included workflow builds the pinned Boris `v0.6.1` release from public
source, compiles this Field Guide, then uploads the generated `dist/` as a
GitHub Pages artifact. Before the first deployment, select **GitHub Actions**
as the publishing source under this repository's **Settings → Pages**. The
workflow only deploys from `main`.

## Evidence boundary

The Build Week collaboration involved continuous human steering, Codex/ChatGPT, and bounded external reviews and experiments. This field guide distinguishes verified code and release evidence from draft art, agent names, and exploratory material. It is a record, not a mythology generator.
