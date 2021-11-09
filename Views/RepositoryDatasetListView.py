from datetime import datetime, timedelta
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QHeaderView, QSplitter, QTreeWidget, QTreeWidgetItem, QWidget

from ModelRepo import getDatasetsInRepository

class RepositoryDatasetListView(QSplitter):
    repositoryLoaded = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.list = QTreeWidget(self)
        self.list.setHeaderLabels(['Title', 'Filename', 'Line-by-line', 'Imported'])
        self.list.setColumnCount(4)
        self.list.setAlternatingRowColors(True)
        self.list.setRootIsDecorated(False)

        h = self.list.header()
        h.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        h.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        h.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        h.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        h.setStretchLastSection(False)

        self.descStuff = QWidget()

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
            print(i)
            metadata = i.get('meta', {})

            title = metadata.get('title', 'Unnamed Dataset')
            lineByLine = metadata.get('lineByLine', False)
            filename = metadata.get('originalFilename', '---')
            importedTime = datetime.fromisoformat(metadata.get('imported', '1970-01-01T00:00:00'))

            item = QTreeWidgetItem(self.list, [
                title, # TODO: let the user name models,
                filename,
                str(lineByLine),
                importedTime.strftime('%d/%m/%y, %I:%I%p')
                ]
                )

            item.setData(0, Qt.ItemDataRole.UserRole, i)