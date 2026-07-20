---
id: stress-tests
title: How to Run Stress Tests & Benchmarks
parent: index
status: published
tags: [stress-tests, benchmarks, scaling, zig]
---

# How to Run Stress Tests & Benchmarks

Boris is optimized for speed, safety, and strict schema validation. To prove the speed claims on real, massive workloads, we subjected the compiler to hostile and heavy stress testing. All benchmarks were compiled in ReleaseFast optimization mode (built with `zig build -Doptimize=ReleaseFast`) and evaluated on the same-machine to ensure identical hardware comparison.

This guide details how those stress tests were constructed, what compiler constraints were uncovered, and how you can run them on your local machine.

***

## 1. The 804-Page GitHub README Dataset (10.57 MB)

This test measures raw, sustained throughput across varying concurrency levels on a massive, chaotic corpus.

* **The Dataset:** A pre-cleaned corpus of 804 of the most starred GitHub repository READMEs (`davidmyersdev/markdown-dataset`), totaling **10.57 MB of raw Markdown**.
* **The Workflow:** Compiles the 10.57 MB of Markdown into **74.21 MB of fully rendered, styled HTML**.
* **Key Findings:** On an Apple M4 (10 cores, 16 GB RAM), the single-threaded build (`-j 1`) completed in **78.85s**, which was actually *faster* than multi-threaded configurations (e.g., `-j 10` took 84.67s).
* **The Bottleneck:** Pushing concurrency levels past physical limitations causes intense **OS lock contention** on file writes. Slower disk I/O and kernel page-table overhead negate multi-threading gains. Single-threaded compilation remains the most efficient, battery-friendly, and "lap-safe" configuration.

### How to Run the README Benchmark

To run this benchmark over 5 cold builds:

1. Ensure the dataset is extracted under the test workspace:
   ```bash
   unzip large-markdown-corpus-benchmark.zip -d fixtures/large-markdown-corpus
   ```
2. Execute the benchmark script:
   ```bash
   python3 benchmark_v3.py
   ```
3. Read the generated JSON results report:
   ```bash
   cat reports/benchmark_v0.7.0_results.json
   ```

***

## 2. The 2,116-Page filed.fyi Starlight Wiki

This test measures graph validation speeds and content-addressed incremental build performance on an structured, deeply parented website.

* **The Dataset:** Converted from `filed.fyi` (a public Starlight-based wiki with **2,111 content files** across poetry/lore categories + 5 indexes).
* **The Workflow:** Validates the entire parent-child hierarchy graph and compiles to static HTML with an accordion-collapsing sidebar.
* **Uptime Speed:** 
  * **j=1 (Single-threaded):** **3.072s** (1.45ms per page)
  * **j=8 (Multi-threaded):** **2.065s** (0.97ms per page) — *Unlike the README benchmark, a structured graph allows successful parallel scaling because pages are smaller, leading to less thread contention.*

### Incremental Rebuild Re-Verification

To verify the `--incremental` content-addressed caching engine:

1. Populate the cache with an initial compilation:
   ```bash
   ./bin/boris \
     --input outputs/filed-fyi-clean/content \
     --theme themes/cozy-typepad \
     --html-dir outputs/filed-fyi-clean/dist-inc \
     --incremental \
     -j 8
   ```
2. Make a single-character modification to a deep leaf page (e.g., `aphorisms/APH-003.blamey-mctypoface.md`):
   ```bash
   echo " " >> outputs/filed-fyi-clean/content/aphorisms/APH-003.blamey-mctypoface.md
   ```
3. Recompile with the same command and observe the timing results:
   * **Rebuild time:** **0.766s** (2.7× faster than a clean build).
   * **Skipped/Cached pages:** **2,115 files skipped**, only **1 recompiled**.
   * **Log output:** Under the hood, Boris takes ~700ms to parse and validate the global content graph for structural health, while rendering is instant.

***

## 3. Core Compiler Constraints Uncovered

Subjecting Boris to these massive datasets exposed strict design boundaries built into the Zig compiler:

* **Strict Frontmatter (`EFRONTMATTER`):** Boris throws a compilation error on standard fields like `description` or `date`. It strictly permits *only* five keys: `id`, `title`, `parent`, `status`, and `tags`. Additional metadata must be rendered directly inside the page body.
* **Strict Tag Limits (`ETAGLIMIT`):** Tags must be formatted as inline lists (`tags: ["a", "b"]`). Each page is capped at **32 tags**, and each individual tag is limited to **64 characters**.
* **Asset Sandboxing (`EASSET`):** Any image reference containing out-of-tree path traversals (e.g., `../../../etc/passwd.png`) is caught immediately, failing the build to guarantee local safety.
* **Setext Parser Bug:** If markdown contains horizontal rule hyphens `---` separated by a blank line after a paragraph, the parser mistakenly treats it as a Setext heading underline, turning entire blocks into oversized headers. 
  * *Workaround:* Replaced all horizontal dividers in markdown files with asterisks `***` instead of hyphens.
