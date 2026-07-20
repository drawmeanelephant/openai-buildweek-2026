#!/usr/bin/env python3
"""Focused unit tests for tools/submission_preflight.py."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import submission_preflight as sp  # noqa: E402


MINIMAL_WORKFLOW = """\
name: Build, Validate and deploy Field Guide

on:
  push:
    branches: [main]
  pull_request:

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Compile
        run: |
          boris --input site/content --theme site/theme --html-dir dist
  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - run: echo deploy
  ci:
    name: ci
    needs: [build]
    if: always()
    runs-on: ubuntu-latest
    steps:
      - name: Require build success
        run: test "${{ needs.build.result }}" = "success"
"""


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _page(page_id: str, title: str, body: str, parent: str | None = None) -> str:
    parent_line = f"parent: {parent}\n" if parent else ""
    return (
        f"---\n"
        f"id: {page_id}\n"
        f"title: {title}\n"
        f"{parent_line}"
        f"status: published\n"
        f"tags: [test]\n"
        f"---\n\n"
        f"{body}\n"
    )


def _scaffold_good_repo(root: Path) -> None:
    _write(
        root / "README.md",
        """# Contest

[Boris](https://github.com/drawmeanelephant/boris)
[Contest](https://github.com/drawmeanelephant/openai-buildweek-2026)
[Release](https://github.com/drawmeanelephant/boris/releases/tag/v0.7.0)
[Live demo](https://drawmeanelephant.github.io/openai-buildweek-2026/)
[Demo video](https://www.youtube.com/watch?v=dQw4w9WgXcQ)

## Build locally

```bash
export BORIS=../boris/zig-out/bin/boris

"$BORIS" \\
  --input site/content \\
  --theme site/theme \\
  --layout-rule default id:index site/theme/layouts/home.html \\
  --html-dir dist \\
  --quiet
```
""",
    )
    _write(root / "site/theme/layouts/home.html", "<html>{{body}}</html>\n")
    _write(root / "site/theme/footer.html", "<footer></footer>\n")
    _write(root / ".github/workflows/pages.yml", MINIMAL_WORKFLOW)

    index_body = """# Home

- [[pipeline|Pipeline]]
- [[migration-evidence|Evidence]]
- [[stress-tests|Stress]]
- [[build-week|Build Week]]
- [[agent-archive|Agents]]
- [[codex-showcase|Codex]]
"""
    _write(root / "site/content/index.md", _page("index", "Home", index_body))
    _write(
        root / "site/content/pipeline.md",
        _page("pipeline", "Pipeline", "Pipeline body.", parent="index"),
    )
    _write(
        root / "site/content/build-week.md",
        _page("build-week", "Build Week", "Build week story.", parent="index"),
    )
    _write(
        root / "site/content/agent-archive.md",
        _page("agent-archive", "Agents", "Roster.", parent="index"),
    )
    _write(
        root / "site/content/codex-showcase.md",
        _page("codex-showcase", "Codex", "Showcase.", parent="index"),
    )

    evidence_body = """# Evidence

## Head-to-Head Shootout

**Benchmark Environment:**
- **Machine:** Apple M4 (10 cores, 16 GB RAM)
- **Corpus Size:** 2,111 content files
- **Build Mode:** ReleaseFast (`zig build -Doptimize=ReleaseFast`)
- **Workers:** `-j 8`

### Shootout Metrics (Same-Machine Comparison)

Boris finished in **2.69 seconds** on the same-machine comparison.
"""
    _write(
        root / "site/content/migration-evidence.md",
        _page("migration-evidence", "Evidence", evidence_body, parent="index"),
    )
    stress_body = """# Stress
 
 Apple M4 (10 cores, 16 GB RAM), corpus of 804 pages, ReleaseFast, `-j 1`,
 same-machine cold runs averaged **78.85 seconds**.
 """
    _write(
        root / "site/content/stress-tests.md",
        _page("stress-tests", "Stress", stress_body, parent="index"),
    )
    _write(root / ".gitignore", "dist/\n.boris/\nsubmission-preflight.json\nSUBMISSION_PREFLIGHT.md\n")


class SubmissionPreflightTests(unittest.TestCase):
    def test_good_fixture_has_no_blockers(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _scaffold_good_repo(root)
            # Initialize git so generated-tracking check can run cleanly.
            subprocess.run(["git", "init"], cwd=root, check=True, capture_output=True)
            subprocess.run(["git", "add", "-A"], cwd=root, check=True, capture_output=True)
            subprocess.run(
                ["git", "commit", "-m", "fixture"],
                cwd=root,
                check=True,
                capture_output=True,
                env={
                    **os.environ,
                    "GIT_AUTHOR_NAME": "test",
                    "GIT_AUTHOR_EMAIL": "test@example.com",
                    "GIT_COMMITTER_NAME": "test",
                    "GIT_COMMITTER_EMAIL": "test@example.com",
                },
            )
            report = sp.run_checks(root)
            blockers = [f for f in report.findings if f.severity == "BLOCKER"]
            self.assertEqual(
                blockers,
                [],
                msg="\n".join(f"{f.code}: {f.message}" for f in blockers),
            )
            self.assertEqual(report.counts()["BLOCKER"], 0)

    def test_missing_required_file_is_blocker(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _scaffold_good_repo(root)
            (root / "site/content/index.md").unlink()
            report = sp.run_checks(root)
            codes = {f.code for f in report.findings if f.severity == "BLOCKER"}
            self.assertIn("required_path_missing", codes)
            self.assertTrue(report.has_blockers())

    def test_stale_todo_is_blocker(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _scaffold_good_repo(root)
            path = root / "site/content/index.md"
            path.write_text(path.read_text(encoding="utf-8") + "\nTODO: fill me in\n", encoding="utf-8")
            report = sp.run_checks(root)
            hits = [
                f
                for f in report.findings
                if f.severity == "BLOCKER" and f.code == "stale_placeholder"
            ]
            self.assertTrue(hits)
            self.assertIn("TODO", hits[0].message)

    def test_broken_wiki_link_is_blocker(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _scaffold_good_repo(root)
            path = root / "site/content/index.md"
            text = path.read_text(encoding="utf-8")
            path.write_text(text + "\nSee [[does-not-exist|Missing]].\n", encoding="utf-8")
            report = sp.run_checks(root)
            hits = [f for f in report.findings if f.code == "broken_wiki_link"]
            self.assertTrue(hits)
            self.assertEqual(hits[0].severity, "BLOCKER")

    def test_missing_external_link_is_blocker(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _scaffold_good_repo(root)
            readme = root / "README.md"
            text = readme.read_text(encoding="utf-8")
            text = text.replace("https://github.com/drawmeanelephant/boris/releases/tag/v0.7.0", "")
            readme.write_text(text, encoding="utf-8")
            report = sp.run_checks(root)
            codes = {f.code for f in report.findings if f.severity == "BLOCKER"}
            self.assertIn("external_link_missing_v0.7.0_release", codes)

    def test_incomplete_benchmark_provenance_is_warning(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _scaffold_good_repo(root)
            path = root / "site/content/migration-evidence.md"
            path.write_text(
                _page(
                    "migration-evidence",
                    "Evidence",
                    "Boris is **11.2x faster** and finishes in 2.69 seconds.",
                    parent="index",
                ),
                encoding="utf-8",
            )
            report = sp.run_checks(root)
            hits = [f for f in report.findings if f.code == "benchmark_provenance_incomplete"]
            self.assertTrue(hits)
            self.assertEqual(hits[0].severity, "WARNING")
            # Incomplete provenance must not alone be a blocker.
            self.assertFalse(any(f.code == "benchmark_provenance_incomplete" and f.severity == "BLOCKER" for f in report.findings))

    def test_workflow_missing_ci_job_is_blocker(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _scaffold_good_repo(root)
            workflow = root / ".github/workflows/pages.yml"
            text = workflow.read_text(encoding="utf-8")
            # Drop the ci job block.
            text = text.split("  ci:")[0]
            workflow.write_text(text, encoding="utf-8")
            report = sp.run_checks(root)
            codes = {f.code for f in report.findings if f.severity == "BLOCKER"}
            self.assertIn("workflow_missing_ci_job", codes)

    def test_generated_output_tracked_is_blocker(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _scaffold_good_repo(root)
            dist = root / "dist" / "index.html"
            _write(dist, "<html></html>\n")
            subprocess.run(["git", "init"], cwd=root, check=True, capture_output=True)
            # Force-add ignored dist to simulate accidental tracking.
            subprocess.run(["git", "add", "-f", "dist/index.html"], cwd=root, check=True, capture_output=True)
            subprocess.run(["git", "add", "README.md", "site", ".github", ".gitignore"], cwd=root, check=True, capture_output=True)
            subprocess.run(
                ["git", "commit", "-m", "tracked dist"],
                cwd=root,
                check=True,
                capture_output=True,
                env={
                    **os.environ,
                    "GIT_AUTHOR_NAME": "test",
                    "GIT_AUTHOR_EMAIL": "test@example.com",
                    "GIT_COMMITTER_NAME": "test",
                    "GIT_COMMITTER_EMAIL": "test@example.com",
                },
            )
            report = sp.run_checks(root)
            hits = [f for f in report.findings if f.code == "generated_output_tracked"]
            self.assertTrue(hits)
            self.assertEqual(hits[0].severity, "BLOCKER")

    def test_reports_are_deterministic_and_path_safe(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _scaffold_good_repo(root)
            # Introduce a stable blocker.
            (root / "site/content/pipeline.md").unlink()
            r1 = sp.run_checks(root)
            r2 = sp.run_checks(root)
            j1 = sp.render_json(r1)
            j2 = sp.render_json(r2)
            self.assertEqual(j1, j2)
            self.assertNotIn(str(root), j1)
            self.assertNotIn(str(Path.home()), j1)
            # No timestamp fields.
            payload = json.loads(j1)
            self.assertNotIn("timestamp", payload)
            self.assertNotIn("generated_at", payload)
            md = sp.render_markdown(r1)
            self.assertNotIn(str(root), md)
            self.assertIn("BLOCKER", md)

    def test_main_writes_reports_and_exit_codes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _scaffold_good_repo(root)
            code = sp.main(["--root", str(root), "--quiet"])
            self.assertEqual(code, 0)
            self.assertTrue((root / "submission-preflight.json").is_file())
            self.assertTrue((root / "SUBMISSION_PREFLIGHT.md").is_file())
            payload = json.loads((root / "submission-preflight.json").read_text(encoding="utf-8"))
            self.assertEqual(payload["status"], "pass")

            # Break a required path and ensure nonzero exit.
            (root / "README.md").unlink()
            code2 = sp.main(["--root", str(root), "--quiet"])
            self.assertEqual(code2, 1)

    def test_extract_jobs_from_workflow(self) -> None:
        jobs = sp._extract_top_level_jobs(MINIMAL_WORKFLOW)
        self.assertEqual(jobs, {"build", "deploy", "ci"})

    def test_no_write_flag_skips_report_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _scaffold_good_repo(root)
            code = sp.main(["--root", str(root), "--no-write", "--quiet"])
            self.assertEqual(code, 0)
            self.assertFalse((root / "submission-preflight.json").exists())
            self.assertFalse((root / "SUBMISSION_PREFLIGHT.md").exists())


if __name__ == "__main__":
    unittest.main()
