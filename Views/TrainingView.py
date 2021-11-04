from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QVBoxLayout, QWidget
from Views.TrainingHyperparameterSetupView import TrainingHyperparameterSetupView
from Views.TrainingInProgressView import TrainingInProgressView
from Views.SwipingPageView import SwipingPageView
from Views.WizardTitleView import WizardTitleView

class TrainingView(QWidget):
    trainingStarted = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.title = WizardTitleView(self)

        self.hpSetupView = TrainingHyperparameterSetupView(self)
        
        self.trainingInProgressView = TrainingInProgressView(self)

        self.pageView = SwipingPageView(self)
        self.pageView.addWidget(self.hpSetupView)
        self.pageView.addWidget(self.trainingInProgressView)

        self.hpSetupView.goButton.clicked.connect(self.startTraining)

        self.ly = QVBoxLayout(self)
        self.ly.addWidget(self.title, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.ly.addWidget(self.pageView)

        self.setupHyperparameters()

    def setupHyperparameters(self):
        self.title.setTitle('Configure Training')
        self.title.setSubtitle('Configure the training session.')
        self.pageView.slideInIdx(0)
        
    def startTraining(self):
        self.title.setTitle('Training...')
        self.title.setSubtitle(f'''Finetuning on \"{self.hpSetupView.getHyperparameters()['dataset']['meta']['title']}\".''')
        self.pageView.slideInIdx(1)
        self.trainingStarted.emit(self.hpSetupView.getHyperparameters())

