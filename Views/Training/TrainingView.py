from logging import error
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QCloseEvent
from PyQt6.QtWidgets import QDialog, QMessageBox, QPushButton, QVBoxLayout, QWidget
from Threads.ATGTrainer import ATGTrainer
from Views.Training.TrainingFreshModelView import SelectHuggingFaceRepoView, TrainingFreshModelGPT2SizeView, TrainingFreshModelView
from Views.Training.TrainingHyperparameterSetupView import TrainingHyperparameterSetupView
from Views.Training.TrainingInProgressView import TrainingInProgressView
from Views.SwipingPageView import SwipingPageView

from traceback import format_exception

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
        self.freshModelView.baseModelOnHuggingFace.connect(self.showHuggingFacePage)

        self.gptSizeView.goBack.connect(self.showIntroPage)
        self.gptSizeView.modelSizeChosen.connect(self.setupHyperparameters)

        self.huggingFaceRepoView.goBack.connect(self.showIntroPage)
        self.huggingFaceRepoView.huggingFaceRepoChosen.connect(self.setupHyperparameters)

        self.hpSetupView.goBack.connect(self.showIntroPage)
        self.hpSetupView.proceed.connect(self.startTraining)

        self.ly = QVBoxLayout(self)
        self.ly.addWidget(self.pageView)
        
    def showIntroPage(self):
        self.pageView.slideInWgt(self.freshModelView)

    def showHuggingFacePage(self):
        self.huggingFaceRepoView.initPage()
        self.pageView.slideInWgt(self.huggingFaceRepoView)

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

    def onStopTriggered(self):
        self.trainingInProgressView.onStopTriggered()


class TrainingModal(QDialog):
    def __init__(self, parent=None, repoName=None):
        super().__init__(parent)
        print(f'going to train for {repoName}')
        self.trainingView = TrainingView(self, repoName=repoName)
        self.trainingView.trainingStarted.connect(self.doTraining)
        self.trainingView.trainingInProgressView.doneButton.clicked.connect(self.accept)
        
        self.ly = QVBoxLayout(self)
        self.ly.setContentsMargins(0,0,0,0)
        self.ly.addWidget(self.trainingView)

        self.__repoName = repoName

        self.trainThread = None

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
        self.trainThread.errorOccurred.connect(self.onErrorOccurred)
        self.trainThread.stopTriggered.connect(self.onStopTriggered)
        self.trainThread.start()

    def closeEvent(self, event: QCloseEvent) -> None:
        if self.trainThread is not None and self.trainThread.isRunning():
            event.ignore()
            confirmCloseBox = QMessageBox(self)
            confirmCloseBox.setText('Training has not yet finished.')
            confirmCloseBox.setInformativeText('Are you sure you want to abort this training session?')
            confirmCloseBox.setIcon(QMessageBox.Icon.Warning)

            confirmCloseBox.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            confirmCloseBox.setDefaultButton(QMessageBox.StandardButton.No)

            result = confirmCloseBox.exec()

            if result == QMessageBox.StandardButton.Yes:
                self.trainThread.triggerStop()
            elif result == QMessageBox.StandardButton.No:
                pass


    def onErrorOccurred(self, e: Exception):
        tracebackString = ''.join(format_exception(etype=type(e), value=e, tb=e.__traceback__))

        errorOccurredBox = QMessageBox(self)
        errorOccurredBox.setText('An error occurred while training.')
        errorOccurredBox.setDetailedText(tracebackString)

        errorOccurredBox.setStandardButtons(QMessageBox.StandardButton.Ok)
        errorOccurredBox.setDefaultButton(QMessageBox.StandardButton.Ok)
        errorOccurredBox.setIcon(QMessageBox.Icon.Critical)

        errorOccurredBox.exec()
        self.close()

    def onStopTriggered(self):
        print('Stop was triggered')
        self.trainingView.onStopTriggered()
        # self.setWindowFlag(Qt.WindowType.WindowCloseButtonHint, False)