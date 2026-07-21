# Devpost Pitch: Boris v0.7.0 vs Astro 6/7 Build Shootout

### 🚀 Performance Headline
On an Apple M4 Mac, **Boris compiles a 2,117-page wiki corpus in just 3.650 seconds** (581.7 pages/sec) from a cold start, outperforming Astro 7 by **6.3x** and using **over 10x less memory**.

### 📊 Comparative Metrics (Apple M4 Mac, 10-run Medians)
- **Cold Compilation:** Boris **3.650s** | Astro 7 **22.826s**
- **Incremental One-Page Edit:** Boris **1.096s** | Astro 7 **22.878s**
- **Peak Resident Set Size (Memory):** Boris **112.6 MB** | Astro 7 **1476.5 MB**
- **Dependency Setup Overhead:** Boris **0.00s** (Zero install, native binary) | Astro 7 **2.41s** (`npm ci`)

### 🧠 Architectural Takeaways
1. **Zero-Overhead Compilation:** By building the Markdown-to-HTML parser natively in Zig, Boris bypasses the Node.js module resolution, JS transpilation, and bundler packaging loops, which dominate the startup costs of Javascript static generators.
2. **Deterministic, Graph-Aware Caching:** Under incremental mode, Boris checks content-addressed file hashes and updates the one-page edit scenario in **1.096s** median.
3. **Multimodal LLM Integrations:** From the same content graph, Boris can also emit machine-readable JSON IR, RAG output, a single context bundle, and `llms.txt` in separate deterministic modes.
