from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QFrame, QGridLayout, QPlainTextEdit, QSizePolicy, QSplitter, QTreeView, QTreeWidget, QTreeWidgetItem, QWidget
from datetime import timedelta
from Threads.ATGTrainer import ATGTrainer

from ModelRepo import getDurationString

from Views.LabeledValueView import LabeledValueView
from Views.Colors import *

SMOOTHING_FACTOR = 0.005

class TrainingInformationView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.trainer: ATGTrainer = None

        self.currentStepLabel = LabeledValueView("Current Step", "---", COLOR_PURPLE)
        self.totalStepLabel = LabeledValueView("Total Steps", f"---", COLOR_PURPLE)

        self.timeElapsedLabel = LabeledValueView("Elapsed", "--:--:--", COLOR_GREEN)
        self.timeRemainingLabel = LabeledValueView("Remaining", "--:--:--", COLOR_GREEN)

        self.currentLossLabel = LabeledValueView("Loss", "-.--", COLOR_YELLOW)
        self.avgLossLabel = LabeledValueView("Avg. Loss", "-.--", COLOR_YELLOW)

        self.stepsToGenTextLabel = LabeledValueView("Next Samples", "---", COLOR_BLUE)
        self.stepsToSaveModelLabel = LabeledValueView("Next Save", "---", COLOR_BLUE)

        self.outputTreeView = QTreeWidget(self, currentItemChanged=self.onSelectedOutputChanged)
        self.outputTreeView.setHeaderHidden(True)

        self.outputTextView = QPlainTextEdit(self)
        self.outputTextView.setReadOnly(True)

        self.outputSplitter = QSplitter(Qt.Orientation.Vertical, self)
        self.outputSplitter.addWidget(self.outputTreeView)
        self.outputSplitter.addWidget(self.outputTextView)

        self.ly = QGridLayout(self)

        self.currentGridRow = 0
        self.addRow(self.currentStepLabel, self.totalStepLabel)
        self.addDivider()
        self.addRow(self.stepsToGenTextLabel, self.stepsToSaveModelLabel)
        self.addDivider()
        self.addRow(self.timeElapsedLabel, self.timeRemainingLabel)
        self.addDivider()
        self.addRow(self.avgLossLabel, self.currentLossLabel)
        self.addDivider()
        self.ly.addWidget(self.outputSplitter, self.currentGridRow, 0, 1, 2)
        self.ly.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeading)

        self.setLayout(self.ly)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)

        self.steps = 0
        self.totalSteps = 0

    def setTrainer(self, trainer: ATGTrainer):
        self.trainer = trainer

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

    def onBatchEnded(self, steps, total, loss, avg_loss):
        self.steps = steps
        self.totalSteps = total
        self.currentStepLabel.setValue(str(steps))
        self.totalStepLabel.setValue(str(total))

        stepsToGen = (total - steps) % self.trainer.config()['genEvery']
        stepsToSave = (total - steps) % self.trainer.config()['saveEvery']
        self.stepsToGenTextLabel.setValue(str(stepsToGen))
        self.stepsToSaveModelLabel.setValue(str(stepsToSave))

        self.avgLossLabel.setValue(f'{avg_loss:.2f}')
        self.currentLossLabel.setValue(f'{loss:.2f}')

    def onSamplesGenerated(self, step, texts):
        item = QTreeWidgetItem([f'{step}'])
        for i in texts:
            iWithoutLinebreaks = i.replace("\n", " ")
            subItem = QTreeWidgetItem(item, [iWithoutLinebreaks])
            subItem.setData(0, Qt.ItemDataRole.UserRole, i)

        self.outputTreeView.addTopLevelItem(item)

    def onSelectedOutputChanged(self, current: QTreeWidgetItem, previous: QTreeWidgetItem):
        data = current.data(0, Qt.ItemDataRole.UserRole)
        if data is not None:
            self.outputTextView.setPlainText(data)

    def onTimePassed(self, passed: timedelta):
        self.timeElapsedLabel.setValue(getDurationString(passed))

        if passed.total_seconds() == 0 or self.steps == 0:
            self.timeRemainingLabel.setValue('--:--:--')
        else:
            lastSpeed = self.steps / passed.total_seconds()

            remainingSteps = self.totalSteps - self.steps

            remaining = timedelta(seconds=remainingSteps / lastSpeed)
            self.timeRemainingLabel.setValue(getDurationString(remaining))