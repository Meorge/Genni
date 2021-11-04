from datetime import datetime, timedelta
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QSplitter, QTreeWidget, QTreeWidgetItem, QWidget

from humanize import naturaltime
from ModelRepo import getDatasetMetadata, getDurationString, getModelsInRepository

class RepositoryModelHistoryView(QSplitter):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.list = QTreeWidget(self)

        """
        List contains fields:
        - title
        - time of training
        - dataset
        - time taken to train
        - learning rate
        - steps
        """
        self.list.setHeaderLabels(['Title', 'Trained', 'Dataset', 'Duration', 'Learning Rate', 'Steps'])
        self.list.setColumnCount(6)
        self.list.setAlternatingRowColors(True)

        self.descStuff = QWidget()

        self.setOrientation(Qt.Orientation.Vertical)
        self.addWidget(self.list)
        self.addWidget(self.descStuff)

        self.populateList()


    def populateList(self):
        self.list.clear()

        for i in getModelsInRepository('./my_model'):
            modelTime = datetime.fromisoformat(i.get('datetime', '1970-01-01T00:00:00'))
            datasetName = getDatasetMetadata('./my_model', i.get('dataset')).get('title', 'Unknown')

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
