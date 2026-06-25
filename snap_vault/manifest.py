import json
import shutil
from datetime import datetime
from pathlib import Path

VAULT_DIR     = ".snapvault"
MANIFESTS_DIR = "manifests"
OBJECTS_DIR   = "objects"
CONFIG_FILE   = "config.json"


def vault_path(dest):
    return Path(dest) / VAULT_DIR

def manifests_path(dest):
    return vault_path(dest) / MANIFESTS_DIR

def objects_path(dest):
    return vault_path(dest) / OBJECTS_DIR

def config_path(dest):
    return vault_path(dest) / CONFIG_FILE


def init_vault(dest, source):
    vault_path(dest).mkdir(parents=True, exist_ok=True)
    manifests_path(dest).mkdir(exist_ok=True)
    objects_path(dest).mkdir(exist_ok=True)
    cfg = config_path(dest)
    if not cfg.exists():
        data = {
            "source": str(Path(source).resolve()),
            "created": datetime.now().isoformat(),
            "snap_count": 0
        }
        cfg.write_text(json.dumps(data, indent=2))


def load_config(dest):
    cfg = config_path(dest)
    if not cfg.exists():
        return None
    return json.loads(cfg.read_text())


def save_config(dest, data):
    config_path(dest).write_text(json.dumps(data, indent=2))


def timestamp_now():
    return datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]


def save_manifest(dest, data):
    ts = data["timestamp"]
    p = manifests_path(dest) / f"{ts}.json"
    p.write_text(json.dumps(data, indent=2))
    return p


def load_manifest(dest, ts):
    p = manifests_path(dest) / f"{ts}.json"
    if not p.exists():
        return None
    return json.loads(p.read_text())


def list_manifests(dest):
    mp = manifests_path(dest)
    if not mp.exists():
        return []
    return sorted(m.stem for m in mp.glob("*.json"))


def latest_manifest(dest):
    history = list_manifests(dest)
    if not history:
        return None
    return load_manifest(dest, history[-1])


def object_path(dest, file_hash):
    return objects_path(dest) / file_hash[:2] / file_hash[2:]


def store_object(dest, file_hash, src_path):
    op = object_path(dest, file_hash)
    op.parent.mkdir(parents=True, exist_ok=True)
    if not op.exists():
        shutil.copy2(src_path, op)
        return True
    return False


def restore_object(dest, file_hash, target_path):
    op = object_path(dest, file_hash)
    if not op.exists():
        return False
    tp = Path(target_path)
    tp.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(op, tp)
    return True
