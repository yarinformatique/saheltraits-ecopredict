import sys
from pathlib import Path

root_dir = str(Path(__file__).parent.parent)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from morpho_vision.cli import main

if __name__ == "__main__":
    main()
