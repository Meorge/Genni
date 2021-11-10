from PyQt6.QtCore import QMargins, QRectF, Qt
from PyQt6.QtGui import QColor, QPaintEvent, QPainter, QPen
from PyQt6.QtWidgets import QAbstractButton, QLabel, QSizePolicy, QVBoxLayout
from PyQt6.QtSvg import QSvgRenderer

COLOR_BLUE_FILL = QColor(15, 150, 255)
COLOR_GREY_FILL = QColor(128, 128, 128)

class ButtonWithIconAndDetailView(QAbstractButton):
    def __init__(self, title='Title', desc='', svg=None, parent=None):
        super().__init__(parent)
        self.setAutoExclusive(True)
        self.setCheckable(True)

        self.__svg = svg

        self.__titleLabel = QLabel(title)
        titleLabelFont = self.__titleLabel.font()
        titleLabelFont.setBold(True)
        self.__titleLabel.setFont(titleLabelFont)

        self.__descLabel = QLabel(desc)
        self.__descLabel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.ly = QVBoxLayout(self)
        self.ly.addWidget(self.__titleLabel, alignment=Qt.AlignmentFlag.AlignLeft)
        self.ly.addWidget(self.__descLabel, alignment=Qt.AlignmentFlag.AlignLeft)
        self.ly.setSpacing(self.ly.spacing() * 0.5)

        contentsMargins = self.ly.contentsMargins()
        contentsMargins.setLeft(contentsMargins.left() * 4)
        self.ly.setContentsMargins(contentsMargins)

    def titleText(self) -> str: return self.__titleLabel.text()
    def setTitleText(self, value: str): self.__titleLabel.setText(value)

    def descText(self) -> str: return self.__descLabel.text()
    def setDescText(self, value: str): self.__descLabel.setText(value)

    def svg(self) -> str: return self.__svg
    def setSvg(self, value: str): self.__svg = value

    def paintEvent(self, e: QPaintEvent) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        if self.isChecked():
            blueBgColor = QColor(COLOR_BLUE_FILL)
            blueBgColor.setAlphaF(0.25)
            p.setBrush(blueBgColor)

            blueBorderColor = QColor(COLOR_BLUE_FILL)
            blueBorderColor.setAlphaF(0.75)
            p.setPen(QPen(blueBorderColor, 0.8))

        elif self.isEnabled():
            p.setBrush(Qt.BrushStyle.NoBrush)
            greyBorderColor = QColor(COLOR_GREY_FILL)
            p.setPen(QPen(greyBorderColor, 0.6))

        else:
            p.setBrush(Qt.BrushStyle.NoBrush)
            greyBorderColor = QColor(COLOR_GREY_FILL)
            p.setPen(QPen(greyBorderColor, 0.3))

        p.drawRoundedRect(e.rect().marginsRemoved(QMargins(1,1,1,1)), 5, 5, Qt.SizeMode.AbsoluteSize)

        # Draw the icon
        if self.svg() is not None:
            iconRenderer = QSvgRenderer(self.svg(), parent=self)

            iconMargins = 15
            iconRectWidth = self.ly.contentsMargins().left() - iconMargins
            iconRectHeight = iconRectWidth

            iconRectHeightHalf = iconRectHeight / 2

            buttonCenter = self.height() / 2
            iconRect = QRectF(iconMargins / 2, buttonCenter - iconRectHeightHalf, iconRectWidth, iconRectHeight)
            iconRenderer.render(p, iconRect)