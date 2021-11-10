from PyQt6.QtCore import QSize, Qt, pyqtSignal
from PyQt6.QtGui import QDoubleValidator
from PyQt6.QtWidgets import QFileDialog, QFormLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QSizePolicy, QSpinBox, QVBoxLayout, QWidget

from Views.DatasetSelectionView import DatasetSelectionView
from Views.WizardTitleView import WizardTitleView

class TrainingHyperparameterSetupView(QWidget):
    """
    Hyperparameters:
    - learning rate
    - total steps
    - steps per generate
    - steps per save
    - source dataset
    """
    proceed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.title = WizardTitleView(self)
        self.title.setTitle('Configure Training')
        self.title.setSubtitle('Configure the training session.')

        self.modelTitleBox = QLineEdit('My Model', self)

        self.learningRateValidator = QDoubleValidator(0.0, 100.0, 5)
        self.learningRateValidator.setNotation(QDoubleValidator.Notation.ScientificNotation)
        self.sourceDatasetPicker = DatasetSelectionView(self)

        self.learningRateBox = QLineEdit('0.01', self)
        self.learningRateBox.setValidator(self.learningRateValidator)
        self.learningRateBox.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        self.totalStepsSpinner = QSpinBox(self, minimum=0, maximum=999999, value=100)
        self.stepsPerGenSpinner = QSpinBox(self, minimum=0, maximum=999999, value=100)
        self.stepsPerSaveSpinner = QSpinBox(self, minimum=0, maximum=999999, value=1000)
        self.goButton = QPushButton('Start Training', self, clicked=self.proceed)

        self.ly = QFormLayout(self)
        self.ly.addRow(self.title)
        self.ly.addRow('Title:', self.modelTitleBox)
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
            'title': self.modelTitleBox.text(),
            'dataset': self.sourceDatasetPicker.dataset(),
            'steps': self.totalStepsSpinner.value(),
            'genEvery': self.stepsPerGenSpinner.value(),
            'saveEvery': self.stepsPerSaveSpinner.value(),
            'learningRate': float(self.learningRateBox.text())
        }