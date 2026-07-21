---
id: migration-evidence
title: Evidence & Benchmarks
parent: index
status: published
tags: [migration, dogfood, wordpress, starlight, benchmarks]
---

# Evidence & Benchmarks

Boris is built on proof, not magic. It includes developer migration laboratories for auditing and converting bounded slices of external content, alongside strict performance benchmarks to validate its speed and determinism at the v0.7.0 release.

<div style="text-align: center; margin-block: 2rem;">
  <img src="assets/images/mediluna-migration-labs.png" alt="Mediluna examining ancient stone tablets of WordPress and HTML with a magnifying glass while neatly organizing them into folders." style="max-width: 450px; width: 100%; height: auto; border-radius: 12px; border: 1px solid var(--line); box-shadow: 0 4px 12px rgba(0,0,0,0.08);" />
  <p style="font-style: italic; color: var(--muted); margin-top: 0.5rem; font-size: 1rem; font-weight: 500;">“Let’s make sure everything is in its proper place.”</p>
</div>

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

To test raw throughput and determinism under heavy stress, Boris v0.7.0 was benchmarked against a pre-cleaned corpus of 804 massive GitHub READMEs.

**Benchmark Environment:**
- **Machine:** Apple M4 (10 cores, 16 GB RAM)
- **Compilation Mode:** ReleaseFast (`zig build -Doptimize=ReleaseFast`)
- **Corpus Size:** 804 Markdown files (10.57 MB of raw text)
- **Output:** 74.21 MB of fully rendered, styled HTML

**Results (5 Cold Runs, Same-Machine):**
- **Average Build Time:** **78.85 seconds** (Single-threaded `-j 1`)
- **Peak RSS:** **160.1 MB** (Peak Resident Set Size)
- **Concurrency Observation:** Increasing thread counts on this specific flat corpus resulted in disk I/O lock contention at the operating system level, validating that a single-threaded configuration (`-j 1`) is the fastest and most efficient setting for this workload.

---

## Head-to-Head Shootout: Astro vs. Boris

To compare compilation efficiency against a modern, widely used framework, we conducted a same-machine benchmark comparing **Astro 7 (v7.0.7)** against **Boris v0.7.0** across 10 consecutive timed runs on the identical `filed.fyi` wiki corpus (2,117 compiled pages total).

**Benchmark Environment:**
- **Machine:** Apple M4 (10 cores, 16 GB RAM)
- **Corpus Size:** 2,111 content files + 5 category index files + 1 root index file (2,117 total pages)
- **Build Mode:** Standard production build commands on both compilers

### Shootout Metrics (Official 10-Run Median Comparison)

| Metric / Scenario | Astro 7 (v7.0.7) | Boris v0.7.0 (Zig) | Performance Advantage |
| :--- | :--- | :--- | :--- |
| **Cold Build (Clean)** | **22.826 seconds** | **3.650 seconds** | **`6.3x Faster`** |
| **One-Page Edit (Leaf Node)** | **22.878 seconds** | **1.096 seconds** | **`20.9x Faster`** |
| **Peak Memory (RSS)** | **1476.5 MB** | **112.6 MB** | **`13.1x Less RAM`** |
| **Dependency Footprint** | Heavy `node_modules` (npm) | **Zero config / Standalone binary** | **Native Execution** |

### Architectural Conclusions
* **Thread Scaling:** Astro's JavaScript-based bundler remains largely single-threaded during key build stages (Vite/Rollup bound to 136% CPU load), whereas Boris (compiled native Zig) efficiently distributes graph rendering across multiple available cores (utilizing **524%** CPU capacity).
* **Zero Dependency Cost:** Astro incurs overhead for arbitrary JS components, asset pipelines, node runtime boot, and search index generation. Boris operates strictly as a native local compiler, producing standard HTML in milliseconds.

---

### Determinism & Immutability

- **100% Deterministic Output:** Across all runs and concurrency levels (`-j 1` to `-j 10`), the generated output directory produced the exact same SHA-256 hash (`b67d1b66...`).
- **Source Immutability:** Boris operates strictly read-only on the input directory.
- **Hostile Testing:** The compiler was subjected to hostile adversarial testing against malformed trees and cyclically linked components. It failed safely and loudly via AST graph validation rather than silently publishing broken HTML.

***

To replicate these benchmark results or read the step-by-step instructions for our massive performance runs, see [[stress-tests|How to Run Stress Tests & Benchmarks]].
