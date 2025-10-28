import json
import time
from pathlib import Path

import pytest
from app.utils.git_utils import (
    extract_commit_content_by_author)
from git import Repo, Actor, Commit, GitCommandError 

# ---------------------------
# Helpers to build test repos
# ---------------------------

def _actor(name="Test User", email="test@example.com"):
    return Actor(name, email)

def create_simple_repo(tmp_path: Path, *, author=_actor()):
    """
    Init repo with 2 commits by the same author (A then M).
    Returns: (repo, paths)
    """
    repo = Repo.init(tmp_path)
    f = tmp_path / "file.txt"

    # Commit 1 (ADD)
    f.write_text("hello\n", encoding="utf-8")
    repo.index.add([str(f)])
    repo.index.commit("add file", author=author)

    time.sleep(1)

    # Commit 2 (MODIFY)
    f.write_text("hello\nworld\n", encoding="utf-8")
    repo.index.add([str(f)])
    repo.index.commit("modify file", author=author)

    return repo, {"file": f}

def create_repo_two_authors(tmp_path: Path):
    """
    2 commits by Test User, 1 by Collaborator.
    """
    repo = Repo.init(tmp_path)
    f = tmp_path / "mix.txt"
    a1 = _actor("Test User", "test@example.com")
    a2 = _actor("Collaborator", "collab@example.com")

    f.write_text("v1\n", encoding="utf-8")
    repo.index.add([str(f)])
    repo.index.commit("t1", author=a1)

    time.sleep(1)

    f.write_text("v2\n", encoding="utf-8")
    repo.index.add([str(f)])
    repo.index.commit("c1", author=a2)

    time.sleep(1)

    f.write_text("v3\n", encoding="utf-8")
    repo.index.add([str(f)])
    repo.index.commit("t2", author=a1)

    return repo

def create_repo_with_merge(tmp_path: Path):
    """
    main: A1 -- A2
                 \ 
    feature:      F1 --(merge)-> M (merge commit by Test User)
    """
    repo = Repo.init(tmp_path)
    a = _actor("Test User", "test@example.com")

    main_file = tmp_path / "main.txt"
    main_file.write_text("base\n", encoding="utf-8")
    repo.index.add([str(main_file)])
    repo.index.commit("base", author=a)

    time.sleep(1)

    # second commit on main
    main_file.write_text("base\nmain\n", encoding="utf-8")
    repo.index.add([str(main_file)])
    repo.index.commit("main change", author=a)

    # create feature branch and switch
    feature = repo.create_head("feature")
    repo.head.reference = feature
    repo.head.reset(index=True, working_tree=True)

    feature_file = tmp_path / "feature.txt"
    feature_file.write_text("feat\n", encoding="utf-8")
    repo.index.add([str(feature_file)])
    repo.index.commit("feature work", author=a)

    # merge feature to main (create merge commit)
    repo.head.reference = repo.heads.master if hasattr(repo.heads, "master") else repo.heads.main
    repo.head.reset(index=True, working_tree=True)
    # Perform merge; author is the committer/author of the merge commit
    repo.git.merge("feature", "--no-ff", "--no-edit", "-m", "merge feature", author=f"{a.name} <{a.email}>")

    return repo

def create_repo_with_deletion_and_large_file(tmp_path: Path):
    """
    Create A (add big file > 500KB), M (modify small), D (delete).
    """
    repo = Repo.init(tmp_path)
    a = _actor()

    big = tmp_path / "big.txt"
    small = tmp_path / "small.txt"

    # ADD big file > 500KB
    big.write_bytes(b"a" * 600_000)
    repo.index.add([str(big)])
    repo.index.commit("add big", author=a)

    time.sleep(1)

    # ADD small
    small.write_text("x\n", encoding="utf-8")
    repo.index.add([str(small)])
    repo.index.commit("add small", author=a)

    time.sleep(1)

    # DELETE small
    (tmp_path / "small.txt").unlink()
    repo.index.remove([str(small)])
    repo.index.commit("delete small", author=a)

    return repo


# ---------------------------
# Tests
# ---------------------------

def test_returns_json_string_when_no_output_path(tmp_path):
    repo, _ = create_simple_repo(tmp_path)
    res = extract_commit_content_by_author(tmp_path, "test@example.com")
    assert isinstance(res, str)
    data = json.loads(res)
    # 2 commits by author
    assert len(data) == 2
    # Each commit should have files list
    assert all("files" in c for c in data)

def test_writes_to_file_when_output_path_provided(tmp_path):
    repo, _ = create_simple_repo(tmp_path)
    out_file = tmp_path / "out.json"
    res = extract_commit_content_by_author(tmp_path, "test@example.com", output_path=out_file)
    assert res is None
    assert out_file.exists()
    data = json.loads(out_file.read_text(encoding="utf-8"))
    assert len(data) == 2

def test_author_filtering_excludes_other_authors(tmp_path):
    create_repo_two_authors(tmp_path)
    # Only "Test User" commits should be returned (2 of them)
    res = extract_commit_content_by_author(tmp_path, "test@example.com")
    data = json.loads(res)
    assert len(data) == 2
    assert all(c["author_email"] == "test@example.com" for c in data)

def test_seen_dedup_across_branches(tmp_path):
    """
    Create two branches pointing to the same HEAD to ensure no duplicate commits
    in output (the seen set prevents double counting).
    """
    repo, _ = create_simple_repo(tmp_path)
    # Create a second branch ref at the same tip
    repo.create_head("mirror", commit=repo.head.commit)

    res = extract_commit_content_by_author(tmp_path, "test@example.com")
    data = json.loads(res)
    # Still only 2 commits
    assert len(data) == 2

def test_skip_merges_by_default(tmp_path):
    create_repo_with_merge(tmp_path)
    res = extract_commit_content_by_author(tmp_path, "test@example.com")
    data = json.loads(res)
    # Expect: base, main change, feature work (authored by same actor), but merge commit skipped.
    messages = [c["message_summary"].strip() for c in data]
    assert "merge feature" not in messages

def test_include_merges_when_flag_set(tmp_path):
    create_repo_with_merge(tmp_path)
    res = extract_commit_content_by_author(tmp_path, "test@example.com", include_merges=True)
    data = json.loads(res)
    messages = [c["message_summary"].strip() for c in data]
    assert "merge feature" in messages

def test_per_file_payload_includes_status_patch_and_content(tmp_path):
    repo, _ = create_simple_repo(tmp_path)
    res = extract_commit_content_by_author(tmp_path, "test@example.com")
    data = json.loads(res)

    # Look at last (oldest) commit first; it should ADD file
    oldest = data[-1]
    files = oldest["files"]
    assert len(files) >= 1
    add_record = next((f for f in files if f["status"] in {"A", "M"}), None)
    assert add_record is not None
    assert "patch" in add_record
    assert "content_after" in add_record
    assert add_record["content_after"] is not None  # small file -> included

def test_large_file_is_capped_with_placeholder(tmp_path):
    create_repo_with_deletion_and_large_file(tmp_path)
    res = extract_commit_content_by_author(tmp_path, "test@example.com")
    data = json.loads(res)

    # Find the commit that added the big file
    big_commit = next(c for c in data if c["message_summary"].startswith("add big"))
    # One file should be big.txt with placeholder
    f = big_commit["files"][0]
    assert f["status"] in {"A", "M"}
    assert "content_after" in f
    assert isinstance(f["content_after"], str)
    assert "File content omitted" in f["content_after"]
    # size_after may be present via b_blob.size in later commits, but here we rely on placeholder text

def test_deleted_file_has_no_content_after(tmp_path):
    create_repo_with_deletion_and_large_file(tmp_path)
    res = extract_commit_content_by_author(tmp_path, "test@example.com")
    data = json.loads(res)

    delete_commit = next(c for c in data if c["message_summary"].startswith("delete small"))
    # Expect at least one file entry with status D and content_after None
    del_entry = next(f for f in delete_commit["files"] if f["status"] == "D")
    # Code sets content_after only for non-deletes, so default None should remain
    assert del_entry.get("content_after") is None

def test_max_commits_limits_output(tmp_path):
    repo, _ = create_simple_repo(tmp_path)
    res = extract_commit_content_by_author(tmp_path, "test@example.com", max_commits=1)
    data = json.loads(res)
    assert len(data) == 1

def test_gitcommanderror_in_diff_is_captured(monkeypatch, tmp_path):
    """
    Monkeypatch Commit.diff to raise GitCommandError. The function should not crash;
    it should attach an error record in 'files'.
    """
    repo, _ = create_simple_repo(tmp_path)

    # Get one commit to patch its class method
    some_commit = next(iter(repo.iter_commits()))
    CommitCls = type(some_commit)

    def _boom(self, *args, **kwargs):
        raise GitCommandError("diff", "simulated failure")

    monkeypatch.setattr(CommitCls, "diff", _boom, raising=True)

    res = extract_commit_content_by_author(tmp_path, "test@example.com")
    data = json.loads(res)
    # All commit entries should include a files list with a single error dict
    assert len(data) >= 1
    assert "files" in data[0]
    assert isinstance(data[0]["files"], list)
    assert data[0]["files"][0].get("error", "").startswith("Could not get diff for commit:")

def test_invalid_repo_path_raises(tmp_path):
    with pytest.raises(ValueError):
        # get_repo inside should raise, propagates
        extract_commit_content_by_author(tmp_path / "not_a_repo", "test@example.com")

def test_output_file_fallback_on_write_error(tmp_path, monkeypatch):
    repo, _ = create_simple_repo(tmp_path)
    out_path = tmp_path / "cannot" / "write" / "here.json"

    # Monkeypatch Path.write_text to raise OSError to trigger fallback
    original_write_text = Path.write_text

    def _oops(self, *args, **kwargs):
        if self == out_path:
            raise OSError("disk full")
        return original_write_text(self, *args, **kwargs)

    monkeypatch.setattr(Path, "write_text", _oops, raising=True)

    res = extract_commit_content_by_author(tmp_path, "test@example.com", output_path=out_path)
    # Should return JSON string instead of None
    assert isinstance(res, str)
    data = json.loads(res)
    assert len(data) == 2