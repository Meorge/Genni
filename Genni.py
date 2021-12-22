from traceback import format_exception
from PyQt6.QtCore import QCoreApplication, QSettings, Qt
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import QMainWindow, QApplication, QMenuBar, QSizePolicy, QSplitter, QStackedWidget, QSystemTrayIcon, QTabBar, QToolBar, QVBoxLayout, QWidget
import sys

from Core.ModelRepo import getRepoMetadata
from Core.GenniCore import GenniCore
from Views.CleanSession.CleanSessionConfigView import CleanSessionModal
from Views.ExportSession.ExportSessionConfigView import ExportSessionModal
from Views.Generation.GeneratingView import GeneratingModal
from Views.ImportDatasetView import ImportDatasetModal
from Views.Preferences.PreferencesView import PreferencesView
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

        self.trainAction = QAction(QIcon('./Icons/Train.svg'), 'Train...', self, triggered=self.openTrainingModal, enabled=False)
        self.genAction = QAction(QIcon('./Icons/Generate.svg'), 'Generate...', self, triggered=self.openGenModal, enabled=False)
        self.addDatasetAction = QAction(QIcon('./Icons/Add Dataset.svg'), 'Add Dataset', self, triggered=self.openAddDatasetModal, enabled=False)

        self.exportSessionAction = QAction(QIcon('Icons/Export.svg'), 'Export...', parent=self, triggered=self.openExportSessionModal, enabled=False)
        self.cleanSessionAction = QAction(QIcon('Icons/Trash.svg'), 'Clean...', self, triggered=self.openCleanSessionModal, enabled=True)
        self.cleanSessionAction.setVisible(False) # don't need this right now

        self.tb.addAction(self.trainAction)
        self.tb.addAction(self.genAction)
        self.tb.addAction(self.addDatasetAction)

        a = QWidget()
        a.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Fixed)
        self.tb.addWidget(a)
        self.tb.addAction(self.exportSessionAction)
        self.tb.addAction(self.cleanSessionAction)

        self.modelHistoryView = RepositoryModelHistoryView(self)
        self.datasetsView = RepositoryDatasetListView(self)
        self.genTextsView = RepositoryGeneratedListView(self)
        
        self.tabBar = QTabBar(self)
        self.tabBar.currentChanged.connect(self.onTabChanged)
        self.genTextsView.currentSessionChanged.connect(lambda: self.onTabChanged(self.tabBar.currentIndex()))
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

        self.prefsWindow = PreferencesView()
        self.prefsWindow.prefsModified.connect(self.refreshContent)

        self.setupMenuBar()

        
    def setupMenuBar(self):
        menuBar = self.menuBar()
        self.prefsAction = menuBar.addMenu("config").addAction("config")
        self.prefsAction.triggered.connect(self.prefsWindow.show)

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


    def onTabChanged(self, index: int):
        # Check if the user currently has a generation session selected
        genSessionIsSelected = True or (index == 2 and self.genTextsView.currentSession() is not None)
        self.exportSessionAction.setEnabled(genSessionIsSelected)
        self.cleanSessionAction.setEnabled(genSessionIsSelected)


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

    def openExportSessionModal(self):
        session = self.genTextsView.currentSession()
        print(f'User wants to export the session {session}')
        self.exportModal = ExportSessionModal(self.repositoryName(), session, self)
        self.exportModal.exec()
        # TODO: session export modal (set format of export, preview output?)

    def openCleanSessionModal(self):
        session = self.genTextsView.currentSession()
        print(f'User wants to clean the session {session}')
        self.cleanModal = CleanSessionModal(self)
        self.cleanModal.exec()
        # TODO: session clean modal (preview texts to be deleted?)

    def refreshContent(self):
        try:
            self.modelHistoryView.refreshContent()
            self.datasetsView.refreshContent()
            self.genTextsView.refreshContent()
        except AttributeError as e:
            tracebackString = ''.join(format_exception(etype=type(e), value=e, tb=e.__traceback__))
            print(f'Error trying to refresh content:\n{tracebackString}')

    __repositoryName: str = None
    def repositoryName(self) -> str: return self.__repositoryName
    def setRepositoryName(self, repositoryName: str): self.__repositoryName = repositoryName

if __name__ == "__main__":
    app = GenniCore([])
    window = RepositoryWindow()
    window.show()
    sys.exit(app.exec())
