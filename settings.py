import os
from pathlib import Path

PORT = int(os.getenv("PORT", 8050))
print(PORT)

CACHE_AGE = 60 * 60 * 24

PROJECT_DIR = Path(__file__).parent.resolve()

STATIC_DIR = PROJECT_DIR / "static"
assert STATIC_DIR.is_dir(), f"missing directory: STATIC_DIR=`{STATIC_DIR}`"

STORAGE_DIR = PROJECT_DIR / "storage"
assert STORAGE_DIR.is_dir(), f"missing directory: STORAGE_DIR=`{STORAGE_DIR}`"

ARTIFACTS_DIR = PROJECT_DIR / "tests" / "artifacts"
assert ARTIFACTS_DIR.is_dir(), f"missing directory: ARTIFACTS_DIR='{ARTIFACTS_DIR}'"
