from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QWidget
from ATGTrainer import ATGTrainer
from Views.Training.TrainingFreshModelView import SelectHuggingFaceRepoView, TrainingFreshModelGPT2SizeView, TrainingFreshModelView
from Views.Training.TrainingHyperparameterSetupView import TrainingHyperparameterSetupView
from Views.Training.TrainingInProgressView import TrainingInProgressView
from Views.SwipingPageView import SwipingPageView

class TrainingView(QWidget):
    trainingStarted = pyqtSignal(dict)

    def __init__(self, parent=None, repoName=None):
        super().__init__(parent)

        self.freshModelView = TrainingFreshModelView(self)
        self.gptSizeView = TrainingFreshModelGPT2SizeView(self)
        self.huggingFaceRepoView = SelectHuggingFaceRepoView(self)
        self.hpSetupView = TrainingHyperparameterSetupView(self, repoName=repoName)
        self.trainingInProgressView = TrainingInProgressView(self)

        self.pageView = SwipingPageView(self)
        self.pageView.addWidget(self.freshModelView)
        self.pageView.addWidget(self.gptSizeView)
        self.pageView.addWidget(self.huggingFaceRepoView)
        self.pageView.addWidget(self.hpSetupView)
        self.pageView.addWidget(self.trainingInProgressView)

        self.freshModelView.makeModelFromScratch.connect(self.setupHyperparameters)
        self.freshModelView.baseModelOnOpenAI.connect(lambda: self.pageView.slideInWgt(self.gptSizeView))
        self.freshModelView.baseModelOnHuggingFace.connect(lambda: self.pageView.slideInWgt(self.huggingFaceRepoView))

        self.gptSizeView.goBack.connect(lambda: self.pageView.slideInWgt(self.freshModelView))
        self.gptSizeView.modelSizeChosen.connect(self.setupHyperparameters)

        self.huggingFaceRepoView.goBack.connect(lambda: self.pageView.slideInWgt(self.freshModelView))
        self.huggingFaceRepoView.huggingFaceRepoChosen.connect(self.setupHyperparameters)

        self.hpSetupView.proceed.connect(self.startTraining)

        self.ly = QVBoxLayout(self)
        self.ly.addWidget(self.pageView)
        

    def setupHyperparameters(self, config=None):
        self.__config = config
        self.pageView.slideInWgt(self.hpSetupView)
        
    def startTraining(self):
        self.pageView.slideInWgt(self.trainingInProgressView)

        # TODO: make this a smooth signal/slot thingy
        hp = self.hpSetupView.getHyperparameters()
        hp['constructorArgs'] = self.__config
        self.trainingInProgressView.setHyperparameters(hp)
        self.trainingStarted.emit(hp)


class TrainingModal(QDialog):
    def __init__(self, parent=None, repoName=None):
        super().__init__(parent)
        self.trainingView = TrainingView(self, repoName=repoName)
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
        
        self.trainThread.setConfig(hp)

        self.trainThread.trainingStarted.connect(self.trainingView.trainingInProgressView.onTrainingStarted)
        self.trainThread.trainingEnded.connect(self.trainingView.trainingInProgressView.onTrainingEnded)
        self.trainThread.batchEnded.connect(self.trainingView.trainingInProgressView.onBatchEnded)
        self.trainThread.sampleTextGenerated.connect(self.trainingView.trainingInProgressView.onSamplesGenerated)
        self.trainThread.timePassed.connect(self.trainingView.trainingInProgressView.trainingInfo.onTimePassed)
        self.trainThread.start()