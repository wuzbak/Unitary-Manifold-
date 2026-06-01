from pathlib import Path
import sys

root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(root))

from src.core.um_sos_graph import write_graph_json

if __name__ == "__main__":
    out = root / "10-UM-SOS" / "graph" / "dag.json"
    write_graph_json(out)
    print(out)
