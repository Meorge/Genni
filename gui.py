from typing import List
from PyQt5.QtCore import QThread, pyqtSignal, QPointF
from PyQt5.QtGui import QColor, QPen
from PyQt5.QtWidgets import QLabel, QMainWindow, QApplication, QProgressBar, QPushButton, QVBoxLayout, QWidget
from PyQt5.QtChart import QChart, QChartView, QLineSeries
import sys

from aitextgen.aitextgen.TokenDataset import TokenDataset
from aitextgen.aitextgen.tokenizers import train_tokenizer
from aitextgen.aitextgen.utils import GPT2ConfigCPU
from aitextgen.aitextgen import aitextgen

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
        # self.chart.setTheme(QChart.ChartThemeBlueCerulean)

        self.chart.axisX().setRange(0,0)
        self.chart.axisY().setRange(0,0)
        self.chart.axisY().setTitleText("Step Number")

        self.chartView = QChartView(self.chart)
        self.stepLabel = QLabel("Steps go here")
        self.lossLabel = QLabel("Loss goes here")
        self.progbar = QProgressBar()
        self.gobutton = QPushButton("Start Training", clicked=self.doTraining)

        self.ly = QVBoxLayout(self)
        self.ly.addWidget(self.chartView)
        self.ly.addWidget(self.stepLabel)
        self.ly.addWidget(self.lossLabel)
        self.ly.addWidget(self.progbar)
        self.ly.addWidget(self.gobutton)

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
        self.progbar.setRange(0,0)

    def onTrainingEnded(self):
        self.gobutton.setEnabled(True)

    def onBatchEnded(self, steps, total, loss, avg_loss):
        self.stepLabel.setText(f'Step {steps}/{total} ({steps*100/total}%)')
        self.lossLabel.setText(f'Loss = {loss:.2f}, Avg = {avg_loss:.2f}')
        self.progbar.setRange(0, total)
        self.progbar.setValue(steps)

        self.chart.axisX().setRange(0, total)
        self.chart.axisY().setRange(0, max(loss, self.chart.axisY(self.lossSeries).max()))

        self.lossSeries << QPointF(steps, loss)
        self.avgLossSeries << QPointF(steps, avg_loss)

        
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