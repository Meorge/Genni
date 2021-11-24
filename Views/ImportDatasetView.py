from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QDialog, QVBoxLayout
from Threads.ATGDatasetTokenizer import ATGDatasetTokenizer
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
        self.sourceSelectView.proceed.connect(self.goToConfigTextFileView)
        # For text file
        self.configTextFileView = DatasetFromTextConfigView(self)
        self.configTextFileView.back.connect(self.goToSourceSelectView)
        self.configTextFileView.proceed.connect(self.goToImportTextFileView)
        self.configTextFileView.proceed.connect(self.runImportDatasetThread)

        self.importTextFileView = DatasetFromTextImportProgressView(self)

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
        info = self.configTextFileView.getConfigData()
        
        self.datasetThread = ATGDatasetTokenizer(self, repoName=self.__repoName)
        self.datasetThread.setTitle(info['title'])
        self.datasetThread.setComment(info['comment'])
        self.datasetThread.setLineByLine(info['lineByLine'])
        self.datasetThread.setDataset(info['filename'])

        self.datasetThread.finished.connect(self.goToImportTextDoneView)
        self.datasetThread.start()

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
        