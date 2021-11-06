from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import QDialog, QMainWindow, QApplication, QToolBar, QVBoxLayout
import sys

from ATGTrainer import ATGTrainer
from ATGDatasetTokenizer import ATGDatasetTokenizer
from ModelRepo import getRepoMetadata
from Views.ImportDatasetView import ImportDatasetModal
from Views.RepositoryModelHistoryView import RepositoryModelHistoryView
from Views.TrainingView import TrainingView

class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)

        # Set up toolbar
        self.tb = QToolBar(self)
        self.tb.setFloatable(False)
        self.tb.setMovable(False)
        self.tb.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.addToolBar(self.tb)
        self.setUnifiedTitleAndToolBarOnMac(True)

        self.trainAction = QAction(QIcon('./Icons/Train.svg'), 'Train', self, triggered=self.openTrainingModal)
        self.genAction = QAction(QIcon('./Icons/Generate.svg'), 'Generate', self)
        self.genAction.setEnabled(False)

        self.addDatasetAction = QAction(QIcon('./Icons/Add Dataset.svg'), 'Add Dataset', self, triggered=self.openAddDatasetModal)
        
        self.tb.addAction(self.trainAction)
        self.tb.addAction(self.genAction)
        self.tb.addSeparator()
        self.tb.addAction(self.addDatasetAction)

        self.w = RepositoryModelHistoryView(self)
        self.w.repositoryLoaded.connect(self.onRepositoryLoaded)
        self.w.loadRepository('./my_model')
        self.setCentralWidget(self.w)

    def onRepositoryLoaded(self, repoName: str):
        repoData: dict = getRepoMetadata(repoName)
        self.setWindowTitle(repoData.get('title', 'Untitled Repository'))

    def openTrainingModal(self):
        self.trainingModal = TrainingModal(self)
        self.trainingModal.exec()
        self.w.refreshContent()

    def openAddDatasetModal(self):
        self.addDatasetModal = ImportDatasetModal(self)
        self.addDatasetModal.exec()
        self.w.refreshContent()

class TrainingModal(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.trainingView = TrainingView(self)
        self.trainingView.trainingStarted.connect(self.doTraining)
        
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


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    sys.exit(app.exec())