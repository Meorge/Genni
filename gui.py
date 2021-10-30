from typing import List
from PyQt5.QtCore import QSize, QThread, Qt, pyqtSignal, QPointF
from PyQt5.QtGui import QColor, QColorConstants, QFont, QPen
from PyQt5.QtWidgets import QFrame, QGridLayout, QLabel, QMainWindow, QApplication, QProgressBar, QPushButton, QSizePolicy, QSplitter, QVBoxLayout, QWidget
from PyQt5.QtChart import QChart, QChartView, QLineSeries
import sys

from aitextgen.aitextgen.TokenDataset import TokenDataset
from aitextgen.aitextgen.tokenizers import train_tokenizer
from aitextgen.aitextgen.utils import GPT2ConfigCPU
from aitextgen.aitextgen import aitextgen

COLOR_PURPLE = QColor(180, 170, 255)
COLOR_BLUE = QColor(170, 240, 255)
COLOR_GREEN = QColor(220, 255, 170)
COLOR_YELLOW = QColor(255, 250, 170)

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
        self.chart.axisX().setTitleText("Step Number")
        self.chart.axisX().setLabelFormat("%d")
        self.chart.axisY().setRange(0,0)
        

        self.trainingLabel = QLabel("Training...  (7.5%)")
        self.trainingLabelFont = QFont()
        self.trainingLabelFont.setBold(True)
        self.trainingLabelFont.setPointSizeF(self.trainingLabelFont.pointSizeF() * 2.0)
        self.trainingLabel.setFont(self.trainingLabelFont)
        self.trainingLabel.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)

        self.chartView = QChartView(self.chart)
        self.gobutton = QPushButton("Start Training", clicked=self.doTraining)

        self.trainingInfo = TrainingInformationView(self)

        self.splitter = QSplitter(self)
        self.splitter.addWidget(self.trainingInfo)
        self.splitter.addWidget(self.chartView)

        self.ly = QVBoxLayout()
        self.ly.addWidget(self.trainingLabel, alignment=Qt.AlignmentFlag.AlignCenter)
        self.ly.addWidget(self.splitter)
        self.ly.addWidget(self.gobutton)

        # self.ly.addWidget(self.trainingLabel, 0, 0, 1, 2, Qt.AlignmentFlag.AlignCenter)
        # self.ly.addWidget(self.chartView, 1, 1)
        # self.ly.addWidget(self.trainingInfo, 1, 0, Qt.AlignmentFlag.AlignTop)
        # self.ly.addWidget(self.gobutton, 2, 0, 1, 2)

        self.setCentralWidget(QWidget())
        self.centralWidget().setLayout(self.ly)

    def doTraining(self):
        self.trainThread = ATGTrainer(self)
        self.trainThread.trainingStarted.connect(self.onTrainingStarted)
        self.trainThread.trainingEnded.connect(self.onTrainingEnded)
        self.trainThread.batchEnded.connect(self.onBatchEnded)
        self.trainThread.start()

    def onTrainingStarted(self):
        self.gobutton.setEnabled(False)

    def onTrainingEnded(self):
        self.gobutton.setEnabled(True)

    def onBatchEnded(self, steps, total, loss, avg_loss):
        # self.stepLabel.setText(f'Step {steps}/{total} ({steps*100/total}%)')
        # self.lossLabel.setText(f'Loss = {loss:.2f}, Avg = {avg_loss:.2f}')

        self.chart.axisX().setRange(0, total)
        self.chart.axisY().setRange(0, max(loss, self.chart.axisY(self.lossSeries).max()))

        self.lossSeries << QPointF(steps, loss)
        self.avgLossSeries << QPointF(steps, avg_loss)

class TrainingInformationView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.currentStepLabel = LabeledValueView("Current Step", "150", COLOR_PURPLE)
        self.totalStepLabel = LabeledValueView("Total Steps", "2000", COLOR_PURPLE)

        self.timeElapsedLabel = LabeledValueView("Elapsed", "00:13:24", COLOR_GREEN)
        self.timeRemainingLabel = LabeledValueView("Remaining", "01:35:21", COLOR_GREEN)

        self.avgLossLabel = LabeledValueView("Avg.  Loss", "3.24", COLOR_YELLOW)
        self.dAvgLossLabel = LabeledValueView("Change in Avg.  Loss", "-0.12", QColor(200, 255, 170))

        self.stepsToGenTextLabel = LabeledValueView("Next Samples In", "200", COLOR_BLUE)
        self.stepsToSaveModelLabel = LabeledValueView("Next Save In", "300", COLOR_BLUE)

        self.ly = QGridLayout(self)

        self.currentGridRow = 0
        self.addRow(self.currentStepLabel, self.totalStepLabel)
        self.addDivider()
        self.addRow(self.stepsToGenTextLabel, self.stepsToSaveModelLabel)
        self.addDivider()
        self.addRow(self.timeElapsedLabel, self.timeRemainingLabel)
        self.addDivider()
        self.addRow(self.avgLossLabel, self.dAvgLossLabel)

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

    def setValueColor(self, color: QColor):
        self.valuePalette.setColor(self.valueLabel.foregroundRole(), color)

class ATGTrainer(QThread):
    trainingStarted = pyqtSignal()
    trainingEnded = pyqtSignal()
    batchEnded = pyqtSignal(int, int, float, float)
    sampleTextGenerated = pyqtSignal(list)
    modelSaved = pyqtSignal(int, int, str)

    def __init__(self, parent=None):
        super().__init__(parent)

    def run(self):
        file_name = "training.txt"
        train_tokenizer(file_name)
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

        self.ai.train(self.data, batch_size=1, num_steps=1000, generate_every=100, save_every=100, print_generated=False, print_saved=False, callbacks=callbacks)

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
    app = QApplication([])
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())