from datetime import datetime, timedelta
from PyQt6.QtCore import QMargins, Qt, pyqtSignal
from PyQt6.QtGui import QColor, QColorConstants, QIcon, QPainter, QPen, QPixmap
from PyQt6.QtWidgets import QHeaderView, QSplitter, QTreeWidget, QTreeWidgetItem, QWidget

from humanize import naturaltime
from ModelRepo import getDatasetMetadata, getDurationString, getModelsInRepository, getRepoMetadata

class RepositoryModelHistoryView(QSplitter):
    repositoryLoaded = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.list = QTreeWidget(self)
        self.list.setHeaderLabels(['Title', 'Trained', 'Dataset', 'Duration', 'Learning Rate', 'Steps'])
        self.list.setColumnCount(6)
        self.list.setAlternatingRowColors(True)
        self.list.setRootIsDecorated(False)

        h = self.list.header()
        h.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        h.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        h.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        h.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        h.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        h.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
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

        # get head
        headModel = getRepoMetadata(self.repository()).get('latest')

        for i in getModelsInRepository(self.repository()):
            modelTime = datetime.fromisoformat(i.get('datetime', '1970-01-01T00:00:00'))
            datasetName = getDatasetMetadata(self.repository(), i.get('dataset')).get('title', 'Unknown')

            durationString = ''
            if i.get('duration', None) is not None:
                durationString = getDurationString(timedelta(seconds=i.get('duration')))

            item = QTreeWidgetItem(self.list, [
                i.get('name', 'Unnamed Model'), # TODO: let the user name models
                modelTime.strftime('%d/%m/%y, %I:%I%p'),
                datasetName,
                durationString,
                str(i.get('learningRate', None)),
                str(i.get('steps', None))
                ]
                )

            item.setIcon(0, self.makeIcon(100, 0.1, i.get('filePath') == headModel))

    def makeIcon(self, size: int, padding: float, head: bool = False) -> QIcon:
        pm = QPixmap(size, size)
        pm.fill(QColorConstants.Transparent)
        effectivePadding = size * padding
        
        if not head: return QIcon(pm)

        with QPainter(pm) as p:
            p: QPainter
            p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
            p.setBrush(QColor(60, 150, 240))
            p.setPen(QPen(QColor(50, 50, 200), 5.0))
            p.drawEllipse(pm.rect().marginsRemoved(QMargins(effectivePadding, effectivePadding, effectivePadding, effectivePadding)))
        return QIcon(pm)
