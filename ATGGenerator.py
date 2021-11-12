from datetime import datetime
from json import dump, load
from PyQt6.QtCore import QThread, pyqtSignal
from os.path import join, exists
from os import mkdir
from os import environ

# TODO: top_p and top_k

environ["TOKENIZERS_PARALLELISM"] = "false"
environ["OMP_NUM_THREADS"] = "1"

class ATGGenerator(QThread):
    samplesGenerated = pyqtSignal(list)
    def __init__(self, parent=None, repoName=None, samplesGenerated=None):
        super().__init__(parent)
        self.__repoName = repoName

        if samplesGenerated is not None:
            self.samplesGenerated.connect(samplesGenerated)

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

    def run(self):
        from aitextgen_dev.aitextgen.utils import GPT2ConfigCPU
        from aitextgen_dev.aitextgen import aitextgen

        repoFolderPath = self.__repoName

        # Get the latest model folder path
        infoFilePath = join(repoFolderPath, 'info.json')

        jsonInfo: dict = {}
        with open(infoFilePath) as f:
            jsonInfo = load(f)

        latestModelName = jsonInfo.get('latest')
        latestModelPath = join(repoFolderPath, 'models', latestModelName)

        # Find out what dataset this model was finetuned on, and grab its tokenizer
        latestModelMetaPath = join(latestModelPath, 'meta.json')
        with open(latestModelMetaPath) as f:
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
            return_as_list=True
        )

        # make generated folder
        generatedFolderPath = join(repoFolderPath, 'generated')
        if not exists(generatedFolderPath): mkdir(generatedFolderPath)

        # make subfolder for our output
        currentTime = datetime.strftime(datetime.now(), '%Y-%m-%dT%H-%M-%S')
        generatedSubfolderPath = join(generatedFolderPath, currentTime)
        mkdir(generatedSubfolderPath)

        metaJsonPath = join(generatedSubfolderPath, 'meta.json')
        with open(metaJsonPath, 'w') as f:
            dump({
                'n': self.n(),
                'prompt': self.prompt(),
                'minLength': self.minLength(),
                'maxLength': self.maxLength(),
                'temperature': self.temperature(),
                'datetime': datetime.now().isoformat(timespec='seconds')
            }, f, indent=4)

        dataJsonPath = join(generatedSubfolderPath, 'texts.json')
        with open(dataJsonPath, 'w') as f:
            dump(self.samples, f, indent=4)

        self.samplesGenerated.emit(self.samples)