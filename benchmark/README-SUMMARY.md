## ⚡ Benchmark Summary: Boris vs Astro 6/7

We evaluated static HTML site compilation on the host M4 machine using the identical, cleaned **Filed & Forgotten** wiki corpus (2,117 compiled pages total) across Astro 6, Astro 7, and Boris v0.7.0.

### Headline Performance metrics (Median values)

| Build Scenario | Astro 6 (v6.4.8) | Astro 7 (v7.0.7) | Boris v0.7.0 (Zig) | Boris Speedup vs Astro 7 |
| --- | --- | --- | --- | --- |
| **Cold Build** (Clean) | 24.827s | 22.826s | 3.650s | **6.3x** |
| **Warm Build** (Unchanged) | 27.365s | 23.352s | 4.152s | **5.6x** |
| **One-Page Edit** (Leaf) | 25.537s | 22.878s | 1.096s | **20.9x** |
| **Peak Memory RSS** | 2328.9 MB | 1476.5 MB | 112.6 MB | **13.1x less RAM** |

*Read the full details, raw execution logs, and architectural conclusions in the [Benchmark Report](benchmark/results.md).*
