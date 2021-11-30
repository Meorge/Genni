from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColorConstants, QFont, QPaintEvent, QPainter, QPixmap
from PyQt6.QtWidgets import QSizePolicy, QVBoxLayout, QWidget, QLabel

class WizardTitleView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.icon = QLabel(self)
        self.icon.setFixedHeight(70)

        self.title = QLabel(self)
        self.titleFont = QFont()
        self.titleFont.setBold(True)
        self.titleFont.setPointSizeF(self.titleFont.pointSizeF() * 2.0)
        self.title.setFont(self.titleFont)
        self.title.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)

        self.subtitle = QLabel(self)
        self.subtitle.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)

        self.ly = QVBoxLayout(self)
        self.ly.addWidget(self.icon, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.ly.addWidget(self.title, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.ly.addWidget(self.subtitle, alignment=Qt.AlignmentFlag.AlignHCenter)

        self.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Fixed)
        self.setLayout(self.ly)

        self.setIcon(None)
        
    def setTitle(self, value: str): self.title.setText(value)
    def setSubtitle(self, value: str): self.subtitle.setText(value)

    def setIcon(self, iconPath: str):
        if iconPath == '' or iconPath is None:
            # self.icon.setFixedHeight(0)
            self.icon.clear()
            self.icon.setVisible(False)
        else:
            self.icon.setPixmap(QPixmap(iconPath).scaledToHeight(self.icon.height(), Qt.TransformationMode.SmoothTransformation))
            self.icon.setVisible(True)

