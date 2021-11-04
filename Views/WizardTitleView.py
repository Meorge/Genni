from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QSizePolicy, QVBoxLayout, QWidget, QLabel

class WizardTitleView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.title = QLabel(self)
        self.titleFont = QFont()
        self.titleFont.setBold(True)
        self.titleFont.setPointSizeF(self.titleFont.pointSizeF() * 2.0)
        self.title.setFont(self.titleFont)
        self.title.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)

        self.subtitle = QLabel(self)
        self.subtitle.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)

        self.ly = QVBoxLayout(self)
        self.ly.addWidget(self.title, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.ly.addWidget(self.subtitle, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.setLayout(self.ly)

    def setTitle(self, value: str): self.title.setText(value)
    def setSubtitle(self, value: str): self.subtitle.setText(value)

