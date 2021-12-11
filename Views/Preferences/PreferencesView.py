from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QCheckBox, QComboBox, QFormLayout, QMainWindow, QSizePolicy, QToolBar, QWidget

class PreferencesView(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.toolbar = QToolBar()
        self.toolbar.setMovable(False)
        self.toolbar.setFloatable(False)


        self.expander1 = QWidget()
        self.expander1.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.expander2 = QWidget()
        self.expander2.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.toolbar.addWidget(self.expander1)
        self.toolbar.addAction("General")
        self.toolbar.addAction("Training")
        self.toolbar.addAction("Generation")
        self.toolbar.addAction("Exporting")
        self.toolbar.addWidget(self.expander2)

        self.setUnifiedTitleAndToolBarOnMac(True)

        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.toolbar)

        self.dateFormatComboBox = QComboBox()
        self.dateFormatComboBox.addItem("DD/MM/YY", "ddmmyy")
        self.dateFormatComboBox.addItem("MM/DD/YY", "mmddyy")
        self.dateFormatComboBox.addItem("YYYY/MM/DD", "mmddyy")
        self.dateFormatComboBox.insertSeparator(self.dateFormatComboBox.count() - 1)
        self.dateFormatComboBox.addItem("DD MMMM YYYY", "dd mmmm yyyy")
        self.dateFormatComboBox.addItem("MMMM DD, YYYY", "mmmm dd yyyy")

        self.use24HourTimeCheckBox = QCheckBox("Use 24-hour time")
        self.ly = QFormLayout()
        self.ly.addRow("Date format:", self.dateFormatComboBox)
        self.ly.addWidget(self.use24HourTimeCheckBox)


        self.w = QWidget()
        self.w.setLayout(self.ly)
        self.setCentralWidget(self.w)

