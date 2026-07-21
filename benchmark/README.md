# ⚡ Boris vs Astro 6/7 Benchmark Suite

This directory contains the code, configurations, scripts, and results for the official OpenAI Build Week 2026 static compilation benchmark shootout.

## 🚀 How to Run the Benchmark in One Command

To run the complete benchmark suite, simply execute the orchestrator script from the repository root:

```bash
./benchmark/run-benchmarks.sh
```

### Sandbox & Permissions Notice
Because the benchmark script:
1. Setup and installs Node/npm dependencies inside two isolated directories (`benchmark/astro6/` and `benchmark/astro7/`) using `npm ci`.
2. Queries the host machine's hardware variables (`sysctl` queries on CPU cores, RAM size, brand string) and software versions (`node`, `npm`, `zig`).
It requires network access and host profile capabilities. Ensure the execution sandbox has bypass permissions enabled when prompted.

---

## 🏗️ Directory Structure

- `run-benchmarks.sh`: Main orchestrator script.
- `run.py`: Core python timing loop, statistical calculation, and report generation engine.
- `prep_filed_fyi.py`: Corpus converter script that transforms the raw Starlight content into the flat-navigation 2,111 content pages + 5 category index pages corpus.
- `astro6/`: Pinned Astro 6.4.8 project environment with committed lockfile.
- `astro7/`: Pinned Astro 7.0.7 project environment with committed lockfile.
- `environment.txt`: Host specifications, OS, compiler, and runtime versions.
- `results.json`: Complete raw JSON dataset of all 10 timed runs across the 4 scenarios for all compilers.
- `results.md`: Beautifully formatted markdown report detailing findings, tables, throughput, memory, and architectural analysis.
- `raw/`: Subdirectory containing raw `stdout` and `stderr` execution logs for every compile run.
- `README-SUMMARY.md`: High-impact summary for the root readme.
- `DEVPOST-SUMMARY.md`: Pitch summary copy-pasteable for Devpost judges.

---

## 📊 Scenarios Measured (10 Runs Each)

1. **Cold Build (Clean Cache):**
   Deletes `dist/` (build output) and cache folders (`.astro/` or `.boris/`), then measures a clean production static compilation.
2. **Repeated Build (Warm Cache):**
   Compiles the site immediately following a successful build without removing any output or cache files. Uses Boris's `--incremental` flag.
3. **One-Page Edit:**
   Appends a comment to a deep leaf node (`haikus/haiku-1.md`), runs a build, and reverts the edit.
4. **Shared-Template Edit:**
   Modifies a component or layout that affects every page (Cozy Typepad's `main.html` for Boris, and `MarkdownContent.astro` for Astro), compiles the site, and reverts the edit.

---

## 🔒 Parity & Reproducibility Constraints

- **Exact Version Pins:** Astro 6 is locked to `astro@6.4.8` and `@astrojs/starlight@0.39.3`. Astro 7 is locked to `astro@7.0.7` and `@astrojs/starlight@0.41.3`. Dedicated lockfiles are committed to block drift.
- **Dependency Isolation:** Separate directories prevent dependency pollution between Astro 6 and Astro 7.
- **Isolated Timing:** Setup phases (like package installations) are measured once and reported separately from static compilation loops. No network requests are made during compilation measurements.
- **Source Parity:** Source manifests and SHA-256 hashes are verified to be identical for all three compilers prior to the benchmarks.
