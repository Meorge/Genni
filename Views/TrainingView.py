from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtWidgets import QLabel, QPushButton, QSizePolicy, QVBoxLayout, QWidget
from Views.TrainingHyperparameterSetupView import TrainingHyperparameterSetupView
from Views.TrainingInProgressView import TrainingInProgressView
from Views.SwipingPageView import SwipingPageView

class TrainingView(QWidget):
    trainingStarted = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.trainingLabel = QLabel(self)
        self.trainingLabelFont = QFont()
        self.trainingLabelFont.setBold(True)
        self.trainingLabelFont.setPointSizeF(self.trainingLabelFont.pointSizeF() * 2.0)
        self.trainingLabel.setFont(self.trainingLabelFont)
        self.trainingLabel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)

        self.trainingSourceLabel = QLabel(self)
        self.trainingSourceLabel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)

        self.hpSetupView = TrainingHyperparameterSetupView(self)
        
        self.trainingInProgressView = TrainingInProgressView(self)

        self.pageView = SwipingPageView(self)
        self.pageView.addWidget(self.hpSetupView)
        self.pageView.addWidget(self.trainingInProgressView)

        self.hpSetupView.goButton.clicked.connect(self.startTraining)

        self.ly = QVBoxLayout(self)
        self.ly.addWidget(self.trainingLabel, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.ly.addWidget(self.trainingSourceLabel, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.ly.addWidget(self.pageView)

        self.setupHyperparameters()

    def setupHyperparameters(self):
        self.trainingLabel.setText('Configure Training')
        self.trainingSourceLabel.setText('Configure the training session.')
        self.pageView.slideInIdx(0)
        
    def startTraining(self):
        self.trainingLabel.setText('Training...')
        self.trainingSourceLabel.setText('Finetuning on the dataset \"NOT A REAL FILE.txt\".')
        self.pageView.slideInIdx(1)
        self.trainingStarted.emit()

