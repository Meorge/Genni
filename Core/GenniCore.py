from PyQt6.QtCore import QCoreApplication, QSettings
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon

class GenniCore(QApplication):
    dateFormats = {
        'ddmmyy': '%d/%m/%y',
        'mmddyy': '%m/%d/%y',
        'yyyymmdd': '%Y/%m/%d',
        'dd mmmm yyyy': '%d %B %Y',
        'mmmm dd yyyy': '%B %d, %Y'
    }

    use24HourTimeFormats = {
        True: '%H:%M',
        False: '%I:%M %p'
    }
    def __init__(self, args = None):
        super().__init__(args)

        QCoreApplication.setOrganizationName("malcolminyo")
        QCoreApplication.setApplicationName("Genni")

        self.__settings = QSettings()
        self.setupSystemTrayIcon()

    def setupSystemTrayIcon(self):
        self.__systemTrayIcon = QSystemTrayIcon(QIcon('./Icons/Train.svg'), self)
        self.__systemTrayIcon.show()

    def getDateTimeFormatString(self) -> str:
        output = self.dateFormats.get(self.__settings.value('datetime/dateFormat', 'ddmmyy'), 'ddmmyy')
        output += ', '
        output += self.use24HourTimeFormats.get(self.__settings.value('datetime/use24HourTime', False), False)
        return output

    @classmethod
    def instance(cls) -> 'GenniCore':
        return QCoreApplication.instance()