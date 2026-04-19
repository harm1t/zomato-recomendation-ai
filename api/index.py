import sys
from pathlib import Path

# Explicitly add the src directory to path in case local package install via pip doesn't trigger on Vercel
src_path = Path(__file__).resolve().parents[1] / "src"
sys.path.append(str(src_path))

from restaurant_rec.phases.phase4.app import app

# Vercel's Python builder looks for an 'app' variable in api/index.py.
# This variable maps directly to our FastAPI application.
