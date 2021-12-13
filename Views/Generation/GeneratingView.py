from typing import List
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QCloseEvent
from PyQt6.QtWidgets import QDialog, QMessageBox, QVBoxLayout, QWidget
from Threads.ATGGenerator import ATGGenerator
from Views.Generation.GeneratingHyperparameterSetupView import GeneratingCompleteView, GeneratingHyperparameterSetupView, GeneratingInProgressView, ProcessingInProgressView
from PyQtPlus.QtOnboarding import QSwipingPage

class GeneratingView(QWidget):
    generationStarted = pyqtSignal(dict)
    accept = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.hpView = GeneratingHyperparameterSetupView(self)
        self.progView = GeneratingInProgressView(self)
        self.processView = ProcessingInProgressView(self)
        self.compView = GeneratingCompleteView(self)
        self.compView.accept.connect(self.accept)

        self.pageView = QSwipingPage(self)
        self.pageView.addWidget(self.hpView)
        self.pageView.addWidget(self.progView)
        self.pageView.addWidget(self.processView)
        self.pageView.addWidget(self.compView)

        # passes hyperparameters out!
        self.hpView.generationStarted.connect(self.startGenerating)

        self.ly = QVBoxLayout(self)
        self.ly.addWidget(self.pageView)

    def startGenerating(self):
        self.pageView.slideInWgt(self.progView)
        self.pageView.animationFinished.connect(self.emitGenerationStarted)

    def emitGenerationStarted(self):
        self.generationStarted.emit(self.hpView.getHyperparameters())
        self.pageView.animationFinished.disconnect(self.emitGenerationStarted)

    def onProcessingStarted(self):
        self.pageView.slideInWgt(self.processView)

    def onGenerationFinished(self, samples: List[str]):
        # Issue: this signal gets emitted before the animation finishes, which means
        # the "complete" slide in animation doesn't get played (there's no queue)
        self.compView.setSamples(samples)
        self.pageView.slideInWgt(self.compView)

class GeneratingModal(QDialog):
    def __init__(self, parent=None, repoName=None):
        super().__init__(parent)
        print(f'going to generate for {repoName}')
        self.trainingView = GeneratingView(self)
        self.trainingView.generationStarted.connect(self.doGeneration)
        self.trainingView.accept.connect(self.accept)
        
        self.ly = QVBoxLayout(self)
        self.ly.setContentsMargins(0,0,0,0)
        self.ly.addWidget(self.trainingView)
        self.__repoName = repoName

        self.genThread = None

    def doGeneration(self, hyperparameters: dict):
        self.genThread = ATGGenerator(self, repoName=self.__repoName)
        self.genThread.processingStarted.connect(self.trainingView.onProcessingStarted)
        self.genThread.processingFinished.connect(self.trainingView.onGenerationFinished)
        self.genThread.setN(hyperparameters['n'])
        self.genThread.setPrompt(hyperparameters['prompt'])
        self.genThread.setMinLength(hyperparameters['minLength'])
        self.genThread.setMaxLength(hyperparameters['maxLength'])
        self.genThread.setTemperature(hyperparameters['temperature'])
        self.genThread.setTopK(hyperparameters['topK'])
        self.genThread.setTopP(hyperparameters['topP'])
        self.genThread.setSeed(hyperparameters['seed'])
        self.genThread.setCheckAgainstDatasets(hyperparameters['checkAgainstDatasets'])
        self.genThread.start()

    def closeEvent(self, event: QCloseEvent) -> None:
        if self.genThread is not None and self.genThread.isRunning():
            confirmCloseBox = QMessageBox(self)
            confirmCloseBox.setText('Generation has not yet finished.')
            confirmCloseBox.setInformativeText('Are you sure you want to abort this generation session?')
            confirmCloseBox.setIcon(QMessageBox.Icon.Warning)

            confirmCloseBox.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            confirmCloseBox.setDefaultButton(QMessageBox.StandardButton.No)

            result = confirmCloseBox.exec()

            if result == QMessageBox.StandardButton.Yes:
                self.genThread.terminate() # docs say it's unsafe but I'm not sure how else to kill aitextgen
                event.accept()
            elif result == QMessageBox.StandardButton.No:
                event.ignore()