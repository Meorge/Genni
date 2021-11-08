from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QWidget
from ATGTrainer import ATGTrainer
from Views.Training.TrainingHyperparameterSetupView import TrainingHyperparameterSetupView
from Views.Training.TrainingInProgressView import TrainingInProgressView
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
        self.hpSetupView.proceed.connect(self.startTraining)

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


class TrainingModal(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.trainingView = TrainingView(self)
        self.trainingView.trainingStarted.connect(self.doTraining)
        self.trainingView.trainingInProgressView.doneButton.clicked.connect(self.accept)
        
        self.ly = QVBoxLayout(self)
        self.ly.setContentsMargins(0,0,0,0)
        self.ly.addWidget(self.trainingView)

    def doTraining(self, hp: dict):
        self.trainThread = ATGTrainer(self)
        self.trainingView.trainingInProgressView.trainingInfo.setTrainer(self.trainThread)
        
        self.trainThread.setDataset(hp['dataset'])
        self.trainThread.setTotalSteps(hp['steps'])
        self.trainThread.setGenEvery(hp['genEvery'])
        self.trainThread.setSaveEvery(hp['saveEvery'])
        self.trainThread.setLearningRate(hp['learningRate'])

        self.trainThread.trainingStarted.connect(self.trainingView.trainingInProgressView.onTrainingStarted)
        self.trainThread.trainingEnded.connect(self.trainingView.trainingInProgressView.onTrainingEnded)
        self.trainThread.batchEnded.connect(self.trainingView.trainingInProgressView.onBatchEnded)
        self.trainThread.sampleTextGenerated.connect(self.trainingView.trainingInProgressView.onSamplesGenerated)
        self.trainThread.timePassed.connect(self.trainingView.trainingInProgressView.trainingInfo.onTimePassed)
        self.trainThread.start()