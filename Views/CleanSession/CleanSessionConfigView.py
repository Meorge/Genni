from PyQt6.QtWidgets import QDialog, QFormLayout, QHBoxLayout, QLabel, QPushButton, QSizePolicy, QTreeWidget, QVBoxLayout, QWidget
from PyQtPlus.QtOnboarding import QWizardTitle, QSwipingPage

class CleanSessionConfigView(QWidget):
    def __init__(self, repoName, sampleName, parent=None):
        super().__init__(parent)
        self.title = QWizardTitle(self)
        self.title.setTitle('Clean Session')
        self.title.setSubtitle('The following samples will be permanently removed.')
        self.title.setIcon('Icons/Trash.svg')

        self.list = QTreeWidget(self)
        self.list.setAlternatingRowColors(True)
        self.list.setHeaderHidden(True)

        # get all of the samples marked as hidden to delete


        self.cancelButton = QPushButton('Cancel', self)
        self.confirmButton = QPushButton('Delete', self)
        self.buttonsLy = QHBoxLayout()
        self.buttonsLy.addWidget(self.cancelButton)
        self.buttonsLy.addWidget(self.confirmButton)

        self.ly = QFormLayout(self)
        self.ly.addRow(self.title)
        self.ly.addRow(self.list)
        self.ly.addRow(self.buttonsLy)


class CleanSessionModal(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.configView = CleanSessionConfigView(self)

        self.slideView = QSwipingPage(self)
        self.slideView.addWidget(self.configView)

        self.ly = QVBoxLayout(self)
        self.ly.addWidget(self.slideView)
        self.ly.setContentsMargins(0,0,0,0)