import csv
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

    __currentStep = 0
    __saveEvery = 500
    __genEvery = 1000
    __totalSteps = 2000
    __learningRate = 0.001
    __dataset = None

    __samples = {}

    __dataRows = []

    def __init__(self, parent=None):
        super().__init__(parent)
        self.timePassedTimer = QTimer()
        self.timePassedTimer.setInterval(100)
        self.timePassedTimer.timeout.connect(self.onTimePassed)

        self.trainingStarted.connect(self.onTrainingStarted_main)
        self.trainingEnded.connect(self.onTrainingEnded_main)

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
        from aitextgen_dev.aitextgen.utils import GPT2ConfigCPU
        from aitextgen_dev.aitextgen import aitextgen

        jsonInfo = {}

        # Find the most recent model
        repoFolderPath = './my_model'

        datasetFolderPath = join(repoFolderPath, 'datasets', self.dataset()['pathName'])
        datasetFilePath = join(datasetFolderPath, 'dataset')

        datasetMetadata: dict = self.dataset()['meta']
        tokenizerFilePath = join(datasetFolderPath, 'aitextgen.tokenizer.json')

        aitextgenArgs = {'tokenizer_file': tokenizerFilePath, 'config': GPT2ConfigCPU()}

        modelsFolderPath = join(repoFolderPath, 'models')

        self.__infoFilePath = join(repoFolderPath, 'info.json')
        
        if exists(self.__infoFilePath):
            f = open(self.__infoFilePath)
            jsonInfo = load(f)
            f.close()

        self.__latestModel = jsonInfo.get('latest', None)

        if self.__latestModel is not None:
            # There is a latest model, so let's use it as a base
            latestModelPath = join(modelsFolderPath, self.__latestModel)
            aitextgenArgs['model_folder'] = latestModelPath

        self.ai = aitextgen(**aitextgenArgs)
        self.data = TokenDataset(datasetFilePath, tokenizer_file=tokenizerFilePath, line_by_line=datasetMetadata.get('lineByLine', False), block_size=64)

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

        self.ai.train(self.data,
            output_dir=self.__fullModelPath,
            learning_rate=self.learningRate(),
            batch_size=1,
            n_generate=5,
            num_steps=self.totalSteps(),
            generate_every=self.genEvery(),
            save_every=self.saveEvery(),
            
            print_generated=False, print_saved=False, callbacks=callbacks)

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
            'name': f'''Model at {datetime.now().strftime('%d %B %Y, %I:%M:%S %p %z')}''',
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
        with open(self.__infoFilePath, 'w') as f: dump(newInfoJson, f)