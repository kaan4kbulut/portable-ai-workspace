"""Evaluate one offline fixture and print a JSON result."""

import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "olcum"))
from destek import evaluator_main

if __name__ == "__main__":
    evaluator_main('inceleme')
