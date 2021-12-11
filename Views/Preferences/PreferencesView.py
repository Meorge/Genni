from PyQt6.QtCore import QSettings, Qt, pyqtSignal
from PyQt6.QtWidgets import QCheckBox, QComboBox, QFormLayout, QLabel, QMainWindow, QSizePolicy, QToolBar, QWidget

"""
TODO:
- Load date format value from settings
- When date format is changed, save to settings
- When date format is changed, update the main views with new date format
"""

class PreferencesView(QMainWindow):
    prefsModified = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.settings = QSettings()

        self.setWindowTitle("Preferences")

        self.dateFormatComboBox = QComboBox(currentIndexChanged=self.onDateFormatChanged)
        self.dateFormatComboBox.blockSignals(True)
        self.dateFormatComboBox.addItem("DD/MM/YY", "ddmmyy")
        self.dateFormatComboBox.addItem("MM/DD/YY", "mmddyy")
        self.dateFormatComboBox.addItem("YYYY/MM/DD", "yyyymmdd")
        self.dateFormatComboBox.insertSeparator(self.dateFormatComboBox.count())
        self.dateFormatComboBox.addItem("DD MMMM YYYY", "dd mmmm yyyy")
        self.dateFormatComboBox.addItem("MMMM DD, YYYY", "mmmm dd yyyy")
        self.dateFormatComboBox.blockSignals(False)

        self.use24HourTimeCheckBox = QCheckBox("Use 24-hour time", toggled=self.onUse24HourTimeChanged)

        self.ly = QFormLayout()
        self.ly.addRow("Date format:", self.dateFormatComboBox)
        self.ly.addWidget(self.use24HourTimeCheckBox)

        self.w = QWidget()
        self.w.setLayout(self.ly)
        self.setCentralWidget(self.w)

    def show(self):
        print("show preferences")
        super().show()
        self.setDefaultValues()

    def onDateFormatChanged(self):
        dateFormat = self.dateFormatComboBox.currentData(Qt.ItemDataRole.UserRole)
        print(f'Set date format to {dateFormat}')
        self.settings.setValue("datetime/dateFormat", dateFormat)
        self.prefsModified.emit()

    def onUse24HourTimeChanged(self):
        self.settings.setValue("datetime/use24HourTime", self.use24HourTimeCheckBox.isChecked())
        self.prefsModified.emit()

    def setDefaultValues(self):
        dateFormat = self.settings.value("datetime/dateFormat", "ddmmyy")
        use24HourTime = self.settings.value("datetime/use24HourTime", False)

        print(f'date format: {dateFormat}, use 24h time: {use24HourTime}')
        # Set date format
        
        self.dateFormatComboBox.setCurrentIndex(self.dateFormatComboBox.findData(dateFormat))

        # Set use 24-hour time
        
        self.use24HourTimeCheckBox.setChecked(use24HourTime)

