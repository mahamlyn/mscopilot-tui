"""
Main entry point for the Copilot TUI application.
"""

import logging
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from copilot_tui.tui_app import CopilotApp
from copilot_tui.config import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(config.PROJECT_ROOT / "copilot_tui.log"),
        logging.StreamHandler(),
    ]
)

logger = logging.getLogger(__name__)


def main():
    """Main entry point."""
    if CopilotApp is None:
        print("Error: Textual framework not installed.")
        print("Please run: pip install -r requirements.txt")
        sys.exit(1)
    
    logger.info("Starting Copilot TUI Application")
    app = CopilotApp()
    app.run()


if __name__ == "__main__":
    main()
