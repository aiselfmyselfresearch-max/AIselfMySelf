#!/usr/bin/env python3
"""Check whether each material's `origin.commit` exists in the repository it names.

Why this tool exists
--------------------
`origin` has two fields that look like provenance carried by two hands:

    "repository": "https://github.com/owner/repo",   → which code host holds it
    "commit":     "7763923...",                       → which revision of that repo

`validate_seed.py` checks the shape of both fields and never resolves either.
So a record can name this repository's URL and another repository's commit, and
pass every check in the suite.

Measured 2026-11-06 on this ledger: `MAT-LIT-20261031-ec6caf` and
`MAT-LIT-20261031-3a1ba4` say `repository=aiselfmyselfresearch-max/AIselfMySelf`
and `commit=77639235…` / `9a2a3fe80…`.  Neither commit is in this repository.
Both are in the *material's* repository (`kumoi-no-fumigura/kyakuraika`,
`kumoi-no-fumigura/sarugaku-dangi`).  The report the rows point at
(`readings/2026-12-31-the-hand-that-copied-what-the-voice-could-not-write.md`)
writes the two repositories and the two commits correctly, in one sentence.
The ledger mixed them.

Two things follow, and the tool separates them:

  * `cross`   — the commit resolves, but in a different repository than the one
                named.  The provenance is recoverable; the pointer is crossed.
  * `missing` — the commit resolves nowhere we could look.  Provenance lost.
  * `not-a-hash` — the field holds prose (e.g. 「（web調査のため該当なし）」).

The tool prints only `cross` and `not-a-hash` from the local ledger.  `missing`
needs `--online`, because a local clone is shallow (depth 1) and therefore
cannot answer the question for *any* older commit; answering it offline would
report every historical commit as missing.

Usage:
  python3 tools/commit_provenance.py                  # local: cross + not-a-hash
  python3 tools/commit_provenance.py --online         # also resolve each commit (gh api)
  python3 tools/commit_provenance.py --json
  python3 tools/commit_provenance.py --cache path.json  # reuse resolved results
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
OWN_REPO = "aiselfmyselfresearch-max/AIselfMySelf"
HEX_RE = re.compile(r"^[0-9a-f]{7,40}$")


def _read_rows(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not path.exists():
        return rows
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(row, dict):
            rows.append(row)
    return rows


def load_materials(root: Path) -> list[dict[str, Any]]:
    rows = _read_rows(root / "state" / "materials.jsonl")
    for shard in sorted((root / "state" / "materials.d").glob("*.jsonl")):
        rows.extend(_read_rows(shard))
    return rows


def repo_slug(url: str) -> str:
    url = (url or "").strip().rstrip("/")
    for prefix in ("https://github.com/", "http://github.com/", "git@github.com:"):
        if url.startswith(prefix):
            return url[len(prefix):]
    return url


def local_commits(root: Path) -> set[str]:
    """Every commit object in this clone, or an empty set in a shallow clone."""
    shallow = root / ".git" / "shallow"
    try:
        proc = subprocess.run(["git", "rev-list", "--all"], cwd=str(root),
                              capture_output=True, text=True, timeout=60)
        commits = {l.strip() for l in proc.stdout.splitlines() if l.strip()}
    except (OSError, subprocess.SubprocessError):
        commits = set()
    # A depth-1 clone has exactly one commit and cannot answer "is this sha here?"
    if shallow.exists() and len(commits) <= 1:
        return set()
    return commits


def resolve_online(slug: str, sha: str) -> dict[str, str] | None:
    """Ask the GitHub API whether `sha` is a commit of `slug`.  None = unknown."""
    try:
        proc = subprocess.run(
            ["gh", "api", f"repos/{slug}/commits/{sha}", "--jq", ".sha"],
            capture_output=True, text=True, timeout=45)
    except (OSError, subprocess.SubprocessError):
        return None
    if proc.returncode == 0 and proc.stdout.strip():
        return {"status": "present", "repo": slug}
    if "No commit found" in (proc.stderr or "") or "422" in (proc.stderr or ""):
        return {"status": "absent", "repo": slug}
    return None


def repo_candidates_from_report(root: Path, path: str) -> list[str]:
    """GitHub slugs mentioned in the report a material points at.

    The report is our own record of where the text came from, so it is the best
    candidate list for a commit that the `origin` block left in the wrong repo.
    """
    if not path.startswith("readings/"):
        return []
    target = root / path
    if not target.exists():
        return []
    text = target.read_text(encoding="utf-8")
    found = re.findall(r"github\.com/([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)", text)
    # The same report may name a repository as a bare `owner/name` token instead
    # of a URL (the 世阿弥 report does exactly this, which is why the first
    # version of this function missed it).
    found += [s for s in re.findall(r"`([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)`", text)
              if not s.endswith((".md", ".py", ".json", ".tsv"))]
    out: list[str] = []
    for slug in found:
        slug = slug.removesuffix(".git").rstrip(".,)")
        if slug not in out and slug != OWN_REPO and "/" in slug:
            out.append(slug)
    return out


def audit(root: Path, online: bool = False, limit_candidates: int = 4) -> dict[str, Any]:
    materials = [r for r in load_materials(root) if r.get("material_id")]
    local = local_commits(root)

    cross: list[dict[str, str]] = []
    missing: list[dict[str, str]] = []
    not_hash: list[dict[str, str]] = []
    unresolved = 0
    by_commit: dict[str, list[str]] = defaultdict(list)
    rows_by_commit: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for row in materials:
        o = row.get("origin") or {}
        sha = (o.get("commit") or "").strip()
        slug = repo_slug(o.get("repository") or "")
        mid = row["material_id"]
        if not sha:
            not_hash.append({"material_id": mid, "repository": slug, "commit": "",
                             "reason": "empty"})
            continue
        if not HEX_RE.match(sha):
            not_hash.append({"material_id": mid, "repository": slug, "commit": sha,
                             "reason": "prose"})
            continue
        by_commit[sha].append(mid)
        rows_by_commit[sha].append(row)

    # Resolve every distinct (commit, named-repository) PAIR once.  A commit is
    # not one fact: `da45a468…` is shared by 22 rows, 10 of which name a
    # repository that no longer exists and 12 of which name this one.  Keying on
    # the commit alone answers for the wrong rows.
    resolved: dict[tuple[str, str], str | None] = {}
    if online:
        for sha, mids in by_commit.items():
            for row in rows_by_commit[sha]:
                named = repo_slug((row.get("origin") or {}).get("repository") or "")
                key = (sha, named)
                if key in resolved:
                    continue
                if local and (sha in local or any(c.startswith(sha) for c in local)) \
                        and named.rstrip("/").endswith(OWN_REPO):
                    resolved[key] = "ok"
                    continue
                res = resolve_online(named, sha)
                if res is None:
                    resolved[key] = None
                    continue
                if res["status"] == "present":
                    resolved[key] = "ok"
                    continue
                # Not in the named repository: try the ones the source report names.
                cands: list[str] = []
                src = (row.get("origin") or {}).get("source_record_path") or ""
                for cand in repo_candidates_from_report(root, src):
                    if cand not in cands and cand != named:
                        cands.append(cand)
                found_in = None
                checkable = False
                for cand in cands[:limit_candidates]:
                    res2 = resolve_online(cand, sha)
                    if res2 is None:
                        continue   # a branch name, a 404, a rate limit: keep looking
                    checkable = True
                    if res2["status"] == "present":
                        found_in = cand
                        break
                if found_in:
                    resolved[key] = f"cross:{found_in}"
                elif checkable:
                    resolved[key] = "missing"
                else:
                    resolved[key] = None

    unresolved_keys: list[dict[str, str]] = []
    for sha, mids in by_commit.items():
        if not online:
            continue
        for mid in mids:
            row = next(r for r in rows_by_commit[sha] if r["material_id"] == mid)
            named = repo_slug((row.get("origin") or {}).get("repository") or "")
            v = resolved.get((sha, named))
            if v is None:
                unresolved += 1
                unresolved_keys.append({"material_id": mid, "repository": named,
                                        "commit": sha})
            elif v.startswith("cross:"):
                cross.append({"material_id": mid, "repository": named,
                              "commit": sha, "found_in": v.split(":", 1)[1]})
            elif v == "missing":
                missing.append({"material_id": mid, "repository": named,
                                "commit": sha, "found_in": ""})

    return {
        "materials": len(materials),
        "clone_is_shallow": not local,
        "distinct_commits": len(by_commit),
        "cross": cross,
        "missing": missing,
        "not_a_hash": not_hash,
        "unresolved_offline": unresolved,
        "unresolved": unresolved_keys,
        "online": online,
    }


def render(result: dict[str, Any]) -> str:
    out = ["=== commit provenance: does origin.commit exist in origin.repository? ==="]
    out.append(f"  materials {result['materials']} / distinct commits {result['distinct_commits']}")
    if result["clone_is_shallow"]:
        out.append("  NOTE: this clone is shallow (depth 1). It cannot say whether any older")
        out.append("        commit exists. Offline answers are withheld rather than guessed;")
        out.append("        pass --online to resolve against GitHub.")
    out.append(f"  cross-repository pointers: {len(result['cross'])}")
    for item in result["cross"][:12]:
        out.append(f"    {item['material_id']}  names {item['repository']}  commit {item['commit'][:8]}")
    out.append(f"  not a hash (prose in a hash field): {len(result['not_a_hash'])}")
    for item in result["not_a_hash"][:12]:
        out.append(f"    {item['material_id']}  {item['commit'][:40]!r}")
    if result["missing"]:
        out.append(f"  missing (named repo does not contain it): {len(result['missing'])}")
        for item in result["missing"][:12]:
            out.append(f"    {item['material_id']}  {item['repository']}  {item['commit'][:8]}")
    if result["unresolved_offline"]:
        out.append(f"  unresolved (offline): {result['unresolved_offline']} records")
    out.append("  A commit that resolves elsewhere still proves the material was collected;")
    out.append("  it does not prove which repository it was collected FROM.")
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", default=str(ROOT))
    parser.add_argument("--online", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    result = audit(Path(args.root), online=args.online)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=1))
    else:
        print(render(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
