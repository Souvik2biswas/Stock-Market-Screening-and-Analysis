"""
Main Entry Point for AI/ML Stock Market Screening & Analysis System.
"""
import sys
import os
import logging
from pathlib import Path

# Add project root directory to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from app.ui.dashboard import LiveDashboardWindow

def main():
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )

    app = QApplication(sys.argv)
    app.setApplicationName("AI/ML Stock Market Screening & Analysis System")
    app.setStyle("Fusion")

    window = LiveDashboardWindow()
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
