from datetime import datetime, timedelta
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QHeaderView, QSplitter, QTreeWidget, QTreeWidgetItem, QWidget
from Core.GenniCore import GenniCore

from Core.ModelRepo import getDatasetsInRepository
from Views.RepositoryDatasetDetailView import RepositoryDatasetDetailView

class RepositoryDatasetListView(QSplitter):
    repositoryLoaded = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.list = QTreeWidget(self, currentItemChanged=self.onCurrentItemChanged)
        self.list.setHeaderLabels(['Title', 'Line-by-line', 'Imported'])
        self.list.setColumnCount(3)
        self.list.setAlternatingRowColors(True)
        self.list.setRootIsDecorated(False)

        h = self.list.header()
        h.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        h.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        h.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        h.setStretchLastSection(False)

        self.descStuff = RepositoryDatasetDetailView()

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

    def populateList(self):
        self.list.clear()

        for i in getDatasetsInRepository(self.repository()):
            metadata = i.get('meta', {})

            title = metadata.get('title', 'Unnamed Dataset')
            lineByLine = metadata.get('lineByLine', False)
            importedTime = datetime.fromisoformat(metadata.get('imported', '1970-01-01T00:00:00'))

            item = QTreeWidgetItem(self.list, [
                title,
                str(lineByLine),
                importedTime.strftime(GenniCore.instance().getDateTimeFormatString())
                ]
                )

            item.setData(0, Qt.ItemDataRole.UserRole, i)


    def onCurrentItemChanged(self, current: QTreeWidgetItem, prev: QTreeWidgetItem):
        if current is None:
            return

        self.descStuff.setData(self.__currentRepo, current.data(0, Qt.ItemDataRole.UserRole))
