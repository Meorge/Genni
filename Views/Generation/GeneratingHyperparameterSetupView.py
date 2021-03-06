from random import randint
from typing import List
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QCheckBox, QDoubleSpinBox, QFormLayout, QLineEdit, QListWidget, QListWidgetItem, QPushButton, QSizePolicy, QSpinBox, QSplitter, QTextEdit, QWidget
from PyQtPlus.QtOnboarding import QWizardTitle

class GeneratingHyperparameterSetupView(QWidget):
    generationStarted = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.title = QWizardTitle(self)
        self.title.setTitle('Generate Samples')
        self.title.setSubtitle('Configure the output you\'d like.')
        self.title.setIcon('Icons/Generate.svg')

        self.promptBox = QTextEdit('', self, acceptRichText=False)
        self.promptBox.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        self.nSamplesSpinner = QSpinBox(self, minimum=0, maximum=999999, value=1)
        self.minLengthSpinner = QSpinBox(self, minimum=0, maximum=999999, value=1)
        self.maxLengthSpinner = QSpinBox(self, minimum=0, maximum=999999, value=256)
        self.tempSpinner = QDoubleSpinBox(self, minimum=0, maximum=999999, value=0.7)

        self.topKSpinner = QSpinBox(self, minimum=0, maximum=999999, value=0)
        self.topPSpinner = QDoubleSpinBox(self, minimum=0, maximum=1, value=0, singleStep=0.1)

        # using same method of generating a random integer as aitextgen's generate_to_file() function
        initialSeed = randint(10 ** 7, 10 ** 8 - 1)
        self.seedSpinner = QSpinBox(self, minimum=0, maximum=99999999, value=initialSeed)

        self.checkAgainstDatasetCheckbox = QCheckBox('Check against datasets', parent=self)
        self.goButton = QPushButton('Generate', self, clicked=lambda: self.generationStarted.emit(self.getHyperparameters()))

        self.ly = QFormLayout(self)
        self.ly.addRow(self.title)
        self.ly.addRow('Prompt (optional):', self.promptBox)
        self.ly.addRow('Number of samples to generate:', self.nSamplesSpinner)
        self.ly.addRow('Minimum length:', self.minLengthSpinner)
        self.ly.addRow('Maximum length:', self.maxLengthSpinner)
        self.ly.addRow('Temperature:', self.tempSpinner) # TODO: descriptions of good temperature ranges?
        self.ly.addRow('Top K:', self.topKSpinner)
        self.ly.addRow('Top P:', self.topPSpinner)
        self.ly.addRow('Seed:', self.seedSpinner)
        self.ly.addWidget(self.checkAgainstDatasetCheckbox)
        self.ly.addRow(self.goButton)

        self.ly.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def getHyperparameters(self) -> dict:
        return {
            'prompt': self.promptBox.toPlainText(),
            'n': self.nSamplesSpinner.value(),
            'minLength': self.minLengthSpinner.value(),
            'maxLength': self.maxLengthSpinner.value(),
            'temperature': self.tempSpinner.value(),
            'topK': self.topKSpinner.value(),
            'topP': self.topPSpinner.value(),
            'seed': self.seedSpinner.value(),
            'checkAgainstDatasets': self.checkAgainstDatasetCheckbox.isChecked()
        }

class GeneratingInProgressView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.title = QWizardTitle(self)
        self.title.setTitle('Generating Samples...')
        self.title.setSubtitle('This might take a little while.')
        self.title.setIcon('Icons/Generate.svg')

        self.ly = QFormLayout(self)
        self.ly.addRow(self.title)

class ProcessingInProgressView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.title = QWizardTitle(self)
        self.title.setTitle('Processing Samples...')
        self.title.setSubtitle('Almost done! We\'re comparing the generated samples against the loaded datasets to check for overtraining.')
        self.title.setIcon('Icons/Generate.svg')

        self.ly = QFormLayout(self)
        self.ly.addRow(self.title)

class GeneratingCompleteView(QWidget):
    accept = pyqtSignal()

    __samples = []

    def __init__(self, parent=None):
        super().__init__(parent)
        self.title = QWizardTitle(self)
        self.title.setTitle('Generation Complete')
        self.title.setSubtitle('Samples have been generated.')
        self.title.setIcon('Icons/Generate.svg')

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
        data = current.data(Qt.ItemDataRole.UserRole)
        if isinstance(data, str):
            self.itemDetail.setText(data)
        elif isinstance(data, dict):
            self.itemDetail.setText(data.get('text', ''))

    def setSamples(self, samples: List[str]):
        self.__samples = samples

        self.listOfItems.clear()
        for i in self.__samples:
            i: dict
            item = QListWidgetItem(self.listOfItems)

            textWithoutNewlines = i['text'].replace('\n', '')
            item.setText(textWithoutNewlines)
            item.setData(Qt.ItemDataRole.UserRole, i)

            if i.get('datasetMatches') is not None and len(i.get('datasetMatches', [])) > 0:
                topMatch = sorted(i.get('datasetMatches', []), key=lambda x: x.get('ratio', 0), reverse=True)[0]
                ratio = topMatch.get('ratio', 0)
                if ratio >= 1.0:
                    item.setIcon(QIcon('Icons/Critical.svg'))
                elif ratio > 0.5:
                    item.setIcon(QIcon('Icons/Warning.svg'))