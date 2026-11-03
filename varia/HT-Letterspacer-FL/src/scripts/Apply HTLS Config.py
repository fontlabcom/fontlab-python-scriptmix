# FLM: Apply HTLS Config
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
if str(root) not in sys.path:
    sys.path.insert(0, str(root))
from htls_fontlab import apply_selection

results = apply_selection()
for r in results:
    print(
        "%s [%s]: %s" % (r["name"], r["master"], r.get("skip") or str(r.get("after")))
    )
