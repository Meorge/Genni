from datetime import datetime, timedelta
from PyQt6.QtCore import QPoint, Qt, pyqtSignal
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QHeaderView, QMenu, QMessageBox, QSplitter, QTreeWidget, QTreeWidgetItem, QWidget

from ModelRepo import deleteTexts, getDatasetsInRepository, getGeneratedTextsInRepository
from Preferences import getDateTimeFormatString
from Views.RepositoryGeneratedDetailView import RepositoryGeneratedDetailView

class RepositoryGeneratedListView(QSplitter):
    repositoryLoaded = pyqtSignal(str)

    __currentRepo = None
    def __init__(self, parent=None):
        super().__init__(parent)

        self.list = QTreeWidget(self, currentItemChanged=self.onCurrentItemChanged)
        self.list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.list.customContextMenuRequested.connect(self.onContextMenuRequested)

        columns = ['Generation Date', '# Samples', 'Min Length', 'Max Length', 'Temperature']
        self.list.setHeaderLabels(columns)
        self.list.setColumnCount(len(columns))
        self.list.setAlternatingRowColors(True)
        self.list.setRootIsDecorated(False)

        h = self.list.header()
        h.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)

        for i in range(1, len(columns)): h.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)
        h.setStretchLastSection(False)

        self.descStuff = RepositoryGeneratedDetailView(self.repository(), parent=self)

        self.setOrientation(Qt.Orientation.Vertical)
        self.addWidget(self.list)
        self.addWidget(self.descStuff)

        # Context menu for a specific repository
        self.deleteTextsAction = QAction('Delete...', self, triggered=self.tryDeleteTexts)
        self.itemContextMenu = QMenu(self)
        self.itemContextMenu.addAction(self.deleteTextsAction)

    def refreshContent(self):
        self.populateList()

    def repository(self) -> str: return self.__currentRepo

    def loadRepository(self, repoName: str):
        self.__currentRepo = repoName
        self.populateList()
        self.repositoryLoaded.emit(repoName)

        self.descStuff.setRepository(repoName)

    def populateList(self):
        self.list.clear()

        for i in getGeneratedTextsInRepository(self.repository()):
            metadata = i.get('meta', {})

            genDate = datetime.fromisoformat(metadata.get('datetime', '1970-01-01T00:00:00'))
            n = metadata.get('n', '---')
            minLength = metadata.get('minLength', '---')
            maxLength = metadata.get('maxLength', '---')
            temperature = metadata.get('temperature', '---')

            item = QTreeWidgetItem(self.list, [
                genDate.strftime(getDateTimeFormatString()),
                str(n),
                str(minLength),
                str(maxLength),
                str(temperature)
                ]
                )
            item.setData(0, Qt.ItemDataRole.UserRole, i)

    def onContextMenuRequested(self, point: QPoint):
        item = self.list.itemAt(point)
        if item is not None:
            self.itemContextMenu.exec(self.list.mapToGlobal(point))

    def tryDeleteTexts(self):
        pathToTexts = self.list.currentItem().data(0, Qt.ItemDataRole.UserRole)['path']

        b = QMessageBox(self)
        b.setText(f'Are you sure you want to delete this set of generated texts?')
        b.setInformativeText('They will be gone forever!')
        b.setIcon(QMessageBox.Icon.Warning)

        b.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        b.setDefaultButton(QMessageBox.StandardButton.No)

        if b.exec() == QMessageBox.StandardButton.Yes:
            deleteTexts(self.__currentRepo, pathToTexts)
            self.refreshContent()

    def onCurrentItemChanged(self, current: QTreeWidgetItem, prev: QTreeWidgetItem):
        if current is None: return
        self.descStuff.setData(current.data(0, Qt.ItemDataRole.UserRole))
