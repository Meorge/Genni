from PyQt5.QtWidgets import QMainWindow, QApplication
import sys
from os import environ
environ["TOKENIZERS_PARALLELISM"] = "false"
environ["OMP_NUM_THREADS"] = "1"

from ATGTrainer import ATGTrainer
from Views.TrainingView import TrainingView

class MyWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)

        self.trainingView = TrainingView(self)
        self.trainingView.trainingStarted.connect(self.doTraining)
        self.trainingView.startTraining()
        self.setCentralWidget(self.trainingView)

    def doTraining(self):
        print('training should start now, create ATGTrainer')
        self.trainThread = ATGTrainer(self)
        self.trainingView.trainingInProgressView.trainingInfo.setTrainer(self.trainThread)

        self.trainThread.trainingStarted.connect(self.trainingView.trainingInProgressView.onTrainingStarted)
        self.trainThread.trainingEnded.connect(self.trainingView.trainingInProgressView.onTrainingEnded)
        self.trainThread.batchEnded.connect(self.trainingView.trainingInProgressView.onBatchEnded)
        self.trainThread.timePassed.connect(self.trainingView.trainingInProgressView.trainingInfo.onTimePassed)
        self.trainThread.start()


if __name__ == "__main__":
    app = QApplication([])
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())