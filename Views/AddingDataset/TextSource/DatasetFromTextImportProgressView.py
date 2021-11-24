from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QVBoxLayout, QWidget
from Views.WizardTitleView import WizardTitleView

class DatasetFromTextImportProgressView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.title = WizardTitleView(self)
        self.title.setTitle('Adding Dataset...')
        self.title.setSubtitle('This shouldn\'t take very long.')

        self.ly = QVBoxLayout(self)
        self.ly.addWidget(self.title, alignment=Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)