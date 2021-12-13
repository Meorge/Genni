from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QHBoxLayout, QLineEdit, QPushButton, QVBoxLayout, QWidget
from PyQtPlus.QtOnboarding import QWizardTitle

class DatasetFromTwitterConfigView(QWidget):
    back = pyqtSignal()
    proceed = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.title = QWizardTitle(self)
        self.title.setTitle('Add Dataset from Twitter')
        self.title.setSubtitle('Enter a search query.')
        self.title.setIcon('Icons/Twitter.svg')

        self.searchQueryBox = QLineEdit()

        self.backButton = QPushButton('Back', clicked=self.back)
        self.nextButton = QPushButton('Download', clicked=self.proceed)

        self.ly = QVBoxLayout(self)
        self.ly.addWidget(self.title, alignment=Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        self.ly.addWidget(self.searchQueryBox)
        self.ly.addStretch()

        self.bLy = QHBoxLayout()
        self.bLy.addWidget(self.backButton)
        self.bLy.addWidget(self.nextButton)
        self.ly.addLayout(self.bLy)

    def searchQuery(self) -> str: return self.searchQueryBox.text()