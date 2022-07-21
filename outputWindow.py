from PyQt5.QtWidgets import QWidget, QPushButton, QCheckBox, QFileDialog
from PyQt5.QtWidgets import QLabel, QLineEdit, QGridLayout


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
