from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QVBoxLayout, QWidget
from Views.TrainingHyperparameterSetupView import TrainingHyperparameterSetupView
from Views.TrainingInProgressView import TrainingInProgressView
from Views.SwipingPageView import SwipingPageView

class TrainingView(QWidget):
    trainingStarted = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.hpSetupView = TrainingHyperparameterSetupView(self)
        
        self.trainingInProgressView = TrainingInProgressView(self)

        self.pageView = SwipingPageView(self)
        self.pageView.addWidget(self.hpSetupView)
        self.pageView.addWidget(self.trainingInProgressView)

        # TODO: have the setup view emit a signal when it's ready to proceed
        self.hpSetupView.goButton.clicked.connect(self.startTraining)

        self.ly = QVBoxLayout(self)
        self.ly.addWidget(self.pageView)

        self.setupHyperparameters()

    def setupHyperparameters(self):
        self.pageView.slideInIdx(0)
        
    def startTraining(self):
        self.pageView.slideInIdx(1)

        # TODO: make this a smooth signal/slot thingy
        self.trainingInProgressView.setHyperparameters(self.hpSetupView.getHyperparameters())
        self.trainingStarted.emit(self.hpSetupView.getHyperparameters())

