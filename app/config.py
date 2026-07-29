import os
from pathlib import Path

# Project Root
BASE_DIR = Path(__file__).resolve().parent.parent

# Folders
LOGS_DIR = BASE_DIR / "logs"
SCREENSHOTS_DIR = BASE_DIR / "screenshots"

# Create folders automatically
LOGS_DIR.mkdir(exist_ok=True)
SCREENSHOTS_DIR.mkdir(exist_ok=True)

# Browser Settings
# Auto-detect Environment: If running on Render or in production, use Headless.
# If running locally, default to HEADLESS = False so you can see the browser window.
IS_PROD = os.getenv("RENDER") is not None or os.getenv("PORT") is not None

HEADLESS = True if IS_PROD else False
SLOW_MO = 0 if IS_PROD else 300

# Timeouts (milliseconds)
PAGE_TIMEOUT = 30000
ELEMENT_TIMEOUT = 15000