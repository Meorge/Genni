from PyQt6.QtCore import QPoint, Qt, pyqtSignal
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import QFileDialog, QMenu, QTreeWidget, QTreeWidgetItem

from ModelRepo import addKnownRepo, getKnownRepos

class RepositoryListView(QTreeWidget):
    currentRepositoryChanged = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setHeaderHidden(True)
        self.setRootIsDecorated(False)
        self.itemDoubleClicked.connect(self.onItemDoubleClicked)
        self.populateList()

        # set up actions
        self.refreshAction = QAction('Refresh Repositories', self, triggered=self.populateList)
        self.addRepoAction = QAction(QIcon('./Icons/Add.svg'), 'Add Repository...', self, triggered=self.addRepository)
        self.contextMenu = QMenu(self)
        self.contextMenu.addAction(self.refreshAction)
        self.contextMenu.addAction(self.addRepoAction)

        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.onContextMenuRequested)

    def populateList(self):
        self.clear()
        for repo in getKnownRepos():
            newItem = QTreeWidgetItem(self, [repo.get('title', 'Untitled Repository')])
            newItem.setIcon(0, QIcon('./Icons/Robot.svg'))
            newItem.setData(0, Qt.ItemDataRole.UserRole, repo)

    def addRepository(self):
        folderName = QFileDialog.getExistingDirectory(self, 'Add Repository', '.')
        if folderName == '': return
        
        addKnownRepo(folderName)
        self.populateList()

    def onContextMenuRequested(self, point: QPoint):
        # Check if the point was on an item
        # If so, show its context menu, otherwise show the general menu
        item = self.itemAt(point)

        if item is None:
            # Display menu with "Add Repository" and "Refresh" and stuff
            self.contextMenu.exec(self.mapToGlobal(point))
        else:
            # TODO: Display menu with "Remove Repository"
            pass
            

        


    def onItemDoubleClicked(self, current: QTreeWidgetItem, column: int):
        if current == None: return

        repoData = current.data(0, Qt.ItemDataRole.UserRole)
        if repoData is None or not isinstance(repoData, dict): return

        print(f'repo data selected: {repoData}')
        repoPath = repoData.get('path')
        self.currentRepositoryChanged.emit(repoPath)
