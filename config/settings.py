import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Templates directory
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')

# Output directory
OUTPUT_DIR = os.path.join(BASE_DIR, 'output')

# File extensions to analyze
DART_EXTENSIONS = ('.dart',)