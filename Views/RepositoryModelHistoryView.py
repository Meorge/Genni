from datetime import datetime
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QSplitter, QTreeWidget, QTreeWidgetItem, QWidget

from ModelRepo import getModelsInRepository

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
        self.list.setHeaderLabels(['Title', 'Date', 'Dataset', 'Duration', 'Learning Rate', 'Steps'])
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
            formattedTime = datetime.fromisoformat(i.get('datetime', '1970-01-01T00:00:00')).strftime('%d %b %Y at %I:%M %p')
            item = QTreeWidgetItem(self.list, [
                i.get('name', 'Unnamed Model'), # TODO: let the user name models
                formattedTime,
                'Some Dataset', # TODO: put the dataset in the meta json why is that not already there?
                '01:02:03', # TODO: grab the duration from the last time recorded in steps.csv
                str(i.get('learningRate', 0)),
                str(i.get('steps', 0))
                ]
                )
