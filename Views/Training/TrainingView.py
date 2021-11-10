from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QWidget
from ATGTrainer import ATGTrainer
from Views.Training.TrainingFreshModelView import TrainingFreshModelGPT2SizeView, TrainingFreshModelView
from Views.Training.TrainingHyperparameterSetupView import TrainingHyperparameterSetupView
from Views.Training.TrainingInProgressView import TrainingInProgressView
from Views.SwipingPageView import SwipingPageView

class TrainingView(QWidget):
    trainingStarted = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.freshModelView = TrainingFreshModelView(self)
        self.gptSizeView = TrainingFreshModelGPT2SizeView(self)
        self.hpSetupView = TrainingHyperparameterSetupView(self)
        self.trainingInProgressView = TrainingInProgressView(self)

        self.pageView = SwipingPageView(self)
        self.pageView.addWidget(self.freshModelView)
        self.pageView.addWidget(self.gptSizeView)
        self.pageView.addWidget(self.hpSetupView)
        self.pageView.addWidget(self.trainingInProgressView)

        self.freshModelView.makeModelFromScratch.connect(self.setupHyperparameters)
        self.freshModelView.baseModelOnOpenAI.connect(lambda: self.pageView.slideInWgt(self.gptSizeView))

        self.gptSizeView.goBack.connect(lambda: self.pageView.slideInWgt(self.freshModelView))
        self.gptSizeView.modelSizeChosen.connect(self.setupHyperparameters)
        self.hpSetupView.proceed.connect(self.startTraining)

        self.ly = QVBoxLayout(self)
        self.ly.addWidget(self.pageView)

        # self.setupHyperparameters()
        

    def setupHyperparameters(self, gptSize=None):
        self.gptSize = gptSize
        self.pageView.slideInWgt(self.hpSetupView)
        
    def startTraining(self):
        self.pageView.slideInWgt(self.trainingInProgressView)

        # TODO: make this a smooth signal/slot thingy
        hp = self.hpSetupView.getHyperparameters()
        hp['gpt2'] = self.gptSize
        self.trainingInProgressView.setHyperparameters(hp)
        self.trainingStarted.emit(hp)


class TrainingModal(QDialog):
    def __init__(self, parent=None, repoName=None):
        super().__init__(parent)
        self.trainingView = TrainingView(self)
        self.trainingView.trainingStarted.connect(self.doTraining)
        self.trainingView.trainingInProgressView.doneButton.clicked.connect(self.accept)
        
        self.ly = QVBoxLayout(self)
        self.ly.setContentsMargins(0,0,0,0)
        self.ly.addWidget(self.trainingView)

        self.__repoName = repoName

    def doTraining(self, hp: dict):
        print(f'train with hps={hp}')
        self.trainThread = ATGTrainer(self, self.__repoName)
        self.trainingView.trainingInProgressView.trainingInfo.setTrainer(self.trainThread)
        
        self.trainThread.setTitle(hp['title'])
        self.trainThread.setGptSize(hp['gpt2'])
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