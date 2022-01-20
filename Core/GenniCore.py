from typing import List, Tuple
from PyQt6.QtCore import QCoreApplication, QSettings, QThread
from PyQt6.QtGui import QIcon, QKeySequence, QAction
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu

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

        self.__jobs: List[Tuple[QAction, QThread]] = []

        self.setQuitOnLastWindowClosed(False)

        QCoreApplication.setOrganizationName("malcolminyo")
        QCoreApplication.setApplicationName("Genni")

        self.__settings = QSettings()
        self.setupSystemTrayIcon()

        from Views.RepositoryWindow import RepositoryWindow
        self.__window = RepositoryWindow()
        self.toggleWindowVisibility()

    def setupSystemTrayIcon(self):
        self.__systemTrayIcon = QSystemTrayIcon(QIcon('./Icons/Train.svg'), self)

        # Set up menu for system tray
        self.__systemTrayMenu = QMenu()

        # Placeholder item, for when nothing is happening
        self.__noOperationsInProgressAction = self.__systemTrayMenu.addAction("No operations in progress")
        self.__noOperationsInProgressAction.setEnabled(False)

        self.__separatorAction = self.__systemTrayMenu.addSeparator()

        self.__toggleWindowAction = self.__systemTrayMenu.addAction("Show Window", self.toggleWindowVisibility)

        self.__quitAction = self.__systemTrayMenu.addAction("Quit Genni", self.quit)
        self.__quitAction.setShortcut(QKeySequence.StandardKey.Quit)

        self.__systemTrayIcon.setContextMenu(self.__systemTrayMenu)

        self.__systemTrayIcon.show()

    def toggleWindowVisibility(self):
        if self.__window.isHidden(): self.showWindow()
        else: self.hideWindow()

    def showWindow(self):
        self.__window.show()
        self.__toggleWindowAction.setText("Hide Window")

    def hideWindow(self):
        self.__window.hide()
        self.__toggleWindowAction.setText("Show Window")

    def getDateTimeFormatString(self) -> str:
        output = self.dateFormats.get(self.__settings.value('datetime/dateFormat', 'ddmmyy'), 'ddmmyy')
        output += ', '
        output += self.use24HourTimeFormats.get(self.__settings.value('datetime/use24HourTime', False), False)
        return output

    def addJob(self, job):
        newJobItemAction = QAction(QIcon('./Icons/Train.svg'), job.name())
        self.__systemTrayMenu.insertAction(self.__separatorAction, newJobItemAction)
        self.__jobs.append((newJobItemAction, job))

        self.__noOperationsInProgressAction.setVisible(False)

    def removeJob(self, job):
        action: QAction = None
        for maybeAction, maybeJob in self.__jobs:
            if job == maybeJob:
                action = maybeAction
                break
        
        self.__jobs.remove((action, job))

        if action is None:
            print("Couldn't find the action corresponding to this job...")
            return

        self.__systemTrayMenu.removeAction(action)

        if len(self.__jobs) == 0:
            self.__noOperationsInProgressAction.setVisible(True)
        

    @classmethod
    def instance(cls) -> 'GenniCore':
        return QCoreApplication.instance()