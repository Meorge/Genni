from PyQt6.QtCore import QPoint, Qt, pyqtSignal
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import QFileDialog, QInputDialog, QMenu, QTreeWidget, QTreeWidgetItem

from ModelRepo import addKnownRepo, getKnownRepos, renameRepo

class RepositoryListView(QTreeWidget):
    currentRepositoryChanged = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setHeaderHidden(True)
        self.setRootIsDecorated(False)
        self.itemDoubleClicked.connect(self.onItemDoubleClicked)
        self.populateList()

        # set up actions
        self.refreshAction = QAction('Refresh', self, triggered=self.populateList)
        self.addRepoAction = QAction(QIcon('./Icons/Add.svg'), 'Add...', self, triggered=self.addRepository)
        self.globalContextMenu = QMenu(self)
        self.globalContextMenu.addAction(self.refreshAction)
        self.globalContextMenu.addAction(self.addRepoAction)

        
        # Context menu for a specific repository
        self.renameRepoAction = QAction('Rename...', self, triggered=self.renameRepository)
        self.removeRepoAction = QAction('Remove...', self)
        self.specificRepoContextMenu = QMenu(self)
        self.specificRepoContextMenu.addAction(self.renameRepoAction)
        self.specificRepoContextMenu.addAction(self.removeRepoAction)


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
            self.globalContextMenu.exec(self.mapToGlobal(point))
        else:
            # TODO: Display menu with "Remove Repository"
            self.specificRepoContextMenu.exec(self.mapToGlobal(point))
            
    def renameRepository(self):
        repoMeta = self.currentItem().data(0, Qt.ItemDataRole.UserRole)
        newName, ok = QInputDialog.getText(self,
            'Rename Repository',
            'New name:',
            text=repoMeta.get('title', 'Untitled Repository')
            )

        if ok and newName != '':
            renameRepo(repoMeta['path'], newName)
            self.populateList()

    def onItemDoubleClicked(self, current: QTreeWidgetItem, column: int):
        if current == None: return

        repoData = current.data(0, Qt.ItemDataRole.UserRole)
        if repoData is None or not isinstance(repoData, dict): return

        print(f'repo data selected: {repoData}')
        repoPath = repoData.get('path')
        self.currentRepositoryChanged.emit(repoPath)
