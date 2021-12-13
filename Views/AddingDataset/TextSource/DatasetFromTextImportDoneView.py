from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QPushButton, QVBoxLayout, QWidget
from PyQtPlus.QtOnboarding import QWizardTitle

class DatasetFromTextImportDoneView(QWidget):
    finished = pyqtSignal()
    def __init__(self, parent=None):
        super().__init__(parent)

        self.title = QWizardTitle(self)
        self.title.setTitle('Dataset Added')
        self.title.setSubtitle('The dataset has been added to this repository and is ready for training.')

        self.closeButton = QPushButton('Close', clicked=self.finished)

        self.ly = QVBoxLayout(self)
        self.ly.addWidget(self.title, alignment=Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        self.ly.addWidget(self.closeButton)