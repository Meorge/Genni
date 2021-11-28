from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QDialog, QVBoxLayout
from Threads.DatasetBuilder import TextDatasetBuilder
from Threads.TwitterDatasetBuilder import TwitterDatasetBuilder
from Views.AddingDataset.TwitterSource.DatasetFromTwitterConfigView import DatasetFromTwitterConfigView
from Views.AddingDataset.TwitterSource.DatasetFromTwitterProgressView import DatasetFromTwitterProgressView
from Views.SwipingPageView import SwipingPageView
from Views.AddingDataset.DatasetSourceSelectView import DatasetSourceSelectView
from Views.AddingDataset.TextSource.DatasetFromTextConfigView import DatasetFromTextConfigView
from Views.AddingDataset.TextSource.DatasetFromTextImportProgressView import DatasetFromTextImportProgressView
from Views.AddingDataset.TextSource.DatasetFromTextImportDoneView import DatasetFromTextImportDoneView

class ImportDatasetView(SwipingPageView):
    finished = pyqtSignal()

    def __init__(self, parent=None, repoName=None):
        super().__init__(parent)
        self.__repoName = repoName
        self.sourceSelectView = DatasetSourceSelectView(self)
        self.sourceSelectView.proceed.connect(self.selectSource)
        self.addWidget(self.sourceSelectView)


        # For text file
        self.textConfigView = DatasetFromTextConfigView(self)
        self.textConfigView.back.connect(self.goToSourceSelectView)
        self.textConfigView.proceed.connect(self.runImportDatasetThread)
        self.textProgressView = DatasetFromTextImportProgressView(self)
        self.addWidget(self.textConfigView)
        self.addWidget(self.textProgressView)


        # For Twitter
        self.twitterConfigView = DatasetFromTwitterConfigView(self)
        self.twitterConfigView.back.connect(self.goToSourceSelectView)
        self.twitterConfigView.proceed.connect(self.runDownloadTweetsThread)
        self.twitterProgressView = DatasetFromTwitterProgressView(self)
        self.twitterDoneView = DatasetFromTextImportDoneView(self)
        self.twitterDoneView.finished.connect(self.finished)

        self.addWidget(self.twitterConfigView)
        self.addWidget(self.twitterProgressView)
        self.addWidget(self.twitterDoneView)

        # For all methods
        self.doneView = DatasetFromTextImportDoneView(self)
        self.doneView.finished.connect(self.finished)
        self.addWidget(self.doneView)
        
    def selectSource(self, source: str):
        {
            'text': self.goToTextConfigView,
            'twitter': self.goToTwitterConfigView
        }[source]()

    def goToSourceSelectView(self): self.slideInWgt(self.sourceSelectView)
    def goToTextConfigView(self): self.slideInWgt(self.textConfigView)
    def goToTextProgressView(self): self.slideInWgt(self.textProgressView)

    def goToTwitterConfigView(self): self.slideInWgt(self.twitterConfigView)
    def goToTwitterProgressView(self): self.slideInWgt(self.twitterProgressView)
    def goToTwitterDoneView(self): self.slideInWgt(self.twitterDoneView)

    def goToDoneView(self): self.slideInWgt(self.doneView)


    def runImportDatasetThread(self):
        self.goToTextProgressView()

        info = self.textConfigView.getConfigData()
        
        self.datasetThread = TextDatasetBuilder(self, repoName=self.__repoName)
        self.datasetThread.setTitle(info['title'])
        self.datasetThread.setComment(info['comment'])
        self.datasetThread.setLineByLine(info['lineByLine'])
        self.datasetThread.setDataset(info['filename'])

        self.datasetThread.finished.connect(self.goToDoneView)
        self.datasetThread.start()

    def runDownloadTweetsThread(self):
        self.goToTwitterProgressView()

        searchQuery = self.twitterConfigView.searchQuery()

        self.twitterThread = TwitterDatasetBuilder(self, repoName=self.__repoName)
        self.twitterThread.setSearchQuery(searchQuery)
        self.twitterThread.finished.connect(self.goToDoneView)
        self.twitterThread.start()

class ImportDatasetModal(QDialog):
    def __init__(self, parent=None, repoName=None):
        super().__init__(parent)
        self.setModal(True)

        self.w = ImportDatasetView(self, repoName=repoName)
        self.w.finished.connect(self.accept)

        self.ly = QVBoxLayout(self)
        self.ly.setContentsMargins(0,0,0,0)
        self.ly.addWidget(self.w)
        self.setLayout(self.ly)
        