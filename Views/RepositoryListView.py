from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QTreeWidget, QTreeWidgetItem

from ModelRepo import getAllRepos

class RepositoryListView(QTreeWidget):
    currentRepositoryChanged = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setHeaderHidden(True)
        self.setRootIsDecorated(False)
        self.itemDoubleClicked.connect(self.onItemDoubleClicked)
        self.populateList()

    def populateList(self):
        self.clear()

        # put all the items here
        for repo in getAllRepos():
            newItem = QTreeWidgetItem(self, [repo.get('title', 'Untitled Repository')])
            newItem.setIcon(0, QIcon('./Icons/Robot.svg'))
            newItem.setData(0, Qt.ItemDataRole.UserRole, repo)


    def onItemDoubleClicked(self, current: QTreeWidgetItem, column: int):
        if current == None: return

        repoData = current.data(0, Qt.ItemDataRole.UserRole)
        if repoData is None or not isinstance(repoData, dict): return
        repoPath = repoData.get('path')
        self.currentRepositoryChanged.emit(repoPath)
