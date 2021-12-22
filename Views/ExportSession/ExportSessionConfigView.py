from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QButtonGroup, QCheckBox, QDialog, QFormLayout, QHBoxLayout, QLabel, QLineEdit, QPlainTextEdit, QPushButton, QRadioButton, QSizePolicy, QTextEdit, QTreeWidget, QVBoxLayout, QWidget
from Core.ModelRepo import getGeneratedTextInRepository
from Views.ButtonWithIconAndDetailView import ButtonWithIconAndDetailView
from PyQtPlus.QtOnboarding import QWizardTitle, QSwipingPage
from random import shuffle

class ExportSessionConfigView(QWidget):
    configDone = pyqtSignal(str)
    def __init__(self, repoName, sessionName, parent=None):
        super().__init__(parent)
        self.__repoName = repoName
        self.__sessionName = sessionName

        self.title = QWizardTitle(self)
        self.title.setTitle('Export Session')
        self.title.setSubtitle('Configure how samples from this session will be exported.')
        self.title.setIcon('Icons/Export.svg')

        # Which items to export
        self.exportOnlyFav = QRadioButton('Favorite samples only', checked=True)
        self.exportAll = QRadioButton('All samples')

        self.exportButtonGroup = QButtonGroup(self)
        self.exportButtonGroup.addButton(self.exportOnlyFav, 0)
        self.exportButtonGroup.addButton(self.exportAll, 1)

        self.exportLy = QVBoxLayout()
        self.exportLy.addWidget(self.exportOnlyFav)
        self.exportLy.addWidget(self.exportAll)
        self.exportLy.setContentsMargins(0,0,0,0)

        # Options for text file
        self.custSeqBox = QTextEdit(acceptRichText=False, enabled=False)
        self.useNewline = QRadioButton('New line', checked=True)
        self.useCustSeq = QRadioButton('Custom string', toggled=self.custSeqBox.setEnabled)

        self.sepButtonGroup = QButtonGroup()
        self.sepButtonGroup.addButton(self.useNewline, 0)
        self.sepButtonGroup.addButton(self.useCustSeq, 1)

        self.sepLy = QVBoxLayout()
        self.sepLy.addWidget(self.useNewline)
        self.sepLy.addWidget(self.useCustSeq)
        self.sepLy.addWidget(self.custSeqBox)
        self.sepLy.setContentsMargins(0,0,0,0)

        # Shuffle samples?
        self.shuffleOption = QCheckBox('Shuffle samples')

        self.nextButton = QPushButton('Export', self, clicked=self.buildOutput)

        self.ly = QFormLayout(self)
        self.ly.addRow(self.title)
        self.ly.addRow('Export:', self.exportLy)
        self.ly.addRow('Separate samples with:', self.sepLy)
        self.ly.addWidget(self.shuffleOption)
        self.ly.addRow(self.nextButton)

    def buildOutput(self):
        # Determine whether to use all samples or only favorited ones
        onlyUseFavorites = self.exportButtonGroup.checkedId() == 0

        # Determine whether to shuffle the samples
        shuffleSamples = self.shuffleOption.isChecked()

        # Determine what string to separate samples with
        sep = '\n'
        if self.sepButtonGroup.checkedId() == 1:
            sep = self.custSeqBox.toPlainText()

        allTexts = [i.get('text', '') for i in
            getGeneratedTextInRepository(self.__repoName, self.__sessionName).get('texts', [])
            if (not onlyUseFavorites) or (onlyUseFavorites and i.get('status', '') == 'favorited')
            ]

        if shuffleSamples: shuffle(allTexts)

        concatenated = sep.join(allTexts)

        print(concatenated)
        self.configDone.emit(concatenated)
        

class ExportSessionResultView(QWidget):
    returnToConfig = pyqtSignal()
    def __init__(self, repoName, sessionName, parent=None):
        super().__init__(parent)
        self.__repoName = repoName
        self.__sessionName = sessionName

        self.title = QWizardTitle(self)
        self.title.setTitle('Export Session')
        self.title.setSubtitle('Copy the text from here.')
        self.title.setIcon('Icons/Export.svg')

        self.textBox = QTextEdit(readOnly=True, acceptRichText=False)

        self.backButton = QPushButton('Back', clicked=self.returnToConfig)

        self.ly = QFormLayout(self)
        self.ly.addRow(self.title)
        self.ly.addRow(self.textBox)
        self.ly.addRow(self.backButton)

    def setText(self, text: str):
        self.__text = text
        self.textBox.setText(text)
        


class ExportSessionModal(QDialog):
    def __init__(self, repoName, sessionName, parent=None):
        super().__init__(parent)

        self.configView = ExportSessionConfigView(repoName, sessionName, self)
        self.resultView = ExportSessionResultView(repoName, sessionName, self)

        self.configView.configDone.connect(self.onConfigDone)
        self.resultView.returnToConfig.connect(self.onReturnToConfig)

        self.slideView = QSwipingPage(self)
        self.slideView.addWidget(self.configView)
        self.slideView.addWidget(self.resultView)

        self.ly = QVBoxLayout(self)
        self.ly.addWidget(self.slideView)
        self.ly.setContentsMargins(0,0,0,0)

    def onConfigDone(self, text: str):
        self.resultView.setText(text)
        self.slideView.slideInWgt(self.resultView)

    def onReturnToConfig(self):
        self.slideView.slideInWgt(self.configView)