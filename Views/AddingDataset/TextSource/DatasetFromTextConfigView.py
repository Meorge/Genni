from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QCheckBox, QFormLayout, QHBoxLayout, QLineEdit, QPushButton, QTextEdit, QWidget
from Views.FilePicker import FilePicker
from Views.WizardTitleView import WizardTitleView

class DatasetFromTextConfigView(QWidget):
    back = pyqtSignal()
    proceed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.title = WizardTitleView(self)
        self.title.setTitle('Add Dataset From Text File')
        self.title.setSubtitle('Select the text file and other information, or whatever.')
        self.title.setIcon('Icons/New File.svg')

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