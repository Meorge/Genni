from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import QListWidget, QMainWindow, QApplication, QSplitter, QStackedWidget, QTabBar, QTabWidget, QToolBar, QTreeWidget, QVBoxLayout, QWidget
import sys
from ATGGenerator import ATGGenerator

from ModelRepo import getRepoMetadata
from Views.Generation.GeneratingView import GeneratingModal
from Views.ImportDatasetView import ImportDatasetModal
from Views.RepositoryDatasetListView import RepositoryDatasetListView
from Views.RepositoryGeneratedListView import RepositoryGeneratedListView
from Views.RepositoryListView import RepositoryListView
from Views.RepositoryModelHistoryView import RepositoryModelHistoryView
from Views.Training.TrainingView import TrainingModal

class RepositoryWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)

        # Set up toolbar
        self.tb = QToolBar(self)
        self.tb.setFloatable(False)
        self.tb.setMovable(False)
        self.tb.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.addToolBar(self.tb)
        self.setUnifiedTitleAndToolBarOnMac(True)

        self.trainAction = QAction(QIcon('./Icons/Train.svg'), 'Train', self, triggered=self.openTrainingModal, enabled=False)
        self.genAction = QAction(QIcon('./Icons/Generate.svg'), 'Generate', self, triggered=self.openGenModal, enabled=False)

        self.addDatasetAction = QAction(QIcon('./Icons/Add Dataset.svg'), 'Add Dataset', self, triggered=self.openAddDatasetModal, enabled=False)
        
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

        self.repoListWidget = RepositoryListView(self)
        self.repoListWidget.currentRepositoryChanged.connect(self.loadRepository)
        self.sidebarSplitter = QSplitter(self)
        self.sidebarSplitter.addWidget(self.repoListWidget)
        self.sidebarSplitter.addWidget(self.w)

        self.setCentralWidget(self.sidebarSplitter)

    def loadRepository(self, repoName: str):
        self.setRepositoryName(repoName)
        repoData: dict = getRepoMetadata(repoName)
        self.setWindowTitle(repoData.get('title', 'Untitled Repository'))

        self.trainAction.setEnabled(True)
        self.genAction.setEnabled(repoData.get('latest') is not None)
        self.addDatasetAction.setEnabled(True)

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
    window = RepositoryWindow()
    window.show()
    sys.exit(app.exec())
