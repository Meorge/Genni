from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QCheckBox, QDialog, QFormLayout, QHBoxLayout, QLineEdit, QPushButton, QTextEdit, QVBoxLayout, QWidget
from ATGDatasetTokenizer import ATGDatasetTokenizer
from Views.ButtonWithIconAndDetailView import ButtonWithIconAndDetailView
from Views.SwipingPageView import SwipingPageView
from Views.FilePicker import FilePicker
from Views.WizardTitleView import WizardTitleView

class ImportDatasetView(SwipingPageView):
    finished = pyqtSignal()

    def __init__(self, parent=None, repoName=None):
        super().__init__(parent)
        self.__repoName = repoName
        self.sourceSelectView = DatasetSourceSelectView(self)
        self.sourceSelectView.proceed.connect(self.goToConfigTextFileView)
        # For text file
        self.configTextFileView = DatasetFromTextConfigView(self)
        self.configTextFileView.back.connect(self.goToSourceSelectView)
        self.configTextFileView.proceed.connect(self.goToImportTextFileView)
        self.configTextFileView.proceed.connect(self.runImportDatasetThread)

        self.importTextFileView = DatasetFromTextImportProressView(self)

        self.importTextDoneView = DatasetFromTextImportDoneView(self)
        self.importTextDoneView.finished.connect(self.finished)


        self.addWidget(self.sourceSelectView)
        self.addWidget(self.configTextFileView)
        self.addWidget(self.importTextFileView)
        self.addWidget(self.importTextDoneView)

    def goToSourceSelectView(self): self.slideInWgt(self.sourceSelectView)
    def goToConfigTextFileView(self): self.slideInWgt(self.configTextFileView)
    def goToImportTextFileView(self): self.slideInWgt(self.importTextFileView)
    def goToImportTextDoneView(self): self.slideInWgt(self.importTextDoneView)

    def runImportDatasetThread(self):
        info = self.configTextFileView.getConfigData()
        
        self.datasetThread = ATGDatasetTokenizer(self, repoName=self.__repoName)
        self.datasetThread.setTitle(info['title'])
        self.datasetThread.setComment(info['comment'])
        self.datasetThread.setLineByLine(info['lineByLine'])
        self.datasetThread.setDataset(info['filename'])

        self.datasetThread.finished.connect(self.goToImportTextDoneView)
        self.datasetThread.start()

class DatasetSourceSelectView(QWidget):
    proceed = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.title = WizardTitleView(self)
        self.title.setTitle('Add Dataset')
        self.title.setSubtitle('Choose a source for the new dataset.')

        self.textFileOptionButton = ButtonWithIconAndDetailView(title='Text file', desc='Train on a text file from your computer.', svg='Icons/New File.svg', parent=self)
        self.twitterAcctOptionButton = ButtonWithIconAndDetailView(title='Twitter account', desc='Train on Tweets from a specific Twitter account.', svg='Icons/Twitter.svg', parent=self)
        self.nextButton = QPushButton('Next', clicked=self.proceed)

        self.textFileOptionButton.setChecked(True)
        self.twitterAcctOptionButton.setEnabled(False)

        self.ly = QVBoxLayout(self)
        self.ly.addWidget(self.title, alignment=Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        self.ly.addWidget(self.textFileOptionButton)
        self.ly.addWidget(self.twitterAcctOptionButton)
        self.ly.addWidget(QWidget())
        self.ly.addWidget(self.nextButton)

class DatasetFromTextConfigView(QWidget):
    back = pyqtSignal()
    proceed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.title = WizardTitleView(self)
        self.title.setTitle('Add Dataset From Text File')
        self.title.setSubtitle('Select the text file and other information, or whatever.')

        self.sourceFilePicker = FilePicker(self)
        self.lineByLineCheckbox = QCheckBox('Treat each line as its own sample', self)

        self.datasetTitleEntry = QLineEdit(self)
        self.datasetDescEntry = QTextEdit(self)

        self.nextButton = QPushButton('Import', clicked=self.proceed)
        self.backButton = QPushButton('Back', clicked=self.back)
        self.buttonsLy = QHBoxLayout()
        self.buttonsLy.addWidget(self.backButton)
        self.buttonsLy.addWidget(self.nextButton)

        self.ly = QFormLayout(self)
        self.ly.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        self.ly.addRow(self.title)
        self.ly.addRow('Dataset file:', self.sourceFilePicker)
        self.ly.addWidget(self.lineByLineCheckbox)
        self.ly.addRow('Title:', self.datasetTitleEntry)
        self.ly.addRow('Description:', self.datasetDescEntry)
        self.ly.addRow(self.buttonsLy)

    def getConfigData(self):
        return {
            'filename': self.sourceFilePicker.filepath(),
            'title': self.datasetTitleEntry.text(),
            'comment': self.datasetDescEntry.toPlainText(),
            'lineByLine': self.lineByLineCheckbox.isChecked()
        }
        
class DatasetFromTextImportProressView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.title = WizardTitleView(self)
        self.title.setTitle('Adding Dataset...')
        self.title.setSubtitle('This shouldn\'t take very long.')

        self.ly = QVBoxLayout(self)
        self.ly.addWidget(self.title, alignment=Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)

class DatasetFromTextImportDoneView(QWidget):
    finished = pyqtSignal()
    def __init__(self, parent=None):
        super().__init__(parent)

        self.title = WizardTitleView(self)
        self.title.setTitle('Dataset Added')
        self.title.setSubtitle('The dataset has been added to this repository and is ready for training.')

        self.closeButton = QPushButton('Close', clicked=self.finished)

        self.ly = QVBoxLayout(self)
        self.ly.addWidget(self.title, alignment=Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        self.ly.addWidget(self.closeButton)


class ImportDatasetModal(QDialog):
    def __init__(self, parent=None, repoName=None):
        super().__init__(parent)
        self.setModal(True)

        self.w = ImportDatasetView(self, repoName=repoName)
        self.w.finished.connect(self.accept)

        self.ly = QVBoxLayout(self)
        self.ly.setContentsMargins(0,0,0,0)
        self.ly.addWidget(self.w)
        self.setLayout(self.ly)
        