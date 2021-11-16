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
    errorOccurred = pyqtSignal(Exception)

    timePassed = pyqtSignal(timedelta, float)

    __config = {}

    __currentStep = 0

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

    def setConfig(self, config: dict): self.__config = config
    def config(self) -> dict: return self.__config

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

        dataset = self.__config['dataset']
        steps = self.__config['steps']
        genEvery = self.__config['genEvery']
        saveEvery = self.__config['saveEvery']
        learningRate = self.__config['learningRate']

        jsonInfo = {}

        # Find the most recent model
        repoFolderPath = self.__repoName

        datasetFolderPath = join(repoFolderPath, 'datasets', dataset['pathName'])
        datasetFilePath = join(datasetFolderPath, 'dataset')

        datasetMetadata: dict = dataset['meta']
        tokenizerFilePath = join(datasetFolderPath, 'aitextgen.tokenizer.json')

        aitextgenArgs = self.__config['constructorArgs']

        modelsFolderPath = join(repoFolderPath, 'models')

        self.__infoFilePath = join(repoFolderPath, 'info.json')
        
        if exists(self.__infoFilePath):

            try:
                f = open(self.__infoFilePath)
            except IOError as e:
                self.errorOccurred.emit(e)
                return

            try:
                jsonInfo = load(f)
            except JSONDecodeError:
                jsonInfo = {}
            except IOError as e:
                self.errorOccurred.emit(e)
                return

            f.close()


        self.__latestModel = jsonInfo.get('latest', None)

        if self.__latestModel is not None and 'model' not in aitextgenArgs and 'tf_gpt2' not in aitextgenArgs:
            # There is a latest model, so let's use it as a base
            latestModelPath = join(modelsFolderPath, self.__latestModel)
            aitextgenArgs['model_folder'] = latestModelPath

        print(f'arguments to aitextgen constructor: {aitextgenArgs}')

        try:
            self.ai = aitextgen(**aitextgenArgs)
        except Exception as e:
            self.errorOccurred.emit(e)
            return

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
            'num_steps': steps,
            'generate_every': genEvery,
            'save_every': saveEvery,
            'learning_rate': learningRate,
            'fp16': False,
            'batch_size': 1,
            'progress_bar_refresh_rate': 1,
            'output_dir': self.__fullModelPath,
            'callbacks': callbacks
        }

        print(f'arguments to train: {trainArgs}')

        try:
            self.ai.train(**trainArgs)
        except Exception as e:
            self.errorOccurred.emit(e)
            return

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
            'name': self.__config['title'],
            'comment': 'User comments go here',
            'datetime': datetime.now().isoformat(timespec='seconds'),
            'duration': (datetime.now() - self.startTime).total_seconds(),
            'dataset': self.__config['dataset'].get('pathName', None),
            'parent': self.__latestModel,
            'learningRate': self.__config['learningRate'],
            'steps': self.currentStep(),
            'samples': self.trainingSamples()
            }

        try:
            with open(hpFilePath, 'w') as f: dump(hpJson, f)
        except IOError as e:
            self.errorOccurred.emit(e)
            return

        # Save step data
        stepFilePath = join(self.__fullModelPath, 'steps.csv')

        try:
            with open(stepFilePath, 'w') as f: csv.writer(f).writerows(self.__dataRows)
        except IOError as e:
            self.errorOccurred.emit(e)
            return

        # Update info.json with new latest model
        newInfoJson = {'latest': self.__modelName}
        try:
            if exists(self.__infoFilePath):
                f = open(self.__infoFilePath, 'r')
                try:
                    newInfoJson = load(f)
                except JSONDecodeError:
                    pass
                f.close()
        except IOError as e:
            self.errorOccurred.emit(e)
            return

        try:
            f = open(self.__infoFilePath, 'w')
            dump(newInfoJson, f)
            f.close()
        except IOError as e:
            self.errorOccurred.emit(e)
            return