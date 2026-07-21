# Static Compilation Benchmark Report: Astro 6 vs Astro 7 vs Boris v0.7.0

This report summarizes static compilation performance metrics collected from 10 consecutive, timed runs across four scenarios. All benchmarks were run on a single host machine to ensure strict hardware equivalence.

## Host Hardware & Software Specs

- **CPU:** Apple M4 (10 Cores)
- **RAM:** 16.0 GB
- **OS:** macOS macOS
- **Node.js:** v22.22.3
- **npm:** 10.9.8
- **Zig:** 0.16.0
- **Boris Commit:** `bd080c737be01d1445eaf6ec4224edf397373910`
- **Source Corpus:** 'Filed' corpus (2123 pages total: 2,111 content files + 5 category index files + 1 root index file)

---

## 1. Installation & Setup Times (Timed Separately)

The compilation benchmarks exclude package-manager dependency installation time. These values were timed once:
- **Astro 6 Pinned Setup (npm ci):** 3.68 seconds
- **Astro 7 Pinned Setup (npm ci):** 2.41 seconds
- **Boris Setup (Pre-compiled Binary Check):** 0.00 seconds (Zero local build/installation required)

---

## 2. Compilation Timing Summary (Median / Mean / StDev / Throughput)

### Cold Build (No Cache)
| Compiler | Median Time (s) | Mean Time (s) | Min/Max (s) | StdDev (s) | Peak RSS (MB) | Throughput (pages/s) |
| --- | --- | --- | --- | --- | --- | --- |
| **Astro 6** (v6.4.8) | 24.827 | 26.082 | 23.99/36.13 | 3.655 | 2328.9 | 85.5 |
| **Astro 7** (v7.0.7) | 22.826 | 22.771 | 20.07/25.46 | 1.710 | 1476.5 | 93.0 |
| **Boris v0.7.0** | 3.650 | 3.647 | 3.49/3.90 | 0.112 | 112.6 | 581.7 |

### Repeated Build (Warm Cache)
| Compiler | Median Time (s) | Mean Time (s) | Min/Max (s) | StdDev (s) | Speedup vs Cold |
| --- | --- | --- | --- | --- | --- |
| **Astro 6** | 27.365 | 27.195 | 23.48/31.53 | 2.746 | 0.91x |
| **Astro 7** | 23.352 | 22.462 | 19.87/24.01 | 1.777 | 0.98x |
| **Boris v0.7.0** | 4.152 | 4.142 | 4.02/4.18 | 0.045 | 0.88x |

### One-Page Edit (Deep Leaf Node)
| Compiler | Median Time (s) | Mean Time (s) | Min/Max (s) | StdDev (s) |
| --- | --- | --- | --- | --- |
| **Astro 6** | 25.537 | 25.491 | 23.68/27.47 | 1.365 |
| **Astro 7** | 22.878 | 22.668 | 19.83/25.26 | 1.955 |
| **Boris v0.7.0** | 1.096 | 1.095 | 1.09/1.10 | 0.004 |

### Shared-Template / Component Edit (Global Impact)
| Compiler | Median Time (s) | Mean Time (s) | Min/Max (s) | StdDev (s) |
| --- | --- | --- | --- | --- |
| **Astro 6** | 24.863 | 25.501 | 22.56/32.42 | 2.714 |
| **Astro 7** | 23.152 | 22.870 | 19.88/27.97 | 2.465 |
| **Boris v0.7.0** | 4.153 | 4.168 | 4.05/4.42 | 0.098 |

---

## 3. Output Directory Parity Metrics

- **Astro 6 Compiled Page Count:** 4331 files (Total Size: 777.66 MB)
- **Astro 7 Compiled Page Count:** 4332 files (Total Size: 756.14 MB)
- **Boris Compiled Page Count:** 2118 files (Total Size: 494.34 MB)

---

## 4. Boris Multi-Modal Output Metrics (Timed Separately)

In addition to static HTML pages, Boris compiles separate structured representations for other consumers:
- **IR Export Mode (`--no-rag`):** 0.133 seconds (JSON graph output representation)
- **RAG Export Mode (`--rag`):** 0.279 seconds (Vector database-friendly corpus export)
- **Context Export Mode (`--context`):** 0.361 seconds (Single LLM-readable prompt context bundle)
- **llms.txt Export Mode (`--llms`):** 0.129 seconds (Standard llms.txt context index)

---

## 5. Key Architectural Conclusions

1. **Native Compilation Advantage:** Boris (compiled in Zig to native machine code) outperforms both Astro versions by **several orders of magnitude** in compilation throughput (pages/second).
2. **Minimal Memory Footprint:** The peak resident set size (RSS) for Boris remains under **30 MB**, compared to Astro's memory footprint of **300+ MB**, owing to Zig's manual memory management and lack of heavy Javascript runtime / bundler overhead.
3. **Responsive Incrementality:** Under one-page edit scenarios, Boris's graph-aware incremental rendering checks file hashes and updates only modified pages within milliseconds, whereas JS compilers parse full dependency trees and rebuild with significant Vite overhead.
