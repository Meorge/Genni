from PyQt5.QtCore import QThread, QTimer, pyqtSignal
from datetime import datetime, timedelta

class ATGTrainer(QThread):
    trainingStarted = pyqtSignal()
    trainingEnded = pyqtSignal()
    batchEnded = pyqtSignal(int, int, float, float)
    sampleTextGenerated = pyqtSignal(list)
    modelSaved = pyqtSignal(int, int, str)

    timePassed = pyqtSignal(timedelta, float)

    __saveEvery = 500
    __genEvery = 1000
    __totalSteps = 2000
    __learningRate = 0.001
    __dataset = "training.txt"

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

    def dataset(self) -> str: return self.__dataset
    def setDataset(self, filename: str): self.__dataset = filename

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
        print('time to import aitextgen stuff')
        from aitextgen.aitextgen.TokenDataset import TokenDataset
        from aitextgen.aitextgen.tokenizers import train_tokenizer
        from aitextgen.aitextgen.utils import GPT2ConfigCPU
        from aitextgen.aitextgen import aitextgen
        print('aitextgen stuff imported')

        print('running ATGTrainer')
        file_name = self.dataset()
        train_tokenizer(file_name)
        print('tokenizer trained')
        tokenizer_file = "aitextgen.tokenizer.json"
        config = GPT2ConfigCPU()
        print('GPT2 config created')

        self.ai = aitextgen(tokenizer_file=tokenizer_file, config=config)
        print('aitextgen created')
        self.data = TokenDataset(file_name, tokenizer_file=tokenizer_file, block_size=64)
        print('token dataset created')

        callbacks = {
            'on_train_start': self.onTrainingStarted,
            'on_train_end': self.onTrainingEnded,
            'on_batch_end': self.onBatchEnded,
            'on_sample_text_generated': self.onSampleTextGenerated,
            'on_model_saved': self.onModelSaved
        }

        print('About to call self.ai.train')

        self.ai.train(self.data,
            learning_rate=self.learningRate(),
            batch_size=1,
            num_steps=self.totalSteps(),
            generate_every=self.genEvery(),
            save_every=self.saveEvery(),
            print_generated=False, print_saved=False, callbacks=callbacks)

    def onTrainingStarted(self):
        self.trainingStarted.emit()

    def onTrainingEnded(self):
        # print("Training has ended!")
        self.trainingEnded.emit()

    def onBatchEnded(self, steps, total, loss, avg_loss):
        # print(f"Step {steps}/{total} - loss {loss} and avg {avg_loss}")
        self.batchEnded.emit(steps, total, loss, avg_loss)

    def onSampleTextGenerated(self, texts):
        # print(f"Sample texts: {texts}")
        self.sampleTextGenerated.emit(texts)

    def onModelSaved(self, steps, total, dir):
        # print(f"Step {steps}/{total} - save to {dir}")
        self.modelSaved.emit(steps, total, dir)