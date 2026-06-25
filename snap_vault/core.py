import hashlib
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from snap_vault import manifest as mv
from snap_vault import display as dp

WORKERS = min(32, (os.cpu_count() or 1) + 4)
CHUNK   = 65536


def hash_file(path):
    h = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            while chunk := f.read(CHUNK):
                h.update(chunk)
        return h.hexdigest()
    except (OSError, PermissionError):
        return None


def scan_directory(source):
    source = Path(source).resolve()
    files = []
    for root, dirs, filenames in os.walk(source):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for fname in filenames:
            fp = Path(root) / fname
            rel = str(fp.relative_to(source))
            files.append((rel, fp))
    return files


def hash_all(source, files):
    source = Path(source).resolve()
    results = {}
    total = len(files)
    done = 0

    def hash_one(rel, fp):
        h = hash_file(fp)
        try:
            st = fp.stat()
            size, mtime = st.st_size, st.st_mtime
        except OSError:
            size, mtime = 0, 0.0
        return rel, h, size, mtime

    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        futures = {ex.submit(hash_one, rel, fp): rel for rel, fp in files}
        for future in as_completed(futures):
            done += 1
            dp.progress_bar(done, total)
            rel, h, size, mtime = future.result()
            if h:
                results[rel] = {"hash": h, "size": size, "mtime": mtime}
    dp.newline()
    return results


def compute_diff(old_files, new_files):
    old_keys = set(old_files)
    new_keys = set(new_files)
    added    = sorted(new_keys - old_keys)
    deleted  = sorted(old_keys - new_keys)
    modified = sorted(
        p for p in old_keys & new_keys
        if old_files[p]["hash"] != new_files[p]["hash"]
    )
    unchanged = sorted(
        p for p in old_keys & new_keys
        if old_files[p]["hash"] == new_files[p]["hash"]
    )
    return added, modified, deleted, unchanged


def do_snap(source, dest):
    source = Path(source).resolve()
    dp.header("SNAP-VAULT  ·  Taking Snapshot")

    if not source.exists():
        dp.error(f"Source not found: {source}")
        return False

    dp.info(f"Source : {source}")
    dp.info(f"Vault  : {dest}")
    dp.divider()

    mv.init_vault(dest, source)
    config = mv.load_config(dest)

    dp.info("Scanning source directory...")
    files = scan_directory(source)
    dp.info(f"Found {len(files)} file(s) — hashing concurrently...")

    new_files = hash_all(source, files)

    last      = mv.latest_manifest(dest)
    old_files = last["files"] if last else {}

    added_l, modified_l, deleted_l, unchanged_l = compute_diff(old_files, new_files)
    changed = added_l + modified_l

    if not changed and not deleted_l:
        dp.success("No changes detected. Vault is already up to date.")
        return True

    dp.divider()
    ts = mv.timestamp_now()
    dp.info(f"Snapshot ID : {ts}")
    dp.info(f"Storing {len(changed)} new/modified object(s)...")

    stored = 0
    deduped = 0

    def store_one(rel):
        fp = source / rel
        h  = new_files[rel]["hash"]
        return mv.store_object(dest, h, fp)

    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        futures = {ex.submit(store_one, rel): rel for rel in changed}
        done = 0
        for future in as_completed(futures):
            done += 1
            dp.progress_bar(done, len(changed))
            if future.result():
                stored += 1
            else:
                deduped += 1
    dp.newline()

    manifest_data = {
        "version":   "1.0",
        "timestamp": ts,
        "source":    str(source),
        "files":     new_files,
        "stats": {
            "added":     len(added_l),
            "modified":  len(modified_l),
            "deleted":   len(deleted_l),
            "unchanged": len(unchanged_l),
            "stored":    stored,
            "deduped":   deduped,
        }
    }
    mv.save_manifest(dest, manifest_data)
    config["snap_count"] = config.get("snap_count", 0) + 1
    mv.save_config(dest, config)

    total_size = sum(f["size"] for f in new_files.values())
    dp.divider()
    dp.table_row("Added",          len(added_l),           dp.Colors.GREEN)
    dp.table_row("Modified",       len(modified_l),        dp.Colors.YELLOW)
    dp.table_row("Deleted",        len(deleted_l),         dp.Colors.RED)
    dp.table_row("Unchanged",      len(unchanged_l),       dp.Colors.DIM)
    dp.table_row("Objects stored", stored,                 dp.Colors.CYAN)
    dp.table_row("Deduplicated",   deduped,                dp.Colors.DIM)
    dp.table_row("Total size",     dp.size_fmt(total_size),dp.Colors.WHITE)
    dp.divider()
    dp.success(f"Snapshot {ts} saved successfully.")
    return True


def do_diff(source, dest):
    dp.header("SNAP-VAULT  ·  Diff")
    source = Path(source).resolve()

    last = mv.latest_manifest(dest)
    if not last:
        dp.warn("No snapshots found. Run 'snap-vault snap' first.")
        return

    dp.info(f"Snapshot  : {last['timestamp']}")
    dp.info(f"Source    : {source}")
    dp.divider()

    files     = scan_directory(source)
    dp.info(f"Hashing {len(files)} file(s)...")
    new_files = hash_all(source, files)
    old_files = last["files"]

    added_l, modified_l, deleted_l, unchanged_l = compute_diff(old_files, new_files)

    if not any([added_l, modified_l, deleted_l]):
        dp.success("No changes since last snapshot.")
        return

    if added_l:
        dp.info(f"Added ({len(added_l)}):")
        for p in added_l:
            dp.added(p)
    if modified_l:
        dp.info(f"Modified ({len(modified_l)}):")
        for p in modified_l:
            dp.modified(p)
    if deleted_l:
        dp.info(f"Deleted ({len(deleted_l)}):")
        for p in deleted_l:
            dp.deleted(p)
    if unchanged_l:
        dp.unchanged(len(unchanged_l))


def do_restore(dest, target, snap_id=None):
    dp.header("SNAP-VAULT  ·  Restore")

    manifest_data = (
        mv.load_manifest(dest, snap_id) if snap_id
        else mv.latest_manifest(dest)
    )
    if not manifest_data:
        dp.error("Snapshot not found." if snap_id else "No snapshots in vault.")
        return False

    files  = manifest_data["files"]
    target = Path(target).resolve()
    target.mkdir(parents=True, exist_ok=True)

    dp.info(f"Snapshot : {manifest_data['timestamp']}")
    dp.info(f"Target   : {target}")
    dp.info(f"Files    : {len(files)}")
    dp.divider()

    # Pre-restore integrity check: verify that all objects exist in the vault
    missing_objects = []
    for rel, info in files.items():
        op = mv.object_path(dest, info["hash"])
        if not op.exists():
            missing_objects.append((rel, info["hash"]))

    if missing_objects:
        dp.error(f"Vault integrity check failed! {len(missing_objects)} object(s) are missing from the vault:")
        for rel, h in missing_objects[:10]:
            dp.error(f"  Missing object for {rel} (hash: {h[:8]}...)")
        if len(missing_objects) > 10:
            dp.error(f"  ... and {len(missing_objects) - 10} more.")
        return False

    total  = len(files)
    done   = 0
    failed = 0

    def restore_one(rel, info):
        return mv.restore_object(dest, info["hash"], target / rel)

    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        futures = {ex.submit(restore_one, rel, info): rel for rel, info in files.items()}
        for future in as_completed(futures):
            done += 1
            dp.progress_bar(done, total)
            if not future.result():
                failed += 1
    dp.newline()
    dp.divider()

    if failed:
        dp.warn(f"{failed} file(s) could not be restored.")
    dp.success(f"Restored {total - failed}/{total} files to {target}")
    return True


def do_history(dest):
    dp.header("SNAP-VAULT  ·  Snapshot History")

    config = mv.load_config(dest)
    if not config:
        dp.error("No vault found at that path.")
        return

    history = mv.list_manifests(dest)
    if not history:
        dp.warn("No snapshots yet.")
        return

    dp.info(f"Vault source    : {config.get('source', 'unknown')}")
    dp.info(f"Total snapshots : {len(history)}")
    dp.divider()

    for ts in reversed(history):
        m = mv.load_manifest(dest, ts)
        if not m:
            continue
        stats = m.get("stats", {})
        d, t  = ts[:8], ts[9:]
        if "_" in t:
            time_parts = t.split("_")
            time_part = time_parts[0]
            ms_part = time_parts[1] if len(time_parts) > 1 else ""
            time_fmt = f"{time_part[:2]}:{time_part[2:4]}:{time_part[4:]}"
            if ms_part:
                time_fmt += f".{ms_part}"
        else:
            time_fmt = f"{t[:2]}:{t[2:4]}:{t[4:]}"
        fmt   = f"{d[:4]}-{d[4:6]}-{d[6:]}  {time_fmt}"
        total_sz = sum(f["size"] for f in m["files"].values())
        print(f"\n  {dp.c(ts, dp.Colors.CYAN)}")
        dp.table_row("  Date",       fmt)
        dp.table_row("  Files",      len(m["files"]))
        dp.table_row("  Added",      stats.get("added",     "—"), dp.Colors.GREEN)
        dp.table_row("  Modified",   stats.get("modified",  "—"), dp.Colors.YELLOW)
        dp.table_row("  Deleted",    stats.get("deleted",   "—"), dp.Colors.RED)
        dp.table_row("  Total size", dp.size_fmt(total_sz))

    dp.divider()
