from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QComboBox
from Views.ImportDatasetView import ImportDatasetModal
from ModelRepo import getDatasetsInRepository

class DatasetSelectionView(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.currentIndexChanged.connect(self.onCurrentIndexChanged)
        self.__repository = './my_model'
        self.setupItems()

    def setupItems(self):
        self.blockSignals(True)
        self.clear()

        for dataset in getDatasetsInRepository(self.__repository):
            self.addItem(f'''{dataset['meta']['title']} - \"{dataset['meta']['originalFilename']}\"''', dataset)

        self.addItem('Add dataset...')
        self.insertSeparator(self.count() - 1)
        self.blockSignals(False)

    def onCurrentIndexChanged(self, index: int):
        indexOfAddDataset = self.count() - 1
        if index == indexOfAddDataset:
            print('time to add a dataset')
            self.bla = ImportDatasetModal(self)
            self.bla.exec()

    def dataset(self) -> str:
        return self.currentData(Qt.ItemDataRole.UserRole)