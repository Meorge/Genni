from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFormLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QSizePolicy, QSpinBox, QVBoxLayout, QWidget

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

        self.sourceDatasetPicker = FilePicker(self)
        self.learningRateBox = QLineEdit('0.001', self)
        self.totalStepsSpinner = QSpinBox(self, value=10000, minimum=0, maximum=999999)
        self.stepsPerGenSpinner = QSpinBox(self, value=500, minimum=0, maximum=999999)
        self.stepsPerSaveSpinner = QSpinBox(self, value=1000, minimum=0, maximum=999999)
        self.goButton = QPushButton('Start Training', self)

        self.ly = QFormLayout(self)
        self.ly.addRow('Dataset', self.sourceDatasetPicker)
        self.ly.addRow('Total steps to train', self.totalStepsSpinner)
        self.ly.addRow('Generate samples every', self.stepsPerGenSpinner)
        self.ly.addRow('Save model every', self.stepsPerSaveSpinner)
        self.ly.addRow('Learning rate', self.learningRateBox)
        self.ly.addRow(self.goButton)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

class FilePicker(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.box = QLabel('dataset.txt', self)
        self.browseButton = QPushButton('Browse...', self)

        self.ly = QHBoxLayout(self)
        self.ly.addWidget(self.box)
        self.ly.addWidget(self.browseButton)
        self.ly.setContentsMargins(0,0,0,0)