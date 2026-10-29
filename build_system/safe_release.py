# -*- coding: utf-8 -*-
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from enterprise import safe_release_zip


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a sanitized release zip.")
    parser.add_argument("--output", default="", help="Output zip path. Defaults to build_system/safe_release.zip")
    args = parser.parse_args()
    result = safe_release_zip(args.output or None)
    print(f"ok={result['ok']}")
    print(f"path={result['path']}")
    print(f"included_files={result['included_files']}")
    print(f"size={result['size']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
