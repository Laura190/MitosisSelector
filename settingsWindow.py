from PyQt5.QtWidgets import QWidget, QPushButton
from PyQt5.QtWidgets import QLabel, QLineEdit, QGridLayout
from PyQt5.QtGui import QIntValidator
import pandas as pd


class settingsWindow(QWidget):
    """
    This "window" is a QWidget where users can change the default settings
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle('Processing Settings')
        self.setFixedWidth(700)
        try:
            settings = pd.read_csv('Settings.csv')
        except FileNotFoundError:
            dict = {'Channel': 0, 'Duration': 20, 'Nuclei Diameter': 20,
                    'Stages': 'Prophase,Metaphase,Anaphase,Telophase'}
            # dict = {'Image': 356978, 'Duration: 20, 'Nuclei Diameter': 120,
            #        'Spot Diameter': 10, 'Threshold Method': ['Yen']}
            settings = pd.DataFrame([dict])
            settings.to_csv('Settings.csv', index=False)
        # OMERO user input
        channelLbl = QLabel()
        channelLbl.setText("Channel")
        self.channelEdt = QLineEdit('%d' % settings['Channel'].values)
        self.channelEdt.setValidator(QIntValidator())
        timeFramesLbl = QLabel()
        timeFramesLbl.setText("Duration (Frames)")
        self.timeFramesEdt = QLineEdit('%d' % settings['Duration'].values)
        self.timeFramesEdt.setValidator(QIntValidator())
        nucleiDiameterLbl = QLabel()
        nucleiDiameterLbl.setText("Nuclei Diameter (um)")
        self.nucleiDiameterEdt = QLineEdit(
            '%d' % settings['Nuclei Diameter'].values)
        self.nucleiDiameterEdt.setValidator(QIntValidator())
        stagesLbl = QLabel()
        stagesLbl.setText("Stages to select, separate with commas")
        self.stagesEdt = QLineEdit(
            '%s' % settings['Stages'].values[0])
        # spotDiameterLbl = QLabel()
        # spotDiameterLbl.setText("Spot Diameter")
        # self.spotDiameterEdt = QLineEdit(
        #    '%d' % defaults['Spot Diameter'].values)
        # self.spotDiameterEdt.setValidator(QIntValidator())
        # threshMethodLbl = QLabel()
        # threshMethodLbl.setText("Threshold Method")
        # self.threshMethodCb = QComboBox()
        # Order list items so default is first
        # threshMethods = ['Isodata', 'Li', 'Local', 'Mean', 'Minimim',
        #                 'Multi Otsu', 'Niblack', 'Otsu', 'Sauvola',
        #                 'Triangle', 'Yen']
        # orderMethods = []
        # orderMethods.append(defaults['Threshold Method'].values[0])
        # orderMethods.extend(set(threshMethods)-set(orderMethods))
        # self.threshMethodCb.addItems(orderMethods)        # Settings
        saveBtn = QPushButton()
        saveBtn.setText('Save')
        saveBtn.clicked.connect(self.saveSettings)
        cancelBtn = QPushButton()
        cancelBtn.setText('Cancel')
        cancelBtn.clicked.connect(self.close)
        # saveBtn.clicked.connect(self.saveSettings)
        # Layout
        grid = QGridLayout(self)
        grid.addWidget(channelLbl, 0, 0, 1, 1)
        grid.addWidget(self.channelEdt, 0, 1, 1, 2)
        grid.addWidget(timeFramesLbl, 1, 0, 1, 1)
        grid.addWidget(self.timeFramesEdt, 1, 1, 1, 2)
        grid.addWidget(nucleiDiameterLbl, 2, 0, 1, 1)
        grid.addWidget(self.nucleiDiameterEdt, 2, 1, 1, 2)
        grid.addWidget(stagesLbl, 3, 0, 1, 1)
        grid.addWidget(self.stagesEdt, 3, 1, 1, 2)
        # grid.addWidget(spotDiameterLbl, 2, 0, 1, 1)
        # grid.addWidget(self.spotDiameterEdt, 2, 1, 1, 2)
        # grid.addWidget(threshMethodLbl, 3, 0, 1, 1)
        # grid.addWidget(self.threshMethodCb, 3, 1, 1, 2)
        grid.addWidget(saveBtn, 4, 1, 1, 2)
        grid.addWidget(cancelBtn, 4, 0, 1, 1)

    def saveSettings(self):
        dict = {'Channel': self.channelEdt.text(),
                'Duration': self.timeFramesEdt.text(),
                'Nuclei Diameter': self.nucleiDiameterEdt.text(),
                'Stages': self.stagesEdt.text()}
        # 'Spot Diameter': self.spotDiameterEdt.text(),
        # 'Threshold Method': [self.threshMethodCb.currentText()]}
        settings = pd.DataFrame([dict])
        settings.to_csv('Settings.csv', index=False)
        self.close()
