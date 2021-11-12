import csv
from json.decoder import JSONDecodeError
from os.path import exists, join
from PyQt6.QtCore import QThread, QTimer, pyqtSignal
from datetime import datetime, timedelta
from os import environ
from json import dump, load

environ["TOKENIZERS_PARALLELISM"] = "false"
environ["OMP_NUM_THREADS"] = "1"
        
class ATGTrainer(QThread):
    trainingStarted = pyqtSignal()
    trainingEnded = pyqtSignal()
    batchEnded = pyqtSignal(int, int, float, float)
    sampleTextGenerated = pyqtSignal(int, list)
    modelSaved = pyqtSignal(int, int, str)

    timePassed = pyqtSignal(timedelta, float)

    __title = 'My Model'
    __gptSize = None
    __currentStep = 0
    __saveEvery = 500
    __genEvery = 1000
    __totalSteps = 2000
    __learningRate = 0.001
    __dataset = None

    __samples = {}

    __dataRows = []

    def __init__(self, parent=None, repoName=None):
        super().__init__(parent)
        self.__repoName = repoName
        self.timePassedTimer = QTimer()
        self.timePassedTimer.setInterval(100)
        self.timePassedTimer.timeout.connect(self.onTimePassed)

        self.trainingStarted.connect(self.onTrainingStarted_main)
        self.trainingEnded.connect(self.onTrainingEnded_main)

    def title(self) -> str: return self.__title
    def setTitle(self, title: str): self.__title = title

    def saveEvery(self) -> int: return self.__saveEvery
    def setSaveEvery(self, steps: int): self.__saveEvery = steps

    def genEvery(self) -> int: return self.__genEvery
    def setGenEvery(self, steps: int): self.__genEvery = steps

    def totalSteps(self) -> int: return self.__totalSteps
    def setTotalSteps(self, steps: int): self.__totalSteps = steps

    def learningRate(self) -> float: return self.__learningRate
    def setLearningRate(self, rate: float): self.__learningRate = rate

    def dataset(self) -> dict: return self.__dataset
    def setDataset(self, dataset: dict): self.__dataset = dataset

    def gptSize(self) -> str: return self.__gptSize
    def setGptSize(self, size: str): self.__gptSize = size

    def currentStep(self) -> int: return self.__currentStep

    def trainingSamples(self) -> dict: return self.__samples

    def onTrainingStarted_main(self):
        print('training started was emitted')
        self.startTime = datetime.now()
        self.timePassedTimer.start()

    def onTrainingEnded_main(self):
        self.timePassedTimer.stop()

    def onTimePassed(self):
        currentTime = datetime.now()
        elapsed = currentTime - self.startTime
        self.timePassed.emit(elapsed, 0)

    def run(self):
        from aitextgen_dev.aitextgen.TokenDataset import TokenDataset
        from aitextgen_dev.aitextgen import aitextgen

        jsonInfo = {}

        # Find the most recent model
        repoFolderPath = self.__repoName

        datasetFolderPath = join(repoFolderPath, 'datasets', self.dataset()['pathName'])
        datasetFilePath = join(datasetFolderPath, 'dataset')

        datasetMetadata: dict = self.dataset()['meta']
        tokenizerFilePath = join(datasetFolderPath, 'aitextgen.tokenizer.json')

        aitextgenArgs = {
            # 'cache_dir': './aitextgen_cache'
            }

        modelsFolderPath = join(repoFolderPath, 'models')

        self.__infoFilePath = join(repoFolderPath, 'info.json')
        
        if exists(self.__infoFilePath):
            f = open(self.__infoFilePath)
            try: jsonInfo = load(f)
            except JSONDecodeError: jsonInfo = {}
            f.close()

        if self.__gptSize is not None:
            # We want to use a GPT model as a base
            aitextgenArgs['tf_gpt2'] = self.__gptSize

        # TODO: only do this if the user wants it!!
        aitextgenArgs['model'] = 'EleutherAI/gpt-neo-125M'

        self.__latestModel = jsonInfo.get('latest', None)

        if self.__latestModel is not None:
            # There is a latest model, so let's use it as a base
            latestModelPath = join(modelsFolderPath, self.__latestModel)
            aitextgenArgs['model_folder'] = latestModelPath

        print(f'arguments to aitextgen constructor: {aitextgenArgs}')
        self.ai = aitextgen(**aitextgenArgs)

        callbacks = {
            'on_train_start': self.onTrainingStarted,
            'on_train_end': self.onTrainingEnded,
            'on_batch_end': self.onBatchEnded,
            'on_sample_text_generated': self.onSampleTextGenerated,
            'on_model_saved': self.onModelSaved
        }

        # Copy the "latest" folder to a new folder
        # yyyy-mm-ddThh-mm-ss
        self.__modelName = datetime.strftime(datetime.now(), '%Y-%m-%dT%H-%M-%S')
        self.__fullModelPath = join(modelsFolderPath, self.__modelName)

        trainArgs = {
            'train_data': datasetFilePath,
            'line_by_line': datasetMetadata.get('lineByLine', False),
            'from_cache': False,
            'num_steps': self.totalSteps(),
            'generate_every': self.genEvery(),
            'save_every': self.saveEvery(),
            'learning_rate': self.learningRate(),
            'fp16': False,
            'batch_size': 1,
            'progress_bar_refresh_rate': 1,
            'output_dir': self.__fullModelPath,
            'callbacks': callbacks
        }

        print(f'arguments to train: {trainArgs}')
        self.ai.train(**trainArgs)

        # Write hp.json with hyperparameters
        self.saveModelMetadata()


    def onTrainingStarted(self):
        self.trainingStarted.emit()

    def onTrainingEnded(self):
        # print("Training has ended!")
        self.trainingEnded.emit()

    def onBatchEnded(self, steps, total, loss, avg_loss):
        # print(f"Step {steps}/{total} - loss {loss} and avg {avg_loss}")
        self.__currentStep = steps

        currentTime = datetime.now()
        elapsed = currentTime - self.startTime
        row = [elapsed.total_seconds(), steps, loss, avg_loss]
        self.__dataRows.append(row)

        self.batchEnded.emit(steps, total, loss, avg_loss)

    def onSampleTextGenerated(self, texts):
        self.__samples[str(self.currentStep())] = texts
        self.sampleTextGenerated.emit(self.currentStep(), texts)

    def onModelSaved(self, steps, total, dir):
        # print(f"Step {steps}/{total} - save to {dir}")
        self.saveModelMetadata()
        self.modelSaved.emit(steps, total, dir)

    def saveModelMetadata(self):
        # Save metadata
        hpFilePath = join(self.__fullModelPath, 'meta.json')
        hpJson = {
            'name': self.title(),
            'comment': 'User comments go here',
            'datetime': datetime.now().isoformat(timespec='seconds'),
            'duration': (datetime.now() - self.startTime).total_seconds(),
            'dataset': self.dataset().get('pathName', None),
            'parent': self.__latestModel,
            'learningRate': self.learningRate(),
            'steps': self.currentStep(),
            'samples': self.trainingSamples()
            }
        with open(hpFilePath, 'w') as f: dump(hpJson, f)

        # Save step data
        stepFilePath = join(self.__fullModelPath, 'steps.csv')
        with open(stepFilePath, 'w') as f: csv.writer(f).writerows(self.__dataRows)

        # Update info.json with new latest model
        newInfoJson = {'latest': self.__modelName}
        if exists(self.__infoFilePath):
            f = open(self.__infoFilePath, 'r')
            try:
                newInfoJson = load(f)
            except JSONDecodeError:
                pass
            f.close()

        f = open(self.__infoFilePath, 'w')
        dump(newInfoJson, f)
        f.close()