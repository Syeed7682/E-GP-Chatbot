"""
Validate Indexes Script (backend/scripts/validate_indexes.py).
Performs multi-point integrity and query validation on an index version bundle.
"""
import argparse
import logging
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.config import INDEX_DIR
from app.indexing.index_manager import IndexManager
from app.services.rag_service import load_rag_service

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s - %(message)s")
logger = logging.getLogger("validate_indexes")


def main():
    parser = argparse.ArgumentParser(description="Validate e-GP Index Version")
    parser.add_argument("--version", type=str, default=None, help="Version to validate (default: active)")
    args = parser.parse_args()

    mgr = IndexManager(INDEX_DIR)
    version = args.version or mgr.get_active_version()
    logger.info("Validating index version: %s", version)

    checks = mgr.validate_version(version)

    print("\n" + "=" * 50)
    print(f"INDEX INTEGRITY REPORT — Version: {version}")
    print("=" * 50)
    print(f"Directory: {checks['path']}")
    print(f"Passed:    {'PASSED' if checks['passed'] else 'FAILED'}")
    print("\nStatistics:")
    for k, v in checks.get("stats", {}).items():
        print(f"  • {k}: {v}")

    if checks.get("warnings"):
        print("\nWarnings:")
        for w in checks["warnings"]:
            print(f"  ⚠️ {w}")

    if checks.get("errors"):
        print("\nErrors:")
        for e in checks["errors"]:
            print(f"  ❌ {e}")

    # Test Query Retrieval
    print("\nRunning Test Query Verification...")
    try:
        rag = load_rag_service()
        if rag:
            test_query = "What is the procedure for Annual Procurement Plan (APP)?"
            context, sources, screens = rag.retrieve(test_query, top_k=3)
            print(f"Test Query: '{test_query}'")
            print(f"Retrieved {len(sources)} sources:")
            for s in sources:
                print(f"  - Page {s['page']} | Section: {s['section']} | Score: {s['score']}")
            print("✅ Retrieval pipeline operational.")
    except Exception as exc:
        print(f"❌ Retrieval verification encountered error: {exc}")

    print("=" * 50 + "\n")
    sys.exit(0 if checks["passed"] else 1)


if __name__ == "__main__":
    main()

