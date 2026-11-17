#!/usr/bin/env bash
# avenoxbeyin v1/v2.0/v2.1/v2.2 -> v2.3 upgrade. Single process, transactional, fail loud.
#
# Why this file exists: the upgrade used to live as a chain of fenced Bash blocks in SETUP.md that
# assigned shell variables in one block and used them in the next. Every Claude Bash call is a
# separate process, so those variables were empty later and the paths collapsed to "/daily",
# "/.beyin-version" and friends. Everything now runs in ONE process with an absolute --vault.
#
# Usage:
#   bash scripts/upgrade.sh --vault /abs/path/to/vault --stage check
#   bash scripts/upgrade.sh --vault /abs/path/to/vault --stage apply     [--confirm-rename] [--confirm-local-hooks]
#   bash scripts/upgrade.sh --vault /abs/path/to/vault --stage finalize
#
# Stages:
#   check     read only. Prints the plan and the confirmations the user must give. Mutates nothing.
#   apply     snapshot, rename, copy, merge, migrate. Does NOT write .beyin-version.
#   finalize  re-runs every gate, commits with an explicit allow-list, then writes .beyin-version
#             atomically as the very last filesystem write.
#
# Exit codes: 0 ok | 1 hard failure | 2 usage | 3 nothing to do | 10 needs --confirm-rename
#             11 needs --confirm-local-hooks
set -euo pipefail

BEYIN_TARGET_VERSION="2.3.0"
BEYIN_SCRIPT_VERSION="2.3.0"
BEYIN_MEMORY_DIR_NAME="🔮 850-Companion"
BEYIN_HOOK_FILES="lib.sh session-start.sh prompt-counter.sh session-end.sh pre-compact.sh"
BEYIN_SCRIPT_FILES="flush.py compile.py _portalock.py render_codex_hooks.py render_antigravity_hooks.py antigravity_hooks.py graf_kontrol.py"
BEYIN_SKILL_DIRS="beyin-doktor gecmis-import"
BEYIN_BACKUP_ROOT="${BEYIN_BACKUP_ROOT:-$HOME/.avenoxbeyin-yedek}"

say()  { printf '%s\n' "$*"; }
step() { printf '\n== %s\n' "$*"; }
die()  { printf 'ERROR: %s\n' "$*" >&2; exit 1; }

canon_dir() { CDPATH= cd -- "$1" 2>/dev/null && pwd -P; }

# ---------------------------------------------------------------- arguments
VAULT=""
STAGE=""
CONFIRM_RENAME=0
CONFIRM_LOCAL_HOOKS=0

while [ "$#" -gt 0 ]; do
  case "$1" in
    --vault)                VAULT="${2:-}"; shift 2 ;;
    --vault=*)              VAULT="${1#--vault=}"; shift ;;
    --stage)                STAGE="${2:-}"; shift 2 ;;
    --stage=*)              STAGE="${1#--stage=}"; shift ;;
    --confirm-rename)       CONFIRM_RENAME=1; shift ;;
    --confirm-local-hooks)  CONFIRM_LOCAL_HOOKS=1; shift ;;
    --version)              say "$BEYIN_SCRIPT_VERSION"; exit 0 ;;
    -h|--help)              sed -n '2,25p' "$0"; exit 0 ;;
    *)                      printf 'Unknown argument: %s\n' "$1" >&2; exit 2 ;;
  esac
done

case "$STAGE" in
  check|apply|finalize) ;;
  "") printf '%s\n' "Missing argument: --stage check|apply|finalize" >&2; exit 2 ;;
  *)  printf 'Invalid --stage: %s\n' "$STAGE" >&2; exit 2 ;;
esac

[ -n "$VAULT" ] || { printf '%s\n' "Missing argument: --vault (absolute path)" >&2; exit 2; }
case "$VAULT" in
  /*) ;;
  *)  printf '%s\n' "--vault must be an absolute path, relative paths are not accepted: $VAULT" >&2; exit 2 ;;
esac

# ---------------------------------------------------------------- paths
SELF_DIR=$(canon_dir "$(dirname -- "$0")") || die "could not resolve my own location"
REPO=$(canon_dir "$SELF_DIR/..") || die "could not resolve the repo root"
[ -d "$REPO/template/.claude/hooks" ] || die "the repo root looks wrong, template/.claude/hooks is missing: $REPO"

[ -d "$VAULT" ] || die "vault folder does not exist: $VAULT"
V=$(canon_dir "$VAULT") || die "could not resolve the vault path: $VAULT"

[ -n "$V" ]      || die "the vault path resolved to empty"
[ "$V" != "/" ]  || die "/ is not accepted as a vault"
[ "$V" != "$HOME" ] || die "the home directory is not accepted as a vault"
[ "$V" != "$REPO" ] || die "the vault cannot be the repo itself: $V"
case "$V/" in "$REPO/"*) die "the vault cannot be inside the repo: $V" ;; esac
case "$REPO/" in "$V/"*) die "the repo cannot be inside the vault: $V" ;; esac

# ---------------------------------------------------------------- v1 markers
[ -f "$V/CLAUDE.md" ] || die "no v1 marker: $V/CLAUDE.md not found. This is not a beyin vault."
MEM_DIR=$(find "$V" -mindepth 1 -maxdepth 1 -type d -name "🔮 850-*" -print 2>/dev/null | head -1)
[ -n "$MEM_DIR" ] || die "no v1 marker: no '🔮 850-*' memory folder found. This is not a beyin vault."
MEM_NAME=$(basename "$MEM_DIR")

command -v python3 >/dev/null 2>&1 || die "python3 not found. The v2 machine layer cannot be installed without python3 (macOS: xcode-select --install)."

CUR_VERSION=""
[ -f "$V/.beyin-version" ] && CUR_VERSION=$(sed -n '1p' "$V/.beyin-version" 2>/dev/null || printf '')

STATE_DIR="$V/.claude/scripts/.state"
MANIFEST="$STATE_DIR/upgrade-manifest.txt"
STAGE_MARK="$STATE_DIR/upgrade-stage"

# ---------------------------------------------------------------- helpers
git_id() {
  # Always pass an identity so an unset global git config cannot turn a real failure into
  # "nothing to commit". Uses the user's own identity when it exists.
  GIT_N=$(git -C "$V" config user.name  2>/dev/null || printf '')
  GIT_E=$(git -C "$V" config user.email 2>/dev/null || printf '')
  [ -n "$GIT_N" ] || GIT_N="avenoxbeyin"
  [ -n "$GIT_E" ] || GIT_E="beyin@localhost"
}

assert_no_secret_staged() {
  # Only ADDING or MODIFYING a secret path is a leak. A staged DELETION of one is the cure
  # (untrack_ignored_secrets stages exactly that), so status D must not trip the alarm,
  # otherwise the cure itself aborts the upgrade.
  BAD=$(git -C "$V" diff --cached --name-status 2>/dev/null \
        | awk '$1 !~ /^D/ { $1=""; sub(/^[ \t]+/, ""); print }' \
        | grep -E '(^|/)\.env$|settings\.local\.json|\.yedek|\.bak$|\.orig$|\.pem$|\.key$' || printf '')
  if [ -n "$BAD" ]; then
    git -C "$V" reset -q >/dev/null 2>&1 || :
    say "Files that must not be staged were found and the stage was cleared:"
    printf '%s\n' "$BAD"
    die "a file that may carry secrets was about to be committed, upgrade stopped"
  fi
}

untrack_ignored_pycache() {
  # .gitignore now carries __pycache__/ and *.pyc, but an ignore rule never untracks a path that
  # is already in the index. A vault upgraded before those rules existed keeps its compiled
  # bytecode tracked: the finalize gate imports the scripts, python rewrites the .pyc files, and
  # "git add" stages them into the upgrade commit on every single run. Untrack them here, before
  # the snapshot, and leave every file on disk.
  #
  # Deliberately separate from untrack_ignored_secrets: bytecode is not a secret, so this must not
  # print the "revoke your API key" warning that function ends with.
  command -v git >/dev/null 2>&1 || return 0
  [ -d "$V/.git" ] || return 0
  TRACKED_PYC=$(git -C "$V" ls-files -- '*.pyc' '*/__pycache__/*' 2>/dev/null | sort -u || printf '')
  [ -n "$TRACKED_PYC" ] || return 0
  PYC_COUNT=$(printf '%s\n' "$TRACKED_PYC" | grep -c . || printf '0')
  printf '%s\n' "$TRACKED_PYC" | while IFS= read -r PYC; do
    [ -n "$PYC" ] || continue
    git -C "$V" rm --cached -q -- "$PYC" >/dev/null 2>&1 \
      || die "could not untrack compiled Python file: $PYC"
  done
  say "untracked (compiled Python, the files stay on disk): $PYC_COUNT"
}

record() { printf '%s\n' "$1" >> "$MANIFEST"; }

copy_file() {
  # copy_file <src-abs> <dst-abs> <manifest-relpath>
  cp "$1" "$2" || die "could not copy: $1 -> $2"
  [ -s "$2" ] || die "the copy came out empty: $2"
  record "$3"
}

ensure_gitignore() {
  GI="$V/.gitignore"
  [ -f "$GI" ] || : > "$GI"
  # Guarantee the file ends with a newline before appending.
  if [ -s "$GI" ] && [ "$(tail -c 1 "$GI" | wc -l | tr -d ' ')" = "0" ]; then
    printf '\n' >> "$GI"
  fi
  GI_ADDED=0
  while IFS= read -r LINE; do
    [ -n "$LINE" ] || continue
    if ! grep -qxF "$LINE" "$GI" 2>/dev/null; then
      printf '%s\n' "$LINE" >> "$GI"
      GI_ADDED=$((GI_ADDED + 1))
    fi
  done <<'IGN'
.claude/settings.local.json
.env
*.yedek
*.yedek-*
*.bak
*.orig
.claude/hooks/.state/
.claude/scripts/.state/*
!.claude/scripts/.state/.gitkeep
.DS_Store
.obsidian/workspace*
.obsidian/cache
__pycache__/
*.pyc
IGN
  say "gitignore: $GI_ADDED lines added"
}

untrack_ignored_secrets() {
  # A v1 vault created on a machine without a global ignore rule has
  # .claude/settings.local.json COMMITTED. Adding the path to .gitignore does not untrack an
  # already-tracked file, so the later "git add -u" restages it, assert_no_secret_staged kills
  # the run, and the upgrade dead-ends with every gate green. Untrack it here, before the
  # snapshot, so the ignore rule can actually take effect.
  command -v git >/dev/null 2>&1 || return 0
  [ -d "$V/.git" ] || return 0
  UNTRACKED_ANY=0
  for SECRET in ".claude/settings.local.json" ".env"; do
    if git -C "$V" ls-files --error-unmatch -- "$SECRET" >/dev/null 2>&1; then
      git -C "$V" rm --cached -q -- "$SECRET" || die "could not untrack: $SECRET"
      say "untracked (the file stays on disk): $SECRET"
      UNTRACKED_ANY=1
    fi
  done
  # Any backup artefact that a previous half-run left tracked.
  TRACKED_BAK=$(git -C "$V" ls-files -- '*.yedek' '*.yedek-*' '*.bak' '*.orig' 2>/dev/null || printf '')
  if [ -n "$TRACKED_BAK" ]; then
    printf '%s\n' "$TRACKED_BAK" | while IFS= read -r B; do
      [ -n "$B" ] || continue
      git -C "$V" rm --cached -q -- "$B" >/dev/null 2>&1 || :
      say "untracked (backup leftover): $B"
    done
    UNTRACKED_ANY=1
  fi
  if [ "$UNTRACKED_ANY" = "1" ]; then
    say ""
    say "!! WARNING: these files are no longer tracked, but they are still in the HISTORY."
    say "!! If they contain an API key, REVOKE the key with the provider and issue a new one."
    say "!! To clean the history: git filter-repo or BFG, a separate job from the upgrade."
    say ""
  fi
}

local_hooks_report() {
  # Prints: "<count-of-v1-beyin-entries> <count-of-unrelated-entries>"
  python3 - "$V" <<'PY'
import json, os, sys
p = os.path.join(sys.argv[1], ".claude", "settings.local.json")
V1 = ("session-start.sh", "prompt-counter.sh", "session-end.sh", "pre-compact.sh")
EV = ("SessionStart", "UserPromptSubmit", "SessionEnd", "PreCompact")
try:
    with open(p, encoding="utf-8") as f:
        d = json.load(f)
except FileNotFoundError:
    print("0 0")
    sys.exit(0)
except ValueError:
    # Present but not parseable. Not the same as absent: the user has a file we cannot
    # reason about, so the caller must stop rather than silently assume "no hooks".
    print("BROKEN invalid-json")
    sys.exit(0)
if not isinstance(d, dict):
    print("BROKEN not-a-json-object")
    sys.exit(0)
mine = other = 0
for ev, matchers in (d.get("hooks") or {}).items():
    for m in (matchers or []):
        for h in (m.get("hooks") or []):
            c = h.get("command", "") or ""
            if ev in EV and any(b in c for b in V1):
                mine += 1
            else:
                other += 1
print(mine, other)
PY
}

# ---------------------------------------------------------------- preconditions shared by stages
if [ "$CUR_VERSION" = "$BEYIN_TARGET_VERSION" ] && [ "$STAGE" != "finalize" ]; then
  say "This vault is already stamped v$BEYIN_TARGET_VERSION: $V"
  say "Nothing to do. If something is missing, run 'beyin doktor'."
  exit 3
fi
case "$CUR_VERSION" in
  ""|2.0.0|2.1.0|2.2.0|"$BEYIN_TARGET_VERSION") ;;
  *) die "incompatible version stamp: '$CUR_VERSION' (supported: empty v1, 2.0.0, 2.1.0, 2.2.0 or $BEYIN_TARGET_VERSION)" ;;
esac

NEED_RENAME=0
[ "$MEM_NAME" = "$BEYIN_MEMORY_DIR_NAME" ] || NEED_RENAME=1

LOCAL_REPORT=$(local_hooks_report 2>/dev/null || printf '')
set -- $LOCAL_REPORT
LOCAL_MINE="${1:-}"
LOCAL_OTHER="${2:-}"
case "$LOCAL_MINE" in
  BROKEN)
    say ".claude/settings.local.json cannot be read: ${LOCAL_OTHER:-unknown reason}"
    say "This file must be a JSON object, for example: {\"hooks\": { ... }}"
    say "Fix it by hand or temporarily move it out of the vault, then run the upgrade again."
    die "upgrade stopped, nothing was changed"
    ;;
esac
case "$LOCAL_MINE" in
  ''|*[!0-9]*) die "the settings.local.json scan did not return the expected number: '${LOCAL_REPORT}'" ;;
esac
case "$LOCAL_OTHER" in
  ''|*[!0-9]*) die "the settings.local.json scan did not return the expected number: '${LOCAL_REPORT}'" ;;
esac

# ---------------------------------------------------------------- STAGE: check
if [ "$STAGE" = "check" ]; then
  step "PLAN (nothing was changed)"
  say "vault           : $V"
  say "repo            : $REPO"
  say "memory folder   : $MEM_NAME"
  say "current version : ${CUR_VERSION:-v1 (no .beyin-version)}"
  say "git repository  : $([ -d "$V/.git" ] && printf 'present' || printf 'none, will be created')"
  say "settings.local  : $LOCAL_MINE v1 beyin hooks, $LOCAL_OTHER unrelated hook entries"
  step "CONFIRMATION REQUIRED"
  NEEDED=0
  if [ "$NEED_RENAME" = "1" ]; then
    NEEDED=1
    say "1) The memory folder is named '$MEM_NAME'. The v2 hooks and scripts read the fixed"
    say "   '$BEYIN_MEMORY_DIR_NAME' path, so the rename is MANDATORY for v2."
    say "   The contents do not change at all, only the folder name; the partner's name is already inside the files."
    say "   If the user says yes: --confirm-rename"
    say "   If the user says no: no upgrade, and no version stamp is written."
  fi
  if [ "$LOCAL_MINE" != "0" ]; then
    NEEDED=1
    say "2) settings.local.json contains $LOCAL_MINE v1 beyin hooks. If they are not cleaned up, every event"
    say "   fires twice. Only these entries are removed; $LOCAL_OTHER unrelated hooks and all other keys"
    say "   such as env and permissions are kept. The backup is written OUTSIDE the repo and vault with 0600."
    say "   If the user says yes: --confirm-local-hooks"
    say "   If the user says no: no upgrade, and no version stamp is written."
  fi
  [ "$NEEDED" = "1" ] || say "(no extra confirmation needed)"
  step "NEXT STEP"
  say "bash \"$REPO/scripts/upgrade.sh\" --vault \"$V\" --stage apply$([ "$NEED_RENAME" = "1" ] && printf ' --confirm-rename')$([ "$LOCAL_MINE" != "0" ] && printf ' --confirm-local-hooks')"
  exit 0
fi

# ---------------------------------------------------------------- STAGE: apply
if [ "$STAGE" = "apply" ]; then
  if [ "$NEED_RENAME" = "1" ] && [ "$CONFIRM_RENAME" != "1" ]; then
    say "CONFIRMATION REQUIRED: the memory folder '$MEM_NAME' must be renamed to '$BEYIN_MEMORY_DIR_NAME'."
    say "This is mandatory for v2. Ask the user; if they say yes, run again with --confirm-rename."
    say "If they say no, do not start the upgrade at all: no version stamp will be written, the vault stays v1."
    exit 10
  fi
  if [ "$LOCAL_MINE" != "0" ] && [ "$CONFIRM_LOCAL_HOOKS" != "1" ]; then
    say "CONFIRMATION REQUIRED: the $LOCAL_MINE v1 beyin hooks in settings.local.json must be cleaned up."
    say "If they are not cleaned up, the hooks run twice on every event. Ask the user; if they say yes,"
    say "run again with --confirm-local-hooks. If they say no, there is no upgrade."
    exit 11
  fi

  mkdir -p "$STATE_DIR"
  : > "$MANIFEST"

  step "1/9 .gitignore (BEFORE the snapshot, so no secret gets staged)"
  ensure_gitignore
  untrack_ignored_secrets
  untrack_ignored_pycache

  step "2/9 snapshot (verified)"
  SNAP_OK=0
  if command -v git >/dev/null 2>&1; then
    if [ ! -d "$V/.git" ]; then
      git -C "$V" init -q || die "git init failed: $V"
      say "git repository created"
    fi
    git_id
    git -C "$V" add -A || die "git add failed"
    assert_no_secret_staged
    HEAD_BEFORE=$(git -C "$V" rev-parse HEAD 2>/dev/null || printf 'NONE')
    STAGED=$(git -C "$V" diff --cached --name-only | wc -l | tr -d ' ')
    if [ "$STAGED" = "0" ]; then
      [ "$HEAD_BEFORE" != "NONE" ] || die "nothing to commit and no HEAD either: could not take a snapshot"
      say "working tree already clean, the current HEAD counts as the snapshot: $HEAD_BEFORE"
      SNAP_OK=1
    else
      git -C "$V" -c user.name="$GIT_N" -c user.email="$GIT_E" \
        commit -q -m "snapshot before the v2 upgrade" \
        || die "the snapshot commit failed, $STAGED files are left staged. Upgrade stopped."
      HEAD_AFTER=$(git -C "$V" rev-parse HEAD 2>/dev/null || printf 'NONE')
      [ "$HEAD_AFTER" != "NONE" ] || die "could not read HEAD after the commit"
      [ "$HEAD_AFTER" != "$HEAD_BEFORE" ] || die "HEAD did not change after the commit, the snapshot was not actually taken"
      say "snapshot taken: $HEAD_AFTER ($STAGED files)"
      SNAP_OK=1
    fi
  fi
  if [ "$SNAP_OK" != "1" ]; then
    say "no git, taking a verified copy OUTSIDE the vault"
    mkdir -p "$BEYIN_BACKUP_ROOT"; chmod 700 "$BEYIN_BACKUP_ROOT" 2>/dev/null || :
    COPY_DST="$BEYIN_BACKUP_ROOT/$(basename "$V")-v1-$(date +%Y%m%d-%H%M%S)"
    cp -R "$V" "$COPY_DST" || die "could not take a backup copy: $COPY_DST"
    SRC_N=$(find "$V" -mindepth 1 | wc -l | tr -d ' ')
    DST_N=$(find "$COPY_DST" -mindepth 1 | wc -l | tr -d ' ')
    [ "$SRC_N" = "$DST_N" ] || die "backup verification failed: source $SRC_N, copy $DST_N"
    say "verified backup: $COPY_DST ($DST_N items)"
  fi

  step "3/9 memory folder name"
  if [ "$NEED_RENAME" = "1" ]; then
    [ ! -e "$V/$BEYIN_MEMORY_DIR_NAME" ] || die "the target folder already exists: $BEYIN_MEMORY_DIR_NAME. This must be resolved by hand."
    BEFORE_N=$(find "$MEM_DIR" -mindepth 1 | wc -l | tr -d ' ')
    if [ -d "$V/.git" ] && command -v git >/dev/null 2>&1; then
      git -C "$V" mv "$MEM_NAME" "$BEYIN_MEMORY_DIR_NAME" || die "git mv failed: $MEM_NAME"
    else
      mv "$MEM_DIR" "$V/$BEYIN_MEMORY_DIR_NAME" || die "mv failed: $MEM_NAME"
    fi
    [ -d "$V/$BEYIN_MEMORY_DIR_NAME" ] || die "the target folder is missing after the rename"
    [ ! -d "$MEM_DIR" ] || die "the old folder is still there after the rename"
    AFTER_N=$(find "$V/$BEYIN_MEMORY_DIR_NAME" -mindepth 1 | wc -l | tr -d ' ')
    [ "$BEFORE_N" = "$AFTER_N" ] || die "the item count changed: before $BEFORE_N, after $AFTER_N"
    say "'$MEM_NAME' -> '$BEYIN_MEMORY_DIR_NAME' ($AFTER_N items kept)"
    MEM_DIR="$V/$BEYIN_MEMORY_DIR_NAME"
    MEM_NAME="$BEYIN_MEMORY_DIR_NAME"
  else
    say "already correct: $MEM_NAME"
  fi

  step "4/9 folders"
  mkdir -p "$V/daily" "$V/knowledge/concepts" "$V/knowledge/connections" \
           "$V/.claude/scripts/.state" "$V/.claude/skills" "$V/.claude/hooks"
  for K in "daily/.gitkeep" "knowledge/concepts/.gitkeep" "knowledge/connections/.gitkeep" \
           ".claude/scripts/.state/.gitkeep"; do
    [ -f "$V/$K" ] || : > "$V/$K"
  done
  say "folders and .gitkeep files in place"

  step "5/9 scripts and skills (code, overwritten)"
  for F in $BEYIN_SCRIPT_FILES; do
    copy_file "$REPO/template/.claude/scripts/$F" "$V/.claude/scripts/$F" ".claude/scripts/$F"
    say "  .claude/scripts/$F"
  done
  for S in $BEYIN_SKILL_DIRS; do
    mkdir -p "$V/.claude/skills/$S"
    copy_file "$REPO/template/.claude/skills/$S/SKILL.md" "$V/.claude/skills/$S/SKILL.md" ".claude/skills/$S/SKILL.md"
    say "  .claude/skills/$S/SKILL.md"
  done

  step "6/9 seed files (only if missing)"
  SEEDS_TMP=$(mktemp)
  printf '%s\n' "knowledge/index.md" "knowledge/log.md" > "$SEEDS_TMP"
  printf '%s\n' "$BEYIN_MEMORY_DIR_NAME/Kurallar.md" >> "$SEEDS_TMP"
  while IFS= read -r S; do
    if [ -f "$V/$S" ]; then
      say "  skipped (already exists): $S"
    else
      copy_file "$REPO/template/$S" "$V/$S" "$S"
      say "  added: $S"
    fi
  done < "$SEEDS_TMP"
  rm -f "$SEEDS_TMP"

  step "7/9 hooks (code, overwritten)"
  for H in $BEYIN_HOOK_FILES; do
    copy_file "$REPO/template/.claude/hooks/$H" "$V/.claude/hooks/$H" ".claude/hooks/$H"
    chmod +x "$V/.claude/hooks/$H" || die "chmod +x failed: $H"
    bash -n "$V/.claude/hooks/$H" || die "syntax error: $H"
    say "  $H (executable, syntax ✓)"
  done

  step "7b/9 shared store, Codex and Antigravity hook registrations"
  mkdir -p "$V/.agents" "$V/.codex"

  if [ ! -e "$V/AGENTS.md" ] && [ ! -L "$V/AGENTS.md" ]; then
    ln -s "CLAUDE.md" "$V/AGENTS.md" || die "could not create the AGENTS.md symlink"
  elif [ -L "$V/AGENTS.md" ] && [ "$(readlink "$V/AGENTS.md" 2>/dev/null || :)" = "CLAUDE.md" ]; then
    :
  elif [ -f "$V/AGENTS.md" ] && cmp -s "$V/AGENTS.md" "$V/CLAUDE.md"; then
    rm -f "$V/AGENTS.md" || die "could not remove the identical AGENTS.md"
    ln -s "CLAUDE.md" "$V/AGENTS.md" || die "could not create the AGENTS.md symlink"
  else
    die "AGENTS.md exists and is not the same as CLAUDE.md; merge the two routers by hand and run again"
  fi

  if [ ! -e "$V/.agents/skills" ] && [ ! -L "$V/.agents/skills" ]; then
    ln -s "../.claude/skills" "$V/.agents/skills" || die "could not create the .agents/skills symlink"
  elif [ -L "$V/.agents/skills" ] && [ "$(readlink "$V/.agents/skills" 2>/dev/null || :)" = "../.claude/skills" ]; then
    :
  else
    die ".agents/skills is already a separate store; merge its contents with .claude/skills by hand"
  fi

  if [ ! -e "$V/.codex/hooks" ] && [ ! -L "$V/.codex/hooks" ]; then
    ln -s "../.claude/hooks" "$V/.codex/hooks" || die "could not create the .codex/hooks symlink"
  elif [ -L "$V/.codex/hooks" ] && [ "$(readlink "$V/.codex/hooks" 2>/dev/null || :)" = "../.claude/hooks" ]; then
    :
  else
    die ".codex/hooks is already a separate store; merge its contents with .claude/hooks by hand"
  fi

  python3 "$V/.claude/scripts/render_codex_hooks.py" --vault "$V" --platform posix \
    >/dev/null || die "could not generate .codex/hooks.json"
  python3 "$V/.claude/scripts/render_antigravity_hooks.py" --vault "$V" --platform posix \
    >/dev/null || die "could not generate .agents/hooks.json"
  record "AGENTS.md"
  record ".agents/skills"
  record ".codex/hooks"
  record ".codex/hooks.json"
  record ".agents/hooks.json"
  say "  AGENTS.md -> CLAUDE.md"
  say "  .agents/skills -> .claude/skills"
  say "  .codex/hooks -> .claude/hooks"
  say "  .codex/hooks.json (absolute paths, SessionEnd 3s)"
  say "  .agents/hooks.json (Antigravity PreInvocation + Stop adapter)"

  step "8/9 settings.json hook registration (merge, safe to re-run)"
  python3 - "$V" "$REPO" <<'PY' || die "settings.json merge failed"
import json, os, sys, tempfile
vault, repo = sys.argv[1], sys.argv[2]
dst = os.path.join(vault, ".claude", "settings.json")
src = os.path.join(repo, "template", ".claude", "settings.json")
with open(src, encoding="utf-8") as f:
    wanted = json.load(f).get("hooks", {})
try:
    with open(dst, encoding="utf-8") as f:
        cur = json.load(f)
except FileNotFoundError:
    cur = {}
except ValueError:
    print("EXISTING settings.json is broken JSON, cannot merge", file=sys.stderr)
    raise SystemExit(1)
cur.setdefault("hooks", {})

def commands(matchers):
    out = []
    for m in matchers or []:
        for h in (m.get("hooks") or []):
            out.append(h.get("command", "") or "")
    return out

added = 0
for event, matchers in wanted.items():
    have = commands(cur["hooks"].setdefault(event, []))
    for m in matchers:
        wants = [os.path.basename(c.strip('"')) for c in commands([m])]
        if any(any(b and b in h for h in have) for b in wants):
            continue
        cur["hooks"][event].append(m)
        have = commands(cur["hooks"][event])
        added += 1

fd, tmp = tempfile.mkstemp(dir=os.path.dirname(dst))
with os.fdopen(fd, "w", encoding="utf-8") as f:
    json.dump(cur, f, indent=2, ensure_ascii=False)
    f.write("\n")
os.replace(tmp, dst)
print("hook entries added:", added)
PY
  record ".claude/settings.json"

  step "9/9 settings.local.json migration"
  if [ "$LOCAL_MINE" = "0" ]; then
    say "no v1 beyin hooks in settings.local.json, left untouched"
  else
    mkdir -p "$BEYIN_BACKUP_ROOT"; chmod 700 "$BEYIN_BACKUP_ROOT" 2>/dev/null || :
    BK="$BEYIN_BACKUP_ROOT/$(basename "$V")-settings.local.json-$(date +%Y%m%d-%H%M%S)"
    ( umask 077; cp "$V/.claude/settings.local.json" "$BK" ) || die "could not take a backup: $BK"
    chmod 600 "$BK" || die "could not set backup permissions: $BK"
    [ -s "$BK" ] || die "backup is empty: $BK"
    say "backup (OUTSIDE the repo and vault, 0600): $BK"
    python3 - "$V" <<'PY' || die "settings.local.json migration failed"
import json, os, sys, tempfile
p = os.path.join(sys.argv[1], ".claude", "settings.local.json")
V1 = ("session-start.sh", "prompt-counter.sh", "session-end.sh", "pre-compact.sh")
EV = ("SessionStart", "UserPromptSubmit", "SessionEnd", "PreCompact")
with open(p, encoding="utf-8") as f:
    d = json.load(f)
before_keys = sorted(d)
hooks = d.get("hooks") or {}
removed = kept = 0
new_hooks = {}
for ev, matchers in hooks.items():
    new_matchers = []
    for m in (matchers or []):
        entries = m.get("hooks") or []
        keep = []
        for h in entries:
            c = h.get("command", "") or ""
            if ev in EV and any(b in c for b in V1):
                removed += 1
            else:
                keep.append(h)
                kept += 1
        if not entries:
            new_matchers.append(m)
            continue
        if keep:
            m2 = dict(m)
            m2["hooks"] = keep
            new_matchers.append(m2)
    if new_matchers:
        new_hooks[ev] = new_matchers
if new_hooks:
    d["hooks"] = new_hooks
else:
    d.pop("hooks", None)
fd, tmp = tempfile.mkstemp(dir=os.path.dirname(p))
os.chmod(tmp, 0o600)
with os.fdopen(fd, "w", encoding="utf-8") as f:
    json.dump(d, f, indent=2, ensure_ascii=False)
    f.write("\n")
os.replace(tmp, p)
print("v1 hook entries removed:", removed, "| unrelated hook entries kept:", kept)
print("keys before:", before_keys)
print("keys after :", sorted(d))
PY
  fi

  printf 'apply %s\n' "$(date +%Y-%m-%dT%H:%M:%S)" > "$STAGE_MARK"

  step "APPLY DONE"
  say "The version stamp has NOT been written YET. This is deliberate."
  LEFT=$(grep -rl "{{" "$V/knowledge" "$V/.claude/skills" "$V/$BEYIN_MEMORY_DIR_NAME" 2>/dev/null || printf '')
  if [ -n "$LEFT" ]; then
    say "These files still contain {{PLACEHOLDER}}, fill them in:"
    printf '%s\n' "$LEFT"
  else
    say "No unresolved {{PLACEHOLDER}}."
  fi
  say ""
  say "Next: fill in the placeholders, run 'beyin doktor', then:"
  say "bash \"$REPO/scripts/upgrade.sh\" --vault \"$V\" --stage finalize"
  exit 0
fi

# ---------------------------------------------------------------- STAGE: finalize
step "FINALIZE: re-running every gate"
[ -f "$STAGE_MARK" ] || die "--stage apply must be run first ($STAGE_MARK missing)"

FAIL=0
gate() { if [ "$2" = "ok" ]; then say "  ✓ $1"; else say "  ✗ $1 :: $2"; FAIL=$((FAIL + 1)); fi; }

R="ok"; [ "$MEM_NAME" = "$BEYIN_MEMORY_DIR_NAME" ] || R="memory folder is still '$MEM_NAME'"
gate "memory folder name" "$R"

for H in $BEYIN_HOOK_FILES; do
  R="ok"
  if [ ! -f "$V/.claude/hooks/$H" ]; then R="file missing"
  elif [ ! -x "$V/.claude/hooks/$H" ]; then R="not executable"
  elif ! bash -n "$V/.claude/hooks/$H" 2>/dev/null; then R="syntax error"
  elif ! grep -q 'BEYIN_INVOKED_BY' "$V/.claude/hooks/$H"; then R="no recursion guard"
  fi
  gate "hook $H" "$R"
done

for F in $BEYIN_SCRIPT_FILES; do
  R="ok"
  if [ ! -s "$V/.claude/scripts/$F" ]; then R="file missing or empty"
  elif ! python3 -m py_compile "$V/.claude/scripts/$F" >/dev/null 2>&1; then R="does not compile"
  fi
  gate "script $F" "$R"
done

for S in $BEYIN_SKILL_DIRS; do
  R="ok"; [ -s "$V/.claude/skills/$S/SKILL.md" ] || R="SKILL.md missing"
  gate "skill $S" "$R"
done

R="ok"
[ -L "$V/AGENTS.md" ] && [ "$(readlink "$V/AGENTS.md" 2>/dev/null || :)" = "CLAUDE.md" ] || R="no AGENTS.md -> CLAUDE.md symlink"
gate "shared router" "$R"

R="ok"
[ -L "$V/.agents/skills" ] && [ "$(readlink "$V/.agents/skills" 2>/dev/null || :)" = "../.claude/skills" ] || R=".agents/skills is not the shared store"
gate "shared skill store" "$R"

R="ok"
[ -L "$V/.codex/hooks" ] && [ "$(readlink "$V/.codex/hooks" 2>/dev/null || :)" = "../.claude/hooks" ] || R=".codex/hooks is not the shared store"
gate "shared hook store" "$R"

R=$(python3 - "$V" <<'PY'
import json, os, sys
v = os.path.realpath(sys.argv[1])
p = os.path.join(v, ".codex", "hooks.json")
try:
    with open(p, encoding="utf-8") as f:
        d = json.load(f)
except (OSError, ValueError) as exc:
    print("could not read hooks.json: %s" % exc)
    raise SystemExit(0)
wanted = {
    "SessionStart": ("session-start.sh", 15),
    "UserPromptSubmit": ("prompt-counter.sh", 5),
    "PreCompact": ("pre-compact.sh", 10),
    "SessionEnd": ("session-end.sh", 3),
}
bad = []
for event, (name, timeout) in wanted.items():
    found = []
    for matcher in (d.get("hooks", {}).get(event) or []):
        for hook in (matcher.get("hooks") or []):
            command = hook.get("command", "") or ""
            if name in command:
                found.append(hook)
    if len(found) != 1:
        bad.append("%s=%d" % (event, len(found)))
    elif not os.path.isabs(found[0].get("command", "").strip("'\"")):
        bad.append("%s relative" % event)
    elif found[0].get("timeout") != timeout:
        bad.append("%s timeout" % event)
print("ok" if not bad else ", ".join(bad))
PY
) || R="check did not run"
gate "Codex absolute hook registration" "$R"

R=$(python3 - "$V" <<'PY'
import json, os, sys
v = os.path.realpath(sys.argv[1])
p = os.path.join(v, ".agents", "hooks.json")
try:
    with open(p, encoding="utf-8") as f:
        d = json.load(f)
except (OSError, ValueError) as exc:
    print("could not read hooks.json: %s" % exc)
    raise SystemExit(0)
managed = d.get("avenox-beyin") if isinstance(d, dict) else None
bad = []
for event, action, timeout in (
    ("PreInvocation", "pre-invocation", 15),
    ("Stop", "stop", 5),
):
    entries = (managed or {}).get(event) or []
    if len(entries) != 1:
        bad.append("%s=%d" % (event, len(entries)))
        continue
    command = entries[0].get("command", "") or ""
    if "antigravity_hooks.py" not in command or action not in command:
        bad.append("%s command" % event)
    elif entries[0].get("timeout") != timeout:
        bad.append("%s timeout" % event)
print("ok" if not bad else ", ".join(bad))
PY
) || R="check did not run"
gate "Antigravity hook registration" "$R"

for D in "daily" "knowledge/concepts" "knowledge/connections" ".claude/scripts/.state"; do
  R="ok"; [ -d "$V/$D" ] || R="folder missing"
  gate "folder $D" "$R"
done
for F in "knowledge/index.md" "knowledge/log.md" "$BEYIN_MEMORY_DIR_NAME/Kurallar.md"; do
  R="ok"; [ -f "$V/$F" ] || R="file missing"
  gate "file $F" "$R"
done

R="ok"
if [ -f "$MANIFEST" ]; then
  PH=""
  while IFS= read -r M; do
    [ -n "$M" ] || continue
    [ -f "$V/$M" ] || continue
    case "$M" in *.md) ;; *) continue ;; esac
    if grep -q "{{" "$V/$M" 2>/dev/null; then PH="$PH $M"; fi
  done < "$MANIFEST"
  [ -z "$PH" ] || R="unresolved placeholder:$PH"
fi
gate "placeholder resolution" "$R"

R=$(python3 - "$V" <<'PY'
import json, os, sys
v = sys.argv[1]
V1 = ("session-start.sh", "prompt-counter.sh", "session-end.sh", "pre-compact.sh")
EV = ("SessionStart", "UserPromptSubmit", "SessionEnd", "PreCompact")
count = {e: 0 for e in EV}
for name in ("settings.json", "settings.local.json"):
    p = os.path.join(v, ".claude", name)
    try:
        with open(p, encoding="utf-8") as f:
            d = json.load(f)
    except FileNotFoundError:
        continue
    except ValueError:
        print("broken JSON: %s" % name)
        raise SystemExit(0)
    for ev, matchers in (d.get("hooks") or {}).items():
        if ev not in EV:
            continue
        for m in (matchers or []):
            for h in (m.get("hooks") or []):
                c = h.get("command", "") or ""
                if any(b in c for b in V1):
                    count[ev] += 1
bad = ["%s=%d" % (e, n) for e, n in count.items() if n != 1]
print("ok" if not bad else "there must be exactly 1 hook per event: " + ", ".join(bad))
PY
) || R="check did not run"
gate "active hook count (settings.json + settings.local.json)" "$R"

R="ok"
LEAK=$(find "$V" -path "$V/.git" -prune -o -type f \( -name "*.yedek" -o -name "settings.local.json.*" -o -name "*.yedek-*" \) -print 2>/dev/null | head -5)
[ -z "$LEAK" ] || R="the vault contains a backup that may carry secrets: $(printf '%s' "$LEAK" | tr '\n' ' ')"
gate "no backup leftovers inside the vault" "$R"

R="ok"; grep -qxF ".claude/settings.local.json" "$V/.gitignore" 2>/dev/null || R=".gitignore does not protect settings.local.json"
gate ".gitignore protection" "$R"

if [ "$FAIL" != "0" ]; then
  say ""
  die "$FAIL gates failed. The version stamp was NOT WRITTEN, the vault stays v1. Fix the above first."
fi

step "commit (explicit allow-list)"
if command -v git >/dev/null 2>&1 && [ -d "$V/.git" ]; then
  git_id
  git -C "$V" reset -q >/dev/null 2>&1 || :
  ALLOW_TMP=$(mktemp)
  printf '%s\n' ".gitignore" "daily" "knowledge" ".claude/hooks" ".claude/scripts" \
                ".claude/skills" ".claude/settings.json" ".agents" ".codex" "AGENTS.md" \
                "$BEYIN_MEMORY_DIR_NAME" > "$ALLOW_TMP"
  while IFS= read -r P; do
    [ -n "$P" ] || continue
    [ -e "$V/$P" ] || continue
    git -C "$V" add -- "$P" || die "git add failed: $P"
  done < "$ALLOW_TMP"
  rm -f "$ALLOW_TMP"
  # A rename leaves the old path staged as a deletion; pick that up without add -A.
  git -C "$V" add -u -- . >/dev/null 2>&1 || :
  assert_no_secret_staged
  HEAD_BEFORE=$(git -C "$V" rev-parse HEAD 2>/dev/null || printf 'NONE')
  STAGED=$(git -C "$V" diff --cached --name-only | wc -l | tr -d ' ')
  if [ "$STAGED" = "0" ]; then
    say "nothing staged (the upgrade may already be committed)"
  else
    git -C "$V" -c user.name="$GIT_N" -c user.email="$GIT_E" \
      commit -q -m "upgraded to v2" \
      || die "the upgrade commit failed, $STAGED files are staged. The version stamp was NOT WRITTEN."
    HEAD_AFTER=$(git -C "$V" rev-parse HEAD 2>/dev/null || printf 'NONE')
    [ "$HEAD_AFTER" != "$HEAD_BEFORE" ] || die "HEAD did not change after the commit, the commit did not actually happen"
    say "commit: $HEAD_AFTER ($STAGED files)"
  fi
else
  say "no git, commit skipped (the snapshot was taken as a copy in the apply stage)"
fi

step "version stamp (last operation, atomic)"
STAMP_TMP="$V/.beyin-version.tmp.$$"
printf '%s\n' "$BEYIN_TARGET_VERSION" > "$STAMP_TMP" || die "could not write the stamp temp file"
mv -f "$STAMP_TMP" "$V/.beyin-version" || { rm -f "$STAMP_TMP"; die "could not put the stamp in place"; }
[ "$(sed -n '1p' "$V/.beyin-version")" = "$BEYIN_TARGET_VERSION" ] || die "could not verify the stamp"
say ".beyin-version = $BEYIN_TARGET_VERSION"

if command -v git >/dev/null 2>&1 && [ -d "$V/.git" ]; then
  git_id
  git -C "$V" add -- ".beyin-version" >/dev/null 2>&1 || :
  git -C "$V" -c user.name="$GIT_N" -c user.email="$GIT_E" \
    commit -q -m "v2 version stamp" >/dev/null 2>&1 \
    || say "WARNING: could not commit the stamp, the file on disk is correct. Check with 'git status' in the vault."
fi

rm -f "$STAGE_MARK"
step "UPGRADE DONE"
say "vault: $V"
say "version: $BEYIN_TARGET_VERSION"
exit 0
