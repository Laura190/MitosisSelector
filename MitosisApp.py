"""
CAMDU Mitosis Selector Application
2021 Laura Cooper, camdu@warwick.ac.uk
"""

# Packages
# PyQt
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QCheckBox
from PyQt5.QtWidgets import QLabel, QLineEdit, QGridLayout, QProgressBar
from PyQt5.QtWidgets import QFileDialog, QComboBox
# from PyQt5.QtWidgets import QComboBox
from PyQt5.QtGui import QIntValidator, QIcon
# Data
import numpy as np
import pandas as pd
# Files and Folders
import os.path
import errno
from shutil import copy
# Mitosis functions
import MitFunc
import miApp


class outputWindow(QWidget):
    """
    This "window" is a QWidget which opens after analysis has been completed,
    giving users the option of what to do with the results
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle('Save Results')
        self.setFixedWidth(700)
        # OMERO user input
        message = QLabel("All cells analysed!")
        localSave = QCheckBox("Save results locally")
        localSave.setChecked(True)
        locSave = QPushButton()
        locSave.setText('Browse')
        locSave.clicked.connect(self.getDirectory)
        self.saveDir = QLineEdit()
        omeroSave = QCheckBox("Save results to OMERO")
        omeroSave.setChecked(True)
        permission = QCheckBox("Grant permission to CAMDU to use images and "
                               "annotations for algorithm development?")
        permission.setChecked(False)
        rmTmp = QCheckBox("Clear temporary files")
        rmTmp.setChecked(True)
        cancelBtn = QPushButton()
        cancelBtn.setText('Cancel')
        cancelBtn.clicked.connect(self.close)
        okBtn = QPushButton()
        okBtn.setText('OK')
        okBtn.clicked.connect(self.saveResults)
        # Layout
        grid = QGridLayout(self)
        grid.addWidget(message, 0, 0, 1, 1)
        grid.addWidget(localSave, 1, 0, 1, 1)
        grid.addWidget(locSave, 1, 2, 1, 1)
        grid.addWidget(self.saveDir, 1, 1, 1, 1)
        grid.addWidget(omeroSave, 2, 0, 1, 1)
        grid.addWidget(permission, 3, 0, 1, 1)
        grid.addWidget(rmTmp, 3, 0, 1, 1)
        grid.addWidget(cancelBtn, 4, 1, 1, 1)
        grid.addWidget(cancelBtn, 4, 0, 1, 1)

    def getDirectory(self):
        directory = str(QFileDialog.getExistingDirectory())
        self.saveDir.setText('{}'.format(directory))

    def saveResults(self):
        print("save")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = miApp.miApp()
    window.show()
    sys.exit(app.exec())
