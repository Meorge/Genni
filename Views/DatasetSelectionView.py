from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QComboBox, QDialog
from Views.ImportDatasetView import ImportDatasetModal
from ModelRepo import getDatasetsInRepository

class DatasetSelectionView(QComboBox):
    datasetChanged = pyqtSignal(dict)

    def __init__(self, parent=None, repoName=None):
        super().__init__(parent)
        self.currentIndexChanged.connect(self.onCurrentIndexChanged)
        self.__repository = repoName
        self.__lastValidIndex = 0
        self.setupItems()

    def setupItems(self):
        self.blockSignals(True)
        self.clear()

        datasetsInRepository = getDatasetsInRepository(self.__repository)

        if len(datasetsInRepository) == 0:
            self.addItem('No datasets added', None)
            self.model().item(0).setEnabled(False)
        else:
            for dataset in datasetsInRepository:
                self.addItem(f'''{dataset['meta']['title']}''', dataset)

        self.addItem('Add dataset...', None)
        self.insertSeparator(self.count() - 1)
        self.blockSignals(False)

    def onCurrentIndexChanged(self, index: int):
        print(f'{self.currentIndex()}, {index}')
        indexOfAddDataset = self.count() - 1
        if index == indexOfAddDataset:
            print('time to add a dataset')
            self.bla = ImportDatasetModal(self, repoName=self.__repository)
            result = self.bla.exec()
            print(f'result of dataset adder thing: {result}')

            if result == QDialog.DialogCode.Accepted:
                self.setupItems()
                self.setCurrentIndex(0)
            else:
                self.setCurrentIndex(self.__lastValidIndex)
        else:
            self.__lastValidIndex = index

        self.datasetChanged.emit(self.dataset())

    def dataset(self) -> str:
        return self.currentData(Qt.ItemDataRole.UserRole)