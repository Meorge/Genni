import csv
from json.decoder import JSONDecodeError
from os.path import exists, join
from typing import Optional, Union
from PyQt6.QtCore import QThread, QTimer, pyqtSignal
from datetime import datetime, timedelta
from os import environ
from json import dump, load

from ModelRepo import getRepoHeadModel

canDoNotifications = True
try:
    from PyQtNotifications.QMacNotification import QMacNotification
    canDoNotifications = True
except ImportError as e:
    print(f'PyQtNotifications not found. Genni will still run, but notifications will not appear on macOS.')
    canDoNotifications = False


environ["TOKENIZERS_PARALLELISM"] = "false"
environ["OMP_NUM_THREADS"] = "1"
        
class ATGTrainer(QThread):
    trainingStarted = pyqtSignal()
    trainingEnded = pyqtSignal()
    batchEnded = pyqtSignal(int, int, object, object)
    sampleTextGenerated = pyqtSignal(int, list)
    modelSaved = pyqtSignal(int, str)
    errorOccurred = pyqtSignal(Exception)
    stopTriggered = pyqtSignal()

    timePassed = pyqtSignal(timedelta)

    __config = {}

    __currentStep = 0

    __samples = {}

    __dataRows = []

    __avgLoss = None

    __shouldStop = False

    def __init__(self, parent=None, repoName=None):
        super().__init__(parent)
        self.__repoName = repoName
        self.timePassedTimer = QTimer()
        self.timePassedTimer.setInterval(1000)
        self.timePassedTimer.timeout.connect(self.onTimePassed)

        self.trainingStarted.connect(self.onTrainingStarted_main)
        self.trainingEnded.connect(self.onTrainingEnded_main)

    def setConfig(self, config: dict): self.__config = config
    def config(self) -> dict: return self.__config

    def currentStep(self) -> int: return self.__currentStep

    def trainingSamples(self) -> dict: return self.__samples

    def triggerStop(self):
        self.__shouldStop = True
        self.stopTriggered.emit()

    def onTrainingStarted_main(self):
        print('training started was emitted')
        self.startTime = datetime.now()
        self.timePassedTimer.start()

    def onTrainingEnded_main(self):
        self.timePassedTimer.stop()

    def onTimePassed(self):
        currentTime = datetime.now()
        elapsed = currentTime - self.startTime
        self.timePassed.emit(elapsed)

    def run(self):
        from aitextgen_dev.aitextgen.utils import GPT2Config
        from aitextgen_dev.aitextgen import aitextgen

        self.__shouldStop = False
        self.__dataRows = []

        dataset = self.__config['dataset']
        steps = self.__config['steps']
        genEvery = self.__config['genEvery']
        saveEvery = self.__config['saveEvery']
        learningRate = self.__config['learningRate']

        if self.__config['constructorArgs'] is None: aitextgenArgs = {}
        else: aitextgenArgs = self.__config['constructorArgs']

        # Find the most recent model
        repoFolderPath = self.__repoName

        # Find dataset information
        datasetFolderPath = join(repoFolderPath, 'datasets', dataset['pathName'])
        datasetFilePath = join(datasetFolderPath, 'dataset')
        datasetTokenizerFilePath = join(datasetFolderPath, 'aitextgen.tokenizer.json')
        datasetMetadata: dict = dataset['meta']

        modelsFolderPath = join(repoFolderPath, 'models')

        self.__infoFilePath = join(repoFolderPath, 'info.json')
        
        if exists(self.__infoFilePath):
            try:
                self.__latestModel = getRepoHeadModel(repoFolderPath)
            except JSONDecodeError as e:
                self.errorOccurred.emit(e)
                return
            except IOError as e:
                self.errorOccurred.emit(e)
                return

        if '__useHeadModel' in aitextgenArgs and self.__latestModel is not None:
            # There is a latest model, so let's use it as a base
            latestModelPath = join(modelsFolderPath, self.__latestModel)
            aitextgenArgs['model_folder'] = latestModelPath
            print(f'Using head model {latestModelPath} as base')
            del aitextgenArgs['__useHeadModel']

        if len(aitextgenArgs) == 0:
            # There are no arguments being passed to aitextgen.
            # This means we want to create a model from scratch.
            print('No base model provided, so training from scratch')
            aitextgenArgs['config'] = GPT2Config()
            aitextgenArgs['tokenizer_file'] = datasetTokenizerFilePath

        print(f'arguments to aitextgen constructor: {aitextgenArgs}')

        try:
            self.ai = aitextgen(**aitextgenArgs)
        except Exception as e:
            self.errorOccurred.emit(e)
            return

        callbacks = {
            'on_train_begin': self.onTrainingStarted,
            'on_train_end': self.onTrainingEnded,
            'on_step_end': self.onBatchEnded,
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
            'custom_callbacks': callbacks
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
        title = f'Training completed'
        body = 'Average loss '
        if self.__avgLoss: body += f'{self.__avgLoss:.2f}'
        else: body += 'unknown'

        if canDoNotifications:
            QMacNotification(
                title,
                body
            ).exec()

        self.trainingEnded.emit()

    def onBatchEnded(self, steps, total, loss, avg_loss, trainer):
        print(f"Step {steps}/{total} - loss {loss} and avg {avg_loss}")

        self.__currentStep = steps
        self.__avgLoss = avg_loss

        currentTime = datetime.now()
        elapsed = currentTime - self.startTime
        row = [elapsed.total_seconds(), steps, loss, avg_loss]
        self.__dataRows.append(row)

        trainer.should_stop = self.__shouldStop

        self.batchEnded.emit(steps, total, loss, avg_loss)

    def onSampleTextGenerated(self, texts):
        title = f'{self.currentStep()} steps reached'
        body = 'Sample texts have been generated - average loss '
        if self.__avgLoss: body += f'{self.__avgLoss:.2f}'
        else: body += 'unknown'

        if canDoNotifications:
            QMacNotification(
                title,
                body
            ).exec()

        self.__samples[str(self.currentStep())] = texts
        self.sampleTextGenerated.emit(self.currentStep(), texts)

    def onModelSaved(self, steps, dir):
        title = f'{steps} steps reached'
        body = 'Model has been saved - average loss '
        if self.__avgLoss: body += f'{self.__avgLoss:.2f}'
        else: body += 'unknown'

        if canDoNotifications:
            QMacNotification(
                title,
                body
            ).exec()

        self.saveModelMetadata()
        self.modelSaved.emit(steps, dir)

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
            with open(hpFilePath, 'w', encoding='utf-8') as f: dump(hpJson, f)
        except IOError as e:
            self.errorOccurred.emit(e)
            return

        # Save step data
        stepFilePath = join(self.__fullModelPath, 'steps.csv')

        try:
            with open(stepFilePath, 'w', encoding='utf-8', newline='') as f:
                csv.writer(f).writerows(self.__dataRows)
        except IOError as e:
            self.errorOccurred.emit(e)
            return

        # Update info.json with new latest model
        newInfoJson = {'latest': self.__modelName}
        if exists(self.__infoFilePath):
            try:            
                f = open(self.__infoFilePath, 'r', encoding='utf-8')
                try:
                    newInfoJson = load(f)
                    newInfoJson['latest'] = self.__modelName
                except JSONDecodeError:
                    pass
                f.close()

                f = open(self.__infoFilePath, 'w', encoding='utf-8')
                dump(newInfoJson, f)
                f.close()

            except IOError as e:
                self.errorOccurred.emit(e)
                return
            except JSONDecodeError as e:
                self.errorOccurred.emit(e)
                return