from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QColor, QPen
from PyQt5.QtWidgets import QSizePolicy, QSplitter, QVBoxLayout
from PyQt5.QtChart import QChart, QChartView, QLineSeries

from .TrainingInformationView import TrainingInformationView

class TrainingInProgressView(QSplitter):
    def __init__(self, parent=None):
        super().__init__(parent)
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

        self.chartView = QChartView(self.chart)

        self.trainingInfo = TrainingInformationView(self)

        self.addWidget(self.trainingInfo)
        self.addWidget(self.chartView)
    

    def onTrainingStarted(self):
        pass

    def onTrainingEnded(self):
        pass

    def onSamplesGenerated(self, step, texts):
        self.trainingInfo.onSamplesGenerated(step, texts)

    def onBatchEnded(self, steps, total, loss, avg_loss):
        self.trainingInfo.onBatchEnded(steps, total, avg_loss)
        self.chart.axisX().setRange(0, total)
        self.chart.axisY().setRange(0, max(loss, self.chart.axisY(self.lossSeries).max()))

        self.lossSeries << QPointF(steps, loss)
        self.avgLossSeries << QPointF(steps, avg_loss)