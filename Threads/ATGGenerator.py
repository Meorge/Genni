from datetime import datetime
from difflib import SequenceMatcher
from json import dump, load
from typing import List
from PyQt6.QtCore import QThread, pyqtSignal
from os.path import join, exists
from os import mkdir
from os import environ

from ModelRepo import getDatasetsInRepository, processGeneratedSamples

# TODO: top_p and top_k

environ["TOKENIZERS_PARALLELISM"] = "false"
environ["OMP_NUM_THREADS"] = "1"

class ATGGenerator(QThread):
    processingStarted = pyqtSignal()
    processingFinished = pyqtSignal(list)

    def __init__(self, parent=None, repoName=None):
        super().__init__(parent)
        self.__repoName = repoName

    __n = 1
    def n(self) -> int: return self.__n
    def setN(self, n: int): self.__n = n

    __prompt = ''
    def prompt(self) -> str: return self.__prompt
    def setPrompt(self, prompt: str): self.__prompt = prompt

    __minLength = None
    def minLength(self) -> int: return self.__minLength
    def setMinLength(self, minLength: int): self.__minLength = minLength

    __maxLength: int = 256
    def maxLength(self) -> int: return self.__maxLength
    def setMaxLength(self, maxLength: int): self.__maxLength = maxLength

    __temperature: float = 0.7
    def temperature(self) -> float: return self.__temperature
    def setTemperature(self, temperature: float): self.__temperature = temperature

    __topK: int = 0
    def topK(self) -> int: return self.__topK
    def setTopK(self, topK: int): self.__topK = topK

    __topP: float = 0
    def topP(self) -> int: return self.__topP
    def setTopP(self, topP: int): self.__topP = topP

    __checkAgainstDatasets: bool = True
    def checkAgainstDatasets(self) -> bool: return self.__checkAgainstDatasets
    def setCheckAgainstDatasets(self, check: bool): self.__checkAgainstDatasets = check

    def run(self):
        from aitextgen_dev.aitextgen.utils import GPT2ConfigCPU
        from aitextgen_dev.aitextgen import aitextgen

        repoFolderPath = self.__repoName

        # Get the latest model folder path
        infoFilePath = join(repoFolderPath, 'info.json')

        jsonInfo: dict = {}
        with open(infoFilePath, encoding='utf-8') as f:
            jsonInfo = load(f)

        latestModelName = jsonInfo.get('latest')
        latestModelPath = join(repoFolderPath, 'models', latestModelName)

        # Find out what dataset this model was finetuned on, and grab its tokenizer
        latestModelMetaPath = join(latestModelPath, 'meta.json')
        with open(latestModelMetaPath, encoding='utf-8') as f:
            modelMeta = load(f)

        datasetName = modelMeta['dataset']

        tokenizerPath = join(
            repoFolderPath,
            'datasets',
            datasetName,
            'aitextgen.tokenizer.json'
        )

        self.ai = aitextgen(
            model_folder=latestModelPath,
            # tokenizer_file=tokenizerPath,
            # config=GPT2ConfigCPU()
        )

        self.samples = self.ai.generate(
            n=self.n(),
            prompt=self.prompt(),
            min_length=self.minLength(),
            max_length=self.maxLength(),
            temperature=self.temperature(),
            return_as_list=True,
            top_k=self.topK(),
            top_p=self.topP()
        )

        self.processingStarted.emit()

        print(f'{datetime.now()} - Processing started')
        self.samplesWithDatasetMatches = processGeneratedSamples(self.__repoName, self.samples, self.prompt(), self.checkAgainstDatasets())
        print(f'{datetime.now()} - Processing complete')

        # make generated folder
        generatedFolderPath = join(repoFolderPath, 'generated')
        if not exists(generatedFolderPath): mkdir(generatedFolderPath)

        # make subfolder for our output
        currentTime = datetime.strftime(datetime.now(), '%Y-%m-%dT%H-%M-%S')
        generatedSubfolderPath = join(generatedFolderPath, currentTime)
        mkdir(generatedSubfolderPath)

        metaJsonPath = join(generatedSubfolderPath, 'meta.json')
        with open(metaJsonPath, 'w', encoding='utf-8') as f:
            dump({
                'n': self.n(),
                'prompt': self.prompt(),
                'minLength': self.minLength(),
                'maxLength': self.maxLength(),
                'temperature': self.temperature(),
                'topP': self.topP(),
                'topK': self.topK(),
                'datetime': datetime.now().isoformat(timespec='seconds')
            }, f, indent=4)

        dataJsonPath = join(generatedSubfolderPath, 'texts.json')
        with open(dataJsonPath, 'w', encoding='utf-8') as f:
            dump(self.samplesWithDatasetMatches, f, indent=4)

        print(f'{datetime.now()} - Generation data saved')
        self.processingFinished.emit(self.samplesWithDatasetMatches)
        

