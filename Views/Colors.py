from PyQt6.QtGui import QColor

COLOR_PURPLE = { 'dark': QColor(180, 170, 255), 'light': QColor(125, 35, 230) }
COLOR_BLUE = { 'dark': QColor(170, 240, 255), 'light': QColor(40, 90, 255) }
COLOR_GREEN = { 'dark': QColor(220, 255, 170), 'light': QColor(120, 195, 10) }
COLOR_YELLOW = { 'dark': QColor(255, 250, 170), 'light': QColor(220, 115, 10) }
COLOR_RED = { 'dark': QColor(255, 175, 180), 'light': QColor(210, 25, 37) }

def lerpColor(a: QColor, b: QColor, t: float) -> QColor:
    lerpedR = lerp(a.redF(), b.redF(), t)
    lerpedG = lerp(a.greenF(), b.greenF(), t)
    lerpedB = lerp(a.blueF(), b.blueF(), t)

    color = QColor()
    color.setRedF(lerpedR)
    color.setGreenF(lerpedG)
    color.setBlueF(lerpedB)
    return color

def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t