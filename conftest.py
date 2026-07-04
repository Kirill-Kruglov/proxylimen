import sys
from pathlib import Path

# gate_harness is a top-level package; make it importable without PYTHONPATH.
sys.path.insert(0, str(Path(__file__).resolve().parent))
