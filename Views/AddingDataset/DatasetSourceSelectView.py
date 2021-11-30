from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QPushButton, QVBoxLayout, QWidget
from Views.ButtonWithIconAndDetailView import ButtonWithIconAndDetailView
from Views.WizardTitleView import WizardTitleView

class DatasetSourceSelectView(QWidget):
    proceed = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.title = WizardTitleView(self)
        self.title.setTitle('Add Dataset')
        self.title.setSubtitle('Choose a source for the new dataset.')
        self.title.setIcon('Icons/Add Dataset.svg')

        self.textFileOptionButton = ButtonWithIconAndDetailView(title='Text file', desc='Train on a text file from your computer.', svg='Icons/New File.svg', parent=self)
        self.twitterAcctOptionButton = ButtonWithIconAndDetailView(title='Twitter', desc='Train on Tweets scraped from Twitter.', svg='Icons/Twitter.svg', parent=self)
        self.nextButton = QPushButton('Next', clicked=self.selectionMade)

        self.textFileOptionButton.setChecked(True)

        self.ly = QVBoxLayout(self)
        self.ly.addWidget(self.title, alignment=Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        self.ly.addWidget(self.textFileOptionButton)
        self.ly.addWidget(self.twitterAcctOptionButton)
        self.ly.addStretch()
        self.ly.addWidget(self.nextButton)

    def selectionMade(self):
        if self.textFileOptionButton.isChecked():
            self.proceed.emit('text')
        elif self.twitterAcctOptionButton.isChecked():
            self.proceed.emit('twitter')