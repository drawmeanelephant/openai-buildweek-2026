#!/usr/bin/env python3
"""Deterministic submission preflight for the OpenAI Build Week contest repo.

Verifies contest readiness without network access, Node/npm, or third-party
packages. Emits machine-readable and human-readable reports. Never modifies
source files.

Exit codes:
  0  no BLOCKERs (WARNINGs and INFO allowed)
  1  one or more BLOCKERs
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from collections import Counter
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Iterable, List, Optional, Sequence, Set, Tuple

SEVERITY_ORDER = {"BLOCKER": 0, "WARNING": 1, "INFO": 2}

REQUIRED_PATHS = (
    "README.md",
    "site/content/index.md",
    "site/theme",
    ".github/workflows/pages.yml",
)

REQUIRED_EVIDENCE_PAGES = (
    "site/content/migration-evidence.md",
    "site/content/stress-tests.md",
    "site/content/build-week.md",
    "site/content/pipeline.md",
    "site/content/agent-archive.md",
    "site/content/codex-showcase.md",
)

GENERATED_GIT_PREFIXES = (
    "dist/",
    ".boris/",
    "rag/",
    "context/",
    "source-rag/",
    "zig-out/",
    "zig-cache/",
    "submission-preflight.json",
    "SUBMISSION_PREFLIGHT.md",
)

PLACEHOLDER_PATTERNS: Tuple[Tuple[str, re.Pattern[str]], ...] = (
    ("TODO", re.compile(r"\bTODO\b")),
    ("REPLACE_WITH", re.compile(r"REPLACE_WITH", re.IGNORECASE)),
    ("INSERT URL", re.compile(r"INSERT\s+URL", re.IGNORECASE)),
    ("TBD link", re.compile(r"\bTBD\b")),
    ("FIXME", re.compile(r"\bFIXME\b")),
    ("pending final upload", re.compile(r"pending\s+final\s+upload", re.IGNORECASE)),
    ("example.com placeholder", re.compile(r"https?://(?:www\.)?example\.com\b", re.IGNORECASE)),
    ("your-url-here", re.compile(r"your[-_]?url[-_]?here", re.IGNORECASE)),
)

WIKI_LINK_RE = re.compile(r"\[\[([a-zA-Z0-9_-]+)(?:\|[^\]]+)?\]\]")
FRONTMATTER_ID_RE = re.compile(r"^id:\s*([a-zA-Z0-9_-]+)\s*$", re.MULTILINE)
MD_LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")

EXTERNAL_LINK_SPECS: Tuple[Tuple[str, Tuple[str, ...], str], ...] = (
    (
        "boris_repository",
        (
            "https://github.com/drawmeanelephant/boris",
            "http://github.com/drawmeanelephant/boris",
        ),
        "BLOCKER",
    ),
    (
        "contest_repository",
        (
            "https://github.com/drawmeanelephant/openai-buildweek-2026",
            "http://github.com/drawmeanelephant/openai-buildweek-2026",
        ),
        "BLOCKER",
    ),
    (
        "v0.7.0_release",
        (
            "https://github.com/drawmeanelephant/boris/releases/tag/v0.7.0",
            "http://github.com/drawmeanelephant/boris/releases/tag/v0.7.0",
        ),
        "BLOCKER",
    ),
    (
        "live_demo",
        (
            "https://drawmeanelephant.github.io/openai-buildweek-2026",
            "http://drawmeanelephant.github.io/openai-buildweek-2026",
            "https://drawmeanelephant.github.io/openai-buildweek-2026/",
        ),
        "BLOCKER",
    ),
)

DEMO_VIDEO_HOST_RE = re.compile(
    r"https?://(?:www\.)?(?:youtube\.com|youtu\.be|vimeo\.com|loom\.com)/[^\s)\]>\"']+",
    re.IGNORECASE,
)
PENDING_DEMO_RE = re.compile(
    r"(demo\s+video|video).{0,80}(pending|todo|tbd|not\s+yet|upload)",
    re.IGNORECASE | re.DOTALL,
)

BENCHMARK_SIGNAL_RE = re.compile(
    r"("
    r"\bbenchmark\b|"
    r"\bthroughput\b|"
    r"\bms/page\b|"
    r"\bms\s*/\s*page\b|"
    r"\bseconds?\b|"
    r"\bx\s+faster\b|"
    r"\d+(?:\.\d+)?\s*(?:s|ms|×|x)\b|"
    r"ReleaseFast|"
    r"-j\s*\d+"
    r")",
    re.IGNORECASE,
)

PROVENANCE_CHECKS: Tuple[Tuple[str, re.Pattern[str]], ...] = (
    (
        "corpus_or_page_count",
        re.compile(
            r"("
            r"\b\d{2,5}[- ]?(?:page|pages|files|markdown files|content files)\b|"
            r"\bcorpus\b|"
            r"\b\d+(?:\.\d+)?\s*MB\b"
            r")",
            re.IGNORECASE,
        ),
    ),
    (
        "hardware",
        re.compile(
            r"("
            r"\bApple\s+M\d\b|"
            r"\bM\d\b|"
            r"\bcores?\b|"
            r"\bRAM\b|"
            r"\bGB\b|"
            r"\bCPU\b|"
            r"\bmachine\b"
            r")",
            re.IGNORECASE,
        ),
    ),
    (
        "optimization_mode",
        re.compile(
            r"("
            r"ReleaseFast|"
            r"ReleaseSafe|"
            r"Debug|"
            r"-Doptimize\s*=|"
            r"optimize(?:d|ation)?\s+mode|"
            r"production\s+build"
            r")",
            re.IGNORECASE,
        ),
    ),
    (
        "worker_count",
        re.compile(
            r"("
            r"-j\s*\d+|"
            r"\bj\s*=\s*\d+|"
            r"single[- ]threaded|"
            r"multi[- ]threaded|"
            r"\bworkers?\b|"
            r"\bthreads?\b|"
            r"parallel"
            r")",
            re.IGNORECASE,
        ),
    ),
    (
        "comparison_scope",
        re.compile(
            r"("
            r"same[- ]machine|"
            r"cross[- ]machine|"
            r"identical\s+(?:machine|host|hardware)|"
            r"same\s+hardware"
            r")",
            re.IGNORECASE,
        ),
    ),
)

BORIS_CMD_HINT_RE = re.compile(
    r'(?P<cmd>"?\$\{?BORIS\}?"?|[^\s]*boris)\s*(?P<body>(?:\\\n|[^\n]){20,800})',
    re.IGNORECASE,
)


@dataclass(frozen=True)
class Finding:
    severity: str
    code: str
    message: str
    path: str = ""
    detail: str = ""

    def sort_key(self) -> Tuple[int, str, str, str]:
        return (
            SEVERITY_ORDER.get(self.severity, 99),
            self.code,
            self.path,
            self.message,
        )


@dataclass
class Report:
    findings: List[Finding] = field(default_factory=list)

    def add(
        self,
        severity: str,
        code: str,
        message: str,
        path: str = "",
        detail: str = "",
    ) -> None:
        self.findings.append(
            Finding(
                severity=severity,
                code=code,
                message=message,
                path=_rel(path),
                detail=detail,
            )
        )

    def sorted_findings(self) -> List[Finding]:
        return sorted(self.findings, key=lambda f: f.sort_key())

    def counts(self) -> dict:
        c = Counter(f.severity for f in self.findings)
        return {
            "BLOCKER": int(c.get("BLOCKER", 0)),
            "WARNING": int(c.get("WARNING", 0)),
            "INFO": int(c.get("INFO", 0)),
        }

    def has_blockers(self) -> bool:
        return any(f.severity == "BLOCKER" for f in self.findings)


def _rel(path: str) -> str:
    """Normalize path to a repo-relative POSIX string (no absolute paths)."""
    if not path:
        return ""
    p = path.replace("\\", "/")
    # Strip accidental absolute prefixes while keeping relative structure.
    if p.startswith("/"):
        # Prefer last repo-ish segment if absolute; still avoid leaking home dirs.
        markers = (
            "/openai-buildweek-2026/",
            "/site/",
            "/tools/",
            "/.github/",
        )
        for marker in markers:
            idx = p.find(marker)
            if idx != -1:
                tail = p[idx + 1 :]  # drop leading slash from absolute
                # If marker includes repo name, keep from after it when useful.
                if marker == "/openai-buildweek-2026/":
                    return p[idx + len(marker) :]
                # For /site/ etc., find a better cut: keep from site/ tools/ .github/
                cut = p.find(marker.lstrip("/"), max(0, idx - 40))
                if cut != -1:
                    return p[cut:]
                return tail.lstrip("/")
        return Path(p).name
    if p.startswith("./"):
        p = p[2:]
    return p


def repo_root_from(start: Optional[Path] = None) -> Path:
    here = (start or Path.cwd()).resolve()
    for candidate in (here, *here.parents):
        if (candidate / "site" / "content").is_dir() and (candidate / "README.md").is_file():
            return candidate
    return here


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def iter_markdown_files(root: Path) -> List[Path]:
    content = root / "site" / "content"
    files: List[Path] = []
    if content.is_dir():
        files.extend(sorted(content.rglob("*.md")))
    for extra in ("README.md", "DESIGN-NOTES.md"):
        p = root / extra
        if p.is_file():
            files.append(p)
    # Deterministic unique order by relative path
    by_rel = { _rel(str(p.relative_to(root))): p for p in files }
    return [by_rel[k] for k in sorted(by_rel)]


def check_required_files(root: Path, report: Report) -> None:
    for rel in REQUIRED_PATHS:
        path = root / rel
        if path.exists():
            report.add("INFO", "required_path_present", f"Required path present: {rel}", rel)
        else:
            report.add("BLOCKER", "required_path_missing", f"Required path missing: {rel}", rel)

    theme = root / "site" / "theme"
    if theme.is_dir():
        # Theme should not be an empty directory.
        has_files = any(theme.rglob("*"))
        if not has_files:
            report.add(
                "BLOCKER",
                "theme_empty",
                "site/theme/ exists but contains no files",
                "site/theme",
            )
    for rel in REQUIRED_EVIDENCE_PAGES:
        path = root / rel
        if path.is_file():
            report.add("INFO", "evidence_page_present", f"Evidence/report page present: {rel}", rel)
        else:
            report.add(
                "BLOCKER",
                "evidence_page_missing",
                f"Required evidence/report page missing: {rel}",
                rel,
            )


def check_placeholders(root: Path, report: Report) -> None:
    # Published content + README are submission-facing.
    # DESIGN-NOTES.md is internal process notes and is not scanned here.
    targets: List[Path] = []
    content_dir = root / "site" / "content"
    if content_dir.is_dir():
        targets.extend(sorted(content_dir.rglob("*.md")))
    readme = root / "README.md"
    if readme.is_file():
        targets.append(readme)

    for path in targets:
        rel = _rel(str(path.relative_to(root)))
        text = read_text(path)
        for label, pattern in PLACEHOLDER_PATTERNS:
            for match in pattern.finditer(text):
                line_no = text.count("\n", 0, match.start()) + 1
                snippet = text[match.start() : match.start() + 80].splitlines()[0]
                # Demo-video pending is a WARNING (may land at checkout);
                # other placeholders in published content are BLOCKERs.
                if label == "pending final upload":
                    severity = "WARNING"
                    code = "placeholder_pending_upload"
                elif label in {"TODO", "REPLACE_WITH", "INSERT URL", "FIXME"}:
                    severity = "BLOCKER"
                    code = "stale_placeholder"
                else:
                    severity = "WARNING"
                    code = "placeholder_suspect"
                report.add(
                    severity,
                    code,
                    f"Placeholder marker '{label}' found at line {line_no}",
                    rel,
                    snippet.strip(),
                )


def discover_page_ids(root: Path) -> Tuple[Set[str], dict]:
    ids: Set[str] = set()
    id_to_path: dict = {}
    content_dir = root / "site" / "content"
    if not content_dir.is_dir():
        return ids, id_to_path
    for path in sorted(content_dir.rglob("*.md")):
        rel = _rel(str(path.relative_to(root)))
        text = read_text(path)
        match = FRONTMATTER_ID_RE.search(text)
        if match:
            page_id = match.group(1)
            ids.add(page_id)
            id_to_path[page_id] = rel
        else:
            # Caller may record missing id separately.
            id_to_path[f"__missing__:{rel}"] = rel
    return ids, id_to_path


def check_frontmatter_ids(root: Path, report: Report) -> Set[str]:
    content_dir = root / "site" / "content"
    ids: Set[str] = set()
    if not content_dir.is_dir():
        return ids
    for path in sorted(content_dir.rglob("*.md")):
        rel = _rel(str(path.relative_to(root)))
        text = read_text(path)
        match = FRONTMATTER_ID_RE.search(text)
        if not match:
            report.add(
                "BLOCKER",
                "missing_page_id",
                "Markdown page is missing a frontmatter id",
                rel,
            )
            continue
        page_id = match.group(1)
        if page_id in ids:
            report.add(
                "BLOCKER",
                "duplicate_page_id",
                f"Duplicate frontmatter id '{page_id}'",
                rel,
            )
        ids.add(page_id)
    if ids:
        report.add(
            "INFO",
            "page_ids_discovered",
            f"Discovered {len(ids)} content page id(s): {', '.join(sorted(ids))}",
        )
    return ids


def check_wiki_links(root: Path, valid_ids: Set[str], report: Report) -> None:
    content_dir = root / "site" / "content"
    if not content_dir.is_dir():
        return
    for path in sorted(content_dir.rglob("*.md")):
        rel = _rel(str(path.relative_to(root)))
        text = read_text(path)
        for line_no, line in enumerate(text.splitlines(), 1):
            for target in WIKI_LINK_RE.findall(line):
                if target not in valid_ids:
                    report.add(
                        "BLOCKER",
                        "broken_wiki_link",
                        f"Wiki-link [[{target}]] does not resolve to a content id (line {line_no})",
                        rel,
                        line.strip(),
                    )
                else:
                    report.add(
                        "INFO",
                        "wiki_link_ok",
                        f"Wiki-link [[{target}]] resolves (line {line_no})",
                        rel,
                    )


def _collect_urls(root: Path) -> Tuple[str, List[str]]:
    chunks: List[str] = []
    paths: List[str] = []
    for path in iter_markdown_files(root):
        rel = _rel(str(path.relative_to(root)))
        text = read_text(path)
        chunks.append(text)
        paths.append(rel)
    return "\n".join(chunks), paths


def check_external_links(root: Path, report: Report) -> None:
    blob, _ = _collect_urls(root)
    lowered = blob.lower()

    for name, candidates, severity in EXTERNAL_LINK_SPECS:
        found = any(c.lower() in lowered for c in candidates)
        # Allow live demo without trailing slash variants via startswith-ish match.
        if not found and name == "live_demo":
            found = "drawmeanelephant.github.io/openai-buildweek-2026" in lowered
        if found:
            report.add(
                "INFO",
                f"external_link_{name}",
                f"External project link present: {name}",
            )
        else:
            report.add(
                severity,
                f"external_link_missing_{name}",
                f"Missing required external project link: {name}",
                detail=f"Expected one of: {', '.join(candidates)}",
            )

    # Demo video: present real host => INFO; pending/missing => WARNING (not always a hard block).
    video_urls = DEMO_VIDEO_HOST_RE.findall(blob)
    if video_urls:
        report.add(
            "INFO",
            "demo_video_link_present",
            f"Demo video link present ({len(video_urls)} match(es))",
            detail=sorted(set(video_urls))[0],
        )
    elif PENDING_DEMO_RE.search(blob):
        report.add(
            "WARNING",
            "demo_video_pending",
            "Demo video is marked pending / not yet uploaded",
        )
    else:
        report.add(
            "WARNING",
            "demo_video_missing",
            "No demo video URL (YouTube/Vimeo/Loom) found in published content or README",
        )


def _benchmark_sections(text: str) -> List[Tuple[int, str]]:
    """Split text into coarse sections that look benchmark-related."""
    lines = text.splitlines()
    sections: List[Tuple[int, str]] = []
    i = 0
    while i < len(lines):
        if BENCHMARK_SIGNAL_RE.search(lines[i]):
            start = i
            # Grow a window around the signal.
            begin = max(0, start - 2)
            end = min(len(lines), start + 25)
            # Extend while subsequent lines still look related.
            j = end
            while j < min(len(lines), start + 60):
                if lines[j].strip() == "" and j + 1 < len(lines) and lines[j + 1].startswith("#"):
                    break
                if lines[j].startswith("## ") and j > start + 5:
                    break
                j += 1
            end = j
            chunk = "\n".join(lines[begin:end])
            sections.append((begin + 1, chunk))
            i = end
        else:
            i += 1
    return sections


def check_benchmark_provenance(root: Path, report: Report) -> None:
    # Focus on evidence pages; also scan other content for bare speed claims.
    targets = sorted((root / "site" / "content").rglob("*.md")) if (root / "site" / "content").is_dir() else []
    for path in targets:
        rel = _rel(str(path.relative_to(root)))
        text = read_text(path)
        # Only evaluate pages that make performance/benchmark claims.
        if not BENCHMARK_SIGNAL_RE.search(text):
            continue
        # Prefer whole-page provenance for dedicated evidence pages.
        dedicated = path.name in {
            "migration-evidence.md",
            "stress-tests.md",
            "index.md",
        }
        windows: List[Tuple[int, str]]
        if dedicated and (
            "benchmark" in text.lower()
            or "shootout" in text.lower()
            or re.search(r"\d+(?:\.\d+)?\s*(?:s|seconds|ms)", text, re.I)
        ):
            windows = [(1, text)]
        else:
            windows = _benchmark_sections(text)
            if not windows:
                continue

        for line_no, window in windows:
            missing = [
                name
                for name, pattern in PROVENANCE_CHECKS
                if not pattern.search(window)
            ]
            # comparison_scope is required only when a comparison claim is present.
            if "comparison_scope" in missing:
                if not re.search(r"\bvs\.?\b|\bversus\b|\bcompared\b|\bshootout\b|\bfaster\b", window, re.I):
                    missing = [m for m in missing if m != "comparison_scope"]

            # Ignore tiny windows that only mention seconds in prose without claims.
            has_numeric_claim = bool(
                re.search(
                    r"("
                    r"\d+(?:\.\d+)?\s*(?:s|ms|seconds)\b|"
                    r"\d+(?:\.\d+)?\s*[×x]\b|"
                    r"\bfaster\b|"
                    r"\bthroughput\b"
                    r")",
                    window,
                    re.I,
                )
            )
            if not has_numeric_claim:
                continue

            if missing:
                report.add(
                    "WARNING",
                    "benchmark_provenance_incomplete",
                    f"Benchmark/performance claim near line {line_no} lacks provenance: {', '.join(missing)}",
                    rel,
                    window.splitlines()[0][:120] if window else "",
                )
            else:
                report.add(
                    "INFO",
                    "benchmark_provenance_ok",
                    f"Benchmark/performance claim near line {line_no} has required provenance fields",
                    rel,
                )


def check_generated_not_tracked(root: Path, report: Report) -> None:
    try:
        proc = subprocess.run(
            ["git", "ls-files", "-z"],
            cwd=str(root),
            check=False,
            capture_output=True,
        )
    except FileNotFoundError:
        report.add(
            "WARNING",
            "git_unavailable",
            "git executable not found; skipped generated-output tracking check",
        )
        return

    if proc.returncode != 0:
        report.add(
            "WARNING",
            "git_ls_files_failed",
            "git ls-files failed; skipped generated-output tracking check",
            detail=(proc.stderr or b"").decode("utf-8", errors="replace")[:200],
        )
        return

    tracked = [p for p in proc.stdout.decode("utf-8", errors="replace").split("\0") if p]
    offenders: List[str] = []
    for path in tracked:
        norm = path.replace("\\", "/")
        for prefix in GENERATED_GIT_PREFIXES:
            if prefix.endswith("/"):
                if norm == prefix[:-1] or norm.startswith(prefix):
                    offenders.append(norm)
                    break
            else:
                if norm == prefix or norm.startswith(prefix + "/"):
                    offenders.append(norm)
                    break

    if offenders:
        for off in sorted(set(offenders)):
            report.add(
                "BLOCKER",
                "generated_output_tracked",
                f"Generated output is tracked in git: {off}",
                off,
            )
    else:
        report.add(
            "INFO",
            "generated_outputs_untracked",
            "No generated output paths are tracked in git",
        )


def check_documented_build_command(root: Path, report: Report) -> None:
    readme = root / "README.md"
    if not readme.is_file():
        report.add("BLOCKER", "readme_missing_for_build", "README.md missing; cannot verify build command")
        return

    text = read_text(readme)
    required_tokens = (
        "--input site/content",
        "--theme site/theme",
        "--html-dir dist",
    )
    missing = [t for t in required_tokens if t not in text]
    if missing:
        report.add(
            "BLOCKER",
            "build_command_incomplete",
            "README.md does not document the expected Boris field-guide build command",
            "README.md",
            f"Missing tokens: {', '.join(missing)}",
        )
        return

    # Paths referenced by the documented command must exist.
    for rel in ("site/content", "site/theme", "site/theme/layouts/home.html"):
        if not (root / rel).exists():
            report.add(
                "BLOCKER",
                "build_path_missing",
                f"Documented build path does not exist: {rel}",
                rel,
            )

    # Optional live compile when BORIS is available (no network).
    boris = os.environ.get("BORIS", "").strip()
    if boris and Path(boris).is_file() and os.access(boris, os.X_OK):
        # Do not write into the real dist/ during preflight unit isolation;
        # use a disposable directory under the repo that is gitignored.
        out_dir = root / "dist"
        cmd = [
            boris,
            "--input",
            "site/content",
            "--theme",
            "site/theme",
            "--layout-rule",
            "default",
            "id:index",
            "site/theme/layouts/home.html",
            "--html-dir",
            "dist",
            "--quiet",
        ]
        try:
            proc = subprocess.run(
                cmd,
                cwd=str(root),
                check=False,
                capture_output=True,
                text=True,
            )
        except OSError as exc:
            report.add(
                "WARNING",
                "boris_exec_failed",
                f"BORIS binary could not be executed: {exc}",
            )
            return
        if proc.returncode == 0 and (out_dir / "index.html").is_file():
            report.add(
                "INFO",
                "field_guide_build_ok",
                "Field guide built successfully with documented Boris command (BORIS env)",
            )
        else:
            report.add(
                "BLOCKER",
                "field_guide_build_failed",
                f"Documented Boris build failed (exit {proc.returncode})",
                detail=(proc.stderr or proc.stdout or "")[:400],
            )
    else:
        report.add(
            "INFO",
            "field_guide_build_documented",
            "Documented Boris build command is present; live compile skipped (set BORIS to verify)",
            "README.md",
        )


def _extract_top_level_jobs(yaml_text: str) -> Set[str]:
    """Best-effort extraction of top-level job ids without a YAML library."""
    jobs: Set[str] = set()
    in_jobs = False
    jobs_indent: Optional[int] = None
    for raw in yaml_text.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        if re.match(r"^jobs:\s*$", raw):
            in_jobs = True
            jobs_indent = indent
            continue
        if in_jobs:
            if jobs_indent is not None and indent <= jobs_indent and not raw.startswith(" "):
                # Left the jobs block (unlikely in GH workflows, but safe).
                if not raw.startswith(" ") and not raw.startswith("\t"):
                    in_jobs = False
                    continue
            # Job keys are direct children of jobs: (indent == jobs_indent + 2 typically).
            m = re.match(r"^([ \t]+)([A-Za-z0-9_-]+):\s*(?:#.*)?$", raw)
            if m:
                child_indent = len(m.group(1).replace("\t", "  "))
                if jobs_indent is not None and child_indent == jobs_indent + 2:
                    jobs.add(m.group(2))
            # Also accept tab-indented or 2-space children when jobs: is at column 0.
            elif jobs_indent == 0:
                m2 = re.match(r"^  ([A-Za-z0-9_-]+):\s*(?:#.*)?$", raw)
                if m2:
                    jobs.add(m2.group(1))
    return jobs


def check_pages_workflow(root: Path, report: Report) -> None:
    path = root / ".github" / "workflows" / "pages.yml"
    rel = ".github/workflows/pages.yml"
    if not path.is_file():
        report.add("BLOCKER", "workflow_missing", "Pages workflow file is missing", rel)
        return

    text = read_text(path)

    # Structural minimums without a YAML parser.
    structural_ok = True
    for token, code, msg in (
        ("on:", "workflow_missing_on", "Workflow is missing an 'on:' trigger section"),
        ("jobs:", "workflow_missing_jobs", "Workflow is missing a 'jobs:' section"),
        ("runs-on:", "workflow_missing_runs_on", "Workflow has no 'runs-on:' runner declaration"),
    ):
        if token not in text:
            structural_ok = False
            report.add("BLOCKER", code, msg, rel)

    jobs = _extract_top_level_jobs(text)
    if "build" not in jobs:
        # Fallback: accept a job whose name line is build-ish.
        if not re.search(r"(?m)^  build:\s*$", text):
            report.add(
                "BLOCKER",
                "workflow_missing_build_job",
                "Pages workflow has no top-level 'build' job",
                rel,
            )
            structural_ok = False
        else:
            jobs.add("build")

    # Require an actual status-check job named `ci`.
    has_ci_job = "ci" in jobs or bool(re.search(r"(?m)^  ci:\s*$", text))
    if not has_ci_job:
        report.add(
            "BLOCKER",
            "workflow_missing_ci_job",
            "Pages workflow is missing a top-level 'ci' status-check job",
            rel,
        )
        structural_ok = False
    else:
        # The ci job should gate on build result somehow.
        ci_section = ""
        m = re.search(r"(?ms)^  ci:\n(.*?)(?=^  [A-Za-z0-9_-]+:|\Z)", text)
        if m:
            ci_section = m.group(1)
        if "needs:" not in ci_section and "needs:" not in text:
            report.add(
                "WARNING",
                "workflow_ci_no_needs",
                "ci job does not declare needs: (status check may not gate on build)",
                rel,
            )
        # Prefer an explicit name: ci for GitHub required checks.
        if re.search(r"(?m)^\s+name:\s*ci\s*$", text) or re.search(
            r"(?m)^  ci:\s*$", text
        ):
            report.add(
                "INFO",
                "workflow_ci_job_present",
                "Pages workflow contains a 'ci' status-check job",
                rel,
            )

    # Must actually build Boris / the field guide in some form.
    if "boris" not in text.lower():
        report.add(
            "WARNING",
            "workflow_no_boris_reference",
            "Pages workflow does not reference Boris; field guide may not be built from source",
            rel,
        )
    if "site/content" not in text:
        report.add(
            "WARNING",
            "workflow_no_content_input",
            "Pages workflow does not reference site/content",
            rel,
        )

    if structural_ok and has_ci_job:
        report.add(
            "INFO",
            "workflow_structurally_valid",
            "Pages workflow is structurally valid for submission gating",
            rel,
        )


def run_checks(root: Path) -> Report:
    report = Report()
    check_required_files(root, report)
    check_placeholders(root, report)
    valid_ids = check_frontmatter_ids(root, report)
    check_wiki_links(root, valid_ids, report)
    check_external_links(root, report)
    check_benchmark_provenance(root, report)
    check_generated_not_tracked(root, report)
    check_documented_build_command(root, report)
    check_pages_workflow(root, report)
    return report


def render_markdown(report: Report) -> str:
    counts = report.counts()
    lines: List[str] = [
        "# Submission Preflight",
        "",
        "Deterministic contest readiness report for the OpenAI Build Week field guide.",
        "",
        "## Summary",
        "",
        f"- **BLOCKER:** {counts['BLOCKER']}",
        f"- **WARNING:** {counts['WARNING']}",
        f"- **INFO:** {counts['INFO']}",
        f"- **Status:** {'FAIL' if report.has_blockers() else 'PASS'}",
        "",
        "## Findings",
        "",
    ]
    findings = report.sorted_findings()
    if not findings:
        lines.append("_No findings._")
        lines.append("")
        return "\n".join(lines)

    # Group by severity for readability; order inside groups is already sorted.
    for severity in ("BLOCKER", "WARNING", "INFO"):
        group = [f for f in findings if f.severity == severity]
        if not group:
            continue
        lines.append(f"### {severity}")
        lines.append("")
        for f in group:
            loc = f" `{f.path}`" if f.path else ""
            lines.append(f"- **{f.code}**{loc}: {f.message}")
            if f.detail:
                # Keep detail single-line-ish for stable markdown.
                detail = " ".join(f.detail.split())
                if len(detail) > 200:
                    detail = detail[:197] + "..."
                lines.append(f"  - detail: {detail}")
        lines.append("")
    return "\n".join(lines)


def render_json(report: Report) -> str:
    counts = report.counts()
    payload = {
        "tool": "submission_preflight",
        "version": 1,
        "status": "fail" if report.has_blockers() else "pass",
        "counts": counts,
        "findings": [
            {
                "severity": f.severity,
                "code": f.code,
                "message": f.message,
                "path": f.path,
                "detail": f.detail,
            }
            for f in report.sorted_findings()
        ],
    }
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def write_reports(root: Path, report: Report) -> Tuple[Path, Path]:
    json_path = root / "submission-preflight.json"
    md_path = root / "SUBMISSION_PREFLIGHT.md"
    json_path.write_text(render_json(report), encoding="utf-8")
    md_path.write_text(render_markdown(report), encoding="utf-8")
    return json_path, md_path


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Deterministic OpenAI Build Week submission preflight",
    )
    parser.add_argument(
        "--root",
        default=".",
        help="Repository root (default: current directory)",
    )
    parser.add_argument(
        "--no-write",
        action="store_true",
        help="Do not write submission-preflight.json / SUBMISSION_PREFLIGHT.md",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress human summary on stdout (reports still written unless --no-write)",
    )
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    root = repo_root_from(Path(args.root))
    report = run_checks(root)

    if not args.no_write:
        write_reports(root, report)

    if not args.quiet:
        counts = report.counts()
        status = "FAIL" if report.has_blockers() else "PASS"
        print(f"submission-preflight: {status}")
        print(
            f"  BLOCKER={counts['BLOCKER']}  WARNING={counts['WARNING']}  INFO={counts['INFO']}"
        )
        # Print blockers and warnings for quick CI logs.
        for f in report.sorted_findings():
            if f.severity == "INFO":
                continue
            loc = f" ({f.path})" if f.path else ""
            print(f"  [{f.severity}] {f.code}{loc}: {f.message}")
        if not args.no_write:
            print("  wrote submission-preflight.json")
            print("  wrote SUBMISSION_PREFLIGHT.md")

    return 1 if report.has_blockers() else 0


if __name__ == "__main__":
    sys.exit(main())
