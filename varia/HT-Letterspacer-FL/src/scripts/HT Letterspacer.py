# FLM: HT Letterspacer
# Compatible with FontLab 9, Python 3.
import os
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
if str(root) not in sys.path:
    sys.path.insert(0, str(root))
from htls_fontlab import show

show()
