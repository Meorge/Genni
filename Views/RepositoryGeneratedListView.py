from datetime import datetime, timedelta
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QHeaderView, QSplitter, QTreeWidget, QTreeWidgetItem, QWidget

from ModelRepo import getDatasetsInRepository, getGeneratedTextsInRepository
from Views.RepositoryGeneratedDetailView import RepositoryGeneratedDetailView

class RepositoryGeneratedListView(QSplitter):
    repositoryLoaded = pyqtSignal(str)

    __currentRepo = None
    def __init__(self, parent=None):
        super().__init__(parent)

        self.list = QTreeWidget(self, currentItemChanged=self.onCurrentItemChanged)

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
                genDate.strftime('%d %B %Y at %I:%M %p'),
                str(n),
                str(minLength),
                str(maxLength),
                str(temperature)
                ]
                )
            item.setData(0, Qt.ItemDataRole.UserRole, i)

    def onCurrentItemChanged(self, current: QTreeWidgetItem, prev: QTreeWidgetItem):
        if current is None: return
        self.descStuff.setData(current.data(0, Qt.ItemDataRole.UserRole))
