"""Git-Metriken je Repository (REQ-002 bis REQ-004).

Die entscheidende Stelle: ``commits_not_on_main`` wird über
``rev-list --count --all --not <default>`` gezählt und damit **einmal** je Commit.
Die naheliegende Alternative — ``rev-list --count default..branch`` pro Branch und
summieren — zählt denselben Commit auf jedem Branch, auf dem er liegt, mehrfach.
"""

from __future__ import annotations

from pathlib import Path

from . import gitio
from .discovery import RepoIdentity
from .models import RepoReport, UnmergedBranch

MAIN_CANDIDATES = ("main", "master")


def _detect_default_branch(repo: Path) -> str | None:
    """Der Default-Branch: origin/HEAD, sonst main, sonst master, sonst None."""
    head = gitio.run_git(repo, "symbolic-ref", "--quiet", "--short", "refs/remotes/origin/HEAD")
    if head:
        return head.rsplit("/", 1)[-1]
    for candidate in MAIN_CANDIDATES:
        if gitio.ref_exists(repo, f"refs/heads/{candidate}"):
            return candidate
    return None


def _current_branch(repo: Path) -> str:
    branch = gitio.run_git(repo, "symbolic-ref", "--quiet", "--short", "HEAD")
    if branch:
        return branch
    sha = gitio.run_git(repo, "rev-parse", "--short", "HEAD")
    return f"(detached@{sha})" if sha else ""


def _unmerged_branches(repo: Path, default: str) -> tuple[UnmergedBranch, ...]:
    """Branches, die nicht auf dem Default-Branch gelandet sind."""
    found: list[UnmergedBranch] = []

    local = gitio.run_git_lines(
        repo, "for-each-ref", "--format=%(refname:short)", "refs/heads"
    )
    for branch in local:
        ahead = gitio.count(repo, "rev-list", "--count", f"{default}..{branch}")
        if ahead:
            found.append(UnmergedBranch(branch, ahead, "local"))

    remotes = gitio.run_git_lines(
        repo, "for-each-ref", "--format=%(refname:short)", "refs/remotes"
    )
    for remote in remotes:
        if remote.endswith("/HEAD"):
            continue
        short = remote.split("/", 1)[-1]
        if short in local:
            continue
        ahead = gitio.count(repo, "rev-list", "--count", f"{default}..{remote}")
        if ahead:
            found.append(UnmergedBranch(short, ahead, "remote-only"))

    found.sort(key=lambda b: (-b.commits_ahead, b.name))
    return tuple(found)


def collect(identity: RepoIdentity, timeout: int = gitio.DEFAULT_TIMEOUT) -> RepoReport:
    """Sammelt alle Git-Metriken eines Repositories."""
    repo = Path(identity.path)
    default = _detect_default_branch(repo)

    commits_total = gitio.count(repo, "rev-list", "--count", "--all", timeout=timeout) or 0

    if default:
        commits_on_main = gitio.count(repo, "rev-list", "--count", default, timeout=timeout) or 0
        commits_not_main = (
            gitio.count(repo, "rev-list", "--count", "--all", "--not", default, timeout=timeout) or 0
        )
        branches_total = len(
            gitio.run_git_lines(repo, "for-each-ref", "--format=%(refname:short)", "refs/heads")
        )
        unmerged = _unmerged_branches(repo, default)
        origin_ref = f"origin/{default}"
        has_origin = gitio.ref_exists(repo, f"refs/remotes/{origin_ref}")
        if has_origin:
            ahead = gitio.count(repo, "rev-list", "--count", f"{origin_ref}..{default}", timeout=timeout)
            behind = gitio.count(repo, "rev-list", "--count", f"{default}..{origin_ref}", timeout=timeout)
        else:
            ahead = None
            behind = None
    else:
        commits_on_main = 0
        commits_not_main = commits_total
        branches_total = len(
            gitio.run_git_lines(repo, "for-each-ref", "--format=%(refname:short)", "refs/heads")
        )
        unmerged = ()
        ahead = None
        behind = None

    status = gitio.run_git_lines(repo, "status", "--porcelain")
    dirty_files = len(status)

    last_date = gitio.run_git(repo, "log", "-1", "--format=%cs")
    last_subject = gitio.run_git(repo, "log", "-1", "--format=%s")
    remote = gitio.run_git(repo, "remote", "get-url", "origin")

    return RepoReport(
        name=identity.name,
        path=identity.path,
        git_common_dir=identity.git_common_dir,
        is_worktree=identity.is_worktree,
        worktree_paths=identity.worktree_paths,
        default_branch=default,
        current_branch=_current_branch(repo),
        commits_total=commits_total,
        commits_on_main=commits_on_main,
        commits_not_on_main=commits_not_main,
        branches_total=branches_total,
        branches_unmerged=len(unmerged),
        unmerged_branches=unmerged,
        ahead_of_origin=ahead,
        behind_origin=behind,
        dirty_files=dirty_files,
        last_commit_date=last_date or None,
        last_commit_subject=last_subject or None,
        remote_url=remote or None,
    )
