from PyQt5.QtWidgets import QWidget, QPushButton
from PyQt5.QtWidgets import QLabel, QLineEdit, QGridLayout
from PyQt5.QtGui import QIntValidator
import pandas as pd
import MitFunc


class manualWindow(QWidget):
    """
    This "window" is a QWidget where users can change the manually identify \
    cells
    """

    def __init__(self, setting):
        super().__init__()
        self.setWindowTitle('Manually Select Cells')
        self.setFixedWidth(700)
        self.progressLbl = QLabel()
        self.progressLbl.setText("Check settings, enter details and click Run")
        # Layout
        self.grid = QGridLayout(self)
        self.grid.addWidget(self.progressLbl, 0, 0, 1, 5)
        self.df, sizeX, sizeY, scaleX, maxPrj, maxZPrj, image = MitFunc.pullOMERO(
            setting['user'], setting['pw'], setting['server'], setting['imageId'],
            setting['channel'], setting['stages'])
