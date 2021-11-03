from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtWidgets import QFileDialog, QFormLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QSizePolicy, QSpinBox, QVBoxLayout, QWidget

from Views.DatasetSelectionView import DatasetSelectionView

class TrainingHyperparameterSetupView(QWidget):
    """
    Hyperparameters:
    - learning rate
    - total steps
    - steps per generate
    - steps per save
    - source dataset
    """
    def __init__(self, parent=None):
        super().__init__(parent)

        self.learningRateValidator = QDoubleValidator(0.0, 100.0, 5)
        self.learningRateValidator.setNotation(QDoubleValidator.Notation.ScientificNotation)
        # self.sourceDatasetPicker = FilePicker(self)
        self.sourceDatasetPicker = DatasetSelectionView(self)


        self.learningRateBox = QLineEdit('0.01', self)
        self.learningRateBox.setValidator(self.learningRateValidator)
        self.learningRateBox.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        self.totalStepsSpinner = QSpinBox(self, minimum=0, maximum=999999, value=100)
        self.stepsPerGenSpinner = QSpinBox(self, minimum=0, maximum=999999, value=100)
        self.stepsPerSaveSpinner = QSpinBox(self, minimum=0, maximum=999999, value=1000)
        self.goButton = QPushButton('Start Training', self)

        self.ly = QFormLayout(self)
        self.ly.addRow('Dataset:', self.sourceDatasetPicker)
        self.ly.addRow('Total steps to train:', self.totalStepsSpinner)
        self.ly.addRow('Generate samples every:', self.stepsPerGenSpinner)
        self.ly.addRow('Save model every:', self.stepsPerSaveSpinner)
        self.ly.addRow('Learning rate:', self.learningRateBox)
        self.ly.addRow(self.goButton)
        self.ly.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def getHyperparameters(self) -> dict:
        return {
            'dataset': self.sourceDatasetPicker.dataset(),
            'steps': self.totalStepsSpinner.value(),
            'genEvery': self.stepsPerGenSpinner.value(),
            'saveEvery': self.stepsPerSaveSpinner.value(),
            'learningRate': float(self.learningRateBox.text())
        }

class FilePicker(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.filenameLabel = QLabel('dataset.txt')
        self.filenameLabel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)

        self.browseButton = QPushButton('Browse...', clicked=self.selectFile)
        self.browseButton.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)

        self.selectedFile = './training.txt'

        self.ly = QHBoxLayout(self)
        self.ly.addWidget(self.filenameLabel)
        self.ly.addWidget(self.browseButton)
        self.ly.setContentsMargins(0,0,0,0)

    def selectFile(self):
        file, ext = QFileDialog.getOpenFileName(self, caption='Select Dataset')
        if file is not None:
            self.selectedFile = file
            self.filenameLabel.setText(file)

    def filepath(self) -> str: return self.selectedFile