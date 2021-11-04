from os.path import exists, join, basename
from os import mkdir
from shutil import copyfile
from PyQt6.QtCore import QThread
from datetime import datetime
from json import dump

class ATGDatasetTokenizer(QThread):
    __dataset = None
    __title = 'Dataset'
    __comment = ''
    __lineByLine = True

    def __init__(self, parent=None):
        super().__init__(parent)

    def dataset(self) -> str: return self.__dataset
    def setDataset(self, value: str): self.__dataset = value

    def title(self) -> str: return self.__title
    def setTitle(self, title: str): self.__title = title

    def comment(self) -> str: return self.__comment
    def setComment(self, comment: str): self.__comment = comment

    def lineByLine(self) -> bool: return self.__lineByLine
    def setLineByLine(self, lineByLine: bool): self.__lineByLine = lineByLine

    def run(self):
        repoFolderPath = './my_model'
        currentTime = datetime.strftime(datetime.now(), '%Y-%m-%dT%H-%M-%S')
        fileName = basename(self.dataset())

        # Ensure that the 'datasets' folder exists
        datasetsFolderPath = join(repoFolderPath, 'datasets')
        if not exists(datasetsFolderPath):
            mkdir(datasetsFolderPath)

        # Create folder inside of datasets with the file name and date
        thisDatasetFolderPath = join(datasetsFolderPath, f'{currentTime}_{fileName}')
        mkdir(thisDatasetFolderPath)

        # Copy dataset file into this folder
        thisDatasetFileDestPath = join(thisDatasetFolderPath, 'dataset')
        copyfile(fileName, thisDatasetFileDestPath)

        # Generate tokenizer json, and put it in this folder
        from aitextgen_dev.aitextgen.tokenizers import train_tokenizer
        train_tokenizer(thisDatasetFileDestPath, save_path=thisDatasetFolderPath)

        # Make meta json
        metaJson = {'title': self.title(), 'comment': self.comment(), 'lineByLine': self.lineByLine(), 'originalFilename': fileName, 'imported': datetime.now().isoformat(timespec='seconds')}
        metaJsonFilePath = join(thisDatasetFolderPath, 'meta.json')
        with open(metaJsonFilePath, 'w') as f: dump(metaJson, f)