from PyQt6.QtCharts import QChart, QChartView, QLineSeries
from PyQt6.QtCore import QPointF, QSize, Qt
from PyQt6.QtGui import QColor, QColorConstants, QPen
from PyQt6.QtWidgets import QFrame, QGridLayout, QLabel, QSizePolicy, QSplitter, QTextEdit, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget
from ModelRepo import getDurationString, getModelStepData
from Preferences import getDateTimeFormatString
from Views.Colors import COLOR_BLUE, COLOR_GREEN, COLOR_PURPLE, COLOR_RED, COLOR_YELLOW
from Views.LabeledValueView import LabeledValueView
from datetime import datetime, timedelta

# TODO: Make this a subclassable thing?
class RepositoryModelDetailView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Title label
        self.titleLabel = QLabel('Name of Model', parent=self)
        self.titleFont = self.titleLabel.font()
        self.titleFont.setBold(True)
        self.titleFont.setPointSizeF(self.titleFont.pointSizeF() * 1.5)
        self.titleLabel.setFont(self.titleFont)
        
        # Training date
        self.dateLabel = QLabel('')

        self.titleLabel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.dateLabel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        # Left-hand side:
        # - Duration
        # - Total Steps
        # - Average Loss
        # - Change in Average Loss
        self.modelStats = RepositoryModelDetailStatsView(self)

        # Right-hand side:
        # the graph
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

        self.statsSplitter = QSplitter(self)
        self.statsSplitter.addWidget(self.modelStats)
        self.statsSplitter.addWidget(self.chartView)
        self.statsSplitter.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.ly = QVBoxLayout(self)
        self.ly.addWidget(self.titleLabel, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeading)
        self.ly.addWidget(self.dateLabel, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeading)
        self.ly.addWidget(self.statsSplitter)

    def setData(self, repoName: str, data: dict):
        self.titleLabel.setText(data.get('name', 'Unnamed Model'))
        self.dateLabel.setText(datetime.fromisoformat(data.get('datetime', '1970-01-01T00:00:00')).strftime(getDateTimeFormatString()))

        self.lossSeries.clear()
        self.avgLossSeries.clear()
        stepData = getModelStepData(repoName, data['filePath'])

        if stepData is not None:
            for i in stepData:
                elapsed, steps, loss, avgLoss = i

                self.xAxis.setRange(0, data['steps'])
                self.yAxis.setRange(0, max(loss, self.yAxis.max()))

                self.lossSeries << QPointF(steps, loss)
                self.avgLossSeries << QPointF(steps, avgLoss)

            data['avgLoss'] = stepData[-1][3]
        self.modelStats.setData(data)



class RepositoryModelDetailStatsView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.durationLabel = LabeledValueView('Duration', '--:--:--', COLOR_GREEN)
        self.totalStepsLabel = LabeledValueView('Total Steps', '---', COLOR_PURPLE)

        self.learningRateLabel = LabeledValueView('Learning Rate', '---', COLOR_RED)

        self.avgLossLabel = LabeledValueView('Avg. Loss', '---', COLOR_YELLOW)

        self.outputTreeView = QTreeWidget(self, currentItemChanged=self.onSelectedOutputChanged)
        self.outputTreeView.setHeaderHidden(True)

        self.outputTextView = QTextEdit(self)
        self.outputTextView.setReadOnly(True)

        self.outputSplitter = QSplitter(Qt.Orientation.Vertical, self)
        self.outputSplitter.addWidget(self.outputTreeView)
        self.outputSplitter.addWidget(self.outputTextView)

        self.ly = QGridLayout(self)
        self.row = 0
        self.addDivider()
        self.addRow(self.durationLabel, self.avgLossLabel)
        self.addDivider()
        self.addRow(self.learningRateLabel, self.totalStepsLabel)
        self.addDivider()
        self.ly.addWidget(self.outputSplitter, self.row, 0, 1, 2)
        self.ly.setContentsMargins(0,11,11,11)

    def addRow(self, widget1: QWidget, widget2: QWidget):
        self.ly.addWidget(widget1, self.row, 0, Qt.AlignmentFlag.AlignTop)
        self.ly.addWidget(widget2, self.row, 1, Qt.AlignmentFlag.AlignTop)
        self.row += 1

    def addDivider(self):
        line = QFrame(self)
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        self.ly.addWidget(line, self.row, 0, 1, 2)
        self.row += 1

    def setData(self, data: dict):
        durationString = '---'
        if data.get('duration') is not None:
            durationString = getDurationString(timedelta(seconds=data.get('duration')))
        self.totalStepsLabel.setValue(str(data.get('steps', '---')))
        self.durationLabel.setValue(durationString)
        self.learningRateLabel.setValue(str(data.get('learningRate', '---')))
        self.avgLossLabel.setValue(f'''{data.get('avgLoss', 0):.2f}''')

        # Set up tree for viewing samples
        self.outputTreeView.clear()

        keys = [int(key) for key in data.get('samples', {}).keys()]
        for key in sorted(keys):
            sampleGroupName = str(key)
            sampleGroup = data.get('samples', {}).get(sampleGroupName)
            topLevelItem = QTreeWidgetItem([sampleGroupName])
            for text in sampleGroup:
                subItem = QTreeWidgetItem(topLevelItem, [text.replace('\n', '')])
                subItem.setData(0, Qt.ItemDataRole.UserRole, text)
            self.outputTreeView.addTopLevelItem(topLevelItem)

    def onSelectedOutputChanged(self, current: QTreeWidgetItem, previous: QTreeWidgetItem):
        if current is None: return
        data = current.data(0, Qt.ItemDataRole.UserRole)
        if data is not None:
            self.outputTextView.setPlainText(data)