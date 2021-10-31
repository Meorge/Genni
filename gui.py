from typing import List
from PyQt5.QtCore import QSize, QThread, QTimer, Qt, pyqtSignal, QPointF
from PyQt5.QtGui import QColor, QColorConstants, QFont, QPen
from PyQt5.QtWidgets import QFrame, QGridLayout, QLabel, QMainWindow, QApplication, QProgressBar, QPushButton, QSizePolicy, QSplitter, QVBoxLayout, QWidget
from PyQt5.QtChart import QChart, QChartView, QLineSeries
import sys
from datetime import datetime, timedelta
from time import gmtime
from os import environ

from aitextgen.aitextgen.TokenDataset import TokenDataset
from aitextgen.aitextgen.tokenizers import train_tokenizer
from aitextgen.aitextgen.utils import GPT2ConfigCPU
from aitextgen.aitextgen import aitextgen

COLOR_PURPLE = QColor(180, 170, 255)
COLOR_BLUE = QColor(170, 240, 255)
COLOR_GREEN = QColor(220, 255, 170)
COLOR_YELLOW = QColor(255, 250, 170)

GENERATE_EVERY = 100
SAVE_EVERY = 500
TOTAL_STEPS = 5000

SMOOTHING_FACTOR = 0.005

class MyWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)

        self.lossSeries = QLineSeries()
        self.lossSeries.setName("Loss")
        self.lossSeries.setPen(QPen(QColor(250,100,80,80), 2))

        self.avgLossSeries = QLineSeries()
        self.avgLossSeries.setName("Average Loss")
        self.avgLossSeries.setPen(QPen(QColor(10,100,250), 4))

        self.chart = QChart()
        self.chart.setTitle("Training Session")
        self.chart.addSeries(self.lossSeries)
        self.chart.addSeries(self.avgLossSeries)
        self.chart.createDefaultAxes()

        self.chart.axisX().setRange(0,0)
        self.chart.axisX().setTitleText("Step")
        self.chart.axisX().setLabelFormat("%d")
        self.chart.axisY().setRange(0,0)
        

        self.trainingLabel = QLabel("Training...")
        self.trainingLabelFont = QFont()
        self.trainingLabelFont.setBold(True)
        self.trainingLabelFont.setPointSizeF(self.trainingLabelFont.pointSizeF() * 2.0)
        self.trainingLabel.setFont(self.trainingLabelFont)
        self.trainingLabel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)

        self.trainingSourceLabel = QLabel("Finetuning on the dataset \"training_data.txt\".")
        self.trainingSourceLabel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)

        self.chartView = QChartView(self.chart)
        self.gobutton = QPushButton("Start Training", clicked=self.doTraining)

        self.trainingInfo = TrainingInformationView(self)

        self.splitter = QSplitter(self)
        self.splitter.addWidget(self.trainingInfo)
        self.splitter.addWidget(self.chartView)
        self.splitter.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.ly = QVBoxLayout()
        self.ly.addWidget(self.trainingLabel, alignment=Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        self.ly.addWidget(self.trainingSourceLabel, alignment=Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        self.ly.addWidget(self.splitter)
        self.ly.addWidget(self.gobutton)

        self.setCentralWidget(QWidget())
        self.centralWidget().setLayout(self.ly)
        
    def doTraining(self):
        self.trainThread = ATGTrainer(self)
        self.trainThread.trainingStarted.connect(self.onTrainingStarted)
        self.trainThread.trainingEnded.connect(self.onTrainingEnded)
        self.trainThread.batchEnded.connect(self.onBatchEnded)
        self.trainThread.timePassed.connect(self.trainingInfo.onTimePassed)
        self.trainThread.start()

    def onTrainingStarted(self):
        self.gobutton.setEnabled(False)

    def onTrainingEnded(self):
        self.gobutton.setEnabled(True)

    def onBatchEnded(self, steps, total, loss, avg_loss):
        self.trainingInfo.onBatchEnded(steps, total, avg_loss)
        self.chart.axisX().setRange(0, total)
        self.chart.axisY().setRange(0, max(loss, self.chart.axisY(self.lossSeries).max()))

        self.lossSeries << QPointF(steps, loss)
        self.avgLossSeries << QPointF(steps, avg_loss)

class TrainingInformationView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.currentStepLabel = LabeledValueView("Current Step", "---", COLOR_PURPLE)
        self.totalStepLabel = LabeledValueView("Total Steps", f"{TOTAL_STEPS}", COLOR_PURPLE)

        self.timeElapsedLabel = LabeledValueView("Elapsed", "--:--:--", COLOR_GREEN)
        self.timeRemainingLabel = LabeledValueView("Remaining", "--:--:--", COLOR_GREEN)

        self.avgLossLabel = LabeledValueView("Avg.  Loss", "-.--", COLOR_YELLOW)
        self.dAvgLossLabel = LabeledValueView("Change in Avg.  Loss", "-.--", QColor(200, 255, 170))

        self.stepsToGenTextLabel = LabeledValueView("Next Samples", "---", COLOR_BLUE)
        self.stepsToSaveModelLabel = LabeledValueView("Next Save", "---", COLOR_BLUE)

        self.ly = QGridLayout(self)

        self.currentGridRow = 0
        self.addRow(self.currentStepLabel, self.totalStepLabel)
        self.addDivider()
        self.addRow(self.stepsToGenTextLabel, self.stepsToSaveModelLabel)
        self.addDivider()
        self.addRow(self.timeElapsedLabel, self.timeRemainingLabel)
        self.addDivider()
        self.addRow(self.avgLossLabel, QWidget())
        # self.ly.addWidget(QWidget(), self.currentGridRow, 0, 4, 2)
        self.ly.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeading)

        self.setLayout(self.ly)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)

    def addRow(self, widget1: QWidget, widget2: QWidget):
        self.ly.addWidget(widget1, self.currentGridRow, 0, Qt.AlignmentFlag.AlignTop)
        self.ly.addWidget(widget2, self.currentGridRow, 1, Qt.AlignmentFlag.AlignTop)
        self.currentGridRow += 1

    def addDivider(self):
        line = QFrame(self)
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        self.ly.addWidget(line, self.currentGridRow, 0, 1, 2)
        self.currentGridRow += 1

    def onBatchEnded(self, steps, total, avg_loss):
        self.currentStepLabel.setValue(str(steps))
        self.totalStepLabel.setValue(str(total))

        stepsToGen = (total - steps) % GENERATE_EVERY
        stepsToSave = (total - steps) % SAVE_EVERY
        self.stepsToGenTextLabel.setValue('Generating' if stepsToGen == 0 else str(stepsToGen))
        self.stepsToSaveModelLabel.setValue('Saving' if stepsToSave == 0 else str(stepsToSave))

        self.avgLossLabel.setValue(f'{avg_loss:.2f}')

    def onTimePassed(self, passed: timedelta, remaining):
        hours, rem = divmod(passed.seconds, 3600)
        minutes, seconds = divmod(rem, 60)
        passedStr = f'{hours:02d}:{minutes:02d}:{seconds:02d}'
        self.timeElapsedLabel.setValue(passedStr)


    def updateAvgSpeed(self, lastSpeed):
        # https://stackoverflow.com/a/3841706
        # TODO: calculate speeds to put into here!
        self.averageSpeed = SMOOTHING_FACTOR * lastSpeed + (1 - SMOOTHING_FACTOR) * self.averageSpeed


class LabeledValueView(QWidget):
    def __init__(self, title: str, value: str, valueColor: QColor = None, parent=None):
        super().__init__(parent)

        self.titleLabel = QLabel(title)

        self.valueLabel = QLabel(value)
        self.valueLabelFont = QFont()
        self.valueLabelFont.setPointSizeF(self.valueLabelFont.pointSizeF() * 2.0)
        self.valueLabel.setFont(self.valueLabelFont)

        self.ly = QVBoxLayout(self)
        self.ly.addWidget(self.titleLabel)
        self.ly.addWidget(self.valueLabel)
        self.ly.setSpacing(0)
        self.ly.setContentsMargins(0,0,0,0)

        self.valuePalette = self.valueLabel.palette()

        if valueColor is not None:
            self.valuePalette.setColor(self.valueLabel.foregroundRole(), valueColor)
        
        self.valueLabel.setPalette(self.valuePalette)

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)

    def setValue(self, value: str):
        self.valueLabel.setText(value)

    def setValueColor(self, color: QColor):
        self.valuePalette.setColor(self.valueLabel.foregroundRole(), color)


class ATGTrainer(QThread):
    trainingStarted = pyqtSignal()
    trainingEnded = pyqtSignal()
    batchEnded = pyqtSignal(int, int, float, float)
    sampleTextGenerated = pyqtSignal(list)
    modelSaved = pyqtSignal(int, int, str)

    timePassed = pyqtSignal(timedelta, float)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.timePassedTimer = QTimer()
        self.timePassedTimer.setInterval(100)
        self.timePassedTimer.timeout.connect(self.onTimePassed)

        self.trainingStarted.connect(self.onTrainingStarted_main)
        self.trainingEnded.connect(self.onTrainingEnded_main)

    def onTrainingStarted_main(self):
        self.startTime = datetime.now()
        self.timePassedTimer.start()

    def onTrainingEnded_main(self):
        self.timePassedTimer.stop()

    def onTimePassed(self):
        currentTime = datetime.now()
        elapsed = currentTime - self.startTime
        self.timePassed.emit(elapsed, 0)

    def run(self):
        file_name = "training.txt"
        # train_tokenizer(file_name)
        tokenizer_file = "aitextgen.tokenizer.json"
        config = GPT2ConfigCPU()

        self.ai = aitextgen(tokenizer_file=tokenizer_file, config=config)
        self.data = TokenDataset(file_name, tokenizer_file=tokenizer_file, block_size=64)

        callbacks = {
            'on_train_start': self.onTrainingStarted,
            'on_train_end': self.onTrainingEnded,
            'on_batch_end': self.onBatchEnded,
            'on_sample_text_generated': self.onSampleTextGenerated,
            'on_model_saved': self.onModelSaved
        }

        self.ai.train(self.data, batch_size=1, num_steps=TOTAL_STEPS, generate_every=GENERATE_EVERY, save_every=SAVE_EVERY, print_generated=False, print_saved=False, callbacks=callbacks)

    def onTrainingStarted(self):
        # print("Training has started!")
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

if __name__ == "__main__":
    environ["TOKENIZERS_PARALLELISM"] = "false"
    environ["OMP_NUM_THREADS"] = "1"
    app = QApplication([])
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())