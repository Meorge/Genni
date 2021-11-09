from PyQt6.QtCore import QSize, Qt, QPointF, pyqtSignal
from PyQt6.QtGui import QColor, QPen
from PyQt6.QtWidgets import QHBoxLayout, QPushButton, QSizePolicy, QSplitter, QVBoxLayout, QWidget
from PyQt6.QtCharts import QChart, QChartView, QLineSeries

from Views.Training.TrainingInformationView import TrainingInformationView
from Views.WizardTitleView import WizardTitleView
from Views.SwipingPageView import SwipingPageView

class TrainingInProgressView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # We need a title for each state - in-progress, and finished.
        self.title = WizardTitleView(self)
        self.title.setTitle('Training...')
        self.title.setSubtitle(f'''Finetuning... This might take a while.''')

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

        self.xAxis, self.yAxis = self.chart.axes()
        self.xAxis.setRange(0,0)
        self.xAxis.setTitleText("Step")
        self.xAxis.setLabelFormat("%d")
        self.yAxis.setRange(0,0)

        self.chartView = QChartView(self.chart)

        self.trainingInfo = TrainingInformationView(self)

        self.splitter = QSplitter(self)
        self.splitter.addWidget(self.trainingInfo)
        self.splitter.addWidget(self.chartView)

        # Control buttons
        self.genSamplesButton = QPushButton('Generate Samples', self, enabled=False)
        self.saveModelButton = QPushButton('Save Model', self, enabled=False)
        self.stopTrainingButton = QPushButton('Abort Training', self, enabled=False)

        # Done button (for when training is complete)
        self.doneButton = QPushButton('Close', self)
        self.doneButton.setVisible(False)

        self.buttonLy = QHBoxLayout()
        self.buttonLy.addWidget(self.genSamplesButton)
        self.buttonLy.addWidget(self.saveModelButton)
        self.buttonLy.addWidget(self.stopTrainingButton)
        self.buttonLy.addWidget(self.doneButton)

        self.ly = QVBoxLayout(self)
        self.ly.addWidget(self.title, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.ly.addWidget(self.splitter)
        self.ly.addLayout(self.buttonLy)

        self.hyperparams = {}

    def setHyperparameters(self, hyperparams: dict):
        self.hyperparams = hyperparams
        self.title.setSubtitle(f'''Finetuning on \"{self.hyperparams.get('dataset', {}).get('meta', {}).get('title', 'an unknown dataset')}\"... This might take a while.''')

    def onTrainingStarted(self):
        print('Training has started')

    def onTrainingEnded(self):
        self.title.setTitle('Training Complete')
        self.title.setSubtitle(f'''Finetuning on \"{self.hyperparams.get('dataset', {}).get('meta', {}).get('title', 'an unknown dataset')}\" has finished. You can view the statistics on this training session at any time from the Repository view.''')
        self.genSamplesButton.setVisible(False)
        self.saveModelButton.setVisible(False)
        self.stopTrainingButton.setVisible(False)
        self.doneButton.setVisible(True)

    def onSamplesGenerated(self, step, texts):
        self.trainingInfo.onSamplesGenerated(step, texts)

    def onBatchEnded(self, steps, total, loss, avg_loss):
        self.trainingInfo.onBatchEnded(steps, total, avg_loss)
        self.xAxis.setRange(0, total)
        self.yAxis.setRange(0, max(loss, self.yAxis.max()))

        self.lossSeries << QPointF(steps, loss)
        self.avgLossSeries << QPointF(steps, avg_loss)