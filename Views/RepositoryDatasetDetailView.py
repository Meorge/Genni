from datetime import datetime
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel, QSizePolicy, QTextEdit, QVBoxLayout, QWidget

from ModelRepo import getDatasetText

class RepositoryDatasetDetailView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Title label
        self.titleLabel = QLabel('Name of Dataset', parent=self)
        self.titleFont = self.titleLabel.font()
        self.titleFont.setBold(True)
        self.titleFont.setPointSizeF(self.titleFont.pointSizeF() * 1.5)
        self.titleLabel.setFont(self.titleFont)
        
        # Training date
        self.dateLabel = QLabel('Imported 8 November 2021 at 9:41 AM')

        self.titleLabel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.dateLabel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)


        # show text of dataset
        self.datasetText = QTextEdit(self, readOnly=True)

        self.ly = QVBoxLayout(self)
        self.ly.addWidget(self.titleLabel, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeading)
        self.ly.addWidget(self.dateLabel, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeading)
        # self.ly.addStretch()
        self.ly.addWidget(self.datasetText)

    def setData(self, currentRepo: str, data: dict):
        print(data)
        self.titleLabel.setText(data.get('meta', {}).get('title', 'Untitled Dataset'))
        self.dateLabel.setText(datetime.fromisoformat(data.get('meta', {}).get('imported', '1970-01-01T00:00:00')).strftime('Imported %d %B %Y at %I:%M %p'))

        # Load the dataset text
        text = getDatasetText(currentRepo, data.get('pathName'))
        if text is None: self.datasetText.setText('DATASET NOT FOUND')
        else: self.datasetText.setText(text)