from PyQt6.QtGui import QColor

COLOR_PURPLE = QColor(180, 170, 255)
COLOR_BLUE = QColor(170, 240, 255)
COLOR_GREEN = QColor(220, 255, 170)
COLOR_YELLOW = QColor(255, 250, 170)
COLOR_RED = QColor(255, 175, 180)

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