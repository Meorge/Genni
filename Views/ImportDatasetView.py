from PyQt6.QtCore import QMargins, QRectF, Qt, pyqtSignal
from PyQt6.QtGui import QColor, QPaintEvent, QPainter, QPen
from PyQt6.QtWidgets import QAbstractButton, QCheckBox, QDialog, QFormLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QSizePolicy, QTextEdit, QVBoxLayout, QWidget
from PyQt6.QtSvg import QSvgRenderer
from ATGDatasetTokenizer import ATGDatasetTokenizer
from Views.SwipingPageView import SwipingPageView
from Views.FilePicker import FilePicker
from Views.WizardTitleView import WizardTitleView

COLOR_BLUE_FILL = QColor(15, 150, 255)
COLOR_GREY_FILL = QColor(128, 128, 128)

class ImportDatasetView(SwipingPageView):
    finished = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.sourceSelectView = DatasetSourceSelectView(self)
        self.sourceSelectView.proceed.connect(self.goToConfigTextFileView)
        # For text file
        self.configTextFileView = DatasetFromTextConfigView(self)
        self.configTextFileView.back.connect(self.goToSourceSelectView)
        self.configTextFileView.proceed.connect(self.goToImportTextFileView)
        self.configTextFileView.proceed.connect(self.runImportDatasetThread)

        self.importTextFileView = DatasetFromTextImportProressView(self)

        self.importTextDoneView = DatasetFromTextImportDoneView(self)
        self.importTextDoneView.finished.connect(self.finished)


        self.addWidget(self.sourceSelectView)
        self.addWidget(self.configTextFileView)
        self.addWidget(self.importTextFileView)
        self.addWidget(self.importTextDoneView)

    def goToSourceSelectView(self): self.slideInWgt(self.sourceSelectView)
    def goToConfigTextFileView(self): self.slideInWgt(self.configTextFileView)
    def goToImportTextFileView(self): self.slideInWgt(self.importTextFileView)
    def goToImportTextDoneView(self): self.slideInWgt(self.importTextDoneView)

    def runImportDatasetThread(self):
        print('run the dataset importer')
        info = self.configTextFileView.getConfigData()
        
        self.datasetThread = ATGDatasetTokenizer(self)
        self.datasetThread.setTitle(info['title'])
        self.datasetThread.setComment(info['comment'])
        self.datasetThread.setLineByLine(info['lineByLine'])
        self.datasetThread.setDataset(info['filename'])

        self.datasetThread.finished.connect(self.goToImportTextDoneView)
        self.datasetThread.start()

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

class DatasetSourceSelectView(QWidget):
    proceed = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.title = WizardTitleView(self)
        self.title.setTitle('Add Dataset')
        self.title.setSubtitle('Choose a source for the new dataset.')

        self.textFileOptionButton = DatasetSourceOption(title='Text file', desc='Train on a text file from your computer.', svg='Icons/New File.svg', parent=self)
        self.twitterAcctOptionButton = DatasetSourceOption(title='Twitter account', desc='Train on Tweets from a specific Twitter account.', svg='Icons/Twitter.svg', parent=self)
        self.nextButton = QPushButton('Next', clicked=self.proceed)

        self.textFileOptionButton.setChecked(True)
        self.twitterAcctOptionButton.setEnabled(False)

        self.ly = QVBoxLayout(self)
        self.ly.addWidget(self.title, alignment=Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        self.ly.addWidget(self.textFileOptionButton)
        self.ly.addWidget(self.twitterAcctOptionButton)
        self.ly.addWidget(self.nextButton)

class DatasetFromTextConfigView(QWidget):
    back = pyqtSignal()
    proceed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.title = WizardTitleView(self)
        self.title.setTitle('Add Dataset From Text File')
        self.title.setSubtitle('Select the text file and other information, or whatever.')

        self.sourceFilePicker = FilePicker(self)
        self.lineByLineCheckbox = QCheckBox('Treat each line as its own sample', self)

        self.datasetTitleEntry = QLineEdit(self)
        self.datasetDescEntry = QTextEdit(self)

        self.nextButton = QPushButton('Import', clicked=self.proceed)
        self.backButton = QPushButton('Back', clicked=self.back)
        self.buttonsLy = QHBoxLayout()
        self.buttonsLy.addWidget(self.backButton)
        self.buttonsLy.addWidget(self.nextButton)

        self.ly = QFormLayout(self)
        self.ly.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        self.ly.addRow(self.title)
        self.ly.addRow('Dataset file:', self.sourceFilePicker)
        self.ly.addWidget(self.lineByLineCheckbox)
        self.ly.addRow('Title:', self.datasetTitleEntry)
        self.ly.addRow('Description:', self.datasetDescEntry)
        self.ly.addRow(self.buttonsLy)

    def getConfigData(self):
        return {
            'filename': self.sourceFilePicker.filepath(),
            'title': self.datasetTitleEntry.text(),
            'comment': self.datasetDescEntry.toPlainText(),
            'lineByLine': self.lineByLineCheckbox.isChecked()
        }
        
class DatasetFromTextImportProressView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.title = WizardTitleView(self)
        self.title.setTitle('Adding Dataset...')
        self.title.setSubtitle('This shouldn\'t take very long.')

        self.ly = QVBoxLayout(self)
        self.ly.addWidget(self.title, alignment=Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)

class DatasetFromTextImportDoneView(QWidget):
    finished = pyqtSignal()
    def __init__(self, parent=None):
        super().__init__(parent)

        self.title = WizardTitleView(self)
        self.title.setTitle('Dataset Added')
        self.title.setSubtitle('The dataset has been added to this repository and is ready for training.')

        self.closeButton = QPushButton('Close', clicked=self.finished)

        self.ly = QVBoxLayout(self)
        self.ly.addWidget(self.title, alignment=Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        self.ly.addWidget(self.closeButton)


class ImportDatasetModal(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setModal(True)

        self.w = ImportDatasetView(self)
        self.w.finished.connect(self.accept)

        self.ly = QVBoxLayout(self)
        self.ly.setContentsMargins(0,0,0,0)
        self.ly.addWidget(self.w)
        self.setLayout(self.ly)
        