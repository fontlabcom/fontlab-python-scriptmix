#!/usr/bin/env python3
"""Developer/managed deployment entry point. Customers double-click the .vfpy installer."""
import argparse
from pathlib import Path
import tempfile
from installer.core import fontlab_data_dir, install
from tools.build_release import make_payload


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--data-dir", type=Path, help="FontLab 9 user data directory (contains Scripts)"
    )
    parser.add_argument(
        "--upstream-archive",
        type=Path,
        help="Optional offline ZIP of the pinned original repository; checksum is still verified",
    )
    args = parser.parse_args()
    if args.data_dir is None:
        try:
            data = fontlab_data_dir()
        except ImportError:
            parser.error(
                "Outside FontLab, supply --data-dir. End users should open the .vfpy installer in FontLab 9."
            )
    else:
        data = args.data_dir
    with tempfile.TemporaryDirectory(prefix="htls-payload-") as temp:
        make_payload(Path(temp))
        result = install(
            Path(temp), data, archive=args.upstream_archive, progress=print
        )
    print(
        "Installed HT Letterspacer "
        + result["version"]
        + " in "
        + result["scripts_dir"]
    )


if __name__ == "__main__":
    main()
