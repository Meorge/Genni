from PyQt6.QtWidgets import QFileDialog, QHBoxLayout, QLabel, QPushButton, QSizePolicy, QWidget

class FilePicker(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.filenameLabel = QLabel('dataset.txt')
        self.filenameLabel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)

        self.browseButton = QPushButton('Browse...', clicked=self.selectFile)
        self.browseButton.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)

        self.selectedFile = './training.txt'

        self.ly = QHBoxLayout(self)
        self.ly.addWidget(self.filenameLabel)
        self.ly.addWidget(self.browseButton)
        self.ly.setContentsMargins(0,0,0,0)

    def selectFile(self):
        file, ext = QFileDialog.getOpenFileName(self, caption='Select Dataset')
        if file is not None:
            self.selectedFile = file
            self.filenameLabel.setText(file)

    def filepath(self) -> str: return self.selectedFile