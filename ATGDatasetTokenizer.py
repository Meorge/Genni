from os.path import exists, join
from os import mkdir
from shutil import copyfile
from PyQt5.QtCore import QThread, pyqtSignal
from datetime import datetime
from json import dump

class ATGDatasetTokenizer(QThread):
    __dataset = None

    def __init__(self, parent=None):
        super().__init__(parent)

    def dataset(self) -> str: return self.__dataset
    def setDataset(self, value: str): self.__dataset = value

    def run(self):
        repoFolderPath = './my_model'
        currentTime = datetime.strftime(datetime.now(), '%Y-%m-%dT%H-%M-%S')
        fileName = self.dataset()

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
        metaJson = {'title': 'My Cool Dataset', 'comment': 'User comments can go here', 'imported': datetime.now().isoformat(timespec='seconds')}
        metaJsonFilePath = join(thisDatasetFolderPath, 'meta.json')
        with open(metaJsonFilePath, 'w') as f: dump(metaJson, f)