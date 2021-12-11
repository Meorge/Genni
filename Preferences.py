from PyQt6.QtCore import QSettings

settings = None

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

def initializeSettings():
    global settings
    settings = QSettings()
    print(f'Initialized settings with name {settings.applicationName()}')

def getDateTimeFormatString() -> str:
    output = dateFormats.get(settings.value('datetime/dateFormat', 'ddmmyy'), 'ddmmyy')
    output += ', '
    output += use24HourTimeFormats.get(settings.value('datetime/use24HourTime', False), False)
    return output