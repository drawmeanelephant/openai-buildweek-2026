---
id: migration-evidence
title: Evidence & Benchmarks
parent: index
status: published
tags: [migration, dogfood, wordpress, starlight, benchmarks]
---

# Evidence & Benchmarks

Boris is built on proof, not magic. It includes developer migration laboratories for auditing and converting bounded slices of external content, alongside strict performance benchmarks to validate its speed and determinism at the v0.7.0 release.

## Migration Laboratories

| Source shape | What the lab does | Honest boundary |
|---|---|---|
| WordPress WXR | Reads posts, pages, taxonomies, and local media into a deterministic Boris candidate tree | Complex HTML and unavailable media remain review items |
| Astro/Starlight | Audits Markdown/MDX documentation and normalizes safe static patterns | Runtime components and arbitrary JSX are not silently reimplemented |
| Filed.fyi | Performs a read-only dogfood preflight on a real, complex archive | Custom frontmatter and interactive MDX require deliberate normalization |
| Frontmatter Review | Normalizes unknown YAML properties against the strict Boris schema | Preserves unrecognized properties in a separate block instead of deleting them |

<Aside kind="warning">
The migration labs are a safer way to understand a move. They do not promise
that an arbitrary production site can become Boris without editorial decisions.
</Aside>

## Large Markdown Corpus Benchmark

To test raw throughput and determinism, Boris v0.7.0 was benchmarked against a 10.57 MB corpus of 804 massive GitHub READMEs (cleaned of invalid local assets/components).

**Benchmark Environment:**
- **Machine:** Apple M4, 10 cores (Cross-machine comparisons are meaningless without matching hardware)
- **Optimization:** ReleaseFast (`zig build -Doptimize=ReleaseFast`)
- **Corpus:** 804 pre-cleaned Markdown files (10.57 MB)

**Results (5 Cold Builds):**
- **Average Time:** 78.85s (Single-threaded `-j 1`)
- **Peak RSS:** 160.1 MB
- **Output:** 74.21 MB of fully rendered HTML

**The strongest honest result:**
Boris compiled the dogfood corpus in seconds on the local test hardware, while Astro’s raw build took substantially longer on the same general site workflow. *(Caveat: Frameworks like Astro incur overhead for arbitrary JS components, asset pipelines, and search indexing—so this compares static compilation speed, not feature parity.)*

### Determinism & Immutability

- **100% Deterministic Output:** Across all runs and concurrency levels (`-j 1` to `-j 10`), the generated output directory produced the exact same SHA-256 hash (`b67d1b66...`).
- **Source Immutability:** Boris operates strictly read-only on the input directory.
- **Hostile Testing:** The compiler was subjected to hostile adversarial testing against malformed trees and cyclically linked components. It failed safely and loudly via AST graph validation rather than silently publishing broken HTML.

***

To replicate these benchmark results or read the step-by-step instructions for our massive performance runs, see [[stress-tests|How to Run Stress Tests & Benchmarks]].
