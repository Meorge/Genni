from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QComboBox, QDialog
from Views.ImportDatasetView import ImportDatasetModal
from ModelRepo import getDatasetsInRepository

class DatasetSelectionView(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.currentIndexChanged.connect(self.onCurrentIndexChanged)
        self.__repository = './my_model'
        self.__lastValidIndex = 0
        self.setupItems()

    def setupItems(self):
        self.blockSignals(True)
        self.clear()

        for dataset in getDatasetsInRepository(self.__repository):
            self.addItem(f'''{dataset['meta']['title']}''', dataset)

        self.addItem('Add dataset...')
        self.insertSeparator(self.count() - 1)
        self.blockSignals(False)

    def onCurrentIndexChanged(self, index: int):
        print(f'{self.currentIndex()}, {index}')
        indexOfAddDataset = self.count() - 1
        if index == indexOfAddDataset:
            print('time to add a dataset')
            self.bla = ImportDatasetModal(self)
            result = self.bla.exec()
            print(f'result of dataset adder thing: {result}')

            if result == QDialog.DialogCode.Accepted:
                self.setupItems()
                self.setCurrentIndex(0)
            else:
                self.setCurrentIndex(self.__lastValidIndex)
        else:
            self.__lastValidIndex = index

    def dataset(self) -> str:
        return self.currentData(Qt.ItemDataRole.UserRole)