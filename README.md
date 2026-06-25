<div align="center">

# 🗄️ snap-vault

### Incremental smart backup CLI with content-addressed object storage

[![PyPI version](https://img.shields.io/pypi/v/snap-vault-cli?color=blue&style=for-the-badge)](https://pypi.org/project/snap-vault-cli/)
[![Python](https://img.shields.io/pypi/pyversions/snap-vault-cli?style=for-the-badge)](https://pypi.org/project/snap-vault-cli/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](https://opensource.org/licenses/MIT)
[![PyPI Downloads](https://img.shields.io/pypi/dm/snap-vault-cli?style=for-the-badge&color=green)](https://pypi.org/project/snap-vault-cli/)

**Zero dependencies · Pure Python stdlib · Blazing fast · Cross-platform**

[Installation](#-installation) · [Usage](#-usage) · [How It Works](#-how-it-works) · [Demo](#-demo) · [Why snap-vault](#-why-snap-vault)

</div>

---

## 🚀 What is snap-vault?

`snap-vault` is a command-line tool that takes **incremental snapshots** of any directory.

Instead of copying everything every time, it only stores what actually changed — using **SHA-256 content hashing** and a **content-addressed object store** (same strategy Git uses internally). Every snapshot is a full manifest, every object is stored exactly once, and you can restore any snapshot at any point in time.

Built entirely with **Python's standard library**. No external dependencies. No APIs. No cloud. Just fast, concurrent, local backup.

---

## ✨ Features

| Feature | Description |
|---|---|
| 📸 **Incremental snapshots** | Only changed files are stored — unchanged files are deduplicated automatically |
| 🔐 **Content-addressed storage** | Files stored by SHA-256 hash, never duplicated on disk |
| ⚡ **Concurrent file I/O** | `ThreadPoolExecutor` for fast parallel hashing and copying |
| 🔍 **Diff engine** | See exactly what changed (added / modified / deleted) since the last snapshot |
| ⏪ **Point-in-time restore** | Restore any snapshot by ID or default to the latest |
| 📊 **Snapshot history** | Full timeline of snapshots with timestamps, file counts, and change stats |
| 🎨 **Beautiful terminal output** | Colored progress bars, tables, and status icons |
| 📦 **Zero dependencies** | Pure Python stdlib — works anywhere Python 3.9+ runs |

---

## 📦 Installation

```bash
pip install snap-vault-cli
```

Or install from source:

```bash
git clone https://github.com/abdulrehman10raja/snap-vault-cli
cd snap-vault-cli
pip install -e .
```

Verify the install:

```bash
snap-vault --version
# snap-vault 0.1.0
```

---

## 🎬 Demo

```
$ snap-vault snap ./my-project ./my-vault

╭────────────────────────────────────────────────────────╮
│             SNAP-VAULT  ·  Taking Snapshot             │
╰────────────────────────────────────────────────────────╯

  → Source : /home/user/my-project
  → Vault  : ./my-vault
  ────────────────────────────────────────────────────────
  → Scanning source directory...
  → Found 42 file(s) — hashing concurrently...
  ████████████████████████████████ 100%
  ────────────────────────────────────────────────────────
  → Snapshot ID : 20260626_103000_123
  → Storing 5 new/modified object(s)...
  ████████████████████████████████ 100%
  ────────────────────────────────────────────────────────
  Added                          3
  Modified                       2
  Deleted                        0
  Unchanged                      37
  Objects stored                 5
  Deduplicated                   0
  Total size                     1.2 MB
  ────────────────────────────────────────────────────────
  ✓ Snapshot 20260626_103000_123 saved successfully.
```

---

## 🛠️ Usage

### `snap` — Take an incremental snapshot

```bash
snap-vault snap <source> <vault>
```

```bash
snap-vault snap ./my-project ./my-vault
```

Scans the source directory, hashes all files concurrently, compares with the last snapshot, and stores only what changed. If nothing changed, it tells you instantly.

---

### `diff` — See what changed since last snapshot

```bash
snap-vault diff <source> <vault>
```

```bash
snap-vault diff ./my-project ./my-vault
```

Shows every file that was **added**, **modified**, or **deleted** since the last snapshot — without taking a new one. Perfect for reviewing before committing a snapshot.

---

### `history` — View all snapshots

```bash
snap-vault history <vault>
```

```bash
snap-vault history ./my-vault
```

Lists every snapshot in the vault with its timestamp, file count, and change statistics.

```
  20260626_014030_196
    Date                         2026-06-26  01:40:30
    Files                        42
    Added                        0
    Modified                     1
    Deleted                      0
    Total size                   1.2 MB
```

---

### `restore` — Restore files from a snapshot

```bash
snap-vault restore <vault> <target> [--snap SNAPSHOT_ID]
```

```bash
# Restore latest snapshot
snap-vault restore ./my-vault ./restored-output

# Restore a specific snapshot by ID (point-in-time restore)
snap-vault restore ./my-vault ./restored-output --snap 20260626_103000_123
```

Restores all files from the chosen snapshot into the target directory. Creates the target if it doesn't exist.

---

## ⚙️ How It Works

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
  (.snapvault/manifests/20260626_103000_123.json)
```

### Vault Structure

```
my-vault/
└── .snapvault/
    ├── config.json                     ← vault metadata
    ├── manifests/
    │   ├── 20260626_103000_123.json    ← snapshot 1
    │   └── 20260626_120000_456.json    ← snapshot 2
    └── objects/
        ├── ab/
        │   └── cdef1234...             ← stored file content (by hash)
        └── 7f/
            └── 9a2b3c...
```

Objects are stored by the first 2 characters of their SHA-256 hash as a subdirectory — the same content-addressing strategy used by **Git**.

---

## 📊 Why snap-vault?

| Feature | snap-vault | `cp -r` | rsync |
|---|:---:|:---:|:---:|
| Incremental (only changed files) | ✅ | ❌ | ✅ |
| Content deduplication | ✅ | ❌ | ❌ |
| Snapshot history | ✅ | ❌ | ❌ |
| Point-in-time restore | ✅ | ❌ | ❌ |
| Zero dependencies | ✅ | ✅ | ❌ |
| Cross-platform | ✅ | ⚠️ | ⚠️ |
| Colored CLI output | ✅ | ❌ | ❌ |
| Works offline | ✅ | ✅ | ✅ |

---

## 🧱 Project Structure

```
snap-vault-cli/
├── snap_vault/
│   ├── __init__.py     ← version info
│   ├── __main__.py     ← entry point
│   ├── cli.py          ← argument parsing
│   ├── core.py         ← snap / diff / restore / history logic
│   ├── display.py      ← terminal colors, progress bars, tables
│   └── manifest.py     ← vault structure, object store, manifests
├── pyproject.toml
└── README.md
```

---

## 📋 Requirements

- Python 3.9+
- No external packages — stdlib only

---

## 📄 License

MIT © [Abdul Rehman](https://github.com/abdulrehman10raja)

---

## 👨💻 Author

Built by **Abdul Rehman** — BSCS student at FAST-NUCES Islamabad, AI Engineering Intern at Prime Innovators Global.

<div align="center">

[![GitHub](https://img.shields.io/badge/GitHub-abdulrehman10raja-black?style=for-the-badge&logo=github)](https://github.com/abdulrehman10raja)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-abdulrehmanraja--cs-blue?style=for-the-badge&logo=linkedin)](https://linkedin.com/in/abdulrehmanraja-cs)
[![PyPI](https://img.shields.io/badge/PyPI-snap--vault--cli-orange?style=for-the-badge&logo=pypi)](https://pypi.org/project/snap-vault-cli/)

</div>

---

<div align="center">

If you found this useful, please ⭐ star the repo — it helps a lot!

</div>
