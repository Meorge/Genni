from PyQt5.QtWidgets import QMainWindow, QApplication
import sys
from os import environ

from ATGTrainer import ATGTrainer
from Views.TrainingView import TrainingView

class MyWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)

        self.trainingView = TrainingView(self)
        self.setCentralWidget(self.trainingView)

    def doTraining(self):
        self.trainThread = ATGTrainer(self)
        self.trainingInProgressView.trainingInfo.setTrainer(self.trainThread)

        self.trainThread.trainingStarted.connect(self.trainingInProgressView.onTrainingStarted)
        self.trainThread.trainingEnded.connect(self.trainingInProgressView.onTrainingEnded)
        self.trainThread.batchEnded.connect(self.trainingInProgressView.onBatchEnded)
        self.trainThread.timePassed.connect(self.trainingInProgressView.trainingInfo.onTimePassed)
        self.trainThread.start()


if __name__ == "__main__":
    environ["TOKENIZERS_PARALLELISM"] = "false"
    environ["OMP_NUM_THREADS"] = "1"
    app = QApplication([])
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())