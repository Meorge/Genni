from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import QMainWindow, QApplication, QStackedWidget, QTabBar, QTabWidget, QToolBar, QVBoxLayout, QWidget
import sys
from ATGGenerator import ATGGenerator

from ModelRepo import getRepoMetadata
from Views.Generation.GeneratingView import GeneratingModal
from Views.ImportDatasetView import ImportDatasetModal
from Views.RepositoryDatasetListView import RepositoryDatasetListView
from Views.RepositoryGeneratedListView import RepositoryGeneratedListView
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

        self.modelHistoryView = RepositoryModelHistoryView(self)
        self.datasetsView = RepositoryDatasetListView(self)
        self.genTextsView = RepositoryGeneratedListView(self)
        
        self.tabBar = QTabBar(self)
        self.tabBar.setDrawBase(False)
        self.tabBar.addTab('Models')
        self.tabBar.addTab('Datasets')
        self.tabBar.addTab('Generated Texts')

        self.tabBarLy = QVBoxLayout()
        self.tabBarLy.addWidget(self.tabBar)
        self.tabBarLy.setContentsMargins(6, 6, 6, 0)

        self.stack = QStackedWidget(self)
        self.stack.addWidget(self.modelHistoryView)
        self.stack.addWidget(self.datasetsView)
        self.stack.addWidget(self.genTextsView)

        self.tabBar.currentChanged.connect(self.stack.setCurrentIndex)

        self.w = QWidget(self)
        self.ly = QVBoxLayout(self.w)
        self.ly.addLayout(self.tabBarLy)
        self.ly.addWidget(self.stack)
        self.ly.setContentsMargins(0,0,0,0)

        self.setCentralWidget(self.w)

        self.loadRepository('./my_model')

    def loadRepository(self, repoName: str):
        self.setRepositoryName(repoName)
        repoData: dict = getRepoMetadata(repoName)
        self.setWindowTitle(repoData.get('title', 'Untitled Repository'))
        self.modelHistoryView.loadRepository(repoName)
        self.datasetsView.loadRepository(repoName)
        self.genTextsView.loadRepository(repoName)

    def openTrainingModal(self):
        self.trainingModal = TrainingModal(self, self.repositoryName())
        self.trainingModal.exec()
        self.refreshContent()

    def openGenModal(self):
        self.genModal = GeneratingModal(self, self.repositoryName())
        self.genModal.exec()
        self.refreshContent()

    def openAddDatasetModal(self):
        self.addDatasetModal = ImportDatasetModal(self, self.repositoryName())
        self.addDatasetModal.exec()
        self.refreshContent()

    def refreshContent(self):
        self.modelHistoryView.refreshContent()
        self.datasetsView.refreshContent()
        self.genTextsView.refreshContent()

    __repositoryName: str = None
    def repositoryName(self) -> str: return self.__repositoryName
    def setRepositoryName(self, repositoryName: str): self.__repositoryName = repositoryName

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    sys.exit(app.exec())