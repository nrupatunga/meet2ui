#!/usr/bin/env python3
"""Meet2UI - Compact camera control application."""

import sys
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from ui.app import App  # noqa: E402


def main():
    app = App()
    app.setup()
    app.run()


if __name__ == "__main__":
    main()
