"""Non-linear animations for modern UI."""

from PyQt5.QtCore import (
    QPropertyAnimation, QEasingCurve, QPoint, 
    QParallelAnimationGroup, QSequentialAnimationGroup
)
from PyQt5.QtWidgets import QWidget


class Easing:
    """Common easing curves."""
    EASE_OUT_CUBIC = QEasingCurve.OutCubic
    EASE_OUT_BACK = QEasingCurve.OutBack
    EASE_OUT_ELASTIC = QEasingCurve.OutElastic
    EASE_IN_OUT_QUAD = QEasingCurve.InOutQuad
    SPRING = QEasingCurve.OutBack


def fade_in(widget, duration=300):
    """Fade in animation."""
    effect = widget.graphicsEffect()
    if not effect:
        from PyQt5.QtWidgets import QGraphicsOpacityEffect
        effect = QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(effect)
    anim = QPropertyAnimation(effect, b"opacity")
    anim.setDuration(duration)
    anim.setStartValue(0)
    anim.setEndValue(1)
    anim.setEasingCurve(Easing.EASE_OUT_CUBIC)
    return anim


def slide_up(widget, distance=50, duration=400):
    """Slide up with spring effect."""
    anim = QPropertyAnimation(widget, b"pos")
    anim.setDuration(duration)
    start = widget.pos()
    anim.setStartValue(QPoint(start.x(), start.y() + distance))
    anim.setEndValue(start)
    anim.setEasingCurve(Easing.EASE_OUT_BACK)
    return anim


def throw_up(widget, start_y, end_y, duration=500):
    """Throw animation with arc."""
    anim = QPropertyAnimation(widget, b"pos")
    anim.setDuration(duration)
    anim.setEasingCurve(Easing.EASE_OUT_CUBIC)
    return anim


class ProgressSpinner:
    """Non-linear progress spinner."""
    
    @staticmethod
    def create_rotation(widget, duration=1000):
        anim = QPropertyAnimation(widget, b"rotation")
        anim.setDuration(duration)
        anim.setStartValue(0)
        anim.setEndValue(360)
        anim.setEasingCurve(Easing.EASE_IN_OUT_QUAD)
        anim.setLoopCount(-1)
        return anim
