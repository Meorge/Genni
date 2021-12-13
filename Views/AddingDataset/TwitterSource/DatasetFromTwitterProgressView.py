from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QVBoxLayout, QWidget
from PyQtPlus.QtOnboarding import QWizardTitle

class DatasetFromTwitterProgressView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.title = QWizardTitle(self)
        self.title.setTitle('Downloading Tweets...')
        self.title.setSubtitle('This shouldn\'t take very long.')

        self.ly = QVBoxLayout(self)
        self.ly.addWidget(self.title, alignment=Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)