from datetime import datetime
from difflib import SequenceMatcher
from typing import List, Union
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QColor, QColorConstants, QIcon
from PyQt6.QtWidgets import QFrame, QGridLayout, QHeaderView, QLabel, QListWidget, QListWidgetItem, QSizePolicy, QSplitter, QTabWidget, QTextEdit, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget
from ModelRepo import getDatasetMetadata
from Preferences import getDateTimeFormatString
from Views.Colors import COLOR_BLUE, COLOR_PURPLE, COLOR_RED, COLOR_YELLOW

from Views.LabeledValueView import LabeledValueView

class RepositoryGeneratedDetailView(QWidget):
    def __init__(self, repoName, parent=None):
        super().__init__(parent)
        self.__repoName = repoName

        # Title label
        self.titleLabel = QLabel('', parent=self)
        self.titleFont = self.titleLabel.font()
        self.titleFont.setBold(True)
        self.titleFont.setPointSizeF(self.titleFont.pointSizeF() * 1.5)
        self.titleLabel.setFont(self.titleFont)

        self.titleLabel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        # Left-hand list of samples
        self.sampleList = QListWidget(self, currentItemChanged=self.onCurrentItemChanged)
        
        # Right-hand detailed sample
        # self.sampleDetail = QTextEdit(self, readOnly=True)
        self.sampleDetail = RepositoryGeneratedDetailVertSplitterView(self.__repoName, parent=self)

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

    def setRepository(self, repoName: str):
        self.__repoName = repoName
        self.sampleDetail.setRepository(repoName)

    def onCurrentItemChanged(self, current: QListWidgetItem, prev: QListWidgetItem):
        self.sampleDetail.setSample({})
        if current is None: return

        currentSelectedSample = current.data(Qt.ItemDataRole.UserRole)

        if isinstance(currentSelectedSample, str):
            self.sampleDetail.setSample({'text': currentSelectedSample})

        elif isinstance(currentSelectedSample, dict):
            self.sampleDetail.setSample(currentSelectedSample)


    def setData(self, data: dict):
        genDate = datetime.fromisoformat(data.get('meta', {}).get('datetime', '1970-01-01T00:00:00'))
        self.titleLabel.setText(genDate.strftime(getDateTimeFormatString()))
        self.setSamples(data.get('texts', []))
        self.hpView.setData(data)
        self.sampleDetail.setPrompt(data.get('meta', {}).get('prompt', ''))


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

                
                if i.get('datasetMatches', None) is not None and len(i.get('datasetMatches', [])) > 0:
                    topMatch = sorted(i.get('datasetMatches', []), key=lambda x: x.get('ratio', 0), reverse=True)[0]
                    ratio = topMatch.get('ratio', 0)

                    if ratio >= 1.0:
                        item.setIcon(QIcon('Icons/Critical.svg'))
                    elif ratio > 0.5:
                        item.setIcon(QIcon('Icons/Warning.svg'))


class RepositoryGeneratedDetailVertSplitterView(QSplitter):
    def __init__(self, repoName, parent=None):
        super().__init__(parent)
        self.__repoName = repoName

        self.setOrientation(Qt.Orientation.Vertical)

        # Create text box on top
        self.rawTextEdit = QTextEdit(self, readOnly=True)

        # Create tree view on bottom
        self.originalityTreeView = QTreeWidget(self)
        cols = ['%', 'Match', 'Dataset']
        self.originalityTreeView.setHeaderLabels(cols)
        self.originalityTreeView.setColumnCount(len(cols))
        self.originalityTreeView.setAlternatingRowColors(True)
        self.originalityTreeView.setRootIsDecorated(False)
        h = self.originalityTreeView.header()
        h.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        h.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        h.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        h.setStretchLastSection(False)
        

        self.addWidget(self.rawTextEdit)
        self.addWidget(self.originalityTreeView)

        self.__sample = {}
        self.__prompt = ''

    def setRepository(self, repoName: str):
        self.__repoName = repoName

    def setPrompt(self, prompt: str):
        self.__prompt = prompt

    def setSample(self, sample: dict):
        self.__sample = sample
        self.rawTextEdit.setText(sample.get('text', ''))

        self.originalityTreeView.clear()
        if sample.get('datasetMatches', None) is None: return
        for match in sorted(sample.get('datasetMatches', []), key=lambda a: a.get('ratio', 0), reverse=True):
            match: dict
            matchItem = QTreeWidgetItem(self.originalityTreeView)

            # Get the matched text
            i = match.get('genTextMatchIndex', 0) + len(self.__prompt)
            l = match.get('size', 0)
            matchText = sample.get('text', '')[i:i+l].strip()

            # Get the name of the dataset
            datasetId = match.get('dataset')
            if datasetId is None:
                datasetName = ''
            else:
                datasetMeta = getDatasetMetadata(self.__repoName, datasetId)
                datasetName = datasetMeta.get('title', '')

            matchItem.setText(0, f'''{match.get('ratio', 0) * 100:.01f}%''')
            matchItem.setText(1, matchText)
            matchItem.setText(2, datasetName)
            


class RepositoryGeneratedDetailHyperparamsView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.minLengthLabel = LabeledValueView('Min Length', '---', COLOR_BLUE)
        self.maxLengthLabel = LabeledValueView('Max Length', '---', COLOR_BLUE)

        self.temperatureLabel = LabeledValueView('Temperature', '---', COLOR_RED)
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
        self.topKLabel.setValue(str(data.get('meta', {}).get('topK', '---')))
        self.topPLabel.setValue(str(data.get('meta', {}).get('topP', '---')))
        self.seedLabel.setValue(str(data.get('meta', {}).get('seed', '---')))
        self.promptBox.setText(data.get('meta', {}).get('prompt', ''))