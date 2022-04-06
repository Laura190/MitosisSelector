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


class miApp(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        # Window setup
        self.resize(600, 600)
        self.setWindowTitle('CAMDU Mitosis Selector')
        self.setWindowIcon(QIcon('square_black.jpg'))
        defaultServer = 'camdu.warwick.ac.uk'
        imageLocal = QLabel()
        imageLocal.setText("Local file path:")
        browse = QPushButton('Browse')
        browse.clicked.connect(self.getFile)
        # OMERO user input
        imageLbl = QLabel()
        imageLbl.setText("OMERO Image ID:")
        self.imageEdt = QComboBox()
        dir_list = [x for x in os.listdir("tmp") if not x.startswith('.')]
        processed_images = []
        for dir in dir_list:
            processed_images.append(dir.split("Image_", 1)[1])
        self.imageEdt.addItems(processed_images)
        self.imageEdt.setEditable(True)
        self.imageEdt.activated.connect(self.createButtons)
        # self.imageEdt = QLineEdit('%s' % defaultImage)
        # self.imageEdt.setValidator(QIntValidator())
        userLbl = QLabel()
        userLbl.setText("Username:")
        self.userEdt = QLineEdit()
        pwLbl = QLabel()
        pwLbl.setText("Password:")
        self.pwEdt = QLineEdit()
        self.pwEdt.setEchoMode(QLineEdit.Password)
        serverLbl = QLabel()
        serverLbl.setText("Server address:")
        self.serverEdt = QLineEdit('%s' % defaultServer.strip(''))
        # Progress Bar
        self.progress = QProgressBar()
        self.progress.setStyleSheet("QProgressBar {"
                                    "background-color : lightblue;"
                                    "border : 1px }")
        self.progressLbl = QLabel()
        self.progressLbl.setText("Check settings, enter details and click Run")
        # Settings
        setBtn = QPushButton('Settings')
        setBtn.clicked.connect(self.showSettingsWindow)
        # Run Button
        runBtn = QPushButton('Run')
        runBtn.clicked.connect(self.processImage)
        # Next Button
        nextBtn = QPushButton('Next')
        nextBtn.clicked.connect(self.replaceButtons)
        # No Mitosis Button
        noMit = QPushButton('No Mitosis')
        noMit.clicked.connect(self.noMitosisButton)
        # Selection Instruction
        self.selectionLbl = QLabel()
        self.selectionLbl.setText("Click image to select time frame")
        # Layout
        self.grid = QGridLayout(self)
        self.grid.addWidget(imageLocal, 0, 4, 1, 1)
        # self.grid.addWidget(browse, 0, 7, 1, 1)
        self.grid.addWidget(imageLbl, 0, 0, 1, 0)
        self.grid.addWidget(self.imageEdt, 0, 1, 1, 3)
        self.grid.addWidget(setBtn, 4, 0, 1, 2)
        self.grid.addWidget(userLbl, 1, 0, 1, 0)
        self.grid.addWidget(self.userEdt, 1, 1, 1, 3)
        self.grid.addWidget(pwLbl, 2, 0, 1, 0)
        self.grid.addWidget(self.pwEdt, 2, 1, 1, 3)
        self.grid.addWidget(serverLbl, 3, 0, 1, 0)
        self.grid.addWidget(self.serverEdt, 3, 1, 1, 3)
        self.grid.addWidget(self.progress, 2, 4, 1, 5)
        self.grid.addWidget(self.progressLbl, 3, 4, 1, 5)
        self.grid.addWidget(runBtn, 4, 4, 1, 5)
        self.progress.hide()
        self.rerun = False
        rows = self.createButtons()
        self.grid.addWidget(self.selectionLbl, rows+4, 4, 1, 5)
        self.grid.addWidget(nextBtn, rows+5, 4, 1, 5)
        self.grid.addWidget(noMit, rows+5, 3, 1, 1)
        self.grid.addWidget(browse, 0, 5, 1, 4)

    def getFile(self):
        self.file = str(QFileDialog.getOpenFileName())
        df, sizeX, sizeY, scaleX, maxPrj, maxZPrj = MitFunc.pullLocal(
            self.file)

    def showSettingsWindow(self):
        self.w = settingsWindow()
        self.w.show()

    def createButtons(self):
        # Image Buttons
        # grid = QGridLayout(self)
        self.imageId = self.imageEdt.currentText()
        localImages = "tmp/Image_%s/" % self.imageId
        try:
            self.results = pd.read_csv(localImages+"Results.csv")
        except FileNotFoundError:
            print('No results file found, redo processing for image %s'
                  % self.imageId)
        #    raise
        try:
            self.settings = pd.read_csv(localImages+"Settings.csv")
        except FileNotFoundError:
            print('No settings file found for image %s' % self.imageId)
            self.settings = pd.read_csv("Settings.csv")
            print(self.settings)
        self.buttonLbl = []
        self.buttons = []
        self.buttonSt = []
        i = -1
        j = 0
        self.totalCells = []
        for self.root, dirs, self.files in os.walk(localImages):
            for file in self.files:
                if file.endswith('.png'):
                    cellNo = file[file.find('Cell')+4:file.find('Time')]
                    if cellNo not in self.totalCells:
                        self.totalCells.append(cellNo)
                        # List of all cells
        listOfFiles = self.listFilesPerCell()
        print(not listOfFiles)
        if not listOfFiles:
            listOfFiles = list()
            listOfFiles.append('square_black.jpg')
        listOfFiles.sort()
        # Initialise buttons and time labels
        for file in listOfFiles:
            self.buttons.append(QPushButton())
            self.buttons[-1].setFixedSize(120, 120)
            self.buttons[-1].setStyleSheet("background-image: url(%s)" % file)
            if file == 'square_black.jpg':
                frame = 'No images found'
            else:
                frame = file[file.find('Time')+4:file.find('.png')]
            # button.clicked.connect(self.output)
            text = frame + " Selected"
            self.buttons[-1].clicked.connect(lambda ch, text=text,
                                             j=j: self.select(text, j))
            # Button state, false if not selected, true if selected
            self.buttonSt.append(False)
            self.buttonLbl.append(QLabel())
            self.buttonLbl[-1].setText(frame)
            hpos = j % 6
            j += 1
            if (hpos == 0):
                i += 2
            self.grid.addWidget(self.buttons[-1], i+6, hpos)
            if not self.rerun:
                self.grid.addWidget(self.buttonLbl[-1], i+7, hpos)
        self.selected = []
        # Save state that createButtons has already been run
        self.rerun = True
        return j

    def reset_all_buttons(self):
        # reset all buttons
        for j in range(len(self.buttonSt)):
            self.buttonSt[j] = False
        listOfFiles = self.listFilesPerCell()
        if listOfFiles:
            # If file list short, pad with dummy images
            if len(listOfFiles) < self.settings['Duration'][0]:
                for j in range(self.settings['Duration'][0]-len(listOfFiles)):
                    listOfFiles.append('square_black.jpg')
            listOfFiles.sort()
            for i in range(self.settings['Duration'][0]):
                file = listOfFiles[i]
                if file == 'square_black.jpg':
                    frame = 'NaN'
                else:
                    frame = file[file.find('Time')+4:file.find('.png')]
                self.buttons[i].setStyleSheet(
                    "background-image: url(%s)" % file)
                text = frame + " Selected"
                self.buttons[i].clicked.disconnect()
                self.buttons[i].clicked.connect(
                    lambda ch, text=text, i=i: self.select(text, i))
                self.buttonLbl[i].setText(frame)
                self.selectionLbl.setText(
                    "Click image to select time frame")

    def replaceButtons(self):
        if self.selectionLbl.text() == "All stages selected" or "No mitosis":
            for k, name in enumerate(self.results.columns[7:]):
                print(int(self.cell), name)
                self.results.loc[self.results['Cell'] == int(self.cell),
                                 name] = float(self.selected[k].strip(' '))
            self.selected = []
            self.reset_all_buttons()

    def noMitosisButton(self):
        self.selectionLbl.setText("No mitosis")
        for k, name in enumerate(self.results.columns[7:]):
            try:
                self.selected[k] = 'NaN'
            except IndexError:
                self.selected.append('NaN')
        self.replaceButtons()

    def listFilesPerCell(self):
        print(self.totalCells)
        if self.totalCells:
            self.cell = self.totalCells[0]
            self.totalCells.remove(self.cell)
            listOfFiles = []
            start = 'Cell'+self.cell+'Time'
            for file in self.files:
                if file.startswith(start) and file.endswith('.png'):
                    listOfFiles.append(os.path.join(self.root, file))
            return listOfFiles
        elif 'self.results' in locals():
            self.results.to_csv('Image_%s_Results.csv' % self.imageId,
                                index=False)
            self.showOutputWindow()
        else:
            listOfFiles = []
            return listOfFiles

    def showOutputWindow(self):
        self.w = outputWindow()
        self.w.show()

    def processImage(self):
        self.imageId = self.imageEdt.currentText()
        self.progress.show()
        self.progress.setValue(0)
        try:
            os.mkdir('tmp')
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
        self.folder = "tmp/Image_" + self.imageId
        try:
            os.mkdir(self.folder)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
        copy('Settings.csv', self.folder+'/Settings.csv')
        self.defaults = pd.read_csv(self.folder+'/Settings.csv')
        self.progressLbl.setText("Connecting to OMERO...")
        self.progressLbl.repaint()
        self.df, sizeX, sizeY, scaleX, maxPrj, maxZPrj, image = MitFunc.pullOMERO(
            self.userEdt.text(), self.pwEdt.text(), self.serverEdt.text(),
            self.imageId, self.defaults['Channel'][0], self.defaults['Stages'][0])
        box_size = 2*np.ceil(self.defaults['Nuclei Diameter'][0]/scaleX)
        self.df = MitFunc.find_rois(self.df, maxPrj, sizeX, sizeY, box_size)
        self.progress.setValue(95)
        self.progressLbl.setText("Saving ROIs")
        self.progressLbl.repaint()
        MitFunc.save_rois_to_omero(self.df, self.userEdt.text(
        ), self.pwEdt.text(), self.serverEdt.text(), self.imageId)
        MitFunc.rois_to_pngs(
            self.df, maxZPrj, self.settings['Duration'][0], self.imageId)
        self.progress.setValue(100)
        self.progressLbl.setText("Processing Finished")

    def select(self, text, j):
        # j is button number
        if self.buttonSt[j]:
            frame = text.partition("Selected")[0]
            self.buttonLbl[j].setText(frame)
            self.selected.remove(frame)
            self.buttonSt[j] = False
        else:
            frame = text.partition("Selected")[0]
            self.buttonLbl[j].setText(text)
            self.selected.append(frame)
            self.selected.sort()
            self.buttonSt[j] = True
        if self.selected:
            if len(self.selected) < len(self.results.columns[7:]):
                self.selectionLbl.setText("Select %s more" % (len(
                    self.results.columns[7:])-len(self.selected)))
            elif len(self.selected) > len(self.results.columns[7:]):
                self.selectionLbl.setText("Too many selected!")
            else:
                self.selectionLbl.setText("All stages selected")
        else:
            self.selectionLbl.setText("Click image to select time frame")
        print(self.selected)


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
    window = miApp()
    window.show()
    sys.exit(app.exec())
