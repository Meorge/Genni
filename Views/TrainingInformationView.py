from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QFrame, QGridLayout, QSizePolicy, QWidget
from datetime import timedelta

from .LabeledValueView import LabeledValueView
from ATGTrainer import ATGTrainer

COLOR_PURPLE = QColor(180, 170, 255)
COLOR_BLUE = QColor(170, 240, 255)
COLOR_GREEN = QColor(220, 255, 170)
COLOR_YELLOW = QColor(255, 250, 170)

SMOOTHING_FACTOR = 0.005

class TrainingInformationView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.trainer = None

        self.currentStepLabel = LabeledValueView("Current Step", "---", COLOR_PURPLE)
        self.totalStepLabel = LabeledValueView("Total Steps", f"---", COLOR_PURPLE)

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
        self.ly.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeading)

        self.setLayout(self.ly)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)

    def setTrainer(self, trainer: ATGTrainer): self.trainer = trainer

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

        stepsToGen = (total - steps) % self.trainer.genEvery()
        stepsToSave = (total - steps) % self.trainer.saveEvery()
        self.stepsToGenTextLabel.setValue(str(stepsToGen))
        self.stepsToSaveModelLabel.setValue(str(stepsToSave))

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