from PyQt6.QtCore import QEvent, Qt
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QSizePolicy, QVBoxLayout, QWidget

from Views.Colors import lerpColor

class LabeledValueView(QWidget):
    def __init__(self, title: str, value: str, valueColor: dict = None, parent=None):
        super().__init__(parent)

        self.titleLabel = QLabel(title)

        self.valueLabel = QLabel(value)
        self.valueLabelFont = QFont()
        self.valueLabelFont.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 0)
        self.valueLabelFont.setPointSizeF(self.valueLabelFont.pointSizeF() * 2.0)
        self.valueLabelFont.setStyleHint(QFont.StyleHint.Monospace)
        self.valueLabel.setFont(self.valueLabelFont)

        self.ly = QVBoxLayout(self)
        self.ly.addWidget(self.titleLabel)
        self.ly.addWidget(self.valueLabel)
        self.ly.setSpacing(0)
        self.ly.setContentsMargins(0,0,0,0)

        self.__valueColor = valueColor
        if self.__valueColor is not None:
            self.setValueColor(self.__valueColor)
        
        self.valueLabel.setPalette(self.valuePalette)

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)

    def setValue(self, value: str):
        self.valueLabel.setText(value)

    def changeEvent(self, event: QEvent) -> None:
        super().changeEvent(event)
        if event.type() == QEvent.Type.PaletteChange:
            self.setValueColor(self.__valueColor)
        
    def setValueColor(self, color: dict[str, QColor]):
        self.__valueColor = color
        adjustedColor = lerpColor(color['light'], color['dark'], self.palette().text().color().redF())
        self.valuePalette = self.valueLabel.palette()
        self.valuePalette.setColor(self.valueLabel.foregroundRole(), adjustedColor)
        self.valueLabel.setPalette(self.valuePalette)