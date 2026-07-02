from __future__ import annotations

import sys
import urllib.error
import urllib.request
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = REPO_ROOT / "data" / "raw" / "german_credit"
DATA_URL = "https://archive.ics.uci.edu/ml/machine-learning-databases/statlog/german/german.data"
DOC_URL = "https://archive.ics.uci.edu/ml/machine-learning-databases/statlog/german/german.doc"


def download_file(url: str, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(url, headers={"User-Agent": "SmartCreditMultiAgent/1.0"})
    with urllib.request.urlopen(request, timeout=30) as response:
        destination.write_bytes(response.read())


def main() -> int:
    try:
        download_file(DATA_URL, RAW_DIR / "german.data")
        download_file(DOC_URL, RAW_DIR / "german.doc")
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        print(
            "Failed to download UCI German Credit data. "
            f"Please manually place german.data and german.doc under {RAW_DIR}. "
            f"Original error: {exc}",
            file=sys.stderr,
        )
        return 1

    print(f"Downloaded German Credit data to {RAW_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
