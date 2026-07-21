#!/bin/bash
set -e

# Resolve script directory and repository root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"

echo "========================================================="
echo "   Boris v0.7.0 vs Astro 6 / Astro 7 Build Shootout     "
echo "========================================================="
echo "Script Location: $SCRIPT_DIR"
echo "Repository Root: $REPO_ROOT"
echo ""

# Ensure we execute the python orchestrator
python3 "$SCRIPT_DIR/run.py"

echo ""
echo "========================================================="
echo "   Benchmark Executed Successfully!                      "
echo "   Reports generated in benchmark/                      "
echo "========================================================="
