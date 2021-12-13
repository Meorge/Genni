from PyQt6.QtCore import QSize, Qt, pyqtSignal
from PyQt6.QtGui import QDoubleValidator
from PyQt6.QtWidgets import QFileDialog, QFormLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QSizePolicy, QSpinBox, QVBoxLayout, QWidget

from Views.DatasetSelectionView import DatasetSelectionView
from PyQtPlus.QtOnboarding import QWizardTitle

class TrainingHyperparameterSetupView(QWidget):
    """
    Hyperparameters:
    - learning rate
    - total steps
    - steps per generate
    - steps per save
    - source dataset
    """
    goBack = pyqtSignal()
    proceed = pyqtSignal()

    def __init__(self, parent=None, repoName=None):
        super().__init__(parent)
        self.title = QWizardTitle(self)
        self.title.setTitle('Configure Training')
        self.title.setSubtitle('Configure the training session.')
        self.title.setIcon('Icons/Train.svg')

        self.modelTitleBox = QLineEdit('My Model', self)

        self.totalStepsSpinner = QSpinBox(self, minimum=0, maximum=999999, value=100)
        self.stepsPerGenSpinner = QSpinBox(self, minimum=0, maximum=999999, value=5)
        self.stepsPerSaveSpinner = QSpinBox(self, minimum=0, maximum=999999, value=5)

        self.learningRateValidator = QDoubleValidator(0.0, 100.0, 5)
        self.learningRateValidator.setNotation(QDoubleValidator.Notation.ScientificNotation)
        self.sourceDatasetPicker = DatasetSelectionView(self, repoName=repoName)
        self.sourceDatasetPicker.datasetChanged.connect(self.onDatasetChanged)

        self.learningRateBox = QLineEdit('0.001', self)
        self.learningRateBox.setValidator(self.learningRateValidator)
        self.learningRateBox.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        self.backButton = QPushButton('Back', self, clicked=self.goBack)
        self.goButton = QPushButton('Start Training', self, clicked=self.proceed)

        self.btnLy = QHBoxLayout()
        self.btnLy.addWidget(self.backButton)
        self.btnLy.addWidget(self.goButton)

        self.formLy = QFormLayout()
        self.formLy.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        self.formLy.addRow('Title:', self.modelTitleBox)
        self.formLy.addRow('Dataset:', self.sourceDatasetPicker)
        self.formLy.addRow('Total steps to train:', self.totalStepsSpinner)
        self.formLy.addRow('Generate samples every:', self.stepsPerGenSpinner)
        self.formLy.addRow('Save model every:', self.stepsPerSaveSpinner)
        self.formLy.addRow('Learning rate:', self.learningRateBox)
        
        self.ly = QVBoxLayout(self)

        self.ly.addWidget(self.title)
        self.ly.addLayout(self.formLy)
        self.ly.addStretch()
        self.ly.addLayout(self.btnLy)
        
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.onDatasetChanged(self.sourceDatasetPicker.dataset())

    def onDatasetChanged(self, dataset):
        if dataset == '': dataset = None
        print(f'Dataset: \"{dataset}\"')
        self.goButton.setEnabled(dataset is not None)

    def getHyperparameters(self) -> dict:
        return {
            'title': self.modelTitleBox.text(),
            'dataset': self.sourceDatasetPicker.dataset(),
            'steps': self.totalStepsSpinner.value(),
            'genEvery': self.stepsPerGenSpinner.value(),
            'saveEvery': self.stepsPerSaveSpinner.value(),
            'learningRate': float(self.learningRateBox.text())
        }