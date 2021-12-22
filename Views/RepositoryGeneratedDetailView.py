from datetime import datetime
from difflib import SequenceMatcher
from typing import Iterable, List, Union
from PyQt6.QtCore import QMimeData, QModelIndex, QPoint, QSize, Qt, pyqtSignal
from PyQt6.QtGui import QColor, QColorConstants, QFont, QIcon, QKeySequence
from PyQt6.QtWidgets import QFrame, QGridLayout, QHeaderView, QLabel, QListWidget, QListWidgetItem, QMenu, QSizePolicy, QSplitter, QTabWidget, QTextEdit, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget
from Core.GenniCore import GenniCore
from Core.ModelRepo import deleteGeneratedSampleInRepository, getDatasetMetadata, getGeneratedTextInRepository, markGeneratedSampleInRepository
from Views.Colors import COLOR_BLUE, COLOR_PURPLE, COLOR_RED, COLOR_YELLOW
from Views.LabeledValueView import LabeledValueView

class RepositoryGeneratedDetailView(QWidget):
    def __init__(self, repoName, parent=None):
        super().__init__(parent)
        self.__repoName = repoName
        self.__currentData = {}

        # Title label
        self.titleLabel = QLabel('', parent=self)
        self.titleFont = self.titleLabel.font()
        self.titleFont.setBold(True)
        self.titleFont.setPointSizeF(self.titleFont.pointSizeF() * 1.5)
        self.titleLabel.setFont(self.titleFont)

        self.titleLabel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        # Left-hand list of samples
        self.sampleList = GeneratedTextsList(self.__repoName, parent=self)
        self.sampleList.currentItemChanged.connect(self.onCurrentItemChanged)
        self.sampleList.genTextDataModified.connect(self.refresh)
        
        # Right-hand detailed sample
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
        self.sampleList.setRepository(repoName)
        self.sampleDetail.setRepository(repoName)

    def onCurrentItemChanged(self, current: QTreeWidgetItem, prev: QTreeWidgetItem):
        self.sampleDetail.setSample({})
        if current is None: return

        currentSelectedSample = current.data(0, Qt.ItemDataRole.UserRole)

        if isinstance(currentSelectedSample, str):
            self.sampleDetail.setSample({'text': currentSelectedSample})

        elif isinstance(currentSelectedSample, dict):
            self.sampleDetail.setSample(currentSelectedSample)


    def setCurrentSessionName(self, name: str):
        """
        Instead of being passed all of the data, this should just be passed the path to the text folder.

        """
        self.__sessionName = name
        self.sampleList.setCurrentSessionName(name)
        self.refresh()

    def refresh(self):
        """
        Get the data for the current generated text collection and update the UI.
        """
        sessionContents = getGeneratedTextInRepository(self.__repoName, self.__sessionName)

        sessionDateStr = sessionContents.get('meta', {}).get('datetime', '1970-01-01T00:00:00')
        sessionDate = datetime.fromisoformat(sessionDateStr)
        self.titleLabel.setText(sessionDate.strftime(GenniCore.instance().getDateTimeFormatString()))

        self.setSamples(sessionContents.get('texts', []))
        self.hpView.setData(sessionContents)


    def setSamples(self, samples: List[Union[str, dict]]):
        self.__samples = samples

        row = -1
        index = self.sampleList.currentIndex()
        if index is not None: row = index.row()

        self.sampleList.clear()
        for i, data in enumerate(self.__samples):
            item = GeneratedTextsListItem(self.sampleList)
            item.setData(0, Qt.ItemDataRole.UserRole, data)
            item.setData(0, Qt.ItemDataRole.UserRole + 1, i)

            # Handle these differently, depending on whether they're just strings
            # or there's extra data associated
            if isinstance(data, str):
                data: str
                item.setText(0, data.replace('\n', ''))
                

            elif isinstance(data, dict):
                data: dict
                item.setText(0, data.get('text', '').replace('\n', ''))

                status: str = data.get('status', None)

                if status == 'favorited': # for when an item is favorited
                    item.setIcon(0, QIcon('Icons/Star.svg'))

                elif status == 'hidden': # for when an item is crossed out
                    item.setIcon(0, QIcon('Icons/Cross Out.svg'))
                    f: QFont = item.font(0)
                    f.setStrikeOut(True)
                    item.setFont(0, f)

                if data.get('datasetMatches', None) is not None and len(data.get('datasetMatches', [])) > 0:
                    topMatch = sorted(data.get('datasetMatches', []), key=lambda x: x.get('ratio', 0), reverse=True)[0]
                    ratio = topMatch.get('ratio', 0)

                    icon = 'Success'
                    if ratio >= 1.0: icon = 'Critical'
                    elif ratio > 0.5: icon = 'Warning'

                    item.setIcon(1, QIcon(f'Icons/{icon}.svg'))
                    item.setText(1, f'{ratio * 100:.01f}%')
                    item.setData(1, Qt.ItemDataRole.UserRole, ratio)

        if row >= 0:
            self.sampleList.setCurrentItem(self.sampleList.topLevelItem(min(row, self.sampleList.topLevelItemCount() - 1)))

class GeneratedTextsList(QTreeWidget):
    genTextDataModified = pyqtSignal()
    def __init__(self, repoName, parent=None):
        super().__init__(parent)
        self.__repoName = repoName
        self.__sessionName = ''

        self.setColumnCount(2)
        self.setHeaderLabels(["Text", "% Match"])

        h = self.header()
        h.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        h.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        h.setStretchLastSection(False)

        h.setSortIndicatorShown(True)
        self.setSortingEnabled(True)
        self.sortByColumn(1, Qt.SortOrder.AscendingOrder)
        self.setRootIsDecorated(False)

        self.setAlternatingRowColors(True)

        # Set up context menu
        self.contextMenu = QMenu(self)
        self.tagMenu = self.contextMenu.addMenu('Add Tag...')
        self.favAction = self.tagMenu.addAction(QIcon('Icons/Star.svg'), 'Favorite', self.onAddFavoriteText, QKeySequence("Q"))
        self.hideAction = self.tagMenu.addAction(QIcon('Icons/Cross Out.svg'), 'Hidden', self.onHideText, QKeySequence("W"))
        self.clearTagAction = self.tagMenu.addAction('None', self.onClearStatusText, QKeySequence("E"))

        self.delAction = self.contextMenu.addAction(QIcon('Icons/Trash.svg'), 'Delete', self.onDeleteText, QKeySequence.StandardKey.Delete)

        self.addAction(self.favAction)
        self.addAction(self.hideAction)
        self.addAction(self.clearTagAction)
        self.addAction(self.delAction)
        

        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.onContextMenuRequested)

    def onContextMenuRequested(self, point: QPoint):
        self.contextMenu.exec(self.mapToGlobal(point))

    def onDeleteText(self):
        index = self.currentItem().data(0, Qt.ItemDataRole.UserRole + 1)
        deleteGeneratedSampleInRepository(self.__repoName, self.__sessionName, index)
        self.genTextDataModified.emit()

    def onAddFavoriteText(self):
        self.setStatusOfCurrentItem('favorited')
        
    def onHideText(self):
        self.setStatusOfCurrentItem('hidden')

    def onClearStatusText(self):
        self.setStatusOfCurrentItem('')

    def setStatusOfCurrentItem(self, status: str):
        if self.currentItem() is None: return
        index = self.currentItem().data(0, Qt.ItemDataRole.UserRole + 1)

        currentTag = self.currentItem().data(0, Qt.ItemDataRole.UserRole).get('status', None)
    
        if currentTag == status:
            markGeneratedSampleInRepository(self.__repoName, self.__sessionName, index, '')
        else:
            markGeneratedSampleInRepository(self.__repoName, self.__sessionName, index, status)

        self.genTextDataModified.emit()

    def setCurrentSessionName(self, name: str):
        self.__sessionName = name

    def setRepository(self, repoName: str):
        self.__repoName = repoName
        
class GeneratedTextsListItem(QTreeWidgetItem):
    def __lt__(self, other: 'GeneratedTextsListItem'):
        return self.data(1, Qt.ItemDataRole.UserRole) < other.data(1, Qt.ItemDataRole.UserRole)

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

        self.__prompt = ''

    def setRepository(self, repoName: str):
        self.__repoName = repoName

    def setPrompt(self, prompt: str):
        self.__prompt = prompt

    def setSample(self, sample: dict):
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