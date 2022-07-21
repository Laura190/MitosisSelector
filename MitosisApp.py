"""
CAMDU Mitosis Selector Application
2021 Laura Cooper, camdu@warwick.ac.uk
"""

# Packages
# PyQt
import sys
from PyQt5.QtWidgets import QApplication
import miApp

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = miApp.miApp()
    window.show()
    sys.exit(app.exec())
