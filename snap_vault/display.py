import sys
import os

if os.name == "nt":
    os.system("")
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass
    if hasattr(sys.stderr, "reconfigure"):
        try:
            sys.stderr.reconfigure(encoding="utf-8")
        except Exception:
            pass

class Colors:
    RESET  = "\033[0m"
    BOLD   = "\033[1m"
    DIM    = "\033[2m"
    RED    = "\033[91m"
    GREEN  = "\033[92m"
    YELLOW = "\033[93m"
    BLUE   = "\033[94m"
    CYAN   = "\033[96m"
    WHITE  = "\033[97m"


def supports_color():
    return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()


def c(text, color):
    if supports_color():
        return f"{color}{text}{Colors.RESET}"
    return text


def header(title):
    width = 56
    line = "─" * width
    pad = (width - len(title)) // 2
    extra = width - pad - len(title)
    print(f"\n{c('╭' + line + '╮', Colors.CYAN)}")
    print(f"{c('│', Colors.CYAN)}{' ' * pad}{c(Colors.BOLD + title + Colors.RESET, Colors.WHITE)}{' ' * extra}{c('│', Colors.CYAN)}")
    print(f"{c('╰' + line + '╯', Colors.CYAN)}\n")


def divider():
    print(f"  {c('─' * 52, Colors.DIM)}")


def newline():
    print()


def success(msg):
    print(f"  {c('✓', Colors.GREEN)} {msg}")


def error(msg):
    print(f"  {c('✗', Colors.RED)} {msg}", file=sys.stderr)


def info(msg):
    print(f"  {c('→', Colors.BLUE)} {msg}")


def warn(msg):
    print(f"  {c('⚠', Colors.YELLOW)} {msg}")


def added(path):
    print(f"  {c('+', Colors.GREEN)} {path}")


def modified(path):
    print(f"  {c('~', Colors.YELLOW)} {path}")


def deleted(path):
    print(f"  {c('-', Colors.RED)} {path}")


def unchanged(count):
    print(f"  {c('=', Colors.DIM)} {count} file(s) unchanged")


def table_row(label, value, color=None):
    color = color or Colors.WHITE
    print(f"  {c(label, Colors.DIM):<38} {c(str(value), color)}")


def progress_bar(current, total, width=32):
    pct = int(current / max(total, 1) * 100)
    filled = int(width * current / max(total, 1))
    bar = "█" * filled + "░" * (width - filled)
    print(f"\r  {c(bar, Colors.CYAN)} {pct:>3}%", end="", flush=True)


def size_fmt(n):
    for unit in ["B", "KB", "MB", "GB"]:
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} TB"
