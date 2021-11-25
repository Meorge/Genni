from os.path import exists, join, basename
from os import mkdir
from shutil import copyfile
from PyQt6.QtCore import QThread
from datetime import datetime
from json import dump

class BaseDatasetBuilder(QThread):
    def __init__(self, parent=None, repoName=None):
        super().__init__(parent)
        self.__repoName = repoName

    __title = 'Dataset'
    def title(self) -> str: return self.__title
    def setTitle(self, title: str): self.__title = title

    __comment = ''
    def comment(self) -> str: return self.__comment
    def setComment(self, comment: str): self.__comment = comment

    __lineByLine = True
    def lineByLine(self) -> bool: return self.__lineByLine
    def setLineByLine(self, lineByLine: bool): self.__lineByLine = lineByLine

    def initialize(self):
        self.currentTime = datetime.now()
        self.repoFolderPath = self.__repoName
        self.currentTimeStr = datetime.strftime(self.currentTime, '%Y-%m-%dT%H-%M-%S')

        # Ensure that the 'datasets' folder exists
        self.datasetsFolderPath = join(self.repoFolderPath, 'datasets')
        if not exists(self.datasetsFolderPath):
            mkdir(self.datasetsFolderPath)

        # Create folder inside of datasets with the file name and date
        self.thisDatasetFolderPath = join(self.datasetsFolderPath, f'{self.currentTimeStr}')
        mkdir(self.thisDatasetFolderPath)

        # Copy dataset file into this folder
        self.thisDatasetFileDestPath = join(self.thisDatasetFolderPath, 'dataset')

    def writeTokenizer(self):
        # Generate tokenizer json, and put it in this folder
        from aitextgen_dev.aitextgen.tokenizers import train_tokenizer
        train_tokenizer(self.thisDatasetFileDestPath, save_path=self.thisDatasetFolderPath)

    def writeMetadata(self, extraMetadata: dict):
        # Make meta json
        metaJson = {'title': self.title(), 'comment': self.comment(), 'lineByLine': self.lineByLine(), 'imported': self.currentTime.isoformat(timespec='seconds')} | extraMetadata
        metaJsonFilePath = join(self.thisDatasetFolderPath, 'meta.json')
        with open(metaJsonFilePath, 'w', encoding='utf-8') as f: dump(metaJson, f)

    def run(self):
        self.initialize()
        extraMetadata = self.createDataset()
        self.writeTokenizer()
        self.writeMetadata(extraMetadata)

    def createDataset(self) -> dict:
        """
        Override this function to create the custom dataset.
        Return a dictionary containing parameters you'd like to add to the metadata.
        """
        return {}


class TextDatasetBuilder(BaseDatasetBuilder):
    __dataset = None
    def dataset(self) -> str: return self.__dataset
    def setDataset(self, value: str): self.__dataset = value

    def createDataset(self) -> dict:
        copyfile(self.dataset(), self.thisDatasetFileDestPath)
        return { 'lineByLine': self.lineByLine() }