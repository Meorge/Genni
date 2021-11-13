from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QHBoxLayout, QLineEdit, QPushButton, QVBoxLayout, QWidget
from Views.ButtonWithIconAndDetailView import ButtonWithIconAndDetailView
from Views.WizardTitleView import WizardTitleView

class TrainingFreshModelView(QWidget):
    makeModelFromScratch = pyqtSignal()
    baseModelOnOpenAI = pyqtSignal()
    baseModelOnHuggingFace = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.title = WizardTitleView(self)
        self.title.setTitle('Initialize Repository')
        self.title.setSubtitle('Choose a a base for the new model repository.')

        self.fromScratchButton = ButtonWithIconAndDetailView(title='From scratch', desc='Train a fresh model, using only your datasets.', svg='Icons/New.svg', parent=self)
        self.fromOpenAIButton = ButtonWithIconAndDetailView(title='OpenAI GPT-2', desc='Use an OpenAI GPT-2 model as a base.', svg='Icons/OpenAI.svg', parent=self)
        self.fromHuggingFaceButton = ButtonWithIconAndDetailView(title='Hugging Face Repository', desc='Use a repository from Hugging Face as a base.', svg='Icons/Hugging Face.svg', parent=self)
        self.nextButton = QPushButton('Next', clicked=self.proceed)

        self.fromScratchButton.setChecked(True)

        self.ly = QVBoxLayout(self)
        self.ly.addWidget(self.title, alignment=Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        self.ly.addWidget(self.fromScratchButton)
        self.ly.addWidget(self.fromOpenAIButton)
        self.ly.addWidget(self.fromHuggingFaceButton)
        self.ly.addStretch()
        self.ly.addWidget(self.nextButton)

    def proceed(self):
        if self.fromScratchButton.isChecked():
            self.makeModelFromScratch.emit()
        elif self.fromOpenAIButton.isChecked():
            self.baseModelOnOpenAI.emit()
        elif self.fromHuggingFaceButton.isChecked():
            self.baseModelOnHuggingFace.emit()


class TrainingFreshModelGPT2SizeView(QWidget):
    goBack = pyqtSignal()
    modelSizeChosen = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.title = WizardTitleView(self)
        self.title.setTitle('Select OpenAI GPT-2 Model Size')
        self.title.setSubtitle('Choose the size of the OpenAI GPT-2 model you\'d like to use as a base. Larger models will take up more space on your computer, but may provide more varied output.')

        self.smallModelButton = ButtonWithIconAndDetailView(title='Small (124M)', svg='Icons/OpenAI.svg', parent=self)
        self.mediumModelButton = ButtonWithIconAndDetailView(title='Medium (355M)', svg='Icons/OpenAI.svg', parent=self)
        self.largeModelButton = ButtonWithIconAndDetailView(title='Large (774M)', svg='Icons/OpenAI.svg', parent=self)
        self.xlModelButton = ButtonWithIconAndDetailView(title='Extra Large (1558M)', svg='Icons/OpenAI.svg', parent=self)

        self.backButton = QPushButton('Back', clicked=self.goBack)
        self.nextButton = QPushButton('Next', clicked=self.onModelSizeChosen)

        self.smallModelButton.setChecked(True)

        self.ly = QVBoxLayout(self)
        self.ly.addWidget(self.title, alignment=Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        self.ly.addWidget(self.smallModelButton)
        self.ly.addWidget(self.mediumModelButton)
        self.ly.addWidget(self.largeModelButton)
        self.ly.addWidget(self.xlModelButton)
        self.ly.addStretch()

        self.btnLy = QHBoxLayout()
        self.btnLy.addWidget(self.backButton)
        self.btnLy.addWidget(self.nextButton)
        self.btnLy.setContentsMargins(0,0,0,0)
        self.ly.addLayout(self.btnLy)

    def onModelSizeChosen(self):
        modelSize = None
        if self.smallModelButton.isChecked(): modelSize = '124M'
        elif self.mediumModelButton.isChecked(): modelSize = '355M'
        elif self.largeModelButton.isChecked(): modelSize = '774M'
        elif self.xlModelButton.isChecked(): modelSize = '1558M'
        self.modelSizeChosen.emit({ 'tf_gpt2': modelSize })

class SelectHuggingFaceRepoView(QWidget):
    goBack = pyqtSignal()
    huggingFaceRepoChosen = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.title = WizardTitleView(self)
        self.title.setTitle('Select Hugging Face Repository')
        self.title.setSubtitle('Type the name of the Hugging Face repository you\'d like to base your model on.')

        self.repoEdit = QLineEdit()

        self.backButton = QPushButton('Back', clicked=self.goBack)
        self.nextButton = QPushButton('Next', clicked=self.onModelSizeChosen)

        self.ly = QVBoxLayout(self)
        self.ly.addWidget(self.title, alignment=Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        self.ly.addWidget(self.repoEdit)
        self.ly.addStretch()

        self.btnLy = QHBoxLayout()
        self.btnLy.addWidget(self.backButton)
        self.btnLy.addWidget(self.nextButton)
        self.btnLy.setContentsMargins(0,0,0,0)
        self.ly.addLayout(self.btnLy)

    def onModelSizeChosen(self):
        self.huggingFaceRepoChosen.emit({ 'model': self.repoEdit.text() })