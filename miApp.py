from PyQt5.QtWidgets import QWidget, QPushButton
from PyQt5.QtWidgets import QLabel, QLineEdit, QGridLayout, QProgressBar
from PyQt5.QtWidgets import QFileDialog, QComboBox
from PyQt5.QtGui import QIcon
import os.path
import errno
from shutil import copy
import pandas as pd
import numpy as np
import MitFunc
import settingsWindow
import outputWindow


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
        self.file, _ = QFileDialog.getOpenFileName(None, 'Single File')
        print(self.file)
        try:
            os.mkdir('tmp')
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
        self.folder = "tmp/Image_"+os.path.basename(self.file)
        try:
            os.mkdir(self.folder)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
        copy('Settings.csv', self.folder+'/Settings.csv')
        self.defaults = pd.read_csv(self.folder+'/Settings.csv')
        self.df, sizeX, sizeY, scaleX, maxPrj, maxZPrj = MitFunc.pullLocal(
            self.file, self.defaults['Stages'][0])
        box_size = 2*np.ceil(self.defaults['Nuclei Diameter'][0]/scaleX)
        self.df = MitFunc.find_rois(self.df, maxPrj, sizeX, sizeY, box_size)
        self.progress.setValue(95)
        self.progressLbl.setText("Saving ROIs")
        self.progressLbl.repaint()
        # TO DO: save ROIS to text file
        MitFunc.rois_to_pngs(
            self.df, maxZPrj, self.settings['Duration'][0])
        self.progress.setValue(100)
        self.progressLbl.setText("Processing Finished")

    def showSettingsWindow(self):
        self.w = settingsWindow.settingsWindow()
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
        self.w = outputWindow.outputWindow()
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
