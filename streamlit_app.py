#!/usr/bin/env python3
"""
Streamlit App Entry Point
This file allows you to run the competitive intelligence tool from the root directory.
"""

import sys
import os

# Add the competitive-intel-tool directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'competitive-intel-tool'))

# Import and run the main application
from main import main

if __name__ == "__main__":
    main()
