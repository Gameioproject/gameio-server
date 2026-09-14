"""Export enabled source mappings for a manually imported client add-on."""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from handler.sources.addon_export import (  # noqa: E402
    build_snapshot,
    read_enabled_sources,
    write_snapshot,
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output", type=Path, required=True, help="New private output directory"
    )
    parser.add_argument(
        "--base-url", required=True, help="HTTPS directory that will serve the shards"
    )
    parser.add_argument("--id", required=True, help="Stable add-on id")
    parser.add_argument("--name", required=True, help="Name displayed on import")
    parser.add_argument(
        "--version", required=True, help="Snapshot version; change for every re-export"
    )
    args = parser.parse_args()
    try:
        rows = read_enabled_sources()
        files = build_snapshot(
            rows,
            addon_id=args.id,
            name=args.name,
            version=args.version,
            base_url=args.base_url,
        )
        write_snapshot(args.output, files)
    except ValueError as exc:
        parser.error(str(exc))
    sizes = [
        len(content)
        for filename, content in files.items()
        if filename != "manifest.json"
    ]
    print(
        json.dumps(
            {
                "sources": len(rows),
                "mappedKeys": len({(row.igdb_id, row.platform_slug) for row in rows}),
                "manifestBytes": len(files["manifest.json"]),
                "shardCount": len(sizes),
                "largestShardBytes": max(sizes),
                "totalShardBytes": sum(sizes),
                "output": str(args.output),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
