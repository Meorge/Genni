from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtWidgets import QLabel, QSizePolicy, QVBoxLayout, QWidget

from Views.TrainingInProgressView import TrainingInProgressView

class TrainingView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.trainingLabel = QLabel("Training...")
        self.trainingLabelFont = QFont()
        self.trainingLabelFont.setBold(True)
        self.trainingLabelFont.setPointSizeF(self.trainingLabelFont.pointSizeF() * 2.0)
        self.trainingLabel.setFont(self.trainingLabelFont)
        self.trainingLabel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)

        self.trainingSourceLabel = QLabel("Finetuning on the dataset \"training_data.txt\".")
        self.trainingSourceLabel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)

        self.trainingInProgressView = TrainingInProgressView(self)

        self.ly = QVBoxLayout(self)
        self.ly.addWidget(self.trainingLabel, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.ly.addWidget(self.trainingSourceLabel, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.ly.addWidget(self.trainingInProgressView)

