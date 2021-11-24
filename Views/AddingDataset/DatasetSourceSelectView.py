from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QCheckBox, QDialog, QFormLayout, QHBoxLayout, QLineEdit, QPushButton, QTextEdit, QVBoxLayout, QWidget
from Threads.ATGDatasetTokenizer import ATGDatasetTokenizer
from Views.ButtonWithIconAndDetailView import ButtonWithIconAndDetailView
from Views.SwipingPageView import SwipingPageView
from Views.FilePicker import FilePicker
from Views.WizardTitleView import WizardTitleView

class DatasetSourceSelectView(QWidget):
    proceed = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.title = WizardTitleView(self)
        self.title.setTitle('Add Dataset')
        self.title.setSubtitle('Choose a source for the new dataset.')

        self.textFileOptionButton = ButtonWithIconAndDetailView(title='Text file', desc='Train on a text file from your computer.', svg='Icons/New File.svg', parent=self)
        self.twitterAcctOptionButton = ButtonWithIconAndDetailView(title='Twitter account', desc='Train on Tweets from a specific Twitter account.', svg='Icons/Twitter.svg', parent=self)
        self.nextButton = QPushButton('Next', clicked=self.proceed)

        self.textFileOptionButton.setChecked(True)

        self.ly = QVBoxLayout(self)
        self.ly.addWidget(self.title, alignment=Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        self.ly.addWidget(self.textFileOptionButton)
        self.ly.addWidget(self.twitterAcctOptionButton)
        self.ly.addStretch()
        self.ly.addWidget(self.nextButton)