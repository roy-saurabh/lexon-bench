"""
Generate LEXON derivation trace examples.

Writes four canonical trace files to outputs/traces/.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from lexon.tracing.derivation_trace import write_trace_examples


def main() -> int:
    written = write_trace_examples("outputs/traces")
    for path in written:
        print(f"  wrote {path}")
    print(f"PASS: {len(written)} trace files written to outputs/traces/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
