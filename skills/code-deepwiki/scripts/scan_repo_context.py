#!/usr/bin/env python3
"""
Scan a local or remote repository and output context files required for DeepWiki generation.
"""

import argparse
import fnmatch
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.parse import quote, urlparse, urlunparse


CODE_EXTENSIONS = {
  ".py",
  ".js",
  ".ts",
  ".tsx",
  ".jsx",
  ".java",
  ".go",
  ".rs",
  ".cpp",
  ".c",
  ".h",
  ".hpp",
  ".cs",
  ".swift",
  ".kt",
  ".php",
  ".rb",
  ".scala",
  ".sql",
}

DOC_EXTENSIONS = {".md", ".rst", ".txt", ".adoc"}

DEFAULT_EXCLUDED_DIRS = [
  ".git",
  ".hg",
  ".svn",
  ".venv",
  "venv",
  "node_modules",
  "__pycache__",
  ".idea",
  ".vscode",
  "dist",
  "build",
  "target",
]

DEFAULT_EXCLUDED_FILES = [
  ".DS_Store",
  "Thumbs.db",
  "*.lock",
  "*.min.js",
  "*.min.css",
  "*.map",
]

CATEGORY_PRIORITY = {"code": 0, "doc": 1, "other": 2}


def normalize_pattern(value: str) -> str:
  raw = value.strip().replace("\\", "/")
  raw = raw.lstrip("./")
  raw = raw.strip("/")
  return raw


def parse_list_arg(raw: Optional[str]) -> List[str]:
  if not raw:
    return []
  items: List[str] = []
  for part in raw.replace("\n", ",").split(","):
    pattern = normalize_pattern(part)
    if pattern:
      items.append(pattern)
  return sorted(dict.fromkeys(items))


def normalize_output_language(raw: str) -> str:
  value = raw.strip()
  if not value:
    raise ValueError("--output-language cannot be empty.")
  return value


def detect_repo_type(repo_url: str) -> str:
  host = urlparse(repo_url).netloc.lower()
  if "gitlab" in host:
    return "gitlab"
  if "bitbucket" in host:
    return "bitbucket"
  return "github"


def read_token(token_env: Optional[str]) -> Optional[str]:
  if not token_env:
    return None
  token = os.environ.get(token_env)
  if not token:
    raise ValueError(f"Environment variable '{token_env}' is not set or empty.")
  return token


def redact_sensitive(text: str, token: Optional[str]) -> str:
  if not token:
    return text
  masked = text.replace(token, "***TOKEN***")
  encoded = quote(token, safe="")
  return masked.replace(encoded, "***TOKEN***")


def build_clone_url(repo_url: str, repo_type: str, token: Optional[str]) -> str:
  if not token:
    return repo_url
  parsed = urlparse(repo_url)
  if not parsed.scheme or not parsed.netloc:
    raise ValueError(f"Invalid repository URL: {repo_url}")
  encoded = quote(token, safe="")
  if repo_type == "gitlab":
    netloc = f"oauth2:{encoded}@{parsed.netloc}"
  elif repo_type == "bitbucket":
    netloc = f"x-token-auth:{encoded}@{parsed.netloc}"
  else:
    netloc = f"{encoded}@{parsed.netloc}"
  return urlunparse(parsed._replace(netloc=netloc))


def run_git_clone(repo_url: str, clone_url: str, target_dir: Path, token: Optional[str]) -> None:
  cmd = ["git", "clone", "--depth", "1", "--single-branch", clone_url, str(target_dir)]
  result = subprocess.run(cmd, capture_output=True, text=True, check=False)
  if result.returncode != 0:
    detail = (result.stderr or result.stdout or "").strip()
    detail = redact_sensitive(detail, token)
    raise RuntimeError(f"Failed to clone repository '{repo_url}': {detail}")


def iter_parent_dirs(rel_path: str) -> List[str]:
  parts = rel_path.split("/")
  parents: List[str] = []
  for index in range(1, len(parts)):
    parents.append("/".join(parts[:index]))
  return parents


def path_matches_dirs(rel_path: str, patterns: List[str]) -> bool:
  parents = iter_parent_dirs(rel_path)
  for pattern in patterns:
    clean = normalize_pattern(pattern)
    if not clean:
      continue
    if rel_path == clean or rel_path.startswith(f"{clean}/"):
      return True
    for parent in parents:
      if parent == clean or fnmatch.fnmatch(parent, clean):
        return True
    if fnmatch.fnmatch(rel_path, f"{clean}/**"):
      return True
  return False


def path_matches_files(rel_path: str, patterns: List[str]) -> bool:
  file_name = rel_path.split("/")[-1]
  for pattern in patterns:
    clean = normalize_pattern(pattern)
    if not clean:
      continue
    if rel_path == clean or file_name == clean:
      return True
    if fnmatch.fnmatch(rel_path, clean) or fnmatch.fnmatch(file_name, clean):
      return True
  return False


def should_keep_file(
  rel_path: str,
  include_dirs: List[str],
  include_files: List[str],
  exclude_dirs: List[str],
  exclude_files: List[str],
) -> bool:
  has_include_rules = bool(include_dirs or include_files)
  if has_include_rules:
    include_hit = False
    if include_dirs and path_matches_dirs(rel_path, include_dirs):
      include_hit = True
    if include_files and path_matches_files(rel_path, include_files):
      include_hit = True
    if not include_hit:
      return False

  if exclude_dirs and path_matches_dirs(rel_path, exclude_dirs):
    return False
  if exclude_files and path_matches_files(rel_path, exclude_files):
    return False
  return True


def classify_file(rel_path: str) -> Tuple[str, str]:
  suffix = Path(rel_path).suffix.lower()
  if suffix in CODE_EXTENSIONS:
    language = suffix.lstrip(".") or "unknown"
    return "code", language
  if suffix in DOC_EXTENSIONS:
    return "doc", suffix.lstrip(".") or "doc"
  return "other", suffix.lstrip(".") or "unknown"


def collect_repository_files(
  repo_root: Path,
  include_dirs: List[str],
  include_files: List[str],
  exclude_dirs: List[str],
  exclude_files: List[str],
) -> List[Dict[str, object]]:
  records: List[Dict[str, object]] = []
  for path in repo_root.rglob("*"):
    if not path.is_file():
      continue
    rel_path = path.relative_to(repo_root).as_posix()
    if not should_keep_file(rel_path, include_dirs, include_files, exclude_dirs, exclude_files):
      continue
    category, language = classify_file(rel_path)
    records.append(
      {
        "path": rel_path,
        "category": category,
        "language": language,
        "size_bytes": path.stat().st_size,
      }
    )
  records.sort(key=lambda item: (CATEGORY_PRIORITY[item["category"]], item["path"]))
  return records


def find_readme_content(repo_root: Path) -> str:
  root_names = ["README.md", "readme.md", "Readme.md", "README.MD"]
  for name in root_names:
    candidate = repo_root / name
    if candidate.is_file():
      return candidate.read_text(encoding="utf-8", errors="replace")

  candidates = [
    item
    for item in repo_root.rglob("*")
    if item.is_file() and item.name.lower().startswith("readme")
  ]
  candidates.sort(key=lambda item: (len(item.relative_to(repo_root).parts), item.as_posix()))
  for candidate in candidates:
    return candidate.read_text(encoding="utf-8", errors="replace")
  return ""


def write_outputs(out_dir: Path, file_tree: str, readme: str, manifest: Dict[str, object]) -> None:
  out_dir.mkdir(parents=True, exist_ok=True)
  (out_dir / "file_tree.txt").write_text(file_tree, encoding="utf-8")
  (out_dir / "readme.md").write_text(readme, encoding="utf-8")
  (out_dir / "source_manifest.json").write_text(
    json.dumps(manifest, indent=2, ensure_ascii=False),
    encoding="utf-8",
  )


def build_manifest(
  repo_meta: Dict[str, object],
  output_language: str,
  include_dirs: List[str],
  include_files: List[str],
  exclude_dirs: List[str],
  exclude_files: List[str],
  files: List[Dict[str, object]],
) -> Dict[str, object]:
  code_files = sum(1 for item in files if item["category"] == "code")
  doc_files = sum(1 for item in files if item["category"] == "doc")
  total_bytes = sum(int(item["size_bytes"]) for item in files)
  return {
    "repo": repo_meta,
    "generation": {
      "output_language": output_language,
    },
    "filters": {
      "include_dirs": include_dirs,
      "include_files": include_files,
      "exclude_dirs": exclude_dirs,
      "exclude_files": exclude_files,
    },
    "summary": {
      "total_files": len(files),
      "code_files": code_files,
      "doc_files": doc_files,
      "other_files": len(files) - code_files - doc_files,
      "total_size_bytes": total_bytes,
    },
    "files": files,
  }


def scan_repository(args: argparse.Namespace) -> int:
  include_dirs = parse_list_arg(args.include_dirs)
  include_files = parse_list_arg(args.include_files)
  exclude_dirs = sorted(dict.fromkeys(DEFAULT_EXCLUDED_DIRS + parse_list_arg(args.exclude_dirs)))
  exclude_files = sorted(dict.fromkeys(DEFAULT_EXCLUDED_FILES + parse_list_arg(args.exclude_files)))

  repo_meta: Dict[str, object]
  token: Optional[str] = None
  temp_dir: Optional[tempfile.TemporaryDirectory] = None

  try:
    output_language = normalize_output_language(args.output_language)
    if args.repo_path:
      repo_root = Path(args.repo_path).expanduser().resolve()
      if not repo_root.exists() or not repo_root.is_dir():
        raise ValueError(f"Local path does not exist or is not a directory: {repo_root}")
      repo_meta = {"mode": "local", "repo_type": "local", "repo_path": str(repo_root)}
    else:
      if not args.repo_url.startswith(("http://", "https://")):
        raise ValueError("--repo-url must start with http:// or https://")
      token = read_token(args.token_env)
      repo_type = args.repo_type or detect_repo_type(args.repo_url)
      temp_dir = tempfile.TemporaryDirectory(prefix="code-deepwiki-repo-")
      repo_root = Path(temp_dir.name) / "repo"
      clone_url = build_clone_url(args.repo_url, repo_type, token)
      run_git_clone(args.repo_url, clone_url, repo_root, token)
      repo_meta = {"mode": "remote", "repo_type": repo_type, "repo_url": args.repo_url}

    files = collect_repository_files(
      repo_root,
      include_dirs=include_dirs,
      include_files=include_files,
      exclude_dirs=exclude_dirs,
      exclude_files=exclude_files,
    )
    file_tree = "\n".join(sorted(item["path"] for item in files))
    readme = find_readme_content(repo_root)
    manifest = build_manifest(
      repo_meta=repo_meta,
      output_language=output_language,
      include_dirs=include_dirs,
      include_files=include_files,
      exclude_dirs=exclude_dirs,
      exclude_files=exclude_files,
      files=files,
    )

    out_dir = Path(args.out_dir).expanduser().resolve()
    write_outputs(out_dir, file_tree, readme, manifest)
    print(f"[OK] Context files generated under: {out_dir}")
    print(f"[OK] Files scanned: {manifest['summary']['total_files']}")
    print(f"[OK] Output language: {output_language}")
    return 0
  except Exception as exc:
    message = redact_sensitive(str(exc), token)
    print(f"[ERROR] {message}", file=sys.stderr)
    return 1
  finally:
    if temp_dir is not None:
      temp_dir.cleanup()


def build_parser() -> argparse.ArgumentParser:
  parser = argparse.ArgumentParser(description="Scan repository and build DeepWiki context files.")
  group = parser.add_mutually_exclusive_group(required=True)
  group.add_argument("--repo-path", help="Local repository path")
  group.add_argument("--repo-url", help="Remote repository URL")
  parser.add_argument(
    "--repo-type",
    choices=["github", "gitlab", "bitbucket"],
    help="Repository type for remote URLs; auto-detected when omitted.",
  )
  parser.add_argument("--token-env", help="Environment variable name that stores private repo token.")
  parser.add_argument("--include-dirs", default="", help="Comma or newline separated directory filters.")
  parser.add_argument("--include-files", default="", help="Comma or newline separated file filters.")
  parser.add_argument("--exclude-dirs", default="", help="Comma or newline separated directory filters.")
  parser.add_argument("--exclude-files", default="", help="Comma or newline separated file filters.")
  parser.add_argument(
    "--output-language",
    default="English",
    help="Target language for generated wiki documents. Default: English.",
  )
  parser.add_argument("--out-dir", default="docs/code-deepwiki", help="Output directory for context files.")
  return parser


def main() -> int:
  parser = build_parser()
  args = parser.parse_args()
  if args.repo_path and args.repo_type:
    parser.error("--repo-type is only valid with --repo-url")
  return scan_repository(args)


if __name__ == "__main__":
  raise SystemExit(main())
