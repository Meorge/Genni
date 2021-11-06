from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QColor, QPen
from PyQt6.QtWidgets import QHBoxLayout, QPushButton, QSizePolicy, QSplitter, QVBoxLayout, QWidget
from PyQt6.QtCharts import QChart, QChartView, QLineSeries

from Views.TrainingInformationView import TrainingInformationView
from Views.WizardTitleView import WizardTitleView

class TrainingInProgressView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
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
        self.genSamplesButton = QPushButton('Generate Samples', self)
        self.saveModelButton = QPushButton('Save Model', self)
        self.stopTrainingButton = QPushButton('Abort Training', self)
        self.buttonLy = QHBoxLayout()
        self.buttonLy.addWidget(self.genSamplesButton)
        self.buttonLy.addWidget(self.saveModelButton)
        self.buttonLy.addWidget(self.stopTrainingButton)

        self.ly = QVBoxLayout(self)
        self.ly.addWidget(self.title, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.ly.addWidget(self.splitter)
        self.ly.addLayout(self.buttonLy)

    def setHyperparameters(self, hyperparams: dict):
        self.title.setSubtitle(f'''Finetuning on \"{hyperparams['dataset']['meta']['title']}\"... This might take a while.''')

    def onTrainingStarted(self):
        pass

    def onTrainingEnded(self):
        pass

    def onSamplesGenerated(self, step, texts):
        self.trainingInfo.onSamplesGenerated(step, texts)

    def onBatchEnded(self, steps, total, loss, avg_loss):
        self.trainingInfo.onBatchEnded(steps, total, avg_loss)
        self.xAxis.setRange(0, total)
        self.yAxis.setRange(0, max(loss, self.yAxis.max()))

        self.lossSeries << QPointF(steps, loss)
        self.avgLossSeries << QPointF(steps, avg_loss)