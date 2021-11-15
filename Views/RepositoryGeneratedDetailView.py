from datetime import datetime
from difflib import SequenceMatcher
from typing import List, Union
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QColor, QColorConstants, QIcon
from PyQt6.QtWidgets import QFrame, QGridLayout, QLabel, QListWidget, QListWidgetItem, QSizePolicy, QSplitter, QTabWidget, QTextEdit, QVBoxLayout, QWidget
from Views.Colors import COLOR_BLUE, COLOR_PURPLE, COLOR_RED, COLOR_YELLOW

from Views.LabeledValueView import LabeledValueView

class RepositoryGeneratedDetailView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Title label
        self.titleLabel = QLabel('Generated on 8 November 2021 at 9:41 AM', parent=self)
        self.titleFont = self.titleLabel.font()
        self.titleFont.setBold(True)
        self.titleFont.setPointSizeF(self.titleFont.pointSizeF() * 1.5)
        self.titleLabel.setFont(self.titleFont)

        self.titleLabel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        # Left-hand list of samples
        self.sampleList = QListWidget(self, currentItemChanged=self.onCurrentItemChanged)
        
        # Right-hand detailed sample
        self.sampleDetail = QTextEdit(self, readOnly=True)

        # Splitter
        self.splitter = QSplitter(self)
        self.splitter.addWidget(self.sampleList)
        self.splitter.addWidget(self.sampleDetail)

        # Hyperparams
        self.hpView = RepositoryGeneratedDetailHyperparamsView(self)

        self.tabWidget = QTabWidget(self)
        self.tabWidget.addTab(self.splitter, 'Texts')
        self.tabWidget.addTab(self.hpView, 'Hyperparameters')

        self.ly = QVBoxLayout(self)
        self.ly.addWidget(self.titleLabel, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeading)
        self.ly.addWidget(self.tabWidget)

    def onCurrentItemChanged(self, current: QListWidgetItem, prev: QListWidgetItem):
        self.sampleDetail.setText('')
        if current is None: return

        currentSelectedSample = current.data(Qt.ItemDataRole.UserRole)

        if isinstance(currentSelectedSample, str):
            self.sampleDetail.setText(currentSelectedSample)
        elif isinstance(currentSelectedSample, dict):
            self.sampleDetail.setText(currentSelectedSample.get('text', ''))


    def setData(self, data: dict):
        genDate = datetime.fromisoformat(data.get('meta', {}).get('datetime', '1970-01-01T00:00:00'))
        self.titleLabel.setText(f'''Generated on {genDate.strftime('%d %B %Y at %I:%M %p')}''')
        self.setSamples(data.get('texts', []))
        self.hpView.setData(data)

        # checkForOvertraining('guybot2', data.get('texts', []), data['meta']['prompt'])


    def setSamples(self, samples: List[Union[str, dict]]):
        self.__samples = samples

        self.sampleList.clear()
        for i in self.__samples:
            item = QListWidgetItem(self.sampleList)
            item.setData(Qt.ItemDataRole.UserRole, i)

            # Handle these differently, depending on whether they're just strings
            # or there's extra data associated
            if isinstance(i, str):
                i: str
                item.setText(i.replace('\n', ''))
                

            elif isinstance(i, dict):
                i: dict
                item.setText(i.get('text', '').replace('\n', ''))

                if len(i.get('datasetMatches', [])) > 0:
                    topMatch = sorted(i.get('datasetMatches', []), key=lambda x: x.get('ratio', 0), reverse=True)[0]
                    ratio = topMatch.get('ratio', 0)

                    if ratio >= 1.0:
                        item.setIcon(QIcon('Icons/Critical.svg'))
                    elif ratio > 0.5:
                        item.setIcon(QIcon('Icons/Warning.svg'))


class RepositoryGeneratedDetailHyperparamsView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.minLengthLabel = LabeledValueView('Min Length', '10', COLOR_BLUE)
        self.maxLengthLabel = LabeledValueView('Max Length', '200', COLOR_BLUE)

        self.temperatureLabel = LabeledValueView('Temperature', '0.7', COLOR_RED)
        self.seedLabel = LabeledValueView('Seed', '---', COLOR_YELLOW)

        self.topPLabel = LabeledValueView('Top P', '---', COLOR_PURPLE)
        self.topKLabel = LabeledValueView('Top K', '---', COLOR_PURPLE)

        self.promptLabel = QLabel('Prompt')
        self.promptBox = QTextEdit(self, readOnly=True)
        self.promptBox.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.promptLy = QVBoxLayout()
        self.promptLy.addWidget(self.promptLabel)
        self.promptLy.addWidget(self.promptBox)

        self.ly = QGridLayout(self)
        self.row = 1
        self.ly.addLayout(self.promptLy, 0, 0, 1, 2, Qt.AlignmentFlag.AlignTop)
        self.addDivider()
        self.addRow(self.minLengthLabel, self.maxLengthLabel)
        self.addDivider()
        self.addRow(self.topPLabel, self.topKLabel)
        self.addDivider()
        self.addRow(self.temperatureLabel, self.seedLabel)
        self.addDivider()

    def addRow(self, widget1: QWidget, widget2: QWidget):
        self.ly.addWidget(widget1, self.row, 0, Qt.AlignmentFlag.AlignTop)
        self.ly.addWidget(widget2, self.row, 1, Qt.AlignmentFlag.AlignTop)
        self.row += 1

    def addDivider(self):
        line = QFrame(self)
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        self.ly.addWidget(line, self.row, 0, 1, 2)
        self.row += 1

    def setData(self, data: dict):
        self.minLengthLabel.setValue(str(data.get('meta', {}).get('minLength', '---')))
        self.maxLengthLabel.setValue(str(data.get('meta', {}).get('maxLength', '---')))
        self.temperatureLabel.setValue(str(data.get('meta', {}).get('temperature', '---')))
        self.promptBox.setText(data.get('meta', {}).get('prompt', ''))