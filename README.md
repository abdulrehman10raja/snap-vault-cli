# 🗄️ snap-vault

> Incremental smart backup CLI with content-addressed object storage — stdlib only, blazing fast, zero dependencies.

[![PyPI version](https://img.shields.io/pypi/v/snap-vault-cli)](https://pypi.org/project/snap-vault-cli/)
[![Python](https://img.shields.io/pypi/pyversions/snap-vault-cli)](https://pypi.org/project/snap-vault-cli/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## What is snap-vault?

`snap-vault` is a command-line tool that takes **incremental snapshots** of any directory. Instead of copying everything every time, it only stores what actually changed — using SHA-256 content hashing and a content-addressed object store. Every snapshot is a full manifest, every object is stored once, and you can restore any snapshot at any time.

Built entirely with Python's standard library. No external dependencies. No APIs. No cloud. Just fast, concurrent, local backup.

---

## Features

- **Incremental snapshots** — only changed files are stored, unchanged files are deduplicated automatically
- **Content-addressed storage** — files are stored by their SHA-256 hash, never duplicated on disk
- **Concurrent file I/O** — uses `ThreadPoolExecutor` for fast parallel hashing and copying
- **Diff engine** — see exactly what changed (added / modified / deleted) since the last snapshot
- **Full restore** — restore any snapshot by ID or default to the latest
- **Snapshot history** — view all snapshots with timestamps, file counts, and change stats
- **Beautiful terminal output** — colored progress bars, tables, and status icons
- **Zero dependencies** — pure Python stdlib, works anywhere Python 3.9+ runs

---

## Installation

### From PyPI

```bash
pip install snap-vault-cli
```

### From source

```bash
git clone https://github.com/abdulrehman10raja/snap-vault-cli
cd snap-vault-cli
pip install -e .
```

---

## Usage

### `snap` — Take an incremental snapshot

```bash
snap-vault snap <source> <vault>
```

```bash
snap-vault snap ./my-project ./my-vault
```

Scans the source directory, hashes all files concurrently, compares with the last snapshot, and stores only what changed.

---

### `diff` — See what changed since last snapshot

```bash
snap-vault diff <source> <vault>
```

```bash
snap-vault diff ./my-project ./my-vault
```

Shows every file that was added, modified, or deleted since the last snapshot — without taking a new one.

---

### `restore` — Restore files from a snapshot

```bash
snap-vault restore <vault> <target> [--snap SNAPSHOT_ID]
```

```bash
# Restore latest snapshot
snap-vault restore ./my-vault ./restored-output

# Restore a specific snapshot by ID
snap-vault restore ./my-vault ./restored-output --snap 20250801_103000
```

Restores all files from the chosen snapshot into the target directory. Creates the target if it doesn't exist.

---

### `history` — View all snapshots

```bash
snap-vault history <vault>
```

```bash
snap-vault history ./my-vault
```

Lists every snapshot in the vault with its timestamp, file count, and change statistics (added / modified / deleted).

---

## How it works

```
snap-vault snap ./project ./vault
        │
        ▼
  Scan source directory
        │
        ▼
  Hash all files concurrently (SHA-256, ThreadPoolExecutor)
        │
        ▼
  Load previous manifest (if any)
        │
        ▼
  Compute diff (added / modified / deleted / unchanged)
        │
        ▼
  Store new/changed files as content-addressed objects
  (.snapvault/objects/ab/cdef1234...)
        │
        ▼
  Save new manifest with full file tree + stats
  (.snapvault/manifests/20250801_103000.json)
```

### Vault structure

```
my-vault/
└── .snapvault/
    ├── config.json               ← vault metadata
    ├── manifests/
    │   ├── 20250801_103000.json  ← snapshot 1
    │   └── 20250801_120000.json  ← snapshot 2
    └── objects/
        ├── ab/
        │   └── cdef1234...       ← stored file content
        └── 7f/
            └── 9a2b3c...
```

Objects are stored by the first 2 chars of their SHA-256 hash as a subdirectory — the same content-addressing strategy used by Git.

---

## Example session

```bash
$ snap-vault snap ./src ./vault

╭────────────────────────────────────────────────────────╮
│               SNAP-VAULT  ·  Taking Snapshot           │
╰────────────────────────────────────────────────────────╯

  → Source : /home/user/src
  → Vault  : ./vault
  ────────────────────────────────────────────────────────
  → Scanning source directory...
  → Found 42 file(s) — hashing concurrently...
  ████████████████████████████████  100%
  ────────────────────────────────────────────────────────
  → Snapshot ID : 20250801_103000
  → Storing 5 new/modified object(s)...
  ████████████████████████████████  100%
  ────────────────────────────────────────────────────────
  Added              3                  
  Modified           2                  
  Deleted            0                  
  Unchanged          37                 
  Objects stored     5                  
  Deduplicated       0                  
  Total size         1.2 MB             
  ────────────────────────────────────────────────────────
  ✓ Snapshot 20250801_103000 saved successfully.
```

---

## Why snap-vault?

| Feature | snap-vault | plain `cp -r` | rsync |
|---|---|---|---|
| Incremental (only changed files) | ✓ | ✗ | ✓ |
| Content deduplication | ✓ | ✗ | ✗ |
| Snapshot history | ✓ | ✗ | ✗ |
| Point-in-time restore | ✓ | ✗ | ✗ |
| Zero dependencies | ✓ | ✓ | requires rsync |
| Cross-platform | ✓ | partial | partial |
| Colored CLI output | ✓ | ✗ | ✗ |

---

## Requirements

- Python 3.9+
- No external packages — stdlib only

---

## License

MIT © [Abdul Rehman](https://github.com/abdulrehman10raja)

---

## Author

Built by **Abdul Rehman** — BSCS student at FAST-NUCES Islamabad, AI Engineering Intern at Prime Innovators Global.

- GitHub: [@abdulrehman10raja](https://github.com/abdulrehman10raja)
- LinkedIn: [abdulrehmanraja-cs](https://linkedin.com/in/abdulrehmanraja-cs)
- PyPI: [snap-vault-cli](https://pypi.org/project/snap-vault-cli/)
