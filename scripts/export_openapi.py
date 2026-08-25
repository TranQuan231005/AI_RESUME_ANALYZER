#!/usr/bin/env python3
"""
Script to export and validate OpenAPI specification from FastAPI AI Service.
Usage:
    python scripts/export_openapi.py           # Exports contracts/openapi/ai-service.json
    python scripts/export_openapi.py --check   # Checks if file is up-to-date
"""

import argparse
import json
import sys
from pathlib import Path

# Add ai-service to sys.path
ROOT_DIR = Path(__file__).resolve().parents[1]
AI_SERVICE_DIR = ROOT_DIR / "ai-service"
if str(AI_SERVICE_DIR) not in sys.path:
    sys.path.insert(0, str(AI_SERVICE_DIR))

try:
    from app.main import app
except ImportError as e:
    print(f"Error importing FastAPI app: {e}", file=sys.stderr)
    sys.exit(1)


def get_openapi_spec() -> dict:
    return app.openapi()


def main():
    parser = argparse.ArgumentParser(description="Export or check OpenAPI spec for ai-service.")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check if exported OpenAPI schema matches current code without modifying file.",
    )
    args = parser.parse_args()

    output_path = ROOT_DIR / "contracts" / "openapi" / "ai-service.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    current_spec = get_openapi_spec()
    current_json = json.dumps(current_spec, indent=2, ensure_ascii=False) + "\n"

    if args.check:
        if not output_path.exists():
            print(f"Error: OpenAPI spec not found at {output_path}. Run without --check first.", file=sys.stderr)
            sys.exit(1)
        
        try:
            existing_spec = json.loads(output_path.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"Error reading existing OpenAPI spec: {e}", file=sys.stderr)
            sys.exit(1)

        if existing_spec != current_spec:
            import difflib
            existing_lines = json.dumps(existing_spec, indent=2, sort_keys=True).splitlines(keepends=True)
            current_lines = json.dumps(current_spec, indent=2, sort_keys=True).splitlines(keepends=True)
            diff = "".join(difflib.unified_diff(existing_lines, current_lines, fromfile="existing", tofile="current"))
            print("Error: contracts/openapi/ai-service.json is out of date! Diff:\n" + diff, file=sys.stderr)
            sys.exit(1)
        print("OK: contracts/openapi/ai-service.json is up-to-date.")
    else:
        output_path.write_text(current_json, encoding="utf-8")
        print(f"Successfully exported OpenAPI schema to {output_path}")


if __name__ == "__main__":
    main()
