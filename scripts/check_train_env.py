from __future__ import annotations

import json

from _bootstrap import ensure_src_path

ensure_src_path()

from schema_reuse.train.backend import probe_training_backend


def main() -> None:
    report = probe_training_backend()
    print(json.dumps(report.to_dict(), ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
