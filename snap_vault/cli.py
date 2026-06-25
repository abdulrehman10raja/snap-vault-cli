import argparse
import sys
from snap_vault import __version__
from snap_vault import core
from snap_vault import display as dp


def build_parser():
    parser = argparse.ArgumentParser(
        prog="snap-vault",
        description="Incremental smart backup CLI with content-addressed storage.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
subcommands:
  snap      Take an incremental snapshot of a directory
  diff      Show what changed since the last snapshot
  restore   Restore files from a snapshot
  history   Show all snapshots in a vault

examples:
  snap-vault snap   ./my-project  ./my-vault
  snap-vault diff   ./my-project  ./my-vault
  snap-vault restore ./my-vault   ./restored
  snap-vault restore ./my-vault   ./restored  --snap 20250801_103000
  snap-vault history ./my-vault
        """,
    )
    parser.add_argument("--version", action="version", version=f"snap-vault {__version__}")

    sub = parser.add_subparsers(dest="command")

    p = sub.add_parser("snap",    help="Take an incremental snapshot")
    p.add_argument("source", help="Directory to back up")
    p.add_argument("dest",   help="Vault directory")

    p = sub.add_parser("diff",    help="Show changes since last snapshot")
    p.add_argument("source", help="Directory to compare")
    p.add_argument("dest",   help="Vault directory")

    p = sub.add_parser("restore", help="Restore from a snapshot")
    p.add_argument("dest",   help="Vault directory")
    p.add_argument("target", help="Where to restore files")
    p.add_argument("--snap", default=None, help="Snapshot ID (default: latest)")

    p = sub.add_parser("history", help="Show snapshot history")
    p.add_argument("dest",   help="Vault directory")

    return parser


def main():
    parser = build_parser()
    args   = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(0)

    if args.command == "snap":
        core.do_snap(args.source, args.dest)
    elif args.command == "diff":
        core.do_diff(args.source, args.dest)
    elif args.command == "restore":
        core.do_restore(args.dest, args.target, snap_id=args.snap)
    elif args.command == "history":
        core.do_history(args.dest)


if __name__ == "__main__":
    main()
