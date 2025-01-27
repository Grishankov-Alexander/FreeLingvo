"""
Implementation of the Application's MainWindow.
Copyright (C) 2019, 2020  ache2014

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

Contact: ache2014@gmail.com
"""

import os

import logging
logger = logging.getLogger("main.mainwindow")

from PySide2.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLineEdit, QPushButton,
    QComboBox, QTextBrowser, QHBoxLayout, QVBoxLayout,
    QLabel, QProgressBar, QMessageBox
    )
from PySide2.QtCore import Signal, Slot, Qt, QObject, QThread
from PySide2.QtGui import (
    QGuiApplication, QKeySequence, QCursor, QIcon, QTextCursor,
    QFont, QFontDatabase
    )

from parsing_and_formatting import load_entries, translate


class Worker(QObject):
    """Special class for time-consuming operations that should
    be used in the different thread."""
    started = Signal(str)
    ended = Signal()
    translationsReady = Signal(list)
    
    @Slot(str)
    def loadDict(self, dictName):
        """Loads the contents of the selected dictionary as an XML
        element tree and saves it locally."""
        self.started.emit(self.tr("Loading dictionary..."))
        self.loadedEntries = load_entries(
            self.mainWindow.appctxt.get_resource(
                "dictionaries/" + dictName + ".tei"
                )
            )
        self.ended.emit()
    
    @Slot()
    def findTranslations(self):
        """Produces the translations list for the entered text
        and emits signal with that list."""
        try:
            self.started.emit(self.tr("Searching for translations..."))
            searchedText = self.mainWindow.searchText.text()
            translations = translate(
                searchedText, self.loadedEntries
                )
            self.translationsReady.emit(translations)
            self.ended.emit()
        except Exception as e:
            logger.exception(
                "Exception happened during translation:\n"
                "Dictionary: \"%s\"\n"
                "Searched text: \"%s\".\n",
                self.mainWindow.dictsCombo.currentText(),
                searchedText
                )

    def __init__(self, mainWindow):
        """Initialize the class with useful variables."""
        super().__init__()
        self.mainWindow = mainWindow
        self.loadedEntries = []


class MainWindow(QMainWindow):
    """Main class for interacting with the applications GUI."""
    @Slot(str)
    def startProgress(self, message):
        """Shows that the window is busy doing some work."""
        self.translateButton.setEnabled(False)
        self.dictsCombo.setEnabled(False)
        label = QLabel(message)
        label.setAlignment(Qt.AlignHCenter)
        progressBar = QProgressBar()
        progressBar.setRange(0, 0)
        self.statusBar().clearMessage()
        self.statusBar().addWidget(label, 1)
        self.statusBar().addWidget(progressBar, 1)
        QGuiApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
        
    @Slot()
    def endProgress(self):
        """Shows that the window is ready for the interaction."""
        self.statusBar().setParent(None)
        self.statusBar().showMessage(self.tr("Done"), 2000)
        QGuiApplication.restoreOverrideCursor()
        self.translateButton.setEnabled(True)
        self.dictsCombo.setEnabled(True)
        
    @Slot()
    def about(self):
        """Shows the "about" message box."""
        title = self.tr("About FreeLingvo")
        text = self.tr(
            "<b>FreeLingvo</b> is a dictionary search application"
            " that can work with over 140 dictionaries without"
            " Internet connection and is available under the"
            " GNU General Public License v3.<br><br>"
            "To search for translations in the selected"
            " dictionary, you must enter the desired word"
            " in the field and press \"Enter\" or click the"
            " \"translate\" button. You can also enter a sentence."
            " In this case, the sentence will be divided into"
            " separate words and possible combinations of these words."
            " The program will search for each word and combination"
            " in the selected dictionary, in which case the"
            " output can be large.<br><br>"
            "<b>Homepage:</b>"
            "<a href=\"https://github.com/ache2014/FreeLingvo\">"
            " GitHub</a><br>"
            "<b>Contact:</b>"
            "<a href=\"mailto:ache2014@gmail.com\">"
            " ache2014@gmail.com</a>"
        )
        QMessageBox.about(self, title, text)

    @Slot(list)
    def showTranslations(self, translations):
        """Shows translations in the translations browser"""
        if translations:
            text = "<hr>".join(translations)
        else:
            text = self.tr("Sorry, no translations were found for:")
            text += "<br><b>{}</b>".format(self.searchText.text())
        cursor = self.translationsBrowser.textCursor()
        cursor.select(QTextCursor.Document)
        cursor.insertHtml(text)

    @Slot(str)
    def changeFontSize(self, size):
        """Changes the font size for the translations browser."""
        self.translationsBrowser.setFont(
            QFont(self.font().family(), int(size))
            )
        self.update()
    
    def __init__(self, parent=None, *args, appctxt=None, **kwargs):
        """Initializes all GUI elements and a separate thread."""
        super().__init__(parent)
        self.appctxt = appctxt
        self.worker = Worker(self)
        self.workerThread = QThread()
        self.worker.moveToThread(self.workerThread)
        self.workerThread.finished.connect(self.worker.deleteLater)
        self.worker.started.connect(self.startProgress)
        self.worker.ended.connect(self.endProgress)
        self.worker.translationsReady.connect(self.showTranslations)
        self.workerThread.start()

        screenGeometry = QGuiApplication.screens()[0].geometry()
        self.setGeometry(
            screenGeometry.width() / 5, screenGeometry.height() / 5,
            screenGeometry.width() / 3, screenGeometry.height() / 3
            )
        self.setMinimumSize(screenGeometry.width() / 4,
                            screenGeometry.height() / 4)

        self.fileMenu = self.menuBar().addMenu(self.tr("&File"))
        self.exitAct = self.fileMenu.addAction(self.tr("&Exit"))
        self.exitAct.setStatusTip(self.tr("Exit from FreeLingvo"))
        self.exitAct.triggered.connect(self.close)

        self.helpMenu = self.menuBar().addMenu(self.tr("&Help"))
        self.aboutAct = self.helpMenu.addAction(self.tr("&About"))
        self.aboutAct.setStatusTip(
            self.tr("Show information about FreeLingvo")
            )
        self.aboutAct.triggered.connect(self.about)

        self.searchText = QLineEdit()
        self.searchText.setPlaceholderText(
            self.tr("What word(s) to look for?")
            )
        self.searchText.setClearButtonEnabled(True)
        self.searchText.returnPressed.connect(self.worker.findTranslations)

        self.translateButton = QPushButton(self.tr("Translate"))
        self.translateButton.clicked.connect(self.worker.findTranslations)

        self.dictsCombo = QComboBox()
        self.dictsCombo.setInsertPolicy(QComboBox.InsertAlphabetically)
        self.dictsCombo.setToolTip(
            self.tr("Dictionary used to search for words")
            )
        dictNames = os.listdir(self.appctxt.get_resource("dictionaries"))
        dictNames = [name.replace(".tei", "") for name in dictNames]
        self.dictsCombo.addItems(dictNames)
        self.dictsCombo.currentIndexChanged[str].connect(self.worker.loadDict)
        self.dictsCombo.setCurrentIndex(1);

        self.translationsBrowser = QTextBrowser()
        self.translationsBrowser.setUndoRedoEnabled(True)

        self.undoButton = QPushButton(
            QIcon(self.appctxt.get_resource("images/arrow_back.png")),
            ""
            )
        self.undoButton.setEnabled(False)
        self.undoButton.setToolTip(self.tr("Show previous translation"))
        self.undoButton.clicked.connect(self.translationsBrowser.undo)
        self.translationsBrowser.undoAvailable.connect(
            self.undoButton.setEnabled
            )
        
        self.redoButton = QPushButton(
            QIcon(self.appctxt.get_resource("images/arrow_forward.png")),
            ""
            )
        self.redoButton.setEnabled(False)
        self.redoButton.setToolTip(self.tr("Show next translation"))
        self.redoButton.clicked.connect(self.translationsBrowser.redo)
        self.translationsBrowser.redoAvailable.connect(
            self.redoButton.setEnabled
            )

        self.sizeLabel = QLabel(self.tr("Font size:"))
        self.sizeCombo = QComboBox()
        for size in QFontDatabase.standardSizes():
            self.sizeCombo.addItem(str(size))
        self.sizeCombo.setCurrentText(str(self.font().pointSize()))
        self.sizeCombo.currentIndexChanged[str].connect(self.changeFontSize)
        
        self.controlsLayout = QHBoxLayout()
        self.controlsLayout.addWidget(self.searchText)
        self.controlsLayout.addWidget(self.translateButton)
        self.controlsLayout.addWidget(self.dictsCombo)

        self.browserToolsLayout = QHBoxLayout()
        self.browserToolsLayout.addWidget(self.undoButton)
        self.browserToolsLayout.addWidget(self.redoButton)
        self.browserToolsLayout.addStretch(1)
        self.browserToolsLayout.addWidget(self.sizeLabel)
        self.browserToolsLayout.addWidget(self.sizeCombo)

        self.centralLayout = QVBoxLayout()
        self.centralLayout.addLayout(self.controlsLayout)
        self.centralLayout.addLayout(self.browserToolsLayout)
        self.centralLayout.addWidget(self.translationsBrowser)

        centralWidget = QWidget()
        centralWidget.setLayout(self.centralLayout)
        self.setCentralWidget(centralWidget)

        self.statusBar().showMessage(self.tr("Ready"), 2000)
        
    def closeEvent(self, event):
        """Destroys the thread properly before exiting."""
        self.workerThread.quit()
        self.workerThread.wait()
        super().closeEvent(event)
