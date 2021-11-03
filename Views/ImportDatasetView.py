from PyQt5.QtCore import QMargins, QMarginsF, QRectF, Qt, pyqtSignal
from PyQt5.QtGui import QColor, QColorConstants, QFont, QPaintEvent, QPainter, QPen, QPixmap
from PyQt5.QtWidgets import QAbstractButton, QDialog, QGridLayout, QLabel, QPushButton, QSizePolicy, QVBoxLayout, QWidget
from PyQt5.QtSvg import QSvgRenderer
from Views.SwipingPageView import SwipingPageView
from Views.WizardTitleView import WizardTitleView

COLOR_BLUE_FILL = QColor(15, 150, 255)

class ImportDatasetView(QWidget):
    trainingStarted = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.title = WizardTitleView(self)
        self.pageView = SwipingPageView(self)

        self.textFileOptionButton = DatasetSourceOption(title='Text file', desc='Train on a text file from your computer.', svg='Icons/New File.svg', parent=self)
        self.twitterAcctOptionButton = DatasetSourceOption(title='Twitter account', desc='Train on Tweets from a specific Twitter account.', svg='Icons/Twitter.svg', parent=self)

        self.nextButton = QPushButton('Next')

        self.textFileOptionButton.setChecked(True)

        self.ly = QVBoxLayout(self)
        self.ly.addWidget(self.title, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.ly.addWidget(self.textFileOptionButton)
        self.ly.addWidget(self.twitterAcctOptionButton)
        self.ly.addWidget(self.nextButton)
        # self.ly.addWidget(self.pageView)

        self.goToFirstPage()

    def goToFirstPage(self):
        self.title.setTitle('Add Dataset')
        self.title.setSubtitle('Choose a source for the new dataset.')

class DatasetSourceOption(QAbstractButton):
    def __init__(self, title='Title', desc='This is a description', svg=None, parent=None):
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

        # self.__iconLabel = QLabel(self)
        # self.__iconLabel.setFixedWidth(self.__iconLabel.height())
        # self.__iconLabel.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        self.ly = QVBoxLayout(self)
        # self.ly.addWidget(self.__iconLabel, 0, 0, 2, 1, alignment=Qt.AlignmentFlag.AlignCenter)
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

        if self.isChecked():
            blueBgColor = QColor(COLOR_BLUE_FILL)
            blueBgColor.setAlphaF(0.25)
            p.setBrush(blueBgColor)

            blueBorderColor = QColor(COLOR_BLUE_FILL)
            blueBorderColor.setAlphaF(0.75)
            p.setPen(QPen(blueBorderColor, 0.8))
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


class ImportDatasetModal(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setModal(True)

        self.w = ImportDatasetView(self)
        self.ly = QVBoxLayout(self)
        self.ly.setContentsMargins(0,0,0,0)
        self.ly.addWidget(self.w)
        self.setLayout(self.ly)
        