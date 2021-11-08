from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import QMainWindow, QApplication, QToolBar
import sys
from ATGGenerator import ATGGenerator

from ModelRepo import getRepoMetadata
from Views.Generation.GeneratingView import GeneratingModal
from Views.ImportDatasetView import ImportDatasetModal
from Views.RepositoryModelHistoryView import RepositoryModelHistoryView
from Views.Training.TrainingView import TrainingModal

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
        self.genAction = QAction(QIcon('./Icons/Generate.svg'), 'Generate', self, triggered=self.openGenModal)

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

    def openGenModal(self):
        self.genModal = GeneratingModal(self)
        self.genModal.exec()
        self.w.refreshContent()

    def openAddDatasetModal(self):
        self.addDatasetModal = ImportDatasetModal(self)
        self.addDatasetModal.exec()
        self.w.refreshContent()


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    sys.exit(app.exec())