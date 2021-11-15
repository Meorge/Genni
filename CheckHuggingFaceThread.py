from PyQt6.QtCore import QThread, pyqtSignal
import requests

class CheckHuggingFaceThread(QThread):
    result = pyqtSignal(bool)

    __modelName: str = ''
    def modelName(self) -> str: return self.__modelName
    def setModelName(self, modelName: str): self.__modelName = modelName

    def __init__(self, parent=None):
        super().__init__(parent)

    def run(self):
        r = requests.get(f'https://huggingface.co/api/models/{self.modelName()}')
        print(f'Request finished with code {r.status_code} and text {r.text}')
        self.result.emit(r.status_code == 200)