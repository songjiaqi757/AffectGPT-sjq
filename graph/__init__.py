"""Actual graph workspace."""
import sys
from pathlib import Path
_workspace=str(Path(__file__).resolve().parent)
if _workspace not in sys.path:sys.path.insert(0,_workspace)
