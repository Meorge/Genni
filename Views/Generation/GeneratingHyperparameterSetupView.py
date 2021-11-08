from typing import List
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QDoubleSpinBox, QFormLayout, QLineEdit, QListWidget, QListWidgetItem, QPushButton, QSizePolicy, QSpinBox, QSplitter, QTextEdit, QWidget
from Views.WizardTitleView import WizardTitleView

class GeneratingHyperparameterSetupView(QWidget):
    generationStarted = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.title = WizardTitleView(self)
        self.title.setTitle('Generate Samples')
        self.title.setSubtitle('Configure the output you\'d like.')

        self.promptBox = QLineEdit('', self)
        self.promptBox.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        self.nSamplesSpinner = QSpinBox(self, minimum=0, maximum=999999, value=1)
        self.minLengthSpinner = QSpinBox(self, minimum=0, maximum=999999, value=1)
        self.maxLengthSpinner = QSpinBox(self, minimum=0, maximum=999999, value=256)
        self.tempSpinner = QDoubleSpinBox(self, minimum=0, maximum=999999, value=0.7)
        self.goButton = QPushButton('Generate', self, clicked=lambda: self.generationStarted.emit(self.getHyperparameters()))

        self.ly = QFormLayout(self)
        self.ly.addRow(self.title)
        self.ly.addRow('Prompt (optional):', self.promptBox)
        self.ly.addRow('Number of samples to generate:', self.nSamplesSpinner)
        self.ly.addRow('Minimum length:', self.minLengthSpinner)
        self.ly.addRow('Maximum length:', self.maxLengthSpinner)
        self.ly.addRow('Temperature:', self.tempSpinner) # TODO: descriptions of good temperature ranges?
        self.ly.addRow(self.goButton)

        self.ly.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def getHyperparameters(self) -> dict:
        return {
            'prompt': self.promptBox.text(),
            'n': self.nSamplesSpinner.value(),
            'minLength': self.minLengthSpinner.value(),
            'maxLength': self.maxLengthSpinner.value(),
            'temperature': self.tempSpinner.value()
        }

class GeneratingInProgressView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.title = WizardTitleView(self)
        self.title.setTitle('Generating Samples...')
        self.title.setSubtitle('This might take a little while.')

        self.ly = QFormLayout(self)
        self.ly.addRow(self.title)

class GeneratingCompleteView(QWidget):
    accept = pyqtSignal()

    __samples = []

    def __init__(self, parent=None):
        super().__init__(parent)
        self.title = WizardTitleView(self)
        self.title.setTitle('Generation Complete')
        self.title.setSubtitle('Samples have been generated.')

        self.listOfItems = QListWidget(self, currentItemChanged=self.onCurrentItemChanged)
        self.itemDetail = QTextEdit(self, readOnly=True)

        self.splitter = QSplitter(self)
        self.splitter.addWidget(self.listOfItems)
        self.splitter.addWidget(self.itemDetail)
        self.splitter.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.MinimumExpanding)

        self.closeButton = QPushButton('Close', self, clicked=self.accept)

        self.ly = QFormLayout(self)
        self.ly.addRow(self.title)
        self.ly.addRow(self.splitter)
        self.ly.addRow(self.closeButton)

    def onCurrentItemChanged(self, current: QListWidgetItem, prev: QListWidgetItem):
        self.itemDetail.setText(current.data(Qt.ItemDataRole.UserRole))

    def setSamples(self, samples: List[str]):
        self.__samples = samples

        self.listOfItems.clear()
        for i in self.__samples:
            item = QListWidgetItem(self.listOfItems)
            item.setText(i.replace('\n', ''))
            item.setData(Qt.ItemDataRole.UserRole, i)