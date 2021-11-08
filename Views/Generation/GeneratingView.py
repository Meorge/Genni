from typing import List
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QWidget
from ATGGenerator import ATGGenerator
from Views.Generation.GeneratingHyperparameterSetupView import GeneratingCompleteView, GeneratingHyperparameterSetupView, GeneratingInProgressView
from Views.SwipingPageView import SwipingPageView

class GeneratingView(QWidget):
    generationStarted = pyqtSignal(dict)
    accept = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.hpView = GeneratingHyperparameterSetupView(self)
        self.progView = GeneratingInProgressView(self)
        self.compView = GeneratingCompleteView(self)
        self.compView.accept.connect(self.accept)

        self.pageView = SwipingPageView(self)
        self.pageView.addWidget(self.hpView)
        self.pageView.addWidget(self.progView)
        self.pageView.addWidget(self.compView)

        # passes hyperparameters out!
        self.hpView.generationStarted.connect(self.generationStarted)
        self.hpView.generationStarted.connect(self.startGenerating)

        self.ly = QVBoxLayout(self)
        self.ly.addWidget(self.pageView)

    def startGenerating(self):
        self.pageView.slideInWgt(self.progView)

    def onGenerationFinished(self, samples: List[str]):
        self.compView.setSamples(samples)
        self.pageView.slideInWgt(self.compView)

class GeneratingModal(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.trainingView = GeneratingView(self)
        self.trainingView.generationStarted.connect(self.doGeneration)
        self.trainingView.accept.connect(self.accept)
        
        self.ly = QVBoxLayout(self)
        self.ly.setContentsMargins(0,0,0,0)
        self.ly.addWidget(self.trainingView)

    def doGeneration(self, hyperparameters: dict):
        self.genThread = ATGGenerator(self)
        self.genThread.setN(hyperparameters['n'])
        self.genThread.setPrompt(hyperparameters['prompt'])
        self.genThread.setMinLength(hyperparameters['minLength'])
        self.genThread.setMaxLength(hyperparameters['maxLength'])
        self.genThread.setTemperature(hyperparameters['temperature'])
        self.genThread.samplesGenerated.connect(self.trainingView.onGenerationFinished)
        self.genThread.start()